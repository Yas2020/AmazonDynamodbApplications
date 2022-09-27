AmazonDynamodbApplications:

In the project, I build a simple CRUD application using Amazon API Gateway, Amazon Lambda and Amazon Dynamodb. 

It is basically a relational data structure with dragons of different types, having different skills and modifiers. However we want to use DynamoDB to store this data (4 JSON files), and leverage that to display card data on the website as part of an online game. We need a script that can upload multiple items to multiple tables using batch processing. We decide to create a table for each JSON file:

1- Dragon Stats Table: using dragon name as the Primary Key (PK) as you will want to search for a dragon by name.

	 dragon_name   damage      description      protection     family      location_country    location_city   location_state    Location_neighborhood
 	  cassidiuma    9            Amazing          3             red            usa               las vegas        nevada          spring valley dragon


2- Dragon Bonus Attack Table: as we might want to search for details on a type of breath_attack, we choose that as our primary key for this table. Also we think it would be nice to see if an attack is "in range", so we add a sort key on range to find out if say "a water attack is in range to do damage".

	breath_attack(PK)       description     extra_damage     range (SK)
	       acid             spews acid            3               5


3- Dragon Family Table: later on in the game engine, we will likely need to be able to bring up information about modifiers relating to the dragon type (family). We decide to use family as the Primary Key (PK).

	breath_attack		 damage_modifier		description		family(PK) 	protection_modifier
	    acid			-2		       Better defense               green               2


Load data: 
1 - Create a python environment : 
			pyhton -m venv /path/to/venv 
Then activate it: 
			source path/to/venv/bin/activate
2 - install aws sdk for python: 
			pip install boto3
3 - SAM CLI: 
			pip install sam
4 - Configure the environment with AWS Access Key ID, AWS Secret Access Key and Default region name 
5 - Host the static website on S3:  
			aws s3 cp /path/to/website s3://$MYBUCKET/website  --recursive
