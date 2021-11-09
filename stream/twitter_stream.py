import json
import os

import boto3
import pandas as pd
import tweepy


class StreamListener(tweepy.Stream):
    
    def __init__(self, save_path='saved_tweets', **kwargs):
        super().__init__(**kwargs)
        self.save_path = save_path
        self.fileds = ['text', 'id', 'created_at', 'user', 'geo', 'lang']
    
    def send_data(self, data):
        pass

    def on_status(self, status):
        print(status.text)
        data = {
            'text': status.text,
            'id': status.id,
            'created_at': str(status.created_at),
            'geo': status.geo,
            'lang': status.lang,
            'user': status.user.screen_name
        }
        self.send_data(data)
        with open(f'{self.save_path}/{status.id}.json', 'w') as f:
            json.dump(data, f)

def get_credentials():
    ssm = boto3.client("ssm", region_name='us-east-1')
    return {
        'consumer_key': ssm.get_parameter(Name="consumer_key")["Parameter"]["Value"],
        'consumer_secret': ssm.get_parameter(Name="consumer_secret")["Parameter"]["Value"],
        'access_token': ssm.get_parameter(Name="access_token")["Parameter"]["Value"],
        'access_token_secret': ssm.get_parameter(Name="access_token_secret")["Parameter"]["Value"],
    }

def main():
    os.makedirs('saved_tweets', exist_ok=True)
    credentials = get_credentials()
    accounts = pd.read_csv('accounts.csv')
    stream = StreamListener(
        **credentials
    )
    stream.filter(
        follow=accounts.id.tolist(),
        filter_level='medium'
    )

if __name__ == '__main__':
    main()
