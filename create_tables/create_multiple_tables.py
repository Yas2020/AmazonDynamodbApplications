import boto3
import asyncio
import time

dynamodb = boto3.resource('dynamodb')

async def create_dragon_stats_table():
    params = {
        'TableName': "dragon_stats",
        'AttributeDefinitions':[
                {
                    "AttributeName": "dragon_name",
                    "AttributeType": "S"
                },],
        'KeySchema':[
                {
                    "AttributeName": "dragon_name",
                    "KeyType": "HASH"
                },],
        'BillingMode': "PAY_PER_REQUEST",
    }
    dynamodb.create_table(**params)
    
async def create_dragon_bonus_attack_table():
    params = {
        'TableName': "dragon_bonus_attack",
        'AttributeDefinitions':[
                {
                    "AttributeName": "breath_attack",
                    "AttributeType": "S"
                },{
                    "AttributeName": "range",
                    "AttributeType": "N"
                },],
        'KeySchema':[
                {
                    "AttributeName": "breath_attack",
                    "KeyType": "HASH"
                },{
                    "AttributeName": "range",
                    "KeyType": "RANGE"
                    },],
        'BillingMode': "PAY_PER_REQUEST",
        }
    dynamodb.create_table(**params)


async def create_dragon_family_table():
    params = {
        'TableName': "dragon_family",
        'AttributeDefinitions':[
                {
                    "AttributeName": "family",
                    "AttributeType": "S"
                },],
        'KeySchema':[
                {
                    "AttributeName": "family",
                    "KeyType": "HASH"
                },],
        'BillingMode': "PAY_PER_REQUEST",
        }
    dynamodb.create_table(**params)
 


async def create_all_tables():

    print(f"started at {time.strftime('%X')}")
    await asyncio.gather(
        create_dragon_stats_table(),
        create_dragon_bonus_attack_table(),
        create_dragon_family_table()
    )
    print(f"finished at {time.strftime('%X')}")

   

asyncio.run(create_all_tables())