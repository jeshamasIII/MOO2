from collections import namedtuple

level_to_rp_cost = {
    1: 50, 2: 80, 3: 150, 4: 250, 5: 400, 6: 650, 7: 900, 8: 1150,
    9: 1500, 10: 2000, 11: 2750, 12: 3500, 13: 4500, 14: 6000, 15: 7500
}

ResearchLevel = namedtuple(
    'ResLevel',
    ['buildings', 'achievements', 'field', 'level', 'rp_cost']
)

# Tech tree for a creative, democratic race.
construction = [
    ResearchLevel([], [], 'construction', 1, level_to_rp_cost[1]),  # removed colonyBase
    ResearchLevel([], [], 'construction', 2, level_to_rp_cost[2]),
    ResearchLevel(['automatedFactory'], [], 'construction', 3, level_to_rp_cost[3]),
    ResearchLevel([], [], 'construction', 4, level_to_rp_cost[4]),
    ResearchLevel(['spaceport'], [], 'construction', 5, level_to_rp_cost[5]),
    ResearchLevel(['roboMinerPlant'], [], 'construction', 6, level_to_rp_cost[6]),
    ResearchLevel([], [], 'construction', 7, level_to_rp_cost[7]),
    ResearchLevel([], [], 'construction', 8, level_to_rp_cost[8]),
    ResearchLevel(['recyclotron'], [], 'construction', 9, level_to_rp_cost[9]),
    ResearchLevel(['roboticFactory'], [], 'construction', 10, level_to_rp_cost[10]),
    ResearchLevel(['coreWasteDump', 'deepCoreMine'], [], 'construction', 12,
                  level_to_rp_cost[12]),
    ResearchLevel([], ['advancedCityPlanning'], 'construction', 14, level_to_rp_cost[14])
]

chemistry = [
    ResearchLevel([], [], 'chemistry', 1, level_to_rp_cost[1]),
    ResearchLevel([], [], 'chemistry', 4, level_to_rp_cost[4]),
    ResearchLevel(['pollutionProcessor'], [], 'chemistry', 6, level_to_rp_cost[6]),
    ResearchLevel(['atmosphereRenewer'], [], 'chemistry', 8, level_to_rp_cost[8]),
    ResearchLevel([], ['microliteConstruction', 'nanoDisassemblers'], 'chemistry', 10,
                  level_to_rp_cost[10])
]

sociology = [
    ResearchLevel([], [], 'sociology', 3, level_to_rp_cost[3]),
    ResearchLevel([], [], 'sociology', 6, level_to_rp_cost[6]),
    ResearchLevel(['stockExchange'], [], 'sociology', 8, level_to_rp_cost[8]),
    ResearchLevel(['astroUniversity'], [], 'sociology', 10, level_to_rp_cost[10]),
    ResearchLevel([], ['federation'], 'sociology', 13, level_to_rp_cost[13]),
    ResearchLevel([], ['currencyExchange'], 'sociology', 14, level_to_rp_cost[14])
]

computers = [
    ResearchLevel([], [], 'computers', 1, level_to_rp_cost[1]),
    ResearchLevel(['researchLab'], [], 'computers', 3, level_to_rp_cost[3]),
    ResearchLevel([], [], 'computers', 5, level_to_rp_cost[5]),
    ResearchLevel(['holoSimulator', 'supercomputer'], [], 'computers', 7,
                  level_to_rp_cost[7]),
    ResearchLevel([], [], 'computers', 9, level_to_rp_cost[9]),
    ResearchLevel(['autolab'], [], 'computers', 11, level_to_rp_cost[11]),
    ResearchLevel([], [], 'computers', 12, level_to_rp_cost[12]),
    ResearchLevel(['galacticCybernet'], ['realityNetwork'], 'computers', 13,
                  level_to_rp_cost[13]),
    ResearchLevel(['pleasureDome'], [], 'computers', 14, level_to_rp_cost[14])
]

# soilEnrichment is treated as a building
biology = [
    ResearchLevel(['biospheres', 'hydroponicFarm'], [], 'biology', 2,
                  level_to_rp_cost[2]),
    ResearchLevel(['cloningCenter', 'soilEnrichment'], [], 'biology', 5,
                  level_to_rp_cost[5]),
    ResearchLevel([], ['microbiotics'], 'biology', 7, level_to_rp_cost[7]),
    ResearchLevel(['terraforming'], [], 'biology', 8, level_to_rp_cost[8]),
    ResearchLevel(['subterraneanFarms', 'weatherController'], [], 'biology', 9,
                  level_to_rp_cost[9]),
    ResearchLevel([], ['heightenedIntelligence'], 'biology', 11, level_to_rp_cost[11]),
    ResearchLevel([], ['universalAntidote'], 'biology', 13, level_to_rp_cost[13]),
    ResearchLevel(['gaiaTransformation'], ['biomorphicFungi'], 'biology', 15,
                  level_to_rp_cost[15])
]

physics = [
    ResearchLevel([], [], 'physics', 1, level_to_rp_cost[1]),
    ResearchLevel([], [], 'physics', 3, level_to_rp_cost[3]),
    ResearchLevel([], [], 'physics', 4, level_to_rp_cost[4]),
    ResearchLevel([], [], 'physics', 7, level_to_rp_cost[7]),
    ResearchLevel(['gravityGenerator'], [], 'physics', 8, level_to_rp_cost[8])
]

force_fields = [
    ResearchLevel([], [], 'force_fields', 4, level_to_rp_cost[4]),
    ResearchLevel([], [], 'force_fields', 6, level_to_rp_cost[6]),
    ResearchLevel(['radiationShield'], [], 'force_fields', 7, level_to_rp_cost[7])
]

tree = {'construction': construction, 'chemistry': chemistry,
        'computers': computers, 'biology': biology, 'sociology': sociology}
