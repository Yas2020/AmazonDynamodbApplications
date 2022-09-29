import boto3
import sys

dynamodb = boto3.client('dynamodb', region_name='ca-central-1')

def stageOne(location_str):
    params = {
        "TableName": "improved_single_dragon_table",
        "IndexName": "location_index",
        "ExpressionAttributeValues": {
            ":location": {
                "S": location_str
            },
            ":stats": {
                "S": "stats"
            }
        },
        "ExpressionAttributeNames": {
            "#location": "location"
        },
        "KeyConditionExpression" :"sk = :stats and begins_with(#location, :location)"
    }
    data = dynamodb.query(**params)
    return data["Items"]

if sys.argv[1] == "test":
    location_str = sys.argv[2]
    dragon = stageOne(location_str)
    if len(dragon) == 0:
        print([])
    else:
        print(dragon)

