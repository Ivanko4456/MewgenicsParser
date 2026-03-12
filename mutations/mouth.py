"""
Мутации рта (mouth.gon)
"""

MUTATIONS = {
    300: {"name": "Sabertoothed", "bonuses": {0: 1}},
    303: {"name": "Delerious", "bonuses": {3: 1}},
    310: {"name": "Lip Fillers", "bonuses": {5: 1}},
    312: {"name": "Bear Trap Mouth", "bonuses": {0: 1}},
    316: {"name": "Horse Face", "bonuses": {5: -1}},
    751: {"name": "Pig Snout", "bonuses": {2: 2}},
    756: {"name": "Tylers Beard", "bonuses": {3: 1}},

    # Дефекты
    700: {"name": "Cleft Palate", "bonuses": {5: -2}},
    701: {"name": "Anodontia", "bonuses": {0: -1, 1: -1}},
    703: {"name": "Underbite", "bonuses": {3: -2, 2: 1}},
    704: {"name": "Overbite", "bonuses": {5: -2, 0: 1}},
}