import boto3
import math
import time
import uuid
import sys
import bcrypt

dynamodb = boto3.client('dynamodb', region_name='ca-central-1')

SESSION_TIMEOUT_IN_MINUTES_INT = 20

def lambda_handler(event, context):
    print('Running lambda')
    if event.get('email_address_str') and event.get('attempted_password_str'):
        return logMeIn(event["email_address_str"], event["attempted_password_str"])
    else:
        return {"errorType": "string",
                "errorMessage": "no credentials passed",
                "trace": []
                }


def create_session(user_name_str, new_session_id_str, admin_boo):
    params = {
        "Item": {
            "session_id": {
                "S": new_session_id_str
            }, 
            "user_name": {
                "S": user_name_str
            }, 
            "expiration_time": {
                "N": str(math.floor(time.time()) + (60 * SESSION_TIMEOUT_IN_MINUTES_INT))
            }
        }, 
        "ReturnConsumedCapacity": "TOTAL", 
        "TableName": "sessions"
    }
    if admin_boo == True:
        params['Items']["admin"] = {'BOOL': True}

    dynamodb.put_item(**params)

def logMeIn(email_address_str, attempted_password_str):
    params = {
        "ExpressionAttributeValues": {
            ":email_address": {
                "S": email_address_str
            }
        },
        "KeyConditionExpression": "email_address = :email_address",
        "TableName": "users",
        "IndexName": "email_admin_index"
    }
    data = dynamodb.query(**params)
    new_session_id_str = str(uuid.uuid4())
    admin_boo = False
    if data['Items'] and data['Items'][0]:
        password = data['Items'][0]['password']['S'] 
        if bcrypt.checkpw(attempted_password_str.encode('utf-8'), password.encode('utf-8')):
            print("Password is correct")
            if data['Items'][0].get('admin') and data.Items[0]['admin']['BOOL']==True:
                admin_boo = True
            create_session(data['Items'][0]['user_name']['S'], new_session_id_str, admin_boo)
            return_me = {"user_name_str": data['Items'][0]['user_name']['S'],
                         "session_id_str": new_session_id_str}
            if admin_boo:
                return_me['admin_boo'] = True
            return return_me
        else:
            return {"errorType": "string",
                    "errorMessage": "password does not match email",
                    "trace": []
            }
    else:
        return {"errorType": "string",
                    "errorMessage": "credential invalid",
                    "trace": []
            }


#if sys.argv[1] == "test":
#        if sys.argv[2] and sys.argv[3]:
#            print("Local test to log in a user with email of ", sys.argv[2])
#            print(boto3.__version__)
#            print(bcrypt.__version__)
#            #logMeIn(sys.argv[2], sys.argv[3])
#        else:
#            print("Pass in email address and password")
