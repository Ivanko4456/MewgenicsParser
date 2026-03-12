"""
Мутации головы (head.gon)
"""

MUTATIONS = {
    # Визуальные мутации головы с бонусами
    300: {"name": "Square Head", "bonuses": {2: 1}},
    301: {"name": "Sloth Head", "bonuses": {0: 1, 2: 1, 3: -1}},
    302: {"name": "Big Brain", "bonuses": {3: 2, 2: -1}},
    304: {"name": "Sludge Head", "bonuses": {5: -2}},
    305: {"name": "Strong Chin", "bonuses": {5: 1}},
    306: {"name": "Alien Head", "bonuses": {3: 1}},
    309: {"name": "Half Moon", "bonuses": {6: 2}},
    757: {"name": "Grey Head", "bonuses": {3: 2}},

    # Дефекты рождения
    700: {"name": "Microcephaly", "bonuses": {3: -2}},
    701: {"name": "Macrocephaly", "bonuses": {3: -2}},
    702: {"name": "Concave Head", "bonuses": {3: -1}},
    705: {"name": "Conjoined Head", "bonuses": {5: -3, 3: 2}},
    706: {"name": "Sloth", "bonuses": {5: -3}},
    900: {"name": "Slender", "bonuses": {5: -1}},

    # Стат-мутации (400-441) уже в body.py - здесь дублировать не нужно
}