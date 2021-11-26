import tweepy
import json
import boto3
from datetime import datetime
import decimal


class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)


def lambda_handler(event, context):

    if "user" not in event:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "User parameter was not provided."}),
        }

    ssm = boto3.client("ssm")
    consumer_key = ssm.get_parameter(Name="consumer_key")["Parameter"]["Value"]
    consumer_secret = ssm.get_parameter(Name="consumer_secret")["Parameter"]["Value"]

    api = tweepy.API(
        tweepy.AppAuthHandler(consumer_key, consumer_secret), wait_on_rate_limit=True
    )

    user = event["user"]
    statuses = []

    try:
        followers = api.get_follower_ids(screen_name='SenShelby')
        friends = api.get_friend_ids(screen_name='SenShelby')
        account_data = api.get_user(screen_name='SenShelby')
        data = {
            'followers': followers,
            'friends': friends,
            'account_data': account_data
        }
    except tweepy.TweepError:
        return {
            "statusCode": 400,
            "body": json.dumps(
                {"error": f"No such user as {user} or it has account protected."}
            ),
        }

    extraction_time = int(datetime.utcnow().timestamp())

    body = {"user": user, "extractionTime": extraction_time, "data": data}

    data = {
        "body": json.dumps(body, cls=Encoder),
        "statusCode": 200,
        "extractionTimestamp": extraction_time,
    }

    return data












