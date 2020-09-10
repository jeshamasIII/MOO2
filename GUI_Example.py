from ColonyClass import Colony, Planet
from GameClass import Game
from GUI import GUI

# Initialize game object
p1 = Planet(size='large',
            mineral_richness='abundant',
            gravity='normal',

            climate='tundra')

c1 = Colony(p1, 'Ecber II', 2, 1, 1,
            ['hydroponicFarm', 'marineBarracks'])

p2 = Planet('large', 'abundant', 'normal', 'desert')
c2 = Colony(p2, 'Fahd II', 2, 1, 1,
            ['marineBarracks', 'hydroponicFarm'])

p3 = Planet('medium', 'abundant', 'heavyG', 'terran')
c3 = Colony(p3, 'Mentar IV', 2, 3, 3,
            ['automatedFactory', 'hydroponicFarm', 'biospheres',
             'marineBarracks', 'soilEnrichment'])

starting_tech_positions = [('construction', 6), ('chemistry', 3),
                           ('sociology', 2), ('computers', 3), ('biology', 2)]

game = Game(starting_tech_positions, [c1, c2, c3], reserve=200, stored_rp=0)

# Initialize GUI
gui = GUI(game)

