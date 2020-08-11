from GameClass import Game
from ColonyClass import Colony
from BuildingDataDictionary import building_data
from itertools import product, combinations, starmap
import random
from copy import deepcopy
from multiprocessing import Pool


class MonteCarloTreeSearch(Game):
    food_altering_buildings = ['astroUniversity', 'holoSimulator',
                               'pleasureDome', 'hydroponicFarm',
                               'soilEnrichment', 'terraforming',
                               'subterraneanFarms', 'weatherController',
                               'gaiaTransformation', 'gravityGenerator']

    def __init__(self, starting_tech_positions, colonies, reserve=200):
        Game.__init__(self, starting_tech_positions, colonies, reserve)

        # variables to store possible actions from current game state
        self.col_distributions_list = []
        self.building_choices_list = []
        self.res_choices_list = []

        # compute initial actions
        self.building_choices()
        self.colonist_distributions()
        self.research_choices()

    # produces a list of tuples where...
    def colonist_distributions(self):
        # TODO check if each colony's climate permits farming
        farmer_choices = product(*[range(c.current_population + 1)
                                   for c in self.colonies])

        # filter out choices of number of farmers that result in starvation
        food_values = {}

        for choice in farmer_choices:

            for c, farmers in zip(self.colonies, choice):
                c.num_farmers = farmers

            if self.food >= 0:
                food_values[choice] = [self.food, self.freighters_needed]

        # what is this doing?
        m1, m2 = min(food_values.values())

        feasible_choices = [choice for choice in food_values if
                            food_values[choice] == [m1, m2]]

        # enumerate all distributions of colonists that don't result in
        # starvation
        col_distributions = []
        for choices in feasible_choices:
            temp = []
            for i, k in zip(choices, [c.current_population for c in self.colonies]):
                temp.append([(i, j, k - i - j) for j in range(0, k - i + 1, 4)])

            col_distributions.extend(product(*temp))

        self.col_distributions_list = col_distributions

    def purchase_choices(self, building_choices_tuple):
        # Compute a list of colony-pairs such that the build can be bought and
        # and the colony's stored production doesn't exceed the buildings
        # purchase cost.

        can_be_purchased = []
        for colony, building in zip(self.colonies, building_choices_tuple):
            if (building not in ['tradeGoods', 'housing', 'storeProduction']
                    and colony.stored_production < building_data[building].cost):
                can_be_purchased.append((colony, building))

        colony_index_map = {colony: colony_index for colony_index, colony
                            in enumerate(self.colonies)}

        # Combinations of colonies such that the building choice for every
        # colony can be purchased without exceeding the game's reserve.
        purchase_combs = []
        for num_colonies in range(len(can_be_purchased) + 1):
            for combination in combinations(can_be_purchased, num_colonies):
                total_cost = sum(self.production_cost(colony, building)
                                 for colony, building in combination)
                if total_cost <= self.reserve:
                    purchase_combs.append(
                        [colony_index_map[colony]
                         for colony, building in combination]
                    )
        return purchase_combs

    def building_choices(self):
        building_choices = product(
            *[colony.building_choices for colony in self.colonies]
        )

        # Pair each tuple of building choices with each way in which it's
        # buildings can be purchased.
        self.building_choices_list = []
        for choice in building_choices:
            self.building_choices_list.extend(
                product([choice], self.purchase_choices(choice))
            )

    # returns a list of choices for the game's research queue
    def research_choices(self):
        if self.res_queue is None:
            if len(self.available_tech_fields) > 0:
                self.res_choices_list = self.available_tech_fields
            else:
                self.res_choices_list = [None]
        else:
            self.res_choices_list = [self.res_queue.field]

    # advance game state by taking the given action
    def advance(self, action):
        [buildings, purchase_combination], col_distributions, research = action

        # assign building choices to build queues in colonies and
        # set distribution of workers for each colony
        for colony, building, col_distribution in zip(self.colonies, buildings,
                                                      col_distributions):
            colony.num_farmers, colony.num_workers, colony.num_scientists = \
                col_distribution

            colony.previous_build_queue = building
            colony.build_queue = building

        # purchase production
        for colony_index in purchase_combination:
            self.buy_production(self.colonies[colony_index])

        # If research queue is empty, and there are unfinished research levels,
        # assign it a new research level.
        if self.res_queue is None and research is not None:
            res_field_index = self.tech_tree_positions[research]
            self.res_queue = Game.tech_tree[research][res_field_index]

        prev_res_queue = self.res_queue
        prev_pop = self.population

        self.turn()

        # compute building choices and corresponding production purchase
        # choices
        self.building_choices()

        # compute research choices
        self.research_choices()

        # Has the food production in the game changed? If so, recompute
        # colonists distributions

        if self.population > prev_pop:
            self.colonist_distributions()

        elif any(colony.build_queue is None and colony.previous_build_queue in
                 self.food_altering_buildings for colony in self.colonies):
            self.colonist_distributions()

        elif (self.res_queue is None and
              len(self.available_tech_fields) > 0 and
              ('realityNetwork' in prev_res_queue.achievements or
               'biomorphicFungi' in prev_res_queue.achievements)):
            self.colonist_distributions()

        # food altering buildings were sold

        # freighters

    def sample(self, action, num_samples):
        scores = []

        for _ in range(num_samples):
            temp_game = deepcopy(self)
            temp_game.advance(action)

            while not temp_game.is_finished():
                next_action = [random.choice(temp_game.building_choices_list),
                               random.choice(temp_game.col_distributions_list),
                               random.choice(temp_game.res_choices_list)]
                temp_game.advance(next_action)

            scores.append(temp_game.turn_count)

        return action, sum(scores) / num_samples

    def choose(self, num_samples):
        actions = product(self.building_choices_list,
                          self.col_distributions_list, self.res_choices_list)

        results = starmap(self.sample, product(actions, [num_samples]))
        choice, value = min(results, key=lambda x: x[1])

        self.advance(choice)

    def choose_parallel(self, num_processes, num_samples):
        actions = product(self.building_choices_list,
                          self.col_distributions_list, self.res_choices_list)

        with Pool(processes=num_processes) as pool:
            # results is an iterable of a list pairs of the form
            # (action, sample(action, num_samples))
            results = pool.starmap(self.sample,
                                   product(actions, [num_samples]))
            choice, value = min(results, key=lambda x: x[1])

        self.advance(choice)
        # self.print_turn_summary(starting_turn=self.turn_count-1)

    def is_finished(self):
        research_complete = (len(self.available_tech_fields) == 0)
        climate_complete = all(colony.climate == 'gaia'
                               for colony in self.colonies)

        pop_complete = all(colony.current_population == colony.max_population
                           for colony in self.colonies)

        final_buildings = {'tradeGoods', 'housing', 'freighterFleet',
                           'pollutionProcessor', 'atmosphereRenewer',
                           'storeProduction'}

        buildings_complete = all(
            set(colony.available_buildings).issubset(final_buildings) for colony in
            self.colonies)

        return (research_complete and pop_complete
                and buildings_complete and climate_complete)
