##python lib for aws
import base64
import json

##python lib for aws
import boto3

ssm = boto3.client("ssm", region_name="us-east-1")

dynamodb = boto3.client('dynamodb', region_name="us-east-1")


def get_nifi_public_ip():
    return ssm.get_parameter(Name="NIFI_PUBLIC_IP")["Parameter"]["Value"]


def lambda_handler(event, context):
    print(event)
    try:
        for record in event["Records"]:
            decoded_data = base64.b64decode(record["kinesis"]["data"]).decode("utf-8")

            print(decoded_data)
            data = json.loads(decoded_data)
            dynamo_types = {
                str(int): 'N',
                str(float): 'N',
                str(str): 'S',
                str(bool): 'BOOL',
                str(dict): 'M',
            }
            for k in data:
                data[k] = {dynamo_types[str(type(data[k]))]: str(data[k])}
            dynamodb.put_item(TableName='RedditPosts', Item=data)
    except Exception as e:
        print(str(e))
