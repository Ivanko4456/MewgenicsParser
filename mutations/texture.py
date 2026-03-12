"""
Мутации текстуры/шерсти (texture.gon)
"""

MUTATIONS = {
    300: {"name": "Stitches", "bonuses": {5: -1}},
    302: {"name": "Conjoined", "bonuses": {6: 1}},
    305: {"name": "Robot Hide", "bonuses": {3: 1}},
    306: {"name": "Veiny", "bonuses": {0: 1}},
    308: {"name": "Heart Tattoo", "bonuses": {5: 1}},

    # Дефекты
    700: {"name": "Neurofibromatosis", "bonuses": {5: -2}},
    701: {"name": "Melanocytic Nevus", "bonuses": {5: -2}},
    703: {"name": "Blue Spots", "bonuses": {5: -2}},
    704: {"name": "Red Dots", "bonuses": {5: -2}},
    705: {"name": "Jaundice", "bonuses": {5: -2}},
    706: {"name": "Vitiligo", "bonuses": {5: -1}},
}