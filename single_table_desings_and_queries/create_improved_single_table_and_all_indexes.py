import boto3

dynamodb = boto3.client('dynamodb', region_name='ca-central-1')                                             

def create_improved_table_and_all_indexes():
    params = {
        "AttributeDefinitions": [{
            "AttributeName": "pk", 
            "AttributeType": "S"
        },{
            "AttributeName": "sk", 
            "AttributeType": "S"
        },{
            "AttributeName": "range", 
            "AttributeType": "N"
        },{
            "AttributeName": "location", 
            "AttributeType": "S"
        },{
            "AttributeName": "dragon_name", 
            "AttributeType": "S"
        },{
            "AttributeName": "bonus_description", 
            "AttributeType": "S"
        }], 
        "KeySchema": [{
            "AttributeName": "pk", 
            "KeyType": "HASH"
        },{
            "AttributeName": "sk", 
            "KeyType": "RANGE"
        }],
        "BillingMode": "PAY_PER_REQUEST",
        "TableName": "improved_single_dragon_table",
        "GlobalSecondaryIndexes": [{
            "IndexName": "dragon_stats_index",
            "KeySchema": [{
                "AttributeName": "dragon_name",
                "KeyType": "HASH"
            }],
            "Projection": {
                "NonKeyAttributes": [
                                "protection",
                                "damage",
                                "description",
                                "family"
                ],
                "ProjectionType": "INCLUDE"
            }
        },{
            "IndexName": "bonus_description_index",
            "KeySchema": [{
                "AttributeName": "bonus_description",
                "KeyType": "HASH"
            }],
            "Projection": {
                "NonKeyAttributes": [
                    "pk"
                ],
                "ProjectionType": "INCLUDE"
            }
        },{
            "IndexName": "range_index",
            "KeySchema": [{
                "AttributeName": "sk",
                "KeyType": "HASH"
            },{
                "AttributeName": "range",
                "KeyType": "RANGE"
            }],
            "Projection": {
                "NonKeyAttributes": [
                    "pk"
                ],
                "ProjectionType": "INCLUDE"
            }
        },{
            "IndexName": "location_index",
            "KeySchema": [{
                "AttributeName": "sk",
                "KeyType": "HASH"
            },{
                "AttributeName": "location",
                "KeyType": "RANGE"
            }],
            "Projection": {
                "NonKeyAttributes": [
                    "dragon_name",
                    "protection",
                    "damage",
                    "description",
                    "family"
                ],
                "ProjectionType": "INCLUDE"
            }
        }]
    }
    data = dynamodb.create_table(**params)
    print(data)

create_improved_table_and_all_indexes()