import boto3

LAMBDA_ROLE_ARN_STR = "Enter Role You Defined for this Lambda Function"

client = boto3.client('lambda')

with open('login.zip', 'rb') as f: 
        code = f.read()
response = client.create_function(
    FunctionName='LoginEdXDragonGame',
    Runtime='python3.9',
    Role=LAMBDA_ROLE_ARN_STR,
    Handler='login.lambda_handler',
    Code={
        'ZipFile': code  # should be binary
    },
    MemorySize=128, 
    Publish=True,
    Timeout=30
)
print(response)