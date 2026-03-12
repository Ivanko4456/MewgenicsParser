#!/usr/bin/env python3
"""
Mewgenics Save Parser - Точка входа.
Экспортирует данные котов в Excel с учётом мутаций.
"""
import os
import sys
import sqlite3
import pandas as pd
from parser import Cat, STAT_NAMES, parse_all, find_save_file


def main():
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
        print("Укажите путь вручную в переменной MEWGENICS_SAVE_PATH")
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
        main_cols = ['ID', 'Имя', 'В доме', 'Комната', 'Пол']  # ← Убрано 'Статус'

        all_cols = main_cols + base_cols + final_cols + bonus_cols
        df = df[[c for c in all_cols if c in df.columns]]

        df.to_excel(output_file, index=False)

        abs_path = os.path.abspath(output_file)
        print(f"\n✅ Готово! {len(cats)} кошек экспортировано")
        print(f"📁 Файл: {abs_path}")
        print(f"\n📊 Структура колонок:")
        print(f"   Base = вложенные очки при уровне")
        print(f"   Final = итоговые статы (Base + Equipment + Mutations)")
        print(f"   Bonus = все бонусы (экипировка + мутации)")
        print(f"\n🧬 Мутации рассчитываются из базы данных mutations/")
        print(f"   Каждая часть тела имеет свою базу мутаций!")

    except Exception as e:
        print(f"\n❌ Ошибка сохранения Excel: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()