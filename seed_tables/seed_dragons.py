import boto3
import json
import asyncio
import time

def batch25(l):
    '''Takes a list and release batches of sizes 25 as a generator'''
    l_ = []
    for i in range(len(l)):
        l_.append(l[i])
        if len(l_) == 25:
            yield l_
            l_ = []
    yield l_

dynamodb = boto3.client('dynamodb')

async def push_to_dragons_stats_table():
    items = []
    dragon_formatted = []
    with open('resources/dragon_stats_one.json', 'r') as f:
        items.extend(json.load(f))
    with open('resources/dragon_stats_two.json', 'r') as f:
        items.extend(json.load(f))

    for i in range(len(items)):
        dragon = {
            "PutRequest": {
                "Item": {
                    "damage": {
                        "N": str(items[i]['damage_int'])
                    },
                    "description": {
                        "S": items[i]['description_str']
                    },
                    "dragon_name": {
                        "S": items[i]['dragon_name_str']
                    },
                    "family": {
                        "S": items[i]['family_str']
                    },
                    "location_city": {
                        "S": items[i]['location_city_str']
                    }, 
                    "location_country": {
                        "S": items[i]['location_country_str']
                    },
                    "location_neighborhood": {
                        "S": items[i]['location_neighborhood_str']
                    },
                    "location_state": {
                        "S": items[i]['location_state_str']
                    },
                    "protection": {
                        "N": str(items[i]['protection_int'])
                    },
                }
            }
        }
        dragon_formatted.append(dragon)
    for batch in batch25(dragon_formatted):
        params = {
            'RequestItems': {
                "dragon_stats": batch
            }
        }
        dynamodb.batch_write_item(**params)


async def push_to_dragon_current_power_table():
    items = []
    dragon_formatted = []
    with open('resources/dragon_current_power.json', 'r') as f:
        items.extend(json.load(f))
    
    for i in range(len(items)):
        dragon = {
            "PutRequest": {
                "Item": {
                    "current_endurance": {
                        "N": str(items[i]['current_endurance_int'])
                    },
                    "current_will_not_fight_credits": {
                        "N": str(items[i]['current_will_not_fight_credits_int'])
                    },
                    "dragon_name": {
                        "S": items[i]['dragon_name_str']
                    },
                    "game_id": {
                        "S": items[i]['game_id_str']
                    }
                }
            }
        }
        dragon_formatted.append(dragon)
    for batch in batch25(dragon_formatted):
        params = {
            'RequestItems': {
                "dragon_current_power": batch
            }
        }
        dynamodb.batch_write_item(**params)


async def push_to_dragon_bonus_attack_table():
    items = []
    dragon_formatted = []
    with open('resources/dragon_bonus_attack.json', 'r') as f:
        items.extend(json.load(f))
    
    for i in range(len(items)):
        dragon = {
            "PutRequest": {
                "Item": {
                    "breath_attack": {
                        "S": items[i]['breath_attack_str']
                    },
                    "extra_damage": {
                        "N": str(items[i]['extra_damage_int'])
                    },
                    "description": {
                        "S": items[i]['description_str']
                    },
                    "range": {
                        "N": str(items[i]['range_int'])
                    }
                }
            }
        }
        dragon_formatted.append(dragon)
    for batch in batch25(dragon_formatted):
        params = {
            'RequestItems': {
                "dragon_bonus_attack": batch
            }
        }
        dynamodb.batch_write_item(**params)


async def push_to_dragon_family_table():
    items = []
    dragon_formatted = []
    with open('resources/dragon_family.json', 'r') as f:
        items.extend(json.load(f))
    
    for i in range(len(items)):
        dragon = {
            "PutRequest": {
                "Item": {
                    "breath_attack": {
                        "S": items[i]['breath_attack_str']
                    },
                    "damage_modifer": {
                        "N": str(items[i]['damage_modifier_int'])
                    },
                    "description": {
                        "S": items[i]['description_str']
                    },
                    "family": {
                        "S": items[i]['family_str']
                    },
                    "protection_moodifier_int": {
                        "N": str(items[i]['protection_modifier_int'])
                    }
                }
            }
        }
        dragon_formatted.append(dragon)
    for batch in batch25(dragon_formatted):
        params = {
            'RequestItems': {
                "dragon_family": batch
            }
        }
        dynamodb.batch_write_item(**params)


async def seed():
    print(f"started at {time.strftime('%X')}")
    await asyncio.gather(
        push_to_dragons_stats_table(),
        push_to_dragon_current_power_table(),
        push_to_dragon_bonus_attack_table(),
        push_to_dragon_family_table()
    )
    print(f"finished at {time.strftime('%X')}")

   

asyncio.run(seed())
