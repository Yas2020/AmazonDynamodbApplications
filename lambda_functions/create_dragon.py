import boto3
import sys
import json
import base64

BUCKET_STR = "dragons01092022"
dynamodb = boto3.client('dynamodb', region_name='ca-central-1')
s3 = boto3.client('s3', region_name='ca-central-1')

def lambda_handler(event, context):
    print("running lambda")
    if event.get('user_name_str') and event.get('session_id_str'):
        if confirm_admin_login(event['user_name_str'], event['session_id_str']):
            print("valid credentials: user is admin")
            if event.get('new_dragon'):
                original_dragon_name_str = event['original_dragon_name_str']
                new_item = event['updates']
                image_base64 = event['image']
                return add_dragon(original_dragon_name_str, new_item, image_base64)
    else:
        return "nope"


def confirm_admin_login(user_name_str, session_id_str):
    params = {
            "ExpressionAttributeValues": {
                ":session_id": {
                    "S": session_id_str
                },
                ":admin_boo": {
                    "BOOL": True
                }
            },
            "KeyConditionExpression": "session_id = :session_id",
            "FilterExpression": "admin = :admin_boo",
            "TableName": "sessions"
        }
    data = dynamodb.query(**params)
    if data['Items'] and data['Items'][0]['user_name']['S'] == user_name_str:
        return True
    else:
        return "nope"



def add_dragon(original_dragon_name_str, new_item, image_base64):
    old_item = get_old_dragon_item(original_dragon_name_str)
    if len(old_item['Items']) > 0:
        return "dragon found with name " + original_dragon_name_str

    new_dragon = {
            "Item":{
                "dragon_name":{
                    "S": new_item['dragon_name_str']
                },
                "description": {
                    "S": new_item['description_str']
                },
                "family": {
                    "S": 'blue'
                },
                "damage": {
                    "N": str(new_item['damage_int'])
                },
                "protection": {
                    "N":  str(new_item['protection_int'])
                },
            },
            "ReturnValues": "ALL_OLD",
            "ReturnConsumedCapacity": "TOTAL",
            "TableName": "dragon_stats"
        }
    s3.put_object(
        Body=base64.b64decode(image_base64),
        Bucket=BUCKET_STR, 
        Key=new_item['dragon_name_str'] + ".png"
    )    
        
    dynamodb.put_item(**new_dragon)
    # update_image_On_S3(dragon['dragon_name']['S'], original_dragon_name_str)
    
    print('Upload to s3 done successfully')
    return new_dragon["Item"]



def get_old_dragon_item(original_dragon_name_str):
    params = {
            "ExpressionAttributeValues": {
                ":dragon_name": {
                    "S": original_dragon_name_str
                }
            },
            "KeyConditionExpression": "dragon_name = :dragon_name",
            "TableName": "dragon_stats",
        }
    return dynamodb.query(**params)

