import boto3
import sys

dynamodb = boto3.client('dynamodb', region_name='ca-central-1')

def stageOne(bonus_description_str):
    params = {
        "TableName": "improved_single_dragon_table",
        "IndexName": "bonus_description_index",
        "ExpressionAttributeValues": {
            ":bonus_description": {
                "S": bonus_description_str
            }
        },
        "KeyConditionExpression": "bonus_description = :bonus_description",
        "ProjectionExpression": "pk"
    }
    data = dynamodb.query(**params)
    return data['Items']

def buildExpressionAttributes(dragon_id_arr):
    expression = {}
    for i in range(len(dragon_id_arr)):
        eval_str = ":uuid_" + str(i)
        expression[eval_str] = {
            "S": dragon_id_arr[i]["pk"]["S"]
        }
    return expression

def buildFilterExpression(dragon_id_arr):
    filter_str = "pk in ("
    for i in range(len(dragon_id_arr)):
        filter_str += ":uuid_" + str(i) + ", "
    return_me_str = filter_str[:-2] + ")"
    return return_me_str

def stageTwo(dragon_id_arr):
    params = {
        "TableName": "improved_single_dragon_table",
        "IndexName": "dragon_stats_index",
        "FilterExpression": buildFilterExpression(dragon_id_arr),
        "ExpressionAttributeValues": buildExpressionAttributes(dragon_id_arr),
        "ProjectionExpression": "dragon_name"
    }
    data = dynamodb.scan(**params)
    return data["Items"]

if(sys.argv[1] == "test"):
    if(sys.argv[2]):
        bonus_description_str = sys.argv[2]
        dragon_id_arr = stageOne(bonus_description_str)
        if len(dragon_id_arr) == 0:
            print([])
        else:
            print(stageTwo(dragon_id_arr))
            print(f'{len(dragon_id_arr)} dragons found that {sys.argv[2]}')