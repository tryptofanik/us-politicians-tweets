import json
import os

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
        data = {field: str(getattr(status, field)) for field in self.fileds}
        self.send_data(data)
        with open(f'{self.save_path}/{status.id}.json', 'w') as f:
            json.dump(data, f)


def main():
    os.mkdir('saved_tweets')
    accounts = pd.read_csv('../accounts.csv')
    stream = StreamListener(
        consumer_key=os.environ['API_KEY'],
        consumer_secret=os.environ['API_SECRET_KEY'],
        access_token=os.environ['ACCESS_TOKEN'],
        access_token_secret=os.environ['ACCESS_SECRET_TOKEN'],
    )
    stream.filter(
        follow=accounts.id.tolist(),
    )

if __name__ == '__main__':
    main()
