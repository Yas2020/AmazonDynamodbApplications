import boto3
import sys

dynamodb = boto3.client('dynamodb', region_name='ca-central-1')

def lambda_handler(event, context):
    if event['user_name_str'] and event['session_id_str']:
        if confirm_login(event['user_name_str'], event['session_id_str']):
            if event["dragon_name_str"] != '' and event["dragon_name_str"] != "All":
                return just_this_dragon(event["dragon_name_str"])
            else:
                return scan_table()
    return "not allowed"

def confirm_login(user_name_str, session_id_str):
    params = {
        "ExpressionAttributeValues": {
                ":session_id": {
                    "S": session_id_str
                }
            },
            "KeyConditionExpression": "session_id = :session_id",
            "TableName": "sessions"
    }
    data = dynamodb.query(**params) 
    print(data)
    if len(data['Items'])>0 and data['Items'][0].get('user_name') and data['Items'][0]['user_name']['S'] == user_name_str:
        return True


def just_this_dragon(dragon_name_str):
    params = {
            "ExpressionAttributeValues": {
                ":dragon_name": {
                    "S": dragon_name_str
                }
            },
            "KeyConditionExpression": "dragon_name = :dragon_name",
            "ExpressionAttributeNames": {
                "#family": "family"
            },
            "ProjectionExpression": "dragon_name, #family, protection, damage, description",
            "TableName": "dragon_stats"
        }
    data = dynamodb.query(**params)
    if len(data['Items'])>0:
        return data['Items']
    else:
        return []

def scan_table():
    params = {
            "TableName": "dragon_stats",
            "ExpressionAttributeNames": {
                "#family": "family"
            },
            "ProjectionExpression": "dragon_name, #family, protection, damage, description"
        }
    items = []
    response = dynamodb.scan(**params)
    items.extend(response['Items'])
    while 'LastEvaluatedKey' in response:
        params['ExclusiveStartKey'] = response['LastEvaluatedKey'] 
        response = dynamodb.scan(**params)
        items.extend(response['Items'])
    return items



# if(sys.argv[1] == "test"):
#     if (sys.argv[2] and sys.argv[2] != "All"):
#         print("Local test for a dragon called " + sys.argv[2])
#         print(just_this_dragon(sys.argv[2]))
#     else:
#         print("Local test for all dragons")
#         print(scan_table())