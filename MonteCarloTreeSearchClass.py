from gameClass import Game
from colonyClass import Colony
from itertools import product, combinations, starmap
import random
from copy import deepcopy
from multiprocessing import Pool


class MonteCarloTreeSearch(Game):
    food_altering_buildings = [
        'astroUniversity', 'holoSimulator', 'pleasureDome',
        'hydroponicFarm', 'soilEnrichment', 'terraforming',
        'subterraneanFarms', 'weatherController', 'gaiaTransformation',
        'gravityGenerator'
    ]

    def __init__(self, starting_tech_positions, colonies):
        Game.__init__(self, starting_tech_positions, colonies)

        # variables to store possible actions from current game state
        self.distributions_list = []
        self.building_choices_list = []
        self.res_choices_list = []

        # compute initial actions
        self.building_choices()
        self.colonist_distributions()
        self.research_choices()

    # produces a list of tuples where...
    def colonist_distributions(self):
        # choices of distributions of colonists
        # TODO check if each colony's climate permits farming
        farmer_choices = product(*[range(c.cur_pop + 1) for c in self.colonies])

        # filter out choices of number of farmers that result in starvation
        food_values = {}

        for choice in farmer_choices:

            for c, farmers in zip(self.colonies, choice):
                c.num_farmers = farmers

            if self.food >= 0:
                food_values[choice] = [self.food, self.freighters_needed]

        # what is this doing?
        m1, m2 = min(food_values.values())

        feasible_choices = [choice for choice in food_values
                            if food_values[choice] == [m1, m2]]

        # enumerate all distributions of colonists that don't result in starvation
        distributions = []
        for choices in feasible_choices:
            temp = []
            for i, k in zip(choices, [c.cur_pop for c in self.colonies]):
                temp.append([(i, j, k - i - j) for j in range(0, k - i + 1, 4)])

            distributions.extend(product(*temp))

        self.distributions_list = distributions

    def purchase_choices(self, building_choices):
        # Here temp is a list of tuples of the form i,c,b where c is a colony,
        # i is it's index in the list game.colonies and b is the building on
        # the colonies build queue.
        # Tuples in which the colony's stored production exceeds the building's production cost
        # or in which the building has an infinite production cost are excluded from this list.

        temp = []
        for (i, c), b in zip(enumerate(self.colonies), building_choices):
            if (b not in ['tradeGoods', 'housing', 'storeProduction'] and
                    c.stored_prod < Colony.building_data[b].cost):
                temp.append((i, c, b))

        # Here output is list of tuples of indexes of colonies such that
        # all of the remaining production points for the buildings on their build queues
        # can be purchased without exceed the game's treasury
        output = []
        for j in range(len(self.colonies) + 1):
            for combs in combinations(temp, j):
                if sum(self.production_cost(c, b) for i, c, b in combs) <= self.reserve:
                    output.append([i for i, c, b in combs])
        return output

    # returns a list of tuples of building choices for each colony
    def building_choices(self):
        building_choices = product(*[c.building_choices for c in self.colonies])

        # compute building choices and corresponding production purchase choices
        output = []
        for choice in building_choices:
            output.extend(product([choice], self.purchase_choices(choice)))

        self.building_choices_list = output

    # returns a list of choices for the game's research queue
    def research_choices(self):
        if self.res_queue is None:
            if len(self.avail_tech_fields) > 0:
                self.res_choices_list = self.avail_tech_fields
            else:
                self.res_choices_list = [None]
        else:
            self.res_choices_list = [self.res_queue.field]

    # advance game state by taking the given action
    def advance(self, action):
        [buildings, prod_choice], distributions, research = action

        # assign building choices to build queues in colonies and
        # set distribution of workers for each colony
        for c, building, distribution in zip(self.colonies, buildings, distributions):
            c.num_farmers, c.num_workers, c.num_scientists = distribution

            c.prev_build_queue = building
            c.build_queue = building

        # purchase production
        for i in prod_choice:
            self.buy_production(self.colonies[i])

        # if research queue is empty, assign it a new research level
        if self.res_queue is None and research is not None:
            index = self.tech_tree_positions[research]
            self.res_queue = Game.tech_tree[research][index]

        prev_res_queue = self.res_queue
        prev_pop = self.pop

        self.turn()

        # compute building choices and corresponding production purchase choices
        self.building_choices()

        # compute research choices
        self.research_choices()

        # did anything alter food production? if so recompute
        # distributions of colonists
        if self.pop > prev_pop:
            self.colonist_distributions()

        elif any(c.build_queue is None and c.prev_build_queue in self.food_altering_buildings
                 for c in self.colonies):
            self.colonist_distributions()

        elif (self.res_queue is None and
              len(self.avail_tech_fields) > 0 and
              ('realityNetwork' in prev_res_queue.achievements or
               'biomorphicFungi' in prev_res_queue.achievements)):
            self.colonist_distributions()

    def choose(self, num_samples):
        actions = product(self.building_choices_list, self.distributions_list,
                          self.res_choices_list)

        results = starmap(self.sample, product(actions, [num_samples]))
        choice, value = min(results, key=lambda x: x[1])

        self.advance(choice)

    def choose_parallel(self, num_processes, num_samples):
        actions = product(self.building_choices_list, self.distributions_list,
                          self.res_choices_list)

        with Pool(processes=num_processes) as pool:
            # results is an iterable of a list pairs of the form
            # (action, sample(action, num_samples))
            results = pool.starmap(self.sample, product(actions, [num_samples]))
            choice, value = min(results, key=lambda x: x[1])

        self.advance(choice)
        # self.print_turn_summary(starting_turn=self.turn_count-1)

    def sample(self, action, num_samples):
        scores = []

        for _ in range(num_samples):
            temp = deepcopy(self)
            temp.advance(action)

            while not temp.is_finished():
                next_action = [random.choice(temp.building_choices_list),
                               random.choice(temp.distributions_list),
                               random.choice(temp.res_choices_list)]
                temp.advance(next_action)

            scores.append(temp.turn_count)

        return action, sum(scores) / num_samples


    def is_finished(self):
        research_complete = (len(self.avail_tech_fields) == 0)
        climate_complete = all(c.climate == 'gaia' for c in self.colonies)
        pop_complete = all(c.cur_pop == c.max_pop for c in self.colonies)
        final_buildings = {'tradeGoods', 'housing', 'freighterFleet',
                           'pollutionProcessor', 'atmosphereRenewer',
                           'storeProduction'
                           }
        buildings_complete = all(set(c.avail_buildings).issubset(final_buildings)
                                 for c in self.colonies)

        return (research_complete and pop_complete
                and buildings_complete and climate_complete)
