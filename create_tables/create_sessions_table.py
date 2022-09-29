import boto3

dynamodb = boto3.resource('dynamodb')

def create_sessions_table():
    params = {
            "AttributeDefinitions": [{
                'AttributeName': "session_id", 
                'AttributeType': "S"
            },{
                'AttributeName': "user_name", 
                'AttributeType': "S"
            }], 
            'KeySchema': [{
                'AttributeName': "session_id", 
                'KeyType': "HASH"
            },{
                'AttributeName': "user_name", 
                'KeyType': "RANGE"
            }],
            'BillingMode': "PAY_PER_REQUEST",
            'TableName': "sessions"
        }
    dynamodb.create_table(**params)

create_sessions_table()