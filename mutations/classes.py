"""
Бонусы классов котов (classes.gon)
Формат: class_name -> {stat_index: bonus_value}
stat_index: 0=STR, 1=DEX, 2=CON, 3=INT, 4=SPD, 5=CHA, 6=LCK
"""

CLASS_BONUSES = {
    "Fighter": {
        "name": "Fighter",
        "bonuses": {0: 2, 4: 1, 3: -1}  # STR+2, SPD+1, INT-1
    },
    "Hunter": {
        "name": "Hunter",
        "bonuses": {1: 3, 6: 2, 2: -1, 4: -2}  # DEX+3, LCK+2, CON-1, SPD-2
    },
    "Mage": {
        "name": "Mage",
        "bonuses": {3: 2, 5: 2, 2: -1, 0: -1}  # INT+2, CHA+2, CON-1, STR-1
    },
    "Medic": {
        "name": "Medic",
        "bonuses": {5: 2, 2: 2, 4: -1, 1: -1}  # CHA+2, CON+2, SPD-1, DEX-1
    },
    "Tank": {
        "name": "Tank",
        "bonuses": {2: 4, 3: -1, 1: -1}  # CON+4, INT-1, DEX-1
    },
    "Thief": {
        "name": "Thief",
        "bonuses": {4: 4, 6: 1, 0: -1, 2: -1}  # SPD+4, LCK+1, STR-1, CON-1
    },
    "Colorless": {
        "name": "Colorless",
        "bonuses": {}  # Нейтральный класс, без бонусов
    },
}