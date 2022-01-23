import os

import boto3
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import numpy as np
import plotly.graph_objects as go
import pandas as pd
import plotly.express as px
from dash_extensions.enrich import Trigger

# place the credentials file in ~/.aws/

session = boto3.Session(profile_name="default")

dynamodb = boto3.resource('dynamodb',
                          region_name='us-east-1')

response = dynamodb.Table('mentions-count').scan()

data = response['Items']

while 'LastEvaluatedKey' in response:
    response = dynamodb.Table('mentions-count').scan(ExclusiveStartKey=response['LastEvaluatedKey'])
    data.extend(response['Items'])

app = dash.Dash()
df = pd.DataFrame(data=response['Items'], columns=['NROWS', 'mention'])
counts = df.NROWS.unique()
counts.sort()
print(counts)

app.layout = html.Div([
    html.H1(children='Counts for each user mentioned'),
    html.H3(children='Choose counts bigger than a set value'),
    dcc.Slider(
        id='my-slider',
        min=min(counts),
        max=max(counts),
        marks={
            0: '0',
            5: '5',
            10: '10',
            50: '50'
        },
        step=1,
        value=1,
    ),
    dcc.Graph(id="graph"),
    dcc.Interval(id="trigger", interval=3000)
])


@app.callback(
    Output("graph", "figure"),
    [Input("my-slider", "value"),
     Trigger("trigger", "n_intervals")])
def display_color(day, refresh_interval):
    response = dynamodb.Table('mentions-count').scan()
    df = pd.DataFrame(data=response['Items'], columns=['NROWS', 'mention'])
    fig = px.bar(df[df["NROWS"] >= day], x='mention', y='NROWS',
                 labels={'NROWS': 'number of mentions', 'mention': 'username'})
    return fig


if __name__ == '__main__':
    app.run_server()
