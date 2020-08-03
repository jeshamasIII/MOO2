from collections import namedtuple

# maybe namedtuple would be better?
Building = namedtuple('Building', ['cost', 'maintenance'])

with open(r"/home/typhode/Documents/Python/moo2/game/buildingData") as file:
    lines = file.readlines()

building_data = {}
for line in lines:
    if line[0] != '#':
        name, cost, maintenance = line.split()
        building_data[name] = Building(int(cost), int(maintenance))

# TODO: add freighter fleet
# TODO: add buy production
# tradegoods and housing
building_data['housing'] = Building(float('inf'), 0)
building_data['tradeGoods'] = Building(float('inf'), 0)
