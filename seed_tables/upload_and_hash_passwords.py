import boto3
import json
import bcrypt
import asyncio
import time

# A untility function for creating batches because dynamodb only allows batch writing of up to 25 elements
def batch25(l):
    '''Takes a list and release batches of sizes 25 as a generator'''
    l_ = []
    for i in range(len(l)):
        l_.append(l[i])
        if len(l_) == 25:
            yield l_
            l_ = []
    yield l_

dynamodb = boto3.client('dynamodb')

async def encrypt_password(password):
    encoded_password = password.encode('utf-8')
    password_binary = bcrypt.hashpw(encoded_password, bcrypt.gensalt(10)) # a binary string
    return password_binary.decode('utf-8') # convert back to a string


async def push_to_user_table():
    items = []
    user_formatted = []
    with open('resources/users.json', 'r') as f:
        items.extend(json.load(f))
    
    for i in range(len(items)):
        # only a very small list of users so no need for async optimization here.
        password_str = await encrypt_password(items[i]['temp_password_str'])
        user = {
            'PutRequest': {
                'Item': {
                    'user_name': {
                        "S": items[i]['user_name_str']
                    },
                    'password': {
                        "S": password_str
                    },
                    'email_address': {
                        "S": items[i]['email_address_str']
                    },
                    'first_name': {
                        "S": items[i]['first_name_str']
                    }
                }
            }
        }
        user_formatted.append(user)
    for batch in batch25(user_formatted):
        params = {
            'RequestItems': {
                "users": batch
            }
        }
        dynamodb.batch_write_item(**params)

async def seed():
    print(f"started at {time.strftime('%X')}")
    await asyncio.gather(
        push_to_user_table(),
    )
    print(f"finished at {time.strftime('%X')}")

   

asyncio.run(seed())

