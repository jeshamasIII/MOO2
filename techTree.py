# research level class
from collections import namedtuple

# maps level to rp cost
cost_map = {1: 50, 2: 80, 3: 150, 4: 250, 5: 400, 6: 650, 7: 900, 8: 1150, 9: 1500,
            10: 2000, 11: 2750, 12: 3500, 13: 4500, 14: 6000, 15: 7500
            }

ResLevel = namedtuple('ResLevel', ['buildings', 'achievements', 'field', 'level', 'cost'])

# the following assumes that the race is creative and democratic
const = [ResLevel([], [], 'const', 1, cost_map[1]),  # removed colonyBase
         ResLevel([], [], 'const', 2, cost_map[2]),
         ResLevel(['automatedFactory'], [], 'const', 3, cost_map[3]),
         ResLevel([], [], 'const', 4, cost_map[4]),
         ResLevel(['spaceport'], [], 'const', 5, cost_map[5]),
         ResLevel(['roboMinerPlant'], [], 'const', 6, cost_map[6]),
         ResLevel([], [], 'const', 7, cost_map[7]),
         ResLevel([], [], 'const', 8, cost_map[8]),
         ResLevel(['recyclotron'], [], 'const', 9, cost_map[9]),
         ResLevel(['roboticFactory'], [], 'const', 10, cost_map[10]),
         ResLevel(['coreWasteDump', 'deepCoreMine'], [], 'const', 12, cost_map[12]),
         ResLevel([], ['advancedCityPlanning'], 'const', 14, cost_map[14])
         ]

chem = [ResLevel([], [], 'chem', 1, cost_map[1]),
        ResLevel([], [], 'chem', 4, cost_map[4]),
        ResLevel(['pollutionProcessor'], [], 'chem', 6, cost_map[6]),
        ResLevel(['atmosphereRenewer'], [], 'chem', 8, cost_map[8]),
        ResLevel([], ['microliteConstruction', 'nanoDisassemblers'], 'chem', 10, cost_map[10])
        ]

soc = [ResLevel([], [], 'soc', 3, cost_map[3]),
       ResLevel([], [], 'soc', 6, cost_map[6]),
       ResLevel(['stockExchange'], [], 'soc', 8, cost_map[8]),
       ResLevel(['astroUniversity'], [], 'soc', 10, cost_map[10]),
       ResLevel([], ['federation'], 'soc', 13, cost_map[13]),
       ResLevel([], ['currencyExchange'], 'soc', 14, cost_map[14])
       ]

comp = [ResLevel([], [], 'comp', 1, cost_map[1]),
        ResLevel(['researchLab'], [], 'comp', 3, cost_map[3]),
        ResLevel([], [], 'comp', 5, cost_map[5]),
        ResLevel(['holoSimulator', 'supercomputer'], [], 'comp', 7, cost_map[7]),
        ResLevel([], [], 'comp', 9, cost_map[9]),
        ResLevel(['autolab'], [], 'comp', 11, cost_map[11]),
        ResLevel([], [], 'comp', 12, cost_map[12]),
        ResLevel(['galacticCybernet'], ['realityNetwork'], 'comp', 13, cost_map[13]),
        ResLevel(['pleasureDome'], [], 'comp', 14, cost_map[14])
        ]

# soilEnrichement is treated as a building
bio = [ResLevel(['biospheres', 'hydroponicFarm'], [], 'bio', 2, cost_map[2]),
       ResLevel(['cloningCenter', 'soilEnrichment'], [], 'bio', 5, cost_map[5]),
       ResLevel([], ['microbiotics'], 'bio', 7, cost_map[7]),
       ResLevel(['terraforming'], [], 'bio', 8, cost_map[8]),
       ResLevel(['subterraneanFarms', 'weatherController'], [], 'bio', 9, cost_map[9]),
       ResLevel([], ['heightenedIntelligence'], 'bio', 11, cost_map[11]),
       ResLevel([], ['universalAntidote'], 'bio', 13, cost_map[13]),
       ResLevel(['gaiaTransformation'], ['biomorphicFungi'], 'bio', 15, cost_map[15])
       ]

phy = [ResLevel([], [], 'phy', 1, cost_map[1]),
       ResLevel([], [], 'phy', 3, cost_map[3]),
       ResLevel([], [], 'phy', 4, cost_map[4]),
       ResLevel([], [], 'phy', 7, cost_map[7]),
       ResLevel(['gravityGenerator'], [], 'phy', 8, cost_map[8])
       ]

ff = [ResLevel([], [], 'ff', 4, cost_map[4]),
      ResLevel([], [], 'ff', 6, cost_map[6]),
      ResLevel(['radiationShield'], [], 'ff', 7, cost_map[7])
      ]

tree = {'const': const, 'chem': chem, 'comp': comp,
        'bio': bio, 'soc': soc}
