"""
Основной парсер сохранений Mewgenics.
Теперь использует раздельные базы мутаций по частям тела.
"""
import os
import sqlite3
import struct
import lz4.block
from typing import Optional
from binary_reader import BinaryReader
from mutations import MUTATION_DB_BY_PART

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
    """
    Рассчитывает бонусы статов от визуальных мутаций.

    Args:
        visual_mutations: список кортежей (part_key, mutation_id)

    Returns:
        Список из 7 значений бонусов [STR, DEX, CON, INT, SPD, CHA, LCK]
    """
    bonuses = [0] * 7

    for part_key, mut_id in visual_mutations:
        # Получаем базу данных для этой части тела
        part_db = MUTATION_DB_BY_PART.get(part_key)

        if part_db and mut_id in part_db:
            # Нашли мутацию в базе для этой части тела
            mut_info = part_db[mut_id]
            for stat_idx, bonus_value in mut_info["bonuses"].items():
                if 0 <= stat_idx < 7:
                    bonuses[stat_idx] += bonus_value
        elif 400 <= mut_id <= 442:
            # Универсальные стат-мутации (400-442) работают на любой части тела
            for db in MUTATION_DB_BY_PART.values():
                if mut_id in db:
                    mut_info = db[mut_id]
                    for stat_idx, bonus_value in mut_info["bonuses"].items():
                        if 0 <= stat_idx < 7:
                            bonuses[stat_idx] += bonus_value
                    break

    return bonuses


class Cat:
    """Представление кота из сохранения."""

    def __init__(self, blob: bytes, cat_key: int, house_info: dict, adventure_keys: set):
        self.db_key = cat_key
        self.name = "Unknown"
        self.gender = "Unknown"

        # Проверка статуса кота
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
        self.visual_mutations: list[tuple[str, int]] = []

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

        # Чтение и очистка пола
        self.gender = clean_gender(reader.str())
        reader.f64()  # ← Теперь работает!

        # Статы
        self.stat_allocations = [reader.u32() for _ in range(7)]
        self.stat_modifiers = [reader.i32() for _ in range(7)]
        self.stat_secondary = [reader.i32() for _ in range(7)]

        # Расчёт бонусов от мутаций
        self.mutation_bonuses = calculate_mutation_bonuses(self.visual_mutations)

        # Финальный расчёт статов
        for i, name in enumerate(STAT_NAMES):
            base = self.stat_allocations[i]
            mod = self.stat_modifiers[i]
            mut = self.mutation_bonuses[i]
            sec = self.stat_secondary[i]

            self.base_stats[name] = base
            self.bonus_stats[name] = mod + mut + sec
            self.final_stats[name] = base + mod + mut + sec

        # Навыки
        self.abilities = []
        self.passive_abilities = []
        self.equipment = []

    def to_dict(self):
        return {
            'ID': self.db_key,
            'Имя': self.name or 'Unknown',
            'В доме': 'Да' if self.inHouse else 'Нет',
            'Комната': self.room,
            'Пол': self.gender,
            **{name: self.base_stats[name] for name in STAT_NAMES},
            **{f'Final_{name}': self.final_stats[name] for name in STAT_NAMES},
            **{f'Bonus_{name}': self.bonus_stats[name] if self.bonus_stats[name] != 0 else ''
               for name in STAT_NAMES},
        }


def clean_gender(gender_str):
    """Очищает название пола от цифр и технических символов."""
    if not gender_str:
        return "?"

    g = gender_str.strip().lower()
    g = ''.join(c for c in g if c.isalpha())

    if g.startswith("male"):
        return "male"
    if g.startswith("female"):
        return "female"
    if g == "spidercat" or g == "ditto":
        return "?"

    return "?" if not g else g


def get_house_info(conn) -> dict:
    """Получить информацию о комнатах котов."""
    house_info = {}
    try:
        row = conn.execute("SELECT data FROM files WHERE key = 'house_state'").fetchone()
        if not row or len(row[0]) < 8:
            return house_info
        data = row[0]
        count = struct.unpack_from('<I', data, 4)[0]
        pos = 8
        for _ in range(count):
            if pos + 8 > len(data):
                break
            cat_key = struct.unpack_from('<I', data, pos)[0]
            pos += 8
            room_len = struct.unpack_from('<I', data, pos)[0]
            pos += 8
            room_name = ""
            if room_len > 0:
                room_name = data[pos:pos + room_len].decode('ascii', errors='ignore')
                pos += room_len
            pos += 24
            house_info[cat_key] = room_name
    except Exception:
        pass
    return house_info


def get_adventure_keys(conn) -> set:
    """Получить ключи котов на приключении."""
    keys = set()
    try:
        row = conn.execute("SELECT data FROM files WHERE key = 'adventure_state'").fetchone()
        if not row or len(row[0]) < 8:
            return keys
        data = row[0]
        count = struct.unpack_from('<I', data, 4)[0]
        pos = 8
        for _ in range(count):
            if pos + 8 > len(data):
                break
            val = struct.unpack_from('<Q', data, pos)[0]
            pos += 8
            cat_key = (val >> 32) & 0xFFFF_FFFF
            if cat_key:
                keys.add(cat_key)
    except Exception:
        pass
    return keys


def find_save_file() -> str | None:
    """Автоматический поиск файла сохранения."""
    home = os.path.expanduser('~')
    possible_bases = [
        os.path.join(home, 'AppData', 'Roaming', 'Glaiel Games', 'Mewgenics'),
        os.path.join(home, 'AppData', 'LocalLow', 'Kitfox Games', 'Mewgenics'),
        os.path.join(home, 'AppData', 'LocalLow', 'Glaiel Games', 'Mewgenics'),
        os.path.join(home, 'AppData', 'Roaming', 'Kitfox Games', 'Mewgenics'),
    ]

    for base_path in possible_bases:
        if os.path.exists(base_path):
            try:
                folders = [f for f in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, f))]
                for folder in folders:
                    if folder.isdigit() and len(folder) > 10:
                        save_path = os.path.join(base_path, folder, 'saves', 'steamcampaign01.sav')
                        if os.path.exists(save_path):
                            return save_path
            except Exception:
                continue
    return None


def parse_all(path: str) -> list[dict]:
    """Парсинг всех котов из сохранения."""
    if not os.path.exists(path):
        print(f"❌ Файл не найден: {path}")
        return []

    try:
        conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
        print("✓ Подключение к базе данных успешно")
    except sqlite3.DatabaseError as e:
        print(f"❌ Ошибка: не является базой данных SQLite ({e})")
        return []

    house_info = get_house_info(conn)
    adventure_keys = get_adventure_keys(conn)
    rows = conn.execute("SELECT key, data FROM cats").fetchall()
    print(f"📦 Найдено записей о кошках: {len(rows)}")

    cats = []
    success = 0
    failed = 0

    for key, blob in rows:
        try:
            cat_obj = Cat(blob, key, house_info, adventure_keys)
            if cat_obj.name and cat_obj.name != "Unknown":
                cat_dict = cat_obj.to_dict()
                cats.append(cat_dict)
                success += 1
            else:
                failed += 1
        except Exception as e:
            failed += 1
            print(f"[{key}] Ошибка: {e}")

    conn.close()
    print(f"✅ Успешно: {success}")
    print(f"❌ Ошибки: {failed}")

    return cats