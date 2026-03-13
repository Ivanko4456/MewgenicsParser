#!/usr/bin/env python3
"""
Mewgenics Save Parser - Точка входа.
"""
import os
import struct
import sys
import sqlite3
import pandas as pd
from parser import Cat, STAT_NAMES


def get_house_info(conn) -> dict:
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


if __name__ == "__main__":
    print("=== Mewgenics Save Parser (With Mutations) ===\n")

    input_file = None
    if os.environ.get("MEWGENICS_SAVE_PATH"):
        if os.path.exists(os.environ["MEWGENICS_SAVE_PATH"]):
            input_file = os.environ["MEWGENICS_SAVE_PATH"]
            print(f"📁 Используем путь из переменной: {input_file}")

    if not input_file:
        input_file = find_save_file()

    if not input_file:
        print("\n❌ НЕ УДАЛОСЬ НАЙТИ ФАЙЛ СОХРАНЕНИЯ")
        sys.exit(1)

    print(f"📁 Файл: {input_file}\n")
    output_file = 'mewgenics_cats.xlsx'

    cats = parse_all(input_file)

    if not cats:
        print("\n❌ Данные не найдены.")
        sys.exit(1)

    try:
        df = pd.DataFrame(cats)

        base_cols = STAT_NAMES
        final_cols = [f'Final_{s}' for s in STAT_NAMES]
        bonus_cols = [f'Bonus_{s}' for s in STAT_NAMES]
        main_cols = ['ID', 'Имя', 'Класс', 'В доме', 'Комната', 'Пол']

        all_cols = main_cols + base_cols + final_cols + bonus_cols
        df = df[[c for c in all_cols if c in df.columns]]

        df.to_excel(output_file, index=False)

        abs_path = os.path.abspath(output_file)
        print(f"\n✅ Готово! {len(cats)} кошек экспортировано")
        print(f"📁 Файл: {abs_path}")
        print(f"\n📊 Структура колонок:")
        print(f"   Base = вложенные очки при уровне")
        print(f"   Final = итоговые статы (Base + Equipment + Mutations + Class)")
        print(f"   Bonus = все бонусы (экипировка + мутации + класс)")

    except Exception as e:
        print(f"\n❌ Ошибка сохранения Excel: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)