import base64
import json

import boto3
from boto3.dynamodb.types import TypeSerializer
ssm = boto3.client("ssm", region_name="us-east-1")

dynamodb = boto3.client('dynamodb', region_name="us-east-1")
serializer = TypeSerializer()


def get_nifi_public_ip():
    return ssm.get_parameter(Name="NIFI_PUBLIC_IP")["Parameter"]["Value"]


def lambda_handler(event, context):
    print(event)
    for record in event["Records"]:
        decoded_data = base64.b64decode(record["kinesis"]["data"]).decode("utf-8")

        print(decoded_data)
        data = json.loads(decoded_data)
        data = {key: serializer.serialize(value) for key, value in data.items()}
        dynamodb.put_item(TableName='RedditPosts', Item=data)
