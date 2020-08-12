from TechTree import tree
from BuildingDataDictionary import building_data
import random
from math import floor
from tabulate import tabulate
from itertools import cycle


class Game:
    tech_tree = tree

    def __init__(self, starting_tech_positions, colonies, reserve=200,
                 stored_rp=0):
        self.tech_tree_positions = {field: 0 for field in tree}
        self.available_tech_fields = [field for field in self.tech_tree]

        self.stored_rp = stored_rp
        self.cumulative_rp = 0
        self.reserve = reserve

        self.systems = []

        self.colonies = colonies
        for colony in self.colonies:
            colony.game = self

        # distances between colonies
        self.distance = {}

        self.research_queue = None
        self.turn_count = 0

        # array of freighter fleet objects transporting colonists
        self.in_transport = []

        # turn summary information
        self.colonies_summary = []
        self.game_summary = []

        self.food_freighters = 0
        self.total_freighters = 10

        # buildings that have been researched so far
        self.buildings = {b: False for b in building_data}
        self.buildings['housing'] = True
        self.buildings['tradeGoods'] = True
        self.buildings['freighterFleet'] = True
        self.buildings['storeProduction'] = True

        # achievements that have been researched so far
        self.achievements = {'advancedCityPlanning': False,
                             'microliteConstruction': False,
                             'nanoDisassemblers': False, 'federation': False,
                             'currencyExchange': False, 'realityNetwork': False,
                             'microbiotics': False, 'universalAntidote': False,
                             'heightenedIntelligence': False,
                             'biomorphicFungi': False}

        # initialize starting tech
        for field, pos in starting_tech_positions:
            for res_level in self.tech_tree[field][:pos]:
                self.process_research_level(res_level)
            self.tech_tree_positions[field] = pos

    @property
    def available_freighters(self):
        return (self.total_freighters - 5 * len(self.in_transport)
                - self.food_freighters)

    @property
    def government_bonus(self):
        return .75 if self.achievements['federation'] else .5

    @property
    def freighters_needed(self):
        return sum(0 if colony.food >= 0 else abs(colony.food)
                   for colony in self.colonies)

    @property
    def food(self):
        return sum(colony.food for colony in self.colonies)

    @property
    def population(self):
        return sum(colony.current_population for colony in self.colonies)

    # If reserve becomes negative, sell buildings at random until reserve is
    # positive I'm not exactly sure how MOO2 chooses buildings at random. It
    # seems like the distribution is skewed towards buildings with lower
    # production costs.
    def sell_buildings(self):
        cannot_be_sold = ['terraforming', 'soilEnrichment',
                          'gaiaTransformation']

        while self.reserve < 0:
            colony = random.choice(self.colonies)

            # buildings that have been built in colony and can be sold
            building_choices = [
                building for building, is_built in colony.buildings.items()
                if is_built and building not in cannot_be_sold
            ]

            building = random.choice(building_choices)

            sold_for = building_data[building].cost // 2
            self.reserve += sold_for
            colony.buildings[building] = False

    # cost to purchase production for building in colony
    @staticmethod
    def production_cost(colony, building):
        production_cost = building_data[building].cost

        if building == 'terraforming':
            production_cost += 250 * colony.terraform_count

        pp = colony.stored_production
        completed = pp / production_cost

        if completed == 0:
            cost = 4 * production_cost
        elif 0 < completed < .10:
            cost = 4 * production_cost - 10 * pp
        elif completed == .10:
            cost = 3 * production_cost
        elif .10 < completed < .5:
            cost = 3.5 * production_cost - 5 * pp
        elif completed == .5:
            cost = production_cost
        elif .5 < completed < 1:
            cost = 2 * production_cost - 2 * pp

        return int(cost)

    # Buy remaining production for the building being built in a colony
    def buy_production(self, colony):
        production_cost = building_data[colony.build_queue].cost

        if colony.build_queue == 'terraforming':
            production_cost += 250 * colony.terraform_count

        if colony.stored_production < production_cost:
            self.reserve -= self.production_cost(colony, colony.build_queue)
            colony.stored_production = production_cost

    @property
    def rp(self):
        return sum(colony.rp for colony in self.colonies)

    @property
    def bc(self):
        return (sum(colony.bc for colony in self.colonies)
                + floor(.5 * self.food) * (self.food > 0)
                - floor(.5 * self.food_freighters)
                - floor(2.5 * len(self.in_transport))
                )

    # distribute surplus food among colonies using freighters
    def distribute_food(self):
        self.food_freighters = 0
        for colony in self.colonies:
            colony.imported_food = 0

        deficit = sum(colony.food for colony in self.colonies
                      if colony.food < 0)
        surplus = sum(colony.food for colony in self.colonies
                      if colony.food > 0)

        # I'm not sure if this distributes food in the exact same way
        # as in the game MOO2. But it looks like MOO2 tries to distribute
        # surplus food evenly among the colonies with food deficits.
        colonies_cycle = cycle(self.colonies)
        while surplus > 0 and deficit < 0 and self.available_freighters > 0:
            colony = next(colonies_cycle)
            if colony.food + colony.imported_food < 0:
                colony.imported_food += 1
                surplus -= 1
                deficit += 1
                self.food_freighters += 1

    def process_research_level(self, res_level):
        for achievement in res_level.achievements:
            self.achievements[achievement] = True

        for building in res_level.buildings:
            self.buildings[building] = True

    def turn(self):
        # turn summary
        self.turn_summary()

        # update attributes cum_rp, stored_rp, bc, and reserve
        self.stored_rp += self.rp
        self.cumulative_rp += sum(colony.rp for colony in self.colonies)
        self.reserve += self.bc

        # distribute food using available freighters if there is a colony
        # with a food deficit and a colony with a food surplus
        if (any(c.food + c.imported_food < 0 for c in self.colonies) and
                any(c.food > 0 for c in self.colonies)):
            self.distribute_food()

        # update colonies
        for colony in self.colonies:
            colony.turn()

        # empty research queue and update game if research is finished
        if (self.research_queue is not None and
                self.stored_rp >= int(1.5 * self.research_queue.rp_cost)):

            # make finished res_level's buildings and achievements available
            self.process_research_level(self.research_queue)

            # update stored_rp and tech_tree_positions
            self.stored_rp -= int(1.5 * self.research_queue.rp_cost)
            self.tech_tree_positions[self.research_queue.field] += 1

            # remove exhausted tech fields
            position = self.tech_tree_positions[self.research_queue.field]
            field = self.research_queue.field
            if position == len(self.tech_tree[field]):
                self.available_tech_fields.remove(field)

            self.research_queue = None

        # if reserve < 0, sell a random buildings until reserve >= 0.
        if self.reserve < 0:
            self.sell_buildings()

        self.turn_count += 1

    # Summarizes the state of the game before the turn button is pressed
    def turn_summary(self):
        # Turn summaries for colonies
        self.colonies_summary.append([])
        for colony in self.colonies:
            building_cost = building_data[colony.build_queue].cost
            self.colonies_summary[-1].append(
                [colony.num_farmers, colony.food, colony.num_workers,
                 colony.production, colony.num_scientists, colony.rp,
                 colony.build_queue,
                 str(colony.stored_production) + '/' + str(building_cost),
                 colony.bc, colony.current_population, colony.climate,
                 colony.max_population
                 ]
            )

        # Turn summary for game
        if self.research_queue is not None:
            field = self.research_queue.field
            research = field + str(self.research_queue.level)
        else:
            research = 'None'

        self.game_summary.append(
            [self.food, self.rp, self.cumulative_rp, self.bc, self.reserve,
             self.population, research, self.food_freighters,
             self.total_freighters]
        )

    def print_turn_summary(self, starting_turn=0):
        col_headers = ['farmers', 'net food', 'workers', 'prod.', 'scient.',
                       'rp', 'building', 'progress', 'net bc', 'pop',
                       'climate', 'pop_max']

        game_headers = ['net food', 'rp', 'cum_rp', 'bc', 'reserve', 'pop',
                        'researching', 'food freighters', 'num freighters']

        turn = starting_turn
        colonies_summary = self.colonies_summary[starting_turn:]
        game_summary = self.game_summary[starting_turn:]
        for col_summary, game_summary in zip(colonies_summary, game_summary):
            print('turn:', turn)
            print()
            print(
                tabulate(col_summary, headers=col_headers, tablefmt='simple'))
            print()
            print(tabulate([game_summary], headers=game_headers,
                           tablefmt='simple'))
            print()
            print()
            turn += 1

    def report(self):
        print(f'turn_count: {self.turn_count}')
        print('reserve:', self.reserve)
        print('income:', self.bc)
        print('population:', self.population)
        print(f'food_freighters, num_freighters: '
              f'{self.food_freighters},{self.total_freighters}')
        print('food:', self.food)
        print('research:', self.rp)
