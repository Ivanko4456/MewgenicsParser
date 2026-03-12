"""
Мутации хвоста (tail.gon)
"""

MUTATIONS = {
    300: {"name": "Extra Paw", "bonuses": {0: 1}},
    304: {"name": "Monkey Tail", "bonuses": {1: 1}},
    306: {"name": "Big Lump Tail", "bonuses": {2: 1}},
    307: {"name": "Antenna Tail", "bonuses": {4: 1}},
    308: {"name": "Baby Tail", "bonuses": {6: 1}},
    309: {"name": "Baboon's Ass", "bonuses": {5: 1}},
    321: {"name": "Extra Head", "bonuses": {3: 1}},
    324: {"name": "Wing Tail", "bonuses": {4: 2}},
    750: {"name": "Bunny Tail", "bonuses": {5: 1}},
    752: {"name": "Pig Tail", "bonuses": {2: 1}},
    900: {"name": "Slender", "bonuses": {4: 1}},
    1500: {"name": "Rat Tail", "bonuses": {1: 1}},

    # Дефекты
    700: {"name": "Kinked Tail", "bonuses": {6: -2}},
    701: {"name": "Lipoma", "bonuses": {4: -1, 5: -1}},
    -2: {"name": "No Tail", "bonuses": {1: -1}},
    703: {"name": "Heavy Tail", "bonuses": {2: 1}},
    704: {"name": "Forked Tail", "bonuses": {6: -2}},
}