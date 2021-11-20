import json
import os
import requests
import boto3
import pandas as pd
import tweepy

ssm = boto3.client("ssm", region_name="us-east-1")


class StreamListener(tweepy.Stream):
    def __init__(self, nifi_instance_public_ip, save_path="saved_tweets", **kwargs):
        super().__init__(**kwargs)
        self.save_path = save_path
        self.fileds = ["text", "id", "created_at", "user", "geo", "lang"]
        self.nifi_instance_public_ip = nifi_instance_public_ip

    def send_data(self, data):
        r = requests.post(
            f"http://{self.nifi_instance_public_ip}:7001/twitterListener", json=data
        )
        print(r.status_code)

    def on_status(self, status):
        print(status.text)
        data = {
            "text": status.text,
            "id": status.id,
            "created_at": int(status.created_at.timestamp()),
            "geo": status.geo,
            "lang": status.lang,
            "user": status.user.screen_name,
        }
        self.send_data(data=data)  # look at TODO
        with open(f"{self.save_path}/{status.id}.json", "w") as f:
            json.dump(data, f)


def get_credentials():
    return {
        "consumer_key": ssm.get_parameter(Name="consumer_key")["Parameter"]["Value"],
        "consumer_secret": ssm.get_parameter(Name="consumer_secret")["Parameter"][
            "Value"
        ],
        "access_token": ssm.get_parameter(Name="access_token")["Parameter"]["Value"],
        "access_token_secret": ssm.get_parameter(Name="access_token_secret")[
            "Parameter"
        ]["Value"],
    }


def get_nifi_public_ip():
    return ssm.get_parameter(Name="NIFI_PUBLIC_IP")["Parameter"]["Value"]


def main():
    os.makedirs("saved_tweets", exist_ok=True)
    credentials = get_credentials()
    nifi_public_ip = get_nifi_public_ip()
    accounts = pd.read_csv("accounts.csv")
    stream = StreamListener(nifi_instance_public_ip=nifi_public_ip, **credentials)
    stream.filter(
        follow=accounts.id.tolist(),
    )


if __name__ == "__main__":
    main()
