import boto3
import sys

dynamodb = boto3.client('dynamodb', region_name='ca-central-1')
G_RANGE = []

def stageOne():
    params = {
        "TableName": "improved_single_dragon_table",
        "IndexName": "range_index",
        "ScanIndexForward": False,
        "ExpressionAttributeValues": {
            ":bonus": {
                "S": "bonus"
            }
        },
        "ExpressionAttributeNames": {
                "#range": "range"
        },
        "KeyConditionExpression": "sk = :bonus",
        "ProjectionExpression": "pk, #range"
        }
    data = dynamodb.query(**params)
    return data['Items']

def buildExpressionAttributes(dragon_id):
    expression = {}
    for i in range(len(dragon_id)):
        eval_str = ":uuid_" + str(i)
        expression[eval_str] = {
            "S": dragon_id[i]["pk"]["S"]
        }
    return expression

def buildFilterExpression(dragon_id):
    filter_str = "pk in ("
    for i in range(len(dragon_id)):
        filter_str += ":uuid_" + str(i) + ", "
    return_me_str = filter_str[:-2] + ")"
    return return_me_str

def addRange(dragons_without_range):
    for i in range(len(G_RANGE)):
        for j in range(len(dragons_without_range)):
            if dragons_without_range[j]["pk"]["S"] == G_RANGE[i]["pk"]["S"]:
                G_RANGE[i]["damage"] = dragons_without_range[j]["damage"]
                G_RANGE[i]["protection"] = dragons_without_range[j]["protection"]
                G_RANGE[i]["family"] = dragons_without_range[j]["family"]
                G_RANGE[i]["description"] = dragons_without_range[j]["description"]
                G_RANGE[i]["dragon_name"] = dragons_without_range[j]["dragon_name"]
                # remove sk and leave pk as is
                del G_RANGE[i]["sk"]
                break
    return G_RANGE

def stageTwo(dragon_id):
    params = {
        "TableName": "improved_single_dragon_table",
        "IndexName": "dragon_stats_index",
        "FilterExpression": buildFilterExpression(dragon_id),
        "ExpressionAttributeValues": buildExpressionAttributes(dragon_id),
        "ProjectionExpression": "dragon_name"
    }
    data = dynamodb.scan(**params)
    return data["Items"]

if(sys.argv[1] == "test"):
    dragon_id = stageOne()
    if len(dragon_id) == 0:
        print([]) #no dragons found
    else:
        print(stageTwo(dragon_id))
