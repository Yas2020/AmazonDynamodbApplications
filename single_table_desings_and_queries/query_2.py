import boto3
import sys

dynamodb = boto3.client('dynamodb', region_name='ca-central-1')

def using_scan(family_str):
    params = {
        "TableName": "improved_single_dragon_table",
        "IndexName": "dragon_stats_index",
        "ExpressionAttributeValues": {
            ":family": {
                "S": family_str
            }
        },
        "ExpressionAttributeNames": {
            "#family": "family"
            },
        "FilterExpression": "#family = :family",
        "ProjectionExpression": "dragon_name"
    }
    data = dynamodb.scan(**params)
    return data['Items']

if sys.argv[1] == "test":
    if sys.argv[2]:
        print(using_scan(sys.argv[2]))