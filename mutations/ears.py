"""
Мутации ушей (ears.gon)
"""

MUTATIONS = {
    300: {"name": "Horn", "bonuses": {0: 1}},
    301: {"name": "Antenna", "bonuses": {3: 1}},
    304: {"name": "Pigtails", "bonuses": {5: 1}},
    306: {"name": "Bunny Ear", "bonuses": {4: 1}},
    307: {"name": "Brains", "bonuses": {3: 1}},
    308: {"name": "Shrek", "bonuses": {0: 1, 5: -1}},
    310: {"name": "Human", "bonuses": {3: 1}},
    322: {"name": "Lamb Ears", "bonuses": {5: 1}},
    342: {"name": "Infested Ears", "bonuses": {2: -1}},

    # Дефекты
    700: {"name": "Anotia", "bonuses": {6: -2}},
    701: {"name": "Turner Syndrome", "bonuses": {3: -2}},
    702: {"name": "Underdeveloped Ears", "bonuses": {5: -1}},
    -2: {"name": "No Ears", "bonuses": {1: -2}},
}