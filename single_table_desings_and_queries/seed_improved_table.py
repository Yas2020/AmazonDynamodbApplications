import boto3
import uuid
import asyncio

dynamodb = boto3.client('dynamodb', region_name='ca-central-1')

DRAGON_STATS = []
DRAGON_FAMILY = []
DRAGON_BONUS = []

async def get_stats():
    global DRAGON_STATS
    params = {
        "TableName": "dragon_stats"
    }
    stats_response = dynamodb.scan(**params)
    DRAGON_STATS = stats_response['Items'][:]

async def get_family():
    global DRAGON_FAMILY
    params = {
        "TableName": "dragon_family"
    }
    stats_response = dynamodb.scan(**params)
    DRAGON_FAMILY = stats_response['Items']

async def get_bonus():
    global DRAGON_BONUS
    params = {
        "TableName": "dragon_bonus_attack"
    }
    stats_response = dynamodb.scan(**params)
    DRAGON_BONUS = stats_response['Items']


async def build():
    for i in range(len(DRAGON_STATS)):
        dragon_uuid_str = str(uuid.uuid4())
        dragon_stats = DRAGON_STATS[i]
        location_str =  dragon_stats['location_country']['S'] + "#" + \
                        dragon_stats['location_state']['S'] + "#" + \
                        dragon_stats['location_city']['S'] + "#" + \
                        dragon_stats['location_neighborhood']['S']
        dragon_family = {}
        dragon_bonus = {}
        
        dragon_stats['sk'] = {
            "S": "stats"
        }
        # delete dragon_stats.pk; 
        dragon_stats['pk'] = {
            "S": dragon_uuid_str
        }
        dragon_stats['location'] = {
            "S": location_str
        }
        del dragon_stats['location_country']
        del dragon_stats['location_state']
        del dragon_stats['location_neighborhood']
        del dragon_stats['location_city']
        for j in range(len(DRAGON_FAMILY)):
            if DRAGON_FAMILY[j]['family']['S'] == dragon_stats['family']['S']:
                dragon_family['pk'] = {
                    "S": dragon_uuid_str
                }
                dragon_family['sk'] = {
                    "S": "family"
                }
                dragon_family['breath_attack'] = DRAGON_FAMILY[j]['breath_attack']
                dragon_family['damage_modifier'] = DRAGON_FAMILY[j]['damage_modifer'] #type
                dragon_family['protection_modifier'] = DRAGON_FAMILY[j]['protection_moodifier_int'] #typo
                dragon_family['family_description'] = DRAGON_FAMILY[j]['description']
                break
        
        for k in range(len(DRAGON_BONUS)):
            if DRAGON_BONUS[k]['breath_attack']['S'] == dragon_family['breath_attack']['S']:
                dragon_bonus['pk'] = {
                    "S": dragon_uuid_str
                }
                dragon_bonus['sk'] = {
                    "S": "bonus"
                }
                dragon_bonus['range'] = DRAGON_BONUS[k]['range']
                dragon_bonus['extra_damage'] = DRAGON_BONUS[k]['extra_damage']
                dragon_bonus['bonus_description'] = DRAGON_BONUS[k]['description']
                break
   
        run_transaction(dragon_stats, dragon_family, dragon_bonus)

def run_transaction(dragon_stats, dragon_family, dragon_bonus):
    params = {
        "TransactItems": [{
            "Put": {
                "Item": dragon_stats,
                "TableName": "improved_single_dragon_table"
            }
        },{
            "Put": {
                "Item": dragon_family,
                "TableName": "improved_single_dragon_table"
            }
        },{
            "Put": {
                "Item": dragon_bonus,
                "TableName": "improved_single_dragon_table"
            }
        }]
    }
    return dynamodb.transact_write_items(**params)



async def seed():
    await asyncio.gather(
        get_stats(),
        get_family(),
        get_bonus(),
        build()
    )
    print('seeded')

asyncio.run(seed())
