#!/usr/bin/python
import praw
import re
import datetime
import sys
import boto3
import json
import time
import logging
import pandas as pd
import random
import decimal
import requests


LOG_FILENAME = '/tmp/reddit-stream.log'
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)

def remove_emoji(comment):
    emoji_pattern = re.compile("["
       u"\U0001F600-\U0001F64F"  # emoticons
       u"\U0001F300-\U0001F5FF"  # symbols & pictographs
       u"\U0001F680-\U0001F6FF"  # transport & map symbols
       u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
       u"\U00002702-\U00002f7B0"
       u"\U000024C2-\U0001F251"
       "]+", flags=re.UNICODE)

    cleaned_comment =  emoji_pattern.sub(r'', comment)

    return cleaned_comment


class StreamListener(praw.Reddit):

    def __init__(self, subreddits='republicans+democrats', **kwargs):
        super().__init__(**kwargs)
        self.num_posts_collected = 0
        self.posts_stream = self.subreddit(subreddits)

    def send_data(self, data, nifi_instance_public_ip):
        r = requests.post(f"http://{nifi_instance_public_ip}:7002/redditListener",
                          json=data)
        print(r.status_code)

    def run_stream(self, nifi_instance_public_ip):
        kinesis_client = boto3.client('kinesis', region_name='us-east-1')
        try:
            for submission in self.posts_stream.stream.submissions():
                txt = submission.selftext if len(submission.selftext) > 0 else submission.url

                cleaned_post = remove_emoji(str(txt))
                post_date = str(datetime.datetime.utcfromtimestamp(submission.created_utc).strftime('%Y/%m/%d %H:%M:%S'))

                commentjson = {'created' : post_date,
                               'post_id': submission.id,
                               'submission_id': submission.title,
                               'subreddit': str(submission.subreddit),
                               'post_body': cleaned_post
                               }

                self.num_posts_collected = self.num_posts_collected + 1
                self.send_data(data=commentjson, nifi_instance_public_ip=nifi_instance_public_ip)

                time.sleep(0.1)
        except Exception as e:
            print(e)

def get_credentials():
    ssm = boto3.client("ssm", region_name='us-east-1')
    return {
        'client_id': ssm.get_parameter(Name="REDDIT_CLIENT_ID")["Parameter"]["Value"],
        'client_secret': ssm.get_parameter(Name="REDDIT_SECRET")["Parameter"]["Value"],
        'username': ssm.get_parameter(Name="REDDIT_USER")["Parameter"]["Value"],
        'password': ssm.get_parameter(Name="REDDIT_PASS")["Parameter"]["Value"],
        'user_agent': ssm.get_parameter(Name="REDDIT_USER_AGENT")["Parameter"]["Value"],
    }

def get_nifi_public_ip():
    ssm = boto3.client("ssm", region_name='us-east-1')
    return ssm.get_parameter(Name="NIFI_PUBLIC_IP")["Parameter"]["Value"]

def get_kinesis():
    ssm = boto3.client("ssm", region_name='us-east-1')
    return ssm.get_parameter(Name="NIFI_PUBLIC_IP")["Parameter"]["Value"]

def main():
    credentials = get_credentials()
    nifi_public_ip = get_nifi_public_ip()
    stream = StreamListener(
      **credentials
    )
    stream.run_stream(
        nifi_public_ip,
    )

if __name__ == '__main__':
    main()