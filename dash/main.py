import os

import boto3
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
import pandas as pd
import plotly.express as px
from cloudpathlib import CloudPath
from dash.dependencies import Input, Output
from dash_extensions.enrich import Trigger

# place the credentials file in ~/.aws/

session = boto3.Session(profile_name="default")


def load_part():
    root_dir = CloudPath('s3://hadoop-data-tja/results/duplicated2.csv/')
    for f in root_dir.glob('*.csv'):
        filename = f.name.replace('/', '_')
        f.download_to(os.path.join('results', 'part.csv'))
    part = pd.read_csv(os.path.join('results', 'part.csv'))
    return part


dynamodb = boto3.resource('dynamodb',
                          aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
                          aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
                          region_name='us-east-1')

response = dynamodb.Table('mentions-count').scan()
response_bert = dynamodb.Table('bert-predictions').scan()
data = response['Items']
data_bert = response_bert['Items']

while 'LastEvaluatedKey' in response:
    response = dynamodb.Table('mentions-count').scan(ExclusiveStartKey=response['LastEvaluatedKey'])
    data.extend(response['Items'])

app = dash.Dash()
df = pd.DataFrame(data=response['Items'], columns=['NROWS', 'mention'])
df_bert = pd.DataFrame(data=data_bert, columns=['text', 'created', 'class', 'processed'])
counts = df.NROWS.unique()
counts.sort()
part = load_part()

app.layout = html.Div(children=[
    html.Div([
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
        dt.DataTable(
            id='table',
            columns=[{"name": i, "id": i} for i in df_bert.columns],
            data=df_bert.to_dict('records'),
        ),
        dcc.Interval(id="trigger", interval=3000)
    ]), html.Div([
        html.H1(children='Metadata visualizations'),
        dcc.Graph(id='proportions'),
        html.H3(children='Visualization per party'),
        dcc.Dropdown(
            id='party-dropdown',
            options=[
                {'label': 'Republican Party members', 'value': 'R'},
                {'label': 'Democratic Party members', 'value': 'D'}
            ],
            value='R'
        ),
        dcc.Graph(
            id="g1"
        ),
        dcc.Graph(
            id="g2"
        ),
        dcc.Graph(
            id="g3"
        )
    ])
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
    fig = px.bar(df[df["NROWS"] >= day], x='mention', y='NROWS',
                 labels={'NROWS': 'number of mentions', 'mention': 'username'})
    return fig


@app.callback(Output('table', 'data'), Input('table', 'active_cell'))
def update_graphs(active_cell):
    response_bert = dynamodb.Table('bert-predictions').scan()
    data_bert = response_bert['Items']
    df_bert = pd.DataFrame(data=data_bert, columns=['text', 'created', 'class', 'processed'])
    return df_bert.to_dict('records')


@app.callback(
    Output("g1", "figure"),
    [Input("party-dropdown", "value")])
def show_g1(party):
    fig = px.bar(part[part['party'] == party], x='user', y='retweet_count', labels={'retweet_count': 'retweet count'})
    return fig


@app.callback(
    Output("g2", "figure"),
    [Input("party-dropdown", "value")])
def show_g2(party):
    fig = px.bar(part[part['party'] == party], x='user', y='favourites_count',
                 labels={'favourites_count': 'favourites count'})
    return fig


@app.callback(
    Output("g3", "figure"),
    [Input("party-dropdown", "value")])
def show_g3(party):
    fig = px.bar(part[part['party'] == party], x='user', y='friends_count', labels={'friends_count': 'friends count'})
    return fig


@app.callback(
    Output("proportions", "figure"),
    [Input("party-dropdown", "value")]
)
def show_gp(input):
    party_counts = pd.DataFrame(part['party'].value_counts().reset_index(name='counts'))
    party_counts['index'] = ['Republican' if i == 'R' else 'Democrat' for i in party_counts['index']]
    fig = px.pie(party_counts, values='counts', names='index', labels={'counts': 'members', 'index': 'party'},
                 title='Proportion of Republicans and Democrats')
    return fig


if __name__ == '__main__':
    app.run_server()
