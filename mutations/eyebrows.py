"""
Мутации бровей (eyebrows.gon)
"""

MUTATIONS = {
    300: {"name": "Bolt Brows", "bonuses": {4: 1}},
    303: {"name": "Fancy Makeup", "bonuses": {5: 1}},
    304: {"name": "Wolfy Brows", "bonuses": {1: 1}},
    305: {"name": "Dotty Brows", "bonuses": {6: 1}},
    308: {"name": "Long Lashes", "bonuses": {5: 1}},

    # Дефекты
    700: {"name": "Bushy Eyebrows", "bonuses": {6: -1}},
    701: {"name": "No Eyebrows", "bonuses": {5: -1}},
    702: {"name": "Unibrow", "bonuses": {3: -1}},
    -2: {"name": "No Eyebrows (Missing)", "bonuses": {5: -2}},
}