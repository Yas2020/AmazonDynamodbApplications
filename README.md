AmazonDynamodbApplications:

In the project, I build a simple CRUD application using Amazon API Gateway, Amazon Lambda and Amazon Dynamodb. 

It is basically a relational data structure with dragons of different types, having different skills and modifiers. However we want to use DynamoDB to store this data (4 JSON files), and leverage that to display card data on the website as part of an online game. We need a script that can upload multiple items to multiple tables using batch processing. We decide to create a table for each JSON file:

   - Dragon Stats Table: using dragon name as the Primary Key (PK) as you will want to search for a dragon by name.

    	  dragon_name   damage     description      protection     family     location_country    location_city   location_state    Location_neighborhood
 	    cassidiuma     9          Amazing            3           red            usa               las vegas        nevada         spring valley dragon


   - Dragon Bonus Attack Table: as we might want to search for details on a type of breath_attack, we choose that as our primary key for this table. Also we think it would be nice to see if an attack is "in range", so we add a sort key on range to find out if say "a water attack is in range to do damage".

	breath_attack(PK)      description     extra_damage     range (SK)
	       acid             spews acid           3               5


   - Dragon Family Table: later on in the game engine, we will likely need to be able to bring up information about modifiers relating to the dragon type (family). We decide to use family as the Primary Key (PK).

	breath_attack		 damage_modifier		description		family(PK) 	protection_modifier
	    acid			-2		       Better defense             green                  2


Load data: 
	
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

Before we deploy our first lambda fucntion, we create a user table and a session table so we allow only registered users to login or give special editing previlage to some users only, that is the admin in our case. Every time a user logs in, a token is generated and sent to the front end and also recorded in session table. This token expires in 20 mins. This is done by activating Time To Live feature for session table. So enable TTL for the session table:

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
   
   11 - Using Lambda console, create a new lambda function called DragonSearch and paste the content of `dragon_search.py`. At the root of our API, create 
   a post method with lambda function as its integration type and choose DragonSearch as its function. After checking for the validity of the session 
   (token is not expired), user can search dragons by name or see all of of the cards. Requesnt sent ot /login end point of our API, will be checked by 
   login lambda function in the backend for whether user is admin or no, which will be communicated to the front end. If the user is admin, then 
   editing/creating previlages will be granted by the front end; dragon cards will be edittable. 

   12 - From API console, create a new resource called "login" with a post method, and choose lambda as its integration type with the function 
   LoginEdXDragonGame created in step 10. Front end first shows the login form whose result will be sent to /login endpoint of our api, handled by a 
   lambda function and permission will be returned to the fornt end. Any search by user is directed to the root of the api handled by DragonSearch lambda 
   function.
  
   13 - Run
   
		create_mary_admin.py
   to add the admin to users table. This is the only user with editing previleges. Editting requires more involved communication between back-end and 
   front-end update. So we create a new end-point for editting in our api called "edit". Create a new lambda function called editDragon and paste the 
   content of `edit.py` to it. This function take requests directed to /edit end-point as input event, implements the changes in the back-end and returns 
   the new update. If the name of the dragon is changed, then that chnage should be done to the image file name of that dragon in S3. So this function 
   needs writing and reading permission to S3 bucket. Updating an item attributes requires transcational change so deleting and putting new items are tied 
   together; either both are done or none. This is called transaction. 
   
   14 - Create another endpoint called "create" that receives requests for creating new dragons. The post method is integrated into a lambda function 
   whose script is `create_dragon.py`.
  
 Now we should have a working website at url given by s3 bucket. The only point left is that we could have combined the three tables into one single 
 table. But before designing the single table, we need to think about the type of queries we might make. That's how dynamodb tables are desinged.  
  



