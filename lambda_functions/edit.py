import boto3
import sys
import json

BUCKET_STR = "dragons01092022"
dynamodb = boto3.client('dynamodb', region_name='ca-central-1')
s3 = boto3.client('s3', region_name='ca-central-1')

def lambda_handler(event, context):
    print("running lambda")
    if event.get('user_name_str') and event.get('session_id_str'):
        if confirm_admin_login(event['user_name_str'], event['session_id_str']):
            print("valid credentials: user is admin")
            update_str = construct_update(event['updates'])
            expression = construct_expression_object(event['updates'])
            if event['updates'].get('dragon_name_str'):
                return handle_special_case(event['original_dragon_name_str'], event['updates'])
            else:
                if update_str == "SE":
                    return "nothing to update"
                return edit_card(event['original_dragon_name_str'], update_str, expression)
    else:
        return "nope"


def update_image_On_S3(new_dragon_name_str, old_dragon_name_str):
# The protection for overwriting existing dragons 
# woud have kicked in before this so we are safe to update here.

    print("swapping image")
    print(new_dragon_name_str, old_dragon_name_str)
    s3.copy_object(
        Bucket=BUCKET_STR, 
        CopySource=BUCKET_STR + "/" + old_dragon_name_str + ".png", 
        Key=new_dragon_name_str + ".png"
    )
    # Delete the old object
    s3.delete_object(
        Bucket=BUCKET_STR, 
        Key=old_dragon_name_str
    )
    print('Image changed!')


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
    if len(data['Items'])>0 and data['Items'][0].get('user_name') and data.Items[0]['user_name']['S'] == user_name_str:
        return True
    else:
        return False

def construct_update(payload):
    update_str = 'SET '
    if payload.get('dragon_name_str'):
        update_str += "dragon_name = :dragon_name, "
    if payload.get('damage_int') and payload['damage_int']>0 and payload['damage_int']<11:
        update_str += "damage = :damage, "
    if payload.get('description_str'):
        update_str += "description = :description, "
    if payload.get('protection_int') and payload['protection_int']>0 and payload['protection_int']<11:
       update_str += "protection = :protection, "
    if payload.get('family_str'):
        update_str += "#family = :family, "
    return update_str[:-2] #remove trailing comma

def construct_expression_object(payload):
    expression = {}
    if payload.get('dragon_name_str'):
        expression[":dragon_name"] = {
            "S": payload['dragon_name_str']
        }
    if payload.get('damage_int') and payload['damage_int']>0 and payload['damage_int']<11:
        expression[":damage"] = {
            "N": str(payload['damage_int'])
        }
    if payload.get('description_str'):
        expression[":description"] = {
            "S": payload['description_str']
        }
    if payload.get('protection_int') and payload['protection_int']>0 and payload['protection_int']<11:
        expression[":protection"] = {
            "N": str(payload.get('protection_int'))
        }
    if payload.get('family_str'):
        expression[":family"] = {
            "N": payload['family_str']
        }
    return expression

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

def edit_card(original_dragon_name_str, update_str, expression):
    if len(expression) == 0:
        return []
    params = {
        "Key": {
            "dragon_name": {
                "S": original_dragon_name_str
            }
        },
        "ExpressionAttributeValues": expression,
        "UpdateExpression": update_str,
        "ReturnValues": "UPDATED_NEW",
        "TableName": "dragon_stats"
    }
    if expression.get(":family"):
        params['ExpressionAttributeNames'] = {"S": "family"}
    data = dynamodb.update_item(**params)
    if data.get('Attributes'):
        return data['Attributes']
    else:
        return []
 
def get_updated_item_from_json(dragon_name_to_edit_str):
    file_path_str = "./resources/"
    file_name_str = "update_to_" + dragon_name_to_edit_str.lower() + ".json"
    f = open(file_path_str + file_name_str)
    data = json.load(f)
    return data

def handle_special_case(original_dragon_name_str, updated_attributes):
    old_item = get_old_dragon_item(original_dragon_name_str)
    if len(old_item['Items']) == 0:
        return "no dragon found with name " + original_dragon_name_str
    dragon = old_item['Items'][0]
    dragon['dragon_name'] = {
        "S": updated_attributes['dragon_name_str']
    }
    if updated_attributes.get('damage_int'):
        dragon['damage'] = {
            "N": str(updated_attributes['damage_int'])
        }
    if updated_attributes.get('description_str'):
        dragon['description'] = {
            "S": updated_attributes['description_str']
        }
    if updated_attributes.get('protection_int'):
        dragon['protection'] = {
            "N": str(updated_attributes['protection_int'])
        }
    if updated_attributes.get('family_str'):
        dragon['family'] = {
            "S": updated_attributes['family_str']
        }
    
    # START TRANSACTION
    new_dragon = run_transaction(dragon, original_dragon_name_str)
    update_image_On_S3(dragon['dragon_name']['S'], original_dragon_name_str)
    return new_dragon

# Transactions needed to make sure deleting one record occurs only when new one is created. Both operations (DELETE and CREATE) are tied together!
def run_transaction(dragon, original_dragon_name_str):
    params = {
            "TransactItems": [{
                "Delete": {
                    "Key": {
                        "dragon_name": {
                            "S": original_dragon_name_str
                        }
                    },
                    "TableName": "dragon_stats"
                }
            },{
                "Put": {
                    "Item": dragon,
                    "TableName": "dragon_stats",
                    # Dont create double dragons with the same name! equivalent to "
                    # CREATE dragon WHERE dragon_name NOT EXIST"
                    "ConditionExpression": "attribute_not_exists(dragon_name)"
                }
            }]
        }
    dynamodb.transact_write_items(**params)
    print("Transaction Sucessful!")
    return dragon

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


# if sys.argv[1] == "test":
#     confirm_admin_login(sys.argv[2], sys.argv[3])
#     updated_attributes = get_updated_item_from_json(sys.argv[4])
#     original_dragon_name_str = sys.argv[4]
#     if updated_attributes.get('dragon_name_str'):
#         handle_special_case(original_dragon_name_str, updated_attributes)
#     else:
#         update_str = construct_update(updated_attributes)
#         expression = construct_expression_object(updated_attributes)
#         edit_card(original_dragon_name_str, update_str, expression)