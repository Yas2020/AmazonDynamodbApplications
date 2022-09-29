import boto3

dynamodb = boto3.resource('dynamodb')

def create_database_table_index():
    params = {
            'TableName': "users",
            'AttributeDefinitions': [{
                'AttributeName': "user_name", 
                'AttributeType': "S"
            },{
                'AttributeName': "email_address", 
                'AttributeType': "S"
            }], 
            'KeySchema': [{
                'AttributeName': "user_name", 
                'KeyType': "HASH"
            }],
            'BillingMode': "PAY_PER_REQUEST",
            'GlobalSecondaryIndexes': [{
                'IndexName': "email_index",
                'KeySchema': [{
                    'AttributeName': "email_address",
                    'KeyType': "HASH"
                }],
                'Projection': {
                    'NonKeyAttributes': [
                        "password",
                    ],
                    'ProjectionType': "INCLUDE"
                }
            }]
        }
    dynamodb.create_table(**params)

create_database_table_index()