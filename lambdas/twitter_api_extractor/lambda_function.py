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

    extractor = tweepy.API(
        tweepy.AppAuthHandler(consumer_key, consumer_secret), wait_on_rate_limit=True
    )

    user = event["user"]
    party = event.get("party")
    limit = int(event.get("limit", 100))
    statuses = []

    try:
        for status in tweepy.Cursor(extractor.user_timeline, user, count=limit).items(
            limit
        ):
            statuses.append(
                {
                    "created_at": status._json["created_at"],
                    "text": status._json["text"],
                    "retweet_count": status._json["retweet_count"],
                    "favorite_count": status._json["favorite_count"],
                    "favorited": status._json["favorited"],
                    "retweeted": status._json["retweeted"],
                    "lang": status._json["lang"],
                    "geo": status._json["geo"],
                    "coordinates": status._json["coordinates"],
                    "place": status._json["place"],
                }
            )
    except tweepy.TweepError:
        return {
            "statusCode": 400,
            "body": json.dumps(
                {"error": f"No such user as {user} or it has account protected."}
            ),
        }

    extraction_time = int(datetime.utcnow().timestamp())

    body = {"user": user, "extractionTime": extraction_time, "data": statuses, "party": party}

    data = {
        "body": json.dumps(body, cls=Encoder),
        "statusCode": 200,
        "extractionTimestamp": extraction_time,
    }

    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("Tweets")

    table.put_item(Item=body)

    return data
