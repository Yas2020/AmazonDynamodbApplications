import boto3

dynamodb = boto3.client('dynamodb') # must be client because resource doesnt have "update_time_to_live" method

def enable_ttl():
    params = {
			"TableName": "sessions",
			"TimeToLiveSpecification": {
				"AttributeName": "expiration_time",
				"Enabled": True
			}
		}
    dynamodb.update_time_to_live(**params) # client has this method

enable_ttl()

