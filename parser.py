"""
Основной парсер сохранений Mewgenics.
"""
import struct
import lz4.block
from binary_reader import BinaryReader
from mutations import MUTATION_DB_BY_PART, CLASS_BONUSES

STAT_NAMES = ["STR", "DEX", "CON", "INT", "SPD", "CHA", "LCK"]

# Маппинг: индекс в T-массиве → ключ части тела
MUTATION_SLOT_TO_PART = {
    0: "texture",
    3: "body",
    8: "head",
    13: "tail",
    18: "legs",
    23: "legs",
    28: "legs",
    33: "legs",
    38: "eyes",
    43: "eyes",
    48: "eyebrows",
    53: "eyebrows",
    58: "ears",
    63: "ears",
    68: "mouth",
}


def decompress_cat_blob(wrapped: bytes) -> bytes:
    """Распаковка LZ4-данных кота."""
    if len(wrapped) < 4:
        raise ValueError("Blob too small")

    uncomp = struct.unpack_from("<I", wrapped, 0)[0]

    if len(wrapped) >= 8:
        comp_len = struct.unpack_from("<I", wrapped, 4)[0]
        if 0 < comp_len <= len(wrapped) - 8:
            stream = wrapped[8:8 + comp_len]
            try:
                return lz4.block.decompress(stream, uncompressed_size=uncomp)
            except Exception:
                pass

    return lz4.block.decompress(wrapped[4:], uncompressed_size=uncomp)


def calculate_mutation_bonuses(visual_mutations: list[tuple[str, int]]) -> list[int]:
    """Рассчитывает бонусы статов от визуальных мутаций."""
    bonuses = [0] * 7

    for part_key, mut_id in visual_mutations:
        part_db = MUTATION_DB_BY_PART.get(part_key)

        if part_db and mut_id in part_db:
            mut_info = part_db[mut_id]
            for stat_idx, bonus_value in mut_info["bonuses"].items():
                if 0 <= stat_idx < 7:
                    bonuses[stat_idx] += bonus_value
        elif 400 <= mut_id <= 442:
            for db in MUTATION_DB_BY_PART.values():
                if mut_id in db:
                    mut_info = db[mut_id]
                    for stat_idx, bonus_value in mut_info["bonuses"].items():
                        if 0 <= stat_idx < 7:
                            bonuses[stat_idx] += bonus_value
                    break

    return bonuses


def clean_gender(gender_str: str | None) -> str:
    """Очищает название пола от цифр и технических символов."""
    if not gender_str:
        return "?"

    g = gender_str.strip().lower()
    g = ''.join(c for c in g if c.isalpha())

    if g.startswith("male"):
        return "male"
    if g.startswith("female"):
        return "female"
    if g in ("spidercat", "ditto", "unknown"):
        return "?"

    return "?" if not g else g


class Cat:
    """Представление кота из сохранения."""

    def __init__(self, blob: bytes, cat_key: int, house_info: dict, adventure_keys: set):
        self.db_key = cat_key
        self.name = "Unknown"
        self.gender = "Unknown"

        # Статус кота
        self.inHouse = cat_key in house_info
        self.onAdventure = cat_key in adventure_keys

        if self.inHouse:
            self.status = "In House"
            self.room = house_info.get(cat_key, "")
        elif self.onAdventure:
            self.status = "Adventure"
            self.room = "Adventure"
        else:
            self.status = "Gone"
            self.room = ""

        # Статы
        self.base_stats = {name: 0 for name in STAT_NAMES}
        self.final_stats = {name: 0 for name in STAT_NAMES}
        self.bonus_stats = {name: 0 for name in STAT_NAMES}
        self.mutation_bonuses = [0] * 7
        self.class_bonuses = [0] * 7
        self.visual_mutations: list[tuple[str, int]] = []
        self.class_name = "Colorless"
        
        # Статы (распределение, модификаторы, вторичные)
        self.stat_allocations = [0] * 7
        self.stat_modifiers = [0] * 7
        self.stat_secondary = [0] * 7

        # Распаковка данных
        try:
            self.decompressed_data = decompress_cat_blob(blob)
        except Exception:
            return

        reader = BinaryReader(self.decompressed_data)

        if len(self.decompressed_data) < 50:
            return

        # Базовые поля
        self.breed_id = reader.u32()
        self.unique_id = reader.u64()
        self.name = reader.utf16str()

        reader.str()
        reader.skip(16)
        self.collar = reader.str()
        reader.u32()
        reader.skip(64)

        # T-массив мутаций (72 элемента)
        T = [reader.u32() for _ in range(72)]
        self.body_parts = {"texture": T[0], "bodyShape": T[3], "headShape": T[8]}

        # Извлекаем мутации с привязкой к части тела
        self.visual_mutations = []
        for slot_idx, part_key in MUTATION_SLOT_TO_PART.items():
            if slot_idx < len(T):
                mut_id = T[slot_idx]
                if mut_id != 0 and mut_id != 0xFFFFFFFF:
                    self.visual_mutations.append((part_key, mut_id))

        reader.skip(12)

        # Пол/голос: структура может быть u32 flag + u64 len + string ИЛИ u64 len + string
        try:
            # Сохраняем позицию
            pos_before = reader.pos
            
            # Пробуем прочитать u32 flag
            flag = reader.u32()
            gender_len = reader.u64()
            
            # Если длина разумная (< 100), читаем строку
            if 0 < gender_len < 100:
                gender_str = self.decompressed_data[reader.pos:reader.pos+gender_len].decode('utf-8', errors='ignore')
                reader.pos += int(gender_len)
                self.gender = clean_gender(gender_str)
            else:
                # Неверная длина, откатываемся и пробуем без flag
                reader.pos = pos_before
                gender_len = reader.u64()
                if 0 < gender_len < 100:
                    gender_str = self.decompressed_data[reader.pos:reader.pos+gender_len].decode('utf-8', errors='ignore')
                    reader.pos += int(gender_len)
                    self.gender = clean_gender(gender_str)
                else:
                    self.gender = "?"
        except:
            self.gender = "?"

        # Возраст (f64)
        try:
            reader.f64()
        except:
            pass

        # Статы
        try:
            self.stat_allocations = [reader.u32() for _ in range(7)]
            self.stat_modifiers = [reader.i32() for _ in range(7)]
            self.stat_secondary = [reader.i32() for _ in range(7)]
        except:
            pass

        # === Поиск класса кота в данных ===
        # Ищем известные названия классов в байтах
        self.class_name = "Colorless"  # класс по умолчанию
        
        known_classes = [b"Fighter", b"Hunter", b"Mage", b"Medic", b"Tank", b"Thief", b"Colorless"]
        for class_bytes in known_classes:
            pos = self.decompressed_data.find(class_bytes)
            if pos != -1:
                self.class_name = class_bytes.decode('utf-8')
                break

        # === Применение бонусов класса ===
        self.class_bonuses = [0] * 7
        if self.class_name in CLASS_BONUSES:
            for stat_idx, bonus in CLASS_BONUSES[self.class_name]["bonuses"].items():
                if 0 <= stat_idx < 7:
                    self.class_bonuses[stat_idx] = bonus

        # Расчёт бонусов от мутаций
        mutation_bonuses = calculate_mutation_bonuses(self.visual_mutations)

        # === Финальный расчёт статов ===
        for i, name in enumerate(STAT_NAMES):
            base = self.stat_allocations[i]
            mod = self.stat_modifiers[i]
            mut = mutation_bonuses[i]
            cls = self.class_bonuses[i]  # Бонусы класса
            sec = self.stat_secondary[i]

            self.base_stats[name] = base
            self.bonus_stats[name] = mod + mut + cls + sec
            self.final_stats[name] = base + mod + mut + cls + sec

        # Навыки
        self.abilities = []
        self.passive_abilities = []
        self.equipment = []

    def to_dict(self):
        return {
            'ID': self.db_key,
            'Имя': self.name or 'Unknown',
            'Класс': self.class_name,
            'В доме': 'Да' if self.inHouse else 'Нет',
            'Комната': self.room,
            'Пол': self.gender,
            **{name: self.base_stats[name] for name in STAT_NAMES},
            **{f'Final_{name}': self.final_stats[name] for name in STAT_NAMES},
            **{f'Bonus_{name}': self.bonus_stats[name] if self.bonus_stats[name] != 0 else ''
               for name in STAT_NAMES},
        }