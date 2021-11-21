import base64
import json
##python lib for aws
import boto3
import datetime
import base64
import json
##python lib for aws
import boto3
import datetime

import time

ssm = boto3.client("ssm", region_name="us-east-1")

#dynamodb = boto3.client('dynamodb', region_name="us-east-1")

def get_nifi_public_ip():
    return ssm.get_parameter(Name="NIFI_PUBLIC_IP")["Parameter"]["Value"]

def lambda_handler(event, context):
	#nifi_public_ip = get_nifi_public_ip()
    try: 
        for record in event["Records"]:
            decoded_data = base64.b64decode(record["kinesis"]["data"]).decode("utf-8")

            encoded_string = decoded_data.encode("utf-8")
            
            #r = requests.post(f"http://{self.nifi_public_ip}:7001/twitterListener", json=data)
	        r = dynamodb.put_item(TableName='RedditPosts', Item=data)

	        print(r)

       
    except Exception as e: 
        print(str(e))
