# TODO
# add CSS style on github to refer as external stylesheet

import urllib.request
import urllib
import json
import pandas as pd
import os
from tqdm import tqdm
import plotly.graph_objects as go

# Manipulate data
import pandas as pd
import sqlite3

# Interactivity
from jupyter_dash import JupyterDash
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# utilities
from datetime import datetime
import configparser as cp

# get the data
assets = ['BTC', 'ETH']
timeframes = ['day', 'hour']

# Get api key
API_key = '8zv2c5w97qfc3sixzmiylq'


# Assets timeseries
bad_request_count = 0
df_list_hour = {}
df_list_day = {}
for asset in assets:
    asset = asset.replace(" ", "")
    url_hour = 'https://api.lunarcrush.com/v2?data=assets&key=' + str(API_key) + '&symbol=' + asset + '&data_points=2000&interval=hour'
    url_day = 'https://api.lunarcrush.com/v2?data=assets&key=' + str(API_key) + '&symbol=' + asset + '&data_points=2000&interval=day'
    while True: # to correct <HTTPError: HTTP Error 504: Gateway Timeout> --- source: https://stackoverflow.com/questions/15786421/http-error-504-gateway-time-out-when-trying-to-read-a-reddit-comments-post 
        try:
            response_hour = urllib.request.urlopen(url_hour)
            response_day = urllib.request.urlopen(url_day)
            if response_hour.getcode() == 200 and  response_day.getcode(): # 200 response (standard response for successful HTTP requests)
                my_bytes_value = response_hour.read()
                my_json = json.loads(my_bytes_value.decode('utf8'))
                df_hour = pd.DataFrame(my_json['data'][0]['timeSeries'])
                
                my_bytes_value = response_day.read()
                my_json = json.loads(my_bytes_value.decode('utf8'))
                df_day = pd.DataFrame(my_json['data'][0]['timeSeries'])
                
                df_list_hour[asset] = df_hour
                df_list_day[asset] = df_day
                break
            
        except Exception as e:
            print('bad request: ', e)


            

            
app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1("Cryptocurrencies Social Data Vizualization"),
    html.Label([
        "Symbol",
        dcc.Dropdown(
            id='symbol-dropdown', clearable=False,
            value='BTC', options=[
                {'label': c, 'value': c}
                for c in assets
            ],
            style={'marginBottom': '1.5em'}
        )
    ]),
    html.Label([
        "Timeframe",
        dcc.Dropdown(
            id='timeframe-dropdown', clearable=False,
            value='day', options=[
                {'label': c, 'value': c}
                for c in timeframes
            ])
    ]),
    html.Br(), 
    dcc.Loading(
            id="loading-1",
            type="graph",
            children=dcc.Graph(id='reddit_graph')
    ),
    dcc.Loading(
            id="loading-2",
            type="graph",
            children=dcc.Graph(id='twitter_graph')
    )
    
])

# Define callback to update graph
@app.callback(
    Output('reddit_graph', 'figure'),
    Output('twitter_graph', 'figure'),
    Input("symbol-dropdown", "value"),
    Input("timeframe-dropdown", "value")
)
def update_figure(symbol, timeframe):
    
    title = 'Reddit Social Information' # title of the chart
    
    columns1 = ['reddit_posts', 'reddit_comments'] # columns in df
    columns1_labels = ['Reddit Posts', 'Reddit Comments'] # columns labels in chart
    
    columns2 = ['tweets', 'tweet_retweets', 'tweet_favorites',] # columns in df
    columns2_labels = ['Tweets', 'Retweets', 'Favorites'] # columns labels in chart


    colors = ['rgb(204,0,0)', 'rgb(255,102,102)','rgb(64,64,64)', 'rgb(160,160,160)'] # color of lines in chart
    mode_size = [8, 8, 8, 8] # size of points
    line_size = [2, 2, 2, 2] # size of line

    if timeframe == 'day':
        df = df_list_day[symbol]
    else:
        df = df_list_hour[symbol]
    
    x_data = pd.to_datetime(df['time'], unit='s')
    y_data = df[columns1]

    fig_reddit = go.Figure()

    for i in range(0, len(columns1)):
        fig_reddit.add_trace(go.Scatter(x=x_data, y=y_data[columns1[i]], mode='lines',
            name=columns1_labels[i],
            line=dict(color=colors[i], width=line_size[i]),
            connectgaps=True,
        ))

    fig_reddit.update_layout(
        title=symbol + ' Reddit Social Volume',
        yaxis_title="# of post or comments",
        xaxis=dict(
            showline=True,
            #showgrid=False,
            showticklabels=True,
            linecolor='rgb(204, 204, 204)',
            linewidth=2,
            ticks='outside',
            tickfont=dict(
                family='Arial',
                size=12,
                color='rgb(82, 82, 82)',
            ),
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=True,
            showline=True,
            linecolor='rgb(204, 204, 204)',
            linewidth=2,
            showticklabels=True,
            ticks='outside',
            tickfont=dict(
                family='Arial',
                size=12,
                color='rgb(82, 82, 82)',
            ),
        ),
        autosize=False,
        margin=dict(
            autoexpand=True,
            l=20,
            r=20,
            t=100,
        ),
        showlegend=True,
        plot_bgcolor='white'
    )
    
    x_data = pd.to_datetime(df['time'], unit='s')
    y_data = df[columns2]    
    
    fig_tweet = go.Figure()

    for i in range(0, len(columns2)):
        fig_tweet.add_trace(go.Scatter(x=x_data, y=y_data[columns2[i]], mode='lines',
            name=columns2_labels[i],
            line=dict(color=colors[i], width=line_size[i]),
            connectgaps=True,
        ))

    fig_tweet.update_layout(
        title=symbol + ' Twitter Social Volume',
        yaxis_title="# of post or comments",
        xaxis=dict(
            showline=True,
            #showgrid=False,
            showticklabels=True,
            linecolor='rgb(204, 204, 204)',
            linewidth=2,
            ticks='outside',
            tickfont=dict(
                family='Arial',
                size=12,
                color='rgb(82, 82, 82)',
            ),
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=True,
            showline=True,
            linecolor='rgb(204, 204, 204)',
            linewidth=2,
            showticklabels=True,
            ticks='outside',
            tickfont=dict(
                family='Arial',
                size=12,
                color='rgb(82, 82, 82)',
            ),
        ),
        autosize=False,
        margin=dict(
            autoexpand=True,
            l=20,
            r=20,
            t=100,
        ),
        showlegend=True,
        plot_bgcolor='white'
    )
    
    return fig_reddit, fig_tweet

app.run_server(dev_tools_ui=True, debug=True,
              dev_tools_hot_reload =True, threaded=True)