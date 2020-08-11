from ColonyClass import Planet, Colony
from MonteCarloTreeSearchClass import MonteCarloTreeSearch
import time

p1 = Planet('huge', 'abundant', 'normal', 'terran')
c1 = Colony(p1, 'colony1', 2, 2, 2,
            ['automatedFactory', 'hydroponicFarm', 'biospheres',
             'researchLab']
            )

p2 = Planet('huge', 'abundant', 'normal', 'terran')
c2 = Colony(p1, 'colony1', 2, 2, 2,
            ['automatedFactory', 'hydroponicFarm', 'biospheres'])

p3 = Planet('huge', 'abundant', 'normal', 'terran')
c3 = Colony(p1, 'colony1', 2, 2, 2,
            ['automatedFactory', 'hydroponicFarm', 'biospheres'])

p4 = Planet('large', 'abundant', 'normal', 'terran')
c4 = Colony(p1, 'colony1', 2, 2, 2,
            ['automatedFactory', 'hydroponicFarm', 'biospheres'])

# starting positions for each research field
starting_tech = [('construction', 6), ('chemistry', 2), ('sociology', 2),
                 ('computers', 3), ('biology', 2) ]

game = MonteCarloTreeSearch(starting_tech, [c1])

tic = time.time()
while not game.is_finished():
    # print(game.turn_count)
    game.choose_parallel(num_processes=6, num_samples=100)

toc = time.time()
print(toc - tic)