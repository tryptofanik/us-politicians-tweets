import os
import time 
import datetime

import boto3
from boto3.dynamodb.conditions import Key, Attr
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import dash_table
import numpy as np
import plotly.graph_objects as go
import pandas as pd
import plotly.express as px


dynamodb = boto3.resource('dynamodb',
                          aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
                          aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
                          region_name='us-east-1'
)

app = dash.Dash()


tweets = dynamodb.Table('Tweets').scan(Limit=10000)['Items']
tweets = pd.DataFrame(tweets)
tweets['ts'] = tweets.extractionTime.astype(int)
tweets['date'] = pd.to_datetime(tweets['ts'], unit='s')
tweets = tweets.loc[tweets.date > '2022-01-20']
marks = {
    k: k #str(pd.to_datetime(k, unit='s'))
    for k in np.linspace(tweets.ts.min(), tweets.ts.max(), 4).astype(int)
}

agged_tweets = (
    tweets.assign(count=1).groupby('user').count()
    ['count'].reset_index()
    .sort_values('count', ascending=False)
)

app.layout = html.Div([
    html.H1(children='Historical tweets'),
    html.H3(children='Choose a range of tweets'),
    dcc.RangeSlider(
        id='my-slider',
        step=1,
        min=tweets.ts.min(),
        max=tweets.ts.max(),
        value=[1642240708, 1642785451],
        # marks=marks,
    ),
    dcc.Graph(id="graph"),
    dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in agged_tweets.columns],
        data=agged_tweets.to_dict('records')
    )    
])


@app.callback(
    Output("graph", "figure"),
    [Input("my-slider", "value")])
def display_tweets(value):
    min_date, max_date = value
    print(tweets)
    data = tweets.loc[(tweets.ts > min_date) & (tweets.ts < max_date)]
    data_ = data.resample('1H', on='date').count()['date']
    fig = px.bar(data_)
    return fig


@app.callback(
    Output("table", "data"),
    [Input('my-slider', 'value')]
)
def update_table(value):
    min_date, max_date = value
    data = tweets.loc[(tweets.ts > min_date) & (tweets.ts < max_date)]
    agged_tweets_ = (
        data.assign(count=1).groupby('user').count()
        ['count'].reset_index()
        .sort_values('count', ascending=False)
    )
    return agged_tweets_.to_dict('records')


if __name__ == '__main__':
    app.run_server(debug=True, )
