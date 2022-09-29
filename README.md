AmazonDynamodbApplications:

In this project, I build a simple CRUD application using Amazon API Gateway, Amazon Lambda and Amazon Dynamodb. This project is part of a course exercise 
I did on Coursera [here](https://www.coursera.org/learn/dynamodb-nosql-database-driven-apps/home/week/1), which was presented in JavaScript. I wrote 
lambda functions in python and extended the front-end (JavaScript and Jquery) for more functionality (creation of dragon etc). 

The data is organized with a relational data structure of items called dragons of different types, having different features and modifiers. However we 
want to use DynamoDB to store this data (4 JSON files), and thent to display data on cards on the website as part of an online game. Here is the structure 
of provided tables in json files:

   - Dragon Stats Table: using dragon name as the Primary Key (PK) as you will want to search for a dragon by name.

    	  dragon_name   damage     description      protection     family     location_country    location_city   location_state    Location_neighborhood
 	    cassidiuma     9          Amazing            3           red            usa               las vegas        nevada         spring valley dragon


   - Dragon Bonus Attack Table: as we might want to search for details on a type of breath_attack, we choose that as our primary key for this table. Also we think it would be nice to see if an attack is "in range", so we add a sort key on range to find out if say "a water attack is in range to do damage".

	breath_attack(PK)      description     extra_damage     range (SK)
	       acid             spews acid           3               5


   - Dragon Family Table: later on in the game engine, we will likely need to be able to bring up information about modifiers relating to the dragon type (family). We decide to use family as the Primary Key (PK).

	breath_attack		 damage_modifier		description		family(PK) 	protection_modifier
	    acid			-2		       Better defense             green                  2

We first try to load data in dynamodb. So we need a script that can upload multiple items to multiple tables using batch processing. Before getting 
started, let's prepare the environment and the tools needed. We then move forward step by step from there: 
	
   1 - Create a python environment :
   
			pyhton -m venv /path/to/venv 
Then activate it: 

			source path/to/venv/bin/activate
	
   2 - Install aws sdk for python:
    
			pip install boto3
			
   3 - SAM CLI: 
   
			pip install sam
			
   4 - Configure the environment with AWS Access Key ID, AWS Secret Access Key and Default region name 
   
   5 - Host the static website on S3: 
   
			aws s3 cp /path/to/website s3://$MYBUCKET/website  --recursive
   6 - Run 
   	
			create_multiple_tables.py 
to create tables concurrently, and then 

			seed_dragons.py 
to batch-write itmes into tables using the provided json files.

Before we deploy our first lambda fucntion, we create a user table and a session table so we allow only registered users to login or give special editing 
previlage to some users only, that is the admin in our case. Every time a user logs in, a token is generated and sent to the front end and also recorded 
in session table. This token expires in 20 mins. This is done by activating Time To Live feature for session table. So enable TTL for the session table:

   7 - Run
   
	    create_user_table_and_index.py
	    create_sessions_table.py
	    enable_ttl.py
	    
Users table has GSI with its index as user_email_address. We search users by their emails in users table. 

   8 - Populate the user table containing the passwords provide in user.json file. Passwords are hashed using python module bcrypt. 
   	
	    upload_and_hash_passwords.py
	    
   9 - Lambda function that is responsible for login functionality is "login.py". It take user_email_address and password as input, gets confirmation from 
   users. table in dynamodb, also checks if the user is admin or not. If paased, it returns user_name and a token to the frontend and lets the user in. We 
   can test our lambda function before moving forward: 
   
   	    python3 login.py test dave@dragoncardgame001.com coffee
	
   10 - Lets package our lambda function "login.py" and deploy it to Amazon Lambda. The neccessary dependency is bcrypt used for hashing. So our function needs to be packaged in a folder called package and then zipped to file name "login.zip" before uploading.
   
   		pip install -t package bcrypt
		cd package
		zip -r ../login.zip .
		cd ..
		zip -g login.zip login.py
		
Note that packaging process is better to be done using a Linux machine that creates the same binary as the ones which run Amazon Lambda (Linux 2). I used 
Cloud9 (create a new python env and so on) for packaging at this stage as I could not successfully do it on my macbook air. One can now use aws sdk to 
deploy our lambda function to Lambda service. 

		python3 create_and_publish_login.py
or SAM CLI:

	 	aws lambda create-function --function-name LoginEdXDragonGame \
					   --runtime python3.9  \
					   --role $ROLE_ARN_READ \
					   --handler login.lambda_handler \
					   --publish \
					   --zip-file fileb://path/to/login.zip
A lambda function can aslo be invoked using sam cli. But it is easier to test the function on Lambda console for me.

   11 - Using API Gateway console, create an api called DragonSearchAPI. Using Lambda console, create a new lambda function called DragonSearch, attach an 
   appropriate role to it and paste the content of `dragon_search.py`. At the root of API, create 
   a post method with lambda function as its integration type and choose DragonSearch as its function (keep Use Lambda Proxy integration unchecked for all 
   methods we create here later on - also timout is to be 10000 (10 sec)). Remember that, every time you make chenges to API, make sure to deploy the api 
   again. Also CORS should be enabled everytime because your website is hosted on one 
   domain and your API on another. Your browser might block this of CORS is not enabled. After deploying, insert the url address into `config.js` to 
   connect website to API.
   
   After checking for the validity of the session 
   (token is not expired) done by DragonSearch, user can search dragons by name or see all of of the cards. This is to prevent unauthorized users to have 
   access to data by calling api directly bypassing the website login protect, that comes in the next step.  
   
   12 - Before we let users login, we need to check for credentials. From API console, create a new resource called "login" with a post method, and choose 
   lambda as its integration type with the function 
   LoginEdXDragonGame created in step 10. Front end first shows users the login form (login page) whose result will be sent to /login endpoint of our api, 
   handled by a lambda function and permission will be returned to the fornt end. Any search by user is directed to the root of the api handled by 
   DragonSearch lambda function. Request sent to /login end point of our API will be checked by 
   login lambda function LoginEdXDragonGame in the backend to see whether user is admin or no, and the result will be communicated to the front end. If 
   the user is admin, then editing/creating previlages will be granted by the front end; dragon cards will be edittable. 

  
   13 - Run
   
		create_mary_admin.py
   to add the admin to users table. This is the only user with editing previleges. Editting requires more involved communication between back-end and 
   front-end update. So we create a new end-point for editting in our api called "edit". Create a new lambda function called editDragon and paste the 
   content of `edit.py` to it. This function take requests directed to /edit end-point as input event, implements the changes in the back-end and returns 
   the new update. If the name of the dragon is changed, then that chnage should be done to the image file name of that dragon in S3. So this function 
   needs writing and reading permission to S3 bucket. Updating an item attributes requires transcational change so deleting and putting new items are tied 
   together; either both are done or none. This is called transaction. 
   
   14 - Create another endpoint called "create" that receives requests for creating new dragons. The post method is integrated into a lambda function 
   whose script is `create_dragon.py`. Front-end takes attributes of the new dragon including its image and send data to this end point. The request is 
   handled by this lambda function. dragon attributes are recoded in dragon_stats table and its image is stored in s3 bucket. Front-end displays the new 
   drgon without refreshing the page (happens in front-end). 
  
Now we should have a working website at url given by s3 bucket that does creation, retreiveing and updating data. 

The table design we had so in dynamodb is only good for very basic queries. For more advanced queries (not used for this app here), we need to use more GSIs (Global Secondary Index). To achieve this with more efficient design, we could have combined the three tables above into one single table with carefully defind 
GSI. To do this, we need to think about the types of queries we might make. That's how dynamodb tables are desinged. For example, to find dragons that 
spew acid or find all drangons of family green, find all dragons living in Arizona, USA or all with range < 5 in increasing order ... . To combine these 
three tables, we can make a new table (improved single table) with PK as a hashing id, and SK to be 'stats', 'bonus', 'family', repeating for each record 
with the same partition key (denormalization, which is agaist relational databse design). Create a GSI for attribute associated with "spew acid": in this case "bonus 
description". Another GSI should be for 'stats' that contains info about dragons (name, fmaily, damage, descritipin and location ...). So the query: "find 
dragons that spew acid" can be done in two stages: 1- return all PK for dragons spew acids, 2- return dragon stats for all dragon with these PKs. 

 
         PK (PK)         SK           Location                     <attributes>
      <SAME- UUID>     stats  <Location_country_value>:        dragon_name: <value>,
                                 <Location_state_value>          protection: <value>,
				 <Location_city_value>:          damage: <value>
				 <Location_neighborhood_value>   description: <value> 
                                                                  family: <value>
	
	<SAME- UUID>    bonus                                    extra_damage: <value> , range: <value> , UUID> bonus_description: <value>
	
	  
       <SAME- UUID>    family                                  breath_attack: <value>,damage_modifier: <value> ,
                                                                 protection_modifier: <value> , family_description:<value>

To create and seed the single table, run python scripts in folder single_table_desings_and_queries. Some query scripts (queries mentioned above) can also 
be find there.

A few words about security and monitoring: Lamda functions need permissions to have access to dynamodb tables (or any other service). One should create an AIM role with minimal previlege (least privilege principle) required for each lambda function. One can activate X-Ray in API Gateway, CloudWatch for dynamodb are useful tools for monitoring of services and logs. Once should create fine-grained Access Control IAM policy conditions for Amazon DynamoDB and move lambda fucntions inside a VPC and also creare VPC gateway endpoint for dynamodb so that lambda and dynamodb dotnthave to communicate over public internet but instead inside a VPC. 



