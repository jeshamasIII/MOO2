from math import floor, ceil, sqrt
from buildDict import building_data


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

    # building cost and maintenance data
    building_data = building_data

    # planet size classes
    planetSizeMap = {'tiny': 1, 'small': 2, 'medium': 3, 'large': 4, 'huge': 5}

    # population multipliers for planet climates
    popMultMap = {'gaia': 1, 'terran': .8, 'arid': .6, 'swamp': .4, 'ocean': .25,
                  'tundra': .25, 'desert': .25, 'barren': .25, 'radiated': .25,
                  'toxic': .25
                  }

    # gravity penalty multipliers
    gravMultMap = {'lowG': .25, 'normal': 0, 'heavyG': .5}

    # base food production per farmer for each climate type
    farmMultMap = {'gaia': 3, 'terran': 2, 'arid': 1, 'swamp': 2, 'ocean': 2,
                   'tundra': 1, 'desert': 1, 'barren': 0, 'radiated': 0,
                   'toxic': 0
                   }

    # base production per worker for each mineral richness
    prodMultMap = {'ultraPoor': 1, 'poor': 2, 'abundant': 3,
                   'rich': 5, 'ultraRich': 8
                   }

    # amount of production added by robotic factory for each mineral richness type
    roboticFactoryMap = {'ultraPoor': 5, 'poor': 8, 'abundant': 10, 'rich': 15,
                         'ultraRich': 20
                         }

    # terraforming progression
    terraformingMap = {'barren': 'tundra', 'desert': 'arid', 'tundra': 'swamp',
                       'ocean': 'terran', 'arid': 'terran', 'swamp': 'terran'
                       }

    # maintenance costs penalties for each climate type
    climateCostMap = {'gaia': 0, 'terran': 0, 'arid': 0, 'swamp': 0, 'ocean': 0,
                      'tundra': 0, 'desert': .25, 'barren': 0, 'radiated': .25,
                      'toxic': .5
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
        self.cur_pop = self.num_workers + self.num_farmers + self.num_scientists
        self.raw_pop = self.cur_pop * 1000

        # used for monte_carlo tree search
        self.prev_pop = self.cur_pop

        # buildings that have been built in the colony
        self.buildings = {b: False for b in building_data}
        for b in initial_buildings:
            self.buildings[b] = True

        # terran planet can't be terraformed any further
        # except by gia transformation
        if self.climate == 'terran':
            self.buildings["terraforming"] = True

        # used for monte carlo tree search
        self.prev_build_queue = None

        self.build_queue = build_queue
        self.stored_prod = 0
        self.turn_count = 0

        # compute colony's size class from planet size
        self.size_class = Colony.planetSizeMap[self.size]

        # base bc produced per colonist
        self.bc_mult = 1

        # base research points produced per scientist
        # rp_mult = base_rp (3) + Psilon_bonus (2)
        self.rp_mult = 5

        # the number of times a planet has been terraformed
        self.terraform_count = 0

        # base food production per farmer
        self.farm_mult = Colony.farmMultMap[self.climate]

        # base production points per worker
        self.prod_mult = Colony.prodMultMap[self.mineral_richness]

        #
        self.pop_mult = Colony.popMultMap[self.climate]

        # food imported with freighters
        self.imported_food = 0

        # number of production points used to clean up pollution in colony
        self.pollution_penalty = 0

    @property
    def avail_buildings(self):
        return [b for b in self.game.buildings
                if self.game.buildings[b] and not self.buildings[b]]

    # Used for monte carlo tree search
    @property
    def building_choices(self):
        if self.build_queue in ['tradeGoods', 'housing',
                                'storeProduction', None]:
            output = self.avail_buildings
            if self.cur_pop == self.max_pop:
                output.remove('housing')
        else:
            output = [self.build_queue]

        return output

    # Used for GUI
    @property
    def unassigned(self):
        return (self.cur_pop
                - self.num_farmers
                - self.num_workers
                - self.num_scientists)

    @property
    def grav_mult(self):
        if self.buildings['gravityGenerator']:
            return 0
        else:
            return Colony.gravMultMap[self.gravity]

    @property
    def pol_tol(self):
        if self.game.achievements['nanoDisassemblers']:
            return 4 * self.size_class
        else:
            return 2 * self.size_class

    @property
    def morale_mult(self):
        return (.2 * self.buildings['holoSimulator']
                + .3 * self.buildings['pleasureDome']
                + .2 * self.game.achievements['realityNetwork']
                )

    @property
    def max_pop(self):
        return (nearest_integer(self.pop_mult * self.size_class * 5)
                + 2 * self.buildings['biospheres']
                + 5 * self.game.achievements['advancedCityPlanning'])

    @property
    def food(self):
        output = self.num_farmers * self.farm_mult

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
        output += output * (self.morale_mult - self.grav_mult)

        # hydroponic farm
        output += 2 * self.buildings['hydroponicFarm']

        # subterranean farm
        output += 4 * self.buildings['subterraneanFarms']

        # return output rounded to nearest integer
        return nearest_integer(output) - self.cur_pop

    @property
    def prod(self):
        worker_prod = self.num_workers * self.prod_mult
        from_buildings = 0

        # astro university
        if self.buildings['astroUniversity']:
            worker_prod += self.num_workers

        # microlite construction
        if self.game.achievements['microliteConstruction']:
            worker_prod += self.num_workers

        # automated factory
        if self.buildings['automatedFactory']:
            worker_prod += self.num_workers
            from_buildings += 5

        # robo miner plant
        if self.buildings['roboMinerPlant']:
            worker_prod += 2 * self.num_workers
            from_buildings += 10

        # deep core mine
        if self.buildings['deepCoreMine']:
            worker_prod += 3 * self.num_workers
            from_buildings += 15

        # gravity penalty and morale bonus
        worker_prod += worker_prod * (self.morale_mult - self.grav_mult)

        # robotic factory (included in pollution penalty)
        if self.buildings['roboticFactory']:
            worker_prod += Colony.roboticFactoryMap[self.mineral_richness]

        # round worker output to nearest integer before computing pollution
        worker_prod = nearest_integer(worker_prod)

        # pollution processor, atmosphere renewer multipliers
        m1 = .5 if self.buildings['pollutionProcessor'] else 1
        m2 = .25 if self.buildings['atmosphereRenewer'] else 1
        m = m1 * m2

        # subtract pollution penalty
        if not self.buildings['coreWasteDump']:
            self.pollution_penalty = ceil(
                max(0, (worker_prod * m - self.pol_tol)) / 2
            )
            worker_prod -= self.pollution_penalty
        else:
            self.pollution_penalty = 0

        # bonus from recyclotron
        from_buildings += self.cur_pop * self.buildings['recyclotron']

        return worker_prod + from_buildings

    @property
    def rp(self):
        fromScientists = self.num_scientists * self.rp_mult
        fromBuildings = 0

        # astro university
        if self.buildings['astroUniversity']:
            fromScientists += self.num_scientists

        # heightened intelligence
        if self.game.achievements['heightenedIntelligence']:
            fromScientists += self.num_scientists

        # research lab
        if self.buildings['researchLab']:
            fromScientists += self.num_scientists
            fromBuildings += 5

        # supercomputer
        if self.buildings['supercomputer']:
            fromScientists += 2 * self.num_scientists
            fromBuildings += 10

        # autolab
        if self.buildings['autolab']:
            fromBuildings += 30

        # galacticCybernet
        if self.buildings['galacticCybernet']:
            fromScientists += 3 * self.num_scientists
            fromBuildings += 15

        # morale, gravity, and gov bonus
        fromScientists += fromScientists * (self.morale_mult
                                            + self.game.gov_bonus
                                            - self.grav_mult)

        return nearest_integer(fromScientists + fromBuildings)

    @property
    def bc(self):
        # taxes collected from colonists
        taxes_collected = self.bc_mult * self.cur_pop

        # morale bonus
        morale_bonus = nearest_integer(taxes_collected * self.morale_mult)

        # spaceport bonus
        spaceport_bonus = int(taxes_collected * .5) * self.buildings['spaceport']

        # stock exchange bonus
        stock_exchange_bonus = taxes_collected * self.buildings['stockExchange']

        # galactic currency exchange bonus
        currency_exchange_bonus = (self.game.achievements['currencyExchange']
                                   * int(taxes_collected * .5))

        # government bonus
        gov_bonus = int(taxes_collected * self.game.gov_bonus)

        # tradegoods
        tradegoods = (self.build_queue == 'tradeGoods') * ceil(.5 * self.prod)

        # total income produced by colony
        total_income = (taxes_collected
                        + morale_bonus
                        + spaceport_bonus
                        + stock_exchange_bonus
                        + currency_exchange_bonus
                        + gov_bonus
                        + tradegoods)

        # maintenance and climate costs will be subtracted from total income

        maint_cost = sum(building_data[b].maintenance for b in building_data
                         if self.buildings[b])
        climate_cost = nearest_integer(maint_cost
                                       * Colony.climateCostMap[self.climate])

        return total_income - maint_cost - climate_cost

    @property
    def pop_increment(self):
        # base population growth
        a = floor(
            sqrt(Colony.factor1
                 * self.cur_pop
                 * (self.max_pop - self.cur_pop)
                 / self.max_pop
                 )
        )

        # housing bonus
        h = 0
        if self.build_queue == 'housing':
            h = floor(Colony.factor2 * self.prod / self.cur_pop)

        # tech bonus
        t = 0
        if self.game.achievements['microbiotics']:
            t = 25

        if self.game.achievements['universalAntidote']:
            t = 50

        b = (100 + t + h) / 100

        # bonus for cloning center
        c = 100 * self.buildings['cloningCenter']

        # penalty for starvation
        short_fall = (self.food + self.imported_food if
                      self.food + self.imported_food < 0 else 0)
        d = 50 * short_fall

        return floor(a * b) + c + d

    def turn(self):
        # update colony population
        if (self.cur_pop < self.max_pop or
                self.cur_pop == self.max_pop and self.pop_increment < 0):
            self.prev_pop = self.cur_pop
            self.raw_pop += self.pop_increment
            self.cur_pop = self.raw_pop // 1000

            # used for GUI
            # if population decreased but is not zero,
            # decrease the numbers of colonists accordingly
            if self.prev_pop > self.cur_pop > 0:
                diff = self.prev_pop - self.cur_pop
                for attr in ['num_farmers', 'num_workers', 'num_scientists']:
                    value = getattr(self, attr)
                    if value > 0:
                        setattr(self, attr, max(value - diff, 0))
                        diff -= value

                    if diff <= 0:
                        break

        # update stored production and buildingQueue
        if self.build_queue not in ['housing', 'tradeGoods']:
            self.stored_prod += self.prod

            # terraforming is a special case
            if self.build_queue == 'terraforming':
                if self.stored_prod >= 250 * (1 + self.terraform_count):
                    self.stored_prod -= 250 * (1 + self.terraform_count)
                    self.terraform_count += 1

                    # update attributes that depend on climate
                    self.climate = Colony.terraformingMap[self.climate]
                    self.farm_mult = Colony.farmMultMap[self.climate]
                    self.pop_mult = Colony.popMultMap[self.climate]

                    # terran planets cannot be further terraformed except
                    # by gaia transformation
                    if self.climate == 'terran':
                        self.buildings['terraforming'] = True

                    self.build_queue = None

            elif self.stored_prod >= building_data[self.build_queue].cost:
                self.buildings[self.build_queue] = True
                self.stored_prod -= building_data[self.build_queue].cost

                # freighter fleet
                if self.build_queue == 'freighterFleet':
                    self.game.num_freighters += 1
                    self.buildings['freighterFleet'] = False

                # radiation shield
                if (self.build_queue == 'radiationShield'
                        and self.climate == 'radiated'):
                    self.climate = 'barren'

                # gia transformation
                if self.build_queue == 'gaiaTransformation':
                    self.climate = 'gaia'
                    self.farm_mult = Colony.farmMultMap[self.climate]
                    self.pop_mult = Colony.popMultMap[self.climate]

                self.build_queue = None

    def report(self):
        print(f'name: {self.name}')
        print(f'net bc: {self.bc}')
        print(f'farmers: {self.num_farmers}, net food: {self.food}')
        print(f'workers: {self.num_workers}, production: {self.prod}')
        print(f'scientists: {self.num_scientists}, rp: {self.rp}')
        print(f'building: {self.build_queue}')
        print(f'raw_pop: {self.raw_pop}')
        print(f'pop_increment: {self.pop_increment}')
