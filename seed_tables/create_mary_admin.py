import boto3
import bcrypt

dynamodb = boto3.client('dynamodb', region_name='ca-central-1')

def encrypt_password(password):
    encoded_password = password.encode('utf-8')
    password_binary = bcrypt.hashpw(encoded_password, bcrypt.gensalt(10)) # a binary string
    return password_binary.decode('utf-8')

def upload_Mary_as_admin():
    admin = {
            "Item":{
                "user_name":{
                    "S": "mary001"
                },
                "first_name": {
                    "S": "mary"
                },
                "email_address": {
                    "S":"mary@dragoncardgame001.com"
                },
                "password": {
                    "S":  encrypt_password("pears")
                },
                "admin": {
                    "BOOL": True
                }
            },
            "ReturnConsumedCapacity": "TOTAL",
            "TableName": "users"
        }
    dynamodb.put_item(**admin)

upload_Mary_as_admin()