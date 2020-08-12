from math import floor, ceil, sqrt
from BuildingDataDictionary import building_data


def nearest_integer(x):
    if x < int(x) + .5:
        return int(x)
    else:
        return int(x) + 1


class Planet:
    def __init__(self, size, mineral_richness, gravity, climate):
        # sizes: tiny, small, medium, large, huge
        self.size = size

        # mineral richness types: ultraPoor, poor, abundant, rich, ultraRich
        self.mineral_richness = mineral_richness

        # types: lowG, normal, heavyG
        self.gravity = gravity

        # climate types: gaia, terran, arid, swamp, ocean, tundra, desert,
        #                barren, radiated, toxic
        self.climate = climate


class Colony(Planet):
    # factor1 and factor2 are used for population growth equation
    factor1 = 2000
    factor2 = 40

    # planet size classes
    planet_size_map = {
        'tiny': 1, 'small': 2, 'medium': 3, 'large': 4, 'huge': 5
    }

    # population multiplier for planet climates
    population_multiplier_map = {
        'gaia': 1, 'terran': .8, 'arid': .6, 'swamp': .4,
        'ocean': .25, 'tundra': .25, 'desert': .25,
        'barren': .25, 'radiated': .25, 'toxic': .25
    }

    # gravity penalty multiplier
    gravity_multiplier_map = {'lowG': .25, 'normal': 0, 'heavyG': .5}

    # base food production per farmer for each climate type
    farming_multiplier_map = {
        'gaia': 3, 'terran': 2, 'arid': 1, 'swamp': 2, 'ocean': 2,
        'tundra': 1, 'desert': 1, 'barren': 0, 'radiated': 0, 'toxic': 0
    }

    # base production per worker for each mineral richness
    production_multiplier_map = {
        'ultraPoor': 1, 'poor': 2, 'abundant': 3, 'rich': 5, 'ultraRich': 8
    }

    # amount of production added by robotic factory for each mineral
    # richness type
    robotic_factory_map = {
        'ultraPoor': 5, 'poor': 8, 'abundant': 10, 'rich': 15, 'ultraRich': 20
    }

    # terraforming progression
    terraforming_map = {
        'barren': 'tundra', 'desert': 'arid', 'tundra': 'swamp',
        'ocean': 'terran', 'arid': 'terran', 'swamp': 'terran'
    }

    # maintenance costs penalties for each climate type
    climate_cost_map = {
        'gaia': 0, 'terran': 0, 'arid': 0, 'swamp': 0, 'ocean': 0,
        'tundra': 0, 'desert': .25, 'barren': 0, 'radiated': .25, 'toxic': .5
    }

    def __init__(self, planet, name, num_farmers,
                 num_workers, num_scientists, initial_buildings,
                 build_queue='tradeGoods'):
        super().__init__(planet.size, planet.mineral_richness, planet.gravity,
                         planet.climate)

        # This reference is supplied when the game object is initialized
        self.game = None

        self.name = name
        self.num_farmers = num_farmers
        self.num_workers = num_workers
        self.num_scientists = num_scientists
        self.current_population = (self.num_workers
                                   + self.num_farmers
                                   + self.num_scientists)

        self.raw_population = self.current_population * 1000

        # used for monte_carlo tree search
        self.previous_population = self.current_population

        # buildings that have been built in the colony
        self.buildings = {b: False for b in building_data}
        for b in initial_buildings:
            self.buildings[b] = True

        # terran planet can't be terraformed any further
        # except by gia transformation
        if self.climate == 'terran':
            self.buildings["terraforming"] = True

        # A gaia planet cannot be further terraformed
        if self.climate == 'gaia':
            self.buildings['terraforming'] = True
            self.buildings['gaiaTransformation'] = True

        # used for monte carlo tree search
        self.previous_build_queue = None

        self.build_queue = build_queue
        self.stored_production = 0
        self.turn_count = 0

        # compute colony's size class from planet size
        self.size_class = Colony.planet_size_map[self.size]

        # base bc produced per colonist
        self.bc_multiplier = 1

        # base research points produced per scientist
        # rp_multiplier = base_rp (3) + Psilon_bonus (2)
        self.rp_multiplier = 5

        # the number of times a planet has been terraformed
        self.terraform_count = 0

        # base production points per worker
        self.production_multiplier = \
            Colony.production_multiplier_map[self.mineral_richness]

        # food imported with freighters
        self.imported_food = 0

        # number of production points used to clean up pollution in colony
        self.pollution_penalty = 0

    @property
    def available_buildings(self):
        return [b for b in self.game.buildings
                if self.game.buildings[b] and not self.buildings[b]]

    # Used for monte carlo tree search
    @property
    def building_choices(self):
        if self.build_queue in ['tradeGoods', 'housing',
                                'storeProduction', None]:
            output = self.available_buildings
            if self.current_population == self.max_population:
                output.remove('housing')
        else:
            output = [self.build_queue]

        return output

    # Used for GUI
    @property
    def unassigned(self):
        return (self.current_population
                - self.num_farmers
                - self.num_workers
                - self.num_scientists)

    # base food production per farmer
    @property
    def farming_multiplier(self):
        return Colony.farming_multiplier_map[self.climate]

    @property
    def population_multiplier(self):
        return Colony.population_multiplier_map[self.climate]

    @property
    def gravity_multiplier(self):
        if self.buildings['gravityGenerator']:
            return 0
        else:
            return Colony.gravity_multiplier_map[self.gravity]

    @property
    def planet_pollution_tolerance(self):
        if self.game.achievements['nanoDisassemblers']:
            return 4 * self.size_class
        else:
            return 2 * self.size_class

    @property
    def morale_multiplier(self):
        return (.2 * self.buildings['holoSimulator']
                + .3 * self.buildings['pleasureDome']
                + .2 * self.game.achievements['realityNetwork']
                )

    @property
    def max_population(self):
        return (nearest_integer(self.population_multiplier * self.size_class * 5)
                + 2 * self.buildings['biospheres']
                + 5 * self.game.achievements['advancedCityPlanning'])

    @property
    def food(self):
        output = self.num_farmers * self.farming_multiplier

        # soil enrichment
        if self.buildings['soilEnrichment']:
            output += self.num_farmers

        # biomorphic fungi
        if self.game.achievements['biomorphicFungi']:
            output += self.num_farmers

        # weather controller
        if self.buildings['weatherController']:
            output += 2 * self.num_farmers

        # astro university
        if self.buildings['astroUniversity']:
            output += self.num_farmers

        # gravity penalty and morale bonus
        output += output * (self.morale_multiplier - self.gravity_multiplier)

        # hydroponic farm
        output += 2 * self.buildings['hydroponicFarm']

        # subterranean farm
        output += 4 * self.buildings['subterraneanFarms']

        # return output rounded to nearest integer
        return nearest_integer(output) - self.current_population

    @property
    def production(self):
        worker_production = self.num_workers * self.production_multiplier
        from_buildings = 0

        # astro university
        if self.buildings['astroUniversity']:
            worker_production += self.num_workers

        # microlite construction
        if self.game.achievements['microliteConstruction']:
            worker_production += self.num_workers

        # automated factory
        if self.buildings['automatedFactory']:
            worker_production += self.num_workers
            from_buildings += 5

        # robo miner plant
        if self.buildings['roboMinerPlant']:
            worker_production += 2 * self.num_workers
            from_buildings += 10

        # deep core mine
        if self.buildings['deepCoreMine']:
            worker_production += 3 * self.num_workers
            from_buildings += 15

        # gravity penalty and morale bonus
        worker_production += (worker_production
                              * (self.morale_multiplier - self.gravity_multiplier))

        # robotic factory (included in pollution penalty)
        if self.buildings['roboticFactory']:
            worker_production += Colony.robotic_factory_map[self.mineral_richness]

        # round worker output to nearest integer before computing pollution
        worker_production = nearest_integer(worker_production)

        # pollution processor, atmosphere renewer multiplier

        pollution_processor_bonus = .5 if self.buildings['pollutionProcessor'] else 1
        atmosphere_renewer_bonus = .25 if self.buildings['atmosphereRenewer'] else 1
        pollution_reduction_multiplier \
            = pollution_processor_bonus * atmosphere_renewer_bonus

        # subtract pollution penalty
        if self.buildings['coreWasteDump']:
            self.pollution_penalty = 0
        else:
            self.pollution_penalty = ceil(
                max(0, (worker_production
                        * pollution_reduction_multiplier
                        - self.planet_pollution_tolerance)) / 2
            )
            worker_production -= self.pollution_penalty

        # bonus from recyclotron
        from_buildings += self.current_population * self.buildings['recyclotron']

        return worker_production + from_buildings

    @property
    def rp(self):
        from_scientists = self.num_scientists * self.rp_multiplier
        from_buildings = 0

        # astro university
        if self.buildings['astroUniversity']:
            from_scientists += self.num_scientists

        # heightened intelligence
        if self.game.achievements['heightenedIntelligence']:
            from_scientists += self.num_scientists

        # research lab
        if self.buildings['researchLab']:
            from_scientists += self.num_scientists
            from_buildings += 5

        # supercomputer
        if self.buildings['supercomputer']:
            from_scientists += 2 * self.num_scientists
            from_buildings += 10

        # autolab
        if self.buildings['autolab']:
            from_buildings += 30

        # galacticCybernet
        if self.buildings['galacticCybernet']:
            from_scientists += 3 * self.num_scientists
            from_buildings += 15

        # morale, gravity, and gov bonus
        from_scientists += from_scientists * (self.morale_multiplier
                                              + self.game.government_bonus
                                              - self.gravity_multiplier)

        return nearest_integer(from_scientists + from_buildings)

    @property
    def bc(self):
        # taxes collected from colonists
        taxes_collected = self.bc_multiplier * self.current_population

        # morale bonus
        morale_bonus = nearest_integer(taxes_collected * self.morale_multiplier)

        # spaceport bonus
        spaceport_bonus = int(taxes_collected * .5) * self.buildings['spaceport']

        # stock exchange bonus
        stock_exchange_bonus = taxes_collected * self.buildings['stockExchange']

        # galactic currency exchange bonus
        currency_exchange_bonus = (self.game.achievements['currencyExchange']
                                   * int(taxes_collected * .5))

        # government bonus
        government_bonus = int(taxes_collected * self.game.government_bonus)

        # tradegoods
        tradegoods = (self.build_queue == 'tradeGoods') * ceil(.5 * self.production)

        # total income produced by colony
        total_income = (taxes_collected
                        + morale_bonus
                        + spaceport_bonus
                        + stock_exchange_bonus
                        + currency_exchange_bonus
                        + government_bonus
                        + tradegoods)

        # maintenance and climate costs will be subtracted from total income

        maintenance_cost = sum(building_data[b].maintenance for b
                               in building_data if self.buildings[b])

        climate_cost = nearest_integer(maintenance_cost
                                       * Colony.climate_cost_map[self.climate])

        return total_income - maintenance_cost - climate_cost

    @property
    def population_increment(self):
        # base population growth
        base_population_growth = floor(
            sqrt(Colony.factor1
                 * self.current_population
                 * (self.max_population - self.current_population)
                 / self.max_population)
        )

        housing_bonus = 0
        if self.build_queue == 'housing':
            housing_bonus = floor(Colony.factor2
                                  * self.production
                                  / self.current_population)

        tech_bonus = 0
        if self.game.achievements['microbiotics']:
            tech_bonus = 25
        if self.game.achievements['universalAntidote']:
            tech_bonus = 50

        cloning_center_bonus = 100 * self.buildings['cloningCenter']

        food_short_fall = (self.food + self.imported_food if
                           self.food + self.imported_food < 0 else 0)

        starvation_penalty = 50 * food_short_fall

        return (floor(base_population_growth
                      * ((100 + tech_bonus + housing_bonus) / 100))
                + cloning_center_bonus
                + starvation_penalty)

    def turn(self):
        # update colony population
        if (self.current_population < self.max_population or
                (self.current_population == self.max_population
                 and self.population_increment < 0)):
            self.previous_population = self.current_population
            self.raw_population += self.population_increment
            self.current_population = self.raw_population // 1000

            # used for GUI
            # if population decreased and is not zero,
            # decrease the numbers of colonists until
            # num_farmers + num_workers + num_scientists = current_population
            if self.previous_population > self.current_population > 0:
                difference = self.previous_population - self.current_population
                for attribute in ['num_farmers', 'num_workers', 'num_scientists']:
                    value = getattr(self, attribute)
                    if value > 0:
                        setattr(self, attribute, max(value - difference, 0))
                        difference -= value

                    if difference <= 0:
                        break

        # update stored production and buildingQueue
        if self.build_queue not in ['housing', 'tradeGoods']:
            self.stored_production += self.production

            # terraforming is a special case
            if self.build_queue == 'terraforming':
                if self.stored_production >= 250 * (1 + self.terraform_count):
                    self.stored_production -= 250 * (1 + self.terraform_count)
                    self.terraform_count += 1

                    self.climate = Colony.terraforming_map[self.climate]

                    # terran planets cannot be further terraformed except
                    # by gaia transformation
                    if self.climate == 'terran':
                        self.buildings['terraforming'] = True

                    self.build_queue = None

            elif self.stored_production >= building_data[self.build_queue].cost:
                self.buildings[self.build_queue] = True
                self.stored_production -= building_data[self.build_queue].cost

                # freighter fleet
                if self.build_queue == 'freighterFleet':
                    self.game.total_freighters += 1
                    self.buildings['freighterFleet'] = False

                # radiation shield
                if (self.build_queue == 'radiationShield'
                        and self.climate == 'radiated'):
                    self.climate = 'barren'

                # gia transformation
                if self.build_queue == 'gaiaTransformation':
                    self.climate = 'gaia'

                self.build_queue = None

    def report(self):
        print(f'name: {self.name}')
        print(f'net bc: {self.bc}')
        print(f'farmers: {self.num_farmers}, net food: {self.food}')
        print(f'workers: {self.num_workers}, production: {self.production}')
        print(f'scientists: {self.num_scientists}, rp: {self.rp}')
        print(f'building: {self.build_queue}')
        print(f'raw_pop: {self.raw_population}')
        print(f'pop_increment: {self.population_increment}')
