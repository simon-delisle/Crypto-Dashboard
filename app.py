# TODO
# add CSS style on github to refer as external stylesheet

import urllib.request
import json
import pandas as pd
import os
import plotly.graph_objects as go

# Interactivity
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash_bootstrap_components as dbc

# utilities
from datetime import datetime

# get the data
assets = ['BTC', 'ETH', 'HEX', 'ADA', 'USDT', 'BNB', 'XRP', 'DOGE', 'USDC']
timeframes = ['day', 'hour']

# Get api key
API_key = '8zv2c5w97qfc3sixzmiylq'

# Assets timeseries
bad_request_count = 0
df_list_hour = {}
df_list_day = {}

for asset in assets:
    asset = asset.replace(" ", "")
    url_hour = 'https://api.lunarcrush.com/v2?data=assets&key=' + str(
        API_key) + '&symbol=' + asset + '&data_points=2000&interval=hour'
    url_day = 'https://api.lunarcrush.com/v2?data=assets&key=' + str(
        API_key) + '&symbol=' + asset + '&data_points=2000&interval=day'
    while True:  # to correct <HTTPError: HTTP Error 504: Gateway Timeout> --- source: https://stackoverflow.com/questions/15786421/http-error-504-gateway-time-out-when-trying-to-read-a-reddit-comments-post
        try:
            response_hour = urllib.request.urlopen(url_hour)
            response_day = urllib.request.urlopen(url_day)
            if response_hour.getcode() == 200 and response_day.getcode():  # 200 response (standard response for successful HTTP requests)
                my_bytes_value = response_hour.read()
                my_json = json.loads(my_bytes_value.decode('utf8'))
                df_hour = pd.DataFrame(my_json['data'][0]['timeSeries'])

                my_bytes_value = response_day.read()
                my_json = json.loads(my_bytes_value.decode('utf8'))
                df_day = pd.DataFrame(my_json['data'][0]['timeSeries'])

                df_list_hour[asset] = df_hour
                df_list_day[asset] = df_day
                #print(df_day.columns)
                break

        except Exception as e:
            print('bad request: ', e)

fonts = ['Arial']
colors = ['Crimson', 'White', '#585858']

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
server = app.server
# Define bootstrap components
## Input form
symbol_dropdown = dbc.FormGroup([
    dbc.Label('Cryptocurrency Symbol', html_for='symbol-dropdown'),
    dcc.Dropdown(
        id='symbol-dropdown', clearable=False,
        value='BTC', options=[
            {'label': c, 'value': c}
            for c in assets
        ],
    )
])

timeframe_dropdown = dbc.FormGroup([
    dbc.Label('Timeframe', html_for='timeframe-dropdown'),
    dcc.Dropdown(
        id='timeframe-dropdown', clearable=False,
        value='day', options=[
            {'label': c, 'value': c}
            for c in timeframes
        ]
    )
])

input_form = dbc.Form([symbol_dropdown, timeframe_dropdown])

# App layout
app.layout = dbc.Container([
    html.H1(" Cryptocurrencies Social Data Vizualization"),
    html.H5("A Dashboard showing the level of activity related to popular cryptocurrencies in social medias."),
    html.Br(),
    html.P(
        "To use this dashboard, first select a cryptocurrency and a timeframe. The figures below will update based on your choice. If you select a time interval on the price chart below, the KPI cards as well the 2 other charts will be updated to represent the time interval you have chosen."),
    input_form,
    # dbc.Row([
    #    dbc.Col(
    #        [dbc.Card(card_content, color="secondary", outline=True), dbc.Card(card_content, color="secondary", outline=True), dbc.Card(card_content, color="secondary", outline=True)], width=3, align="center"
    #    ),
    #    dbc.Col(
    #        [dbc.Card(card_content, color="secondary", outline=True), dbc.Card(card_content, color="secondary", outline=True), dbc.Card(card_content, color="secondary", outline=True)], width=3, align="center"
    #    ),
    #    dbc.Col(
    #        [dcc.Graph(id='price_graph'), dcc.Graph(id='reddit_graph'), dcc.Graph(id='twitter_graph')], width=6
    #    ),
    # ], justify="center")
    html.H3("Price Information"),
    # html.Pre(id='relayoutData'),
    # html.Pre(id='relayoutData2'),
    # html.Pre(id='relayoutData3'),
    dbc.Row([
        dbc.Col([dbc.Card(id='card1')], width=3, align="center"),
        dbc.Col([dbc.Card(id='card2')], width=3, align="center"),
        dbc.Col([dcc.Graph(id='price_graph')], width=6, align="center")
    ]),
    html.H3("Reddit Trends"),
    dbc.Row([
        dbc.Col([dbc.Card(id='card3')], width=3, align="center"),
        dbc.Col([dbc.Card(id='card4')], width=3, align="center"),
        dbc.Col([dcc.Graph(id='reddit_graph')], width=6, align="center")
    ]),
    html.H3("Twitter Trends"),
    dbc.Row([
        dbc.Col([dbc.Card(id='card5')], width=3, align="center"),
        dbc.Col([dbc.Card(id='card6')], width=3, align="center"),
        dbc.Col([dcc.Graph(id='twitter_graph')], width=6, align="center")
    ]),
    html.P(id='relayoutData'),
    html.P(id='relayoutData2'),
    html.P(id='relayoutData3')

])


# define the callback for relayout
@app.callback(
    # Output('price_graph', 'figure'),
    # Output('reddit_graph', 'figure'),
    # Output('twitter_graph', 'figure'),
    Output('relayoutData3', 'children'),
    Output('relayoutData2', 'children'),
    Output('relayoutData', 'children'),
    Input('price_graph', 'relayoutData'),
    Input('reddit_graph', 'relayoutData'),
    Input('twitter_graph', 'relayoutData')
)
def update_relayout_data(relayoutData, relayoutData2, relayoutData3):
    return json.dumps(relayoutData, indent=2), json.dumps(relayoutData2, indent=2), json.dumps(relayoutData3, indent=2)


# Define callback to update graph
@app.callback(
    Output('reddit_graph', 'figure'),
    Output('twitter_graph', 'figure'),
    Output('price_graph', 'figure'),
    Output('card1', 'children'),
    Output('card2', 'children'),
    Output('card3', 'children'),
    Output('card4', 'children'),
    Output('card5', 'children'),
    Output('card6', 'children'),
    Input("symbol-dropdown", "value"),
    Input("timeframe-dropdown", "value"),
    Input('relayoutData', 'children'),
    Input('relayoutData2', 'children'),
    Input('relayoutData3', 'children')
)
def update_figure(symbol, timeframe, relayoutData, relayoutData2, relayoutData3):
    title = 'Reddit Social Information'  # title of the chart

    columns1 = ['reddit_posts', 'reddit_comments']  # columns in df
    columns1_labels = ['Reddit Posts', 'Reddit Comments']  # columns labels in chart

    columns2 = ['tweets', 'tweet_retweets', 'tweet_favorites', ]  # columns in df
    columns2_labels = ['Tweets', 'Retweets', 'Favorites']  # columns labels in chart

    colors = ['rgb(0,32,255)', 'rgb(0,128,255)', 'rgb(96,96,96)',
              'rgb(160,160,160)']  # color of lines in chart - blue color scale
    mode_size = [8, 8, 8, 8]  # size of points
    line_size = [2, 2, 2, 2]  # size of line

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
        # title=dict(
        #    text=symbol + ' Reddit Social Volume',
        #    font=dict(
        #      family= 'Arial',
        #      size=24,
        #    )
        # ),
        yaxis_title="# of post or comments",
        xaxis=dict(
            showline=True,
            # showgrid=False,
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
            t=10,
        ),
        showlegend=True,
        plot_bgcolor='white',
        legend=dict(
            yanchor="top",
            y=1,
            xanchor="left",
            x=0
        )
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
        # title=dict(
        #    text=symbol + ' twitter social volume',
        #    font=dict(
        #      family= 'arial',
        #      size=24,
        #    )
        # ),
        yaxis_title="# of post or comments",
        xaxis=dict(
            showline=True,
            # showgrid=False,
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
            t=10,
        ),
        showlegend=True,
        plot_bgcolor='white',
        legend=dict(
            yanchor="top",
            y=1,
            xanchor="left",
            x=0
        )
    )

    fig_price = make_subplots(specs=[[{"secondary_y": True}]])

    # include candlestick with rangeselector
    df['time'] = pd.to_datetime(df['time'], unit='s')  # convert from timestamp to datetime
    fig_price.add_trace(go.Candlestick(x=df['time'],  # pd.to_datetime(df['datetime'], unit='ns')
                                       open=df['open'], high=df['high'],
                                       low=df['low'], close=df['close'],
                                       increasing_line_color='rgb(0,128,255)', decreasing_line_color='rgb(96,96,96)',
                                       name="Price"),
                        secondary_y=False,
                        )

    # include a go.Bar trace for volumes
    fig_price.add_trace(go.Bar(x=df['time'], y=df['volume'], name="Volume"),
                        secondary_y=True,
                        )
    fig_price.update_traces(marker=dict(color='rgb(0,0,255)', opacity=0.3),
                            selector=dict(type="bar"))

    fig_price.layout.yaxis2.showgrid = False
    fig_price.update_yaxes(title_text="Price (USD)", secondary_y=False)
    fig_price.update_yaxes(title_text="Volume", secondary_y=True)

    fig_price.update_layout(
        # title=dict(
        #    text=symbol + ' Price Information',
        #    font=dict(
        #      family= 'Arial',
        #      size=24,
        #    )
        # ),
        xaxis=dict(
            showline=True,
            # showgrid=False,
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
            t=10,
        ),
        showlegend=False,
        plot_bgcolor='white',
        xaxis_rangeslider_visible=False,
        legend=dict(
            yanchor="top",
            y=1,
            xanchor="left",
            x=0
        )
    )
    # for dynamic time region selection

    if "xaxis.range" in relayoutData3:
        relayout = json.loads(relayoutData3)
        xlim1 = relayout["xaxis.range[0]"]
        xlim2 = relayout["xaxis.range[1]"]
        df = df[(df['time'] >= xlim1) & (df['time'] <= xlim2)]

        fig_price.update_xaxes(range=list([xlim1, xlim2]))
        fig_reddit.update_xaxes(range=list([xlim1, xlim2]))
        fig_tweet.update_xaxes(range=list([xlim1, xlim2]))

        # Price cards information
        start_price = df.head(1).close.values[0]
        start_price_str = "${:,.2f}".format(float(start_price))
        end_price = df.tail(1).close.values[0]
        percent_change = (end_price - start_price) / start_price * 100
        if percent_change > 0:
            percent_change_str = "+{:,.1f}%".format(float(percent_change))
        else:
            percent_change_str = "{:,.1f}%".format(float(percent_change))

        # Reddit Cards Information
        start_reddit = df.head(1)['reddit_posts'].values[0]
        start_reddit_str = "{:,.0f}".format(float(start_reddit))
        end_reddit = df.tail(1)['reddit_posts'].values[0]
        percent_change_reddit = (end_reddit - start_reddit) / start_reddit * 100
        if percent_change_reddit > 0:
            percent_change_reddit_str = "+{:,.1f}%".format(float(percent_change_reddit))
        else:
            percent_change_reddit_str = "{:,.1f}%".format(float(percent_change_reddit))

        # Twitter Cards Information
        start_tweets = df.head(1)['tweets'].values[0]
        start_tweets_str = "{:,.0f}".format(float(start_tweets))
        end_tweets = df.tail(1)['tweets'].values[0]
        percent_change_tweets = (end_tweets - start_tweets) / start_tweets * 100
        if percent_change_tweets > 0:
            percent_change_tweets_str = "+{:,.1f}%".format(float(percent_change_tweets))
        else:
            percent_change_tweets_str = "{:,.1f}%".format(float(percent_change_tweets))

        # Cards
        card_content1 = [
            dbc.CardHeader('Starting Price'),
            dbc.CardBody(
                [
                    html.H2(start_price_str, className="kpi"),
                    html.P(
                        "The closing price in the beginning of the period.",
                        className="card-text",
                    ),
                    html.Br()
                ]
            )
        ]
        card1 = dbc.Card(card_content1, color="secondary", outline=True)

        card_content2 = [
            dbc.CardHeader('Price Change'),
            dbc.CardBody(
                [
                    html.H2(percent_change_str, className="kpi"),
                    html.P(
                        "Closing Price change during the period.",
                        className="card-text",
                    ),
                    html.Br()
                ]
            )
        ]
        card2 = dbc.Card(card_content2, color="secondary", outline=True)

        card_content3 = [
            dbc.CardHeader('Starting Reddit Posts'),
            dbc.CardBody(
                [
                    html.H2(start_reddit_str, className="kpi"),
                    html.P(
                        "The number of Reddit posts in the beginning of the period.",
                        className="card-text",
                    ),
                    html.Br()
                ]
            )
        ]
        card3 = dbc.Card(card_content3, color="secondary", outline=True)

        card_content4 = [
            dbc.CardHeader('Reddit Posts Change'),
            dbc.CardBody(
                [
                    html.H2(percent_change_reddit_str, className="kpi"),
                    html.P(
                        "Reddit posts change during the period.",
                        className="card-text",
                    ),
                    html.Br()
                ]
            )
        ]
        card4 = dbc.Card(card_content4, color="secondary", outline=True)

        card_content5 = [
            dbc.CardHeader('Starting Tweets'),
            dbc.CardBody(
                [
                    html.H2(start_tweets_str, className="kpi"),
                    html.P(
                        "The number of tweets in the beginning of the period.",
                        className="card-text",
                    ),
                    html.Br()
                ]
            )
        ]
        card5 = dbc.Card(card_content5, color="secondary", outline=True)

        card_content6 = [
            dbc.CardHeader('Tweets Change'),
            dbc.CardBody(
                [
                    html.H2(percent_change_tweets_str, className="kpi"),
                    html.P(
                        "Tweets change during the period.",
                        className="card-text",
                    ),
                    html.Br()
                ]
            )
        ]
        card6 = dbc.Card(card_content6, color="secondary", outline=True)


    else:
        fig_price.update_layout(autosize=True)
        fig_reddit.update_layout(autosize=True)
        fig_tweet.update_layout(autosize=True)

        # Price cards information
        start_price = df.head(1).close.values[0]
        start_price_str = "${:,.2f}".format(float(start_price))
        end_price = df.tail(1).close.values[0]
        percent_change = (end_price - start_price) / start_price * 100
        if percent_change > 0:
            percent_change_str = "+{:,.1f}%".format(float(percent_change))
        else:
            percent_change_str = "{:,.1f}%".format(float(percent_change))

        # Reddit Cards Information
        start_reddit = df.head(1)['reddit_posts'].values[0]
        start_reddit_str = "{:,.0f}".format(float(start_reddit))
        end_reddit = df.tail(1)['reddit_posts'].values[0]
        percent_change_reddit = (end_reddit - start_reddit) / start_reddit * 100
        if percent_change_reddit > 0:
            percent_change_reddit_str = "+{:,.1f}%".format(float(percent_change_reddit))
        else:
            percent_change_reddit_str = "{:,.1f}%".format(float(percent_change_reddit))

        # Twitter Cards Information
        start_tweets = df.head(1)['tweets'].values[0]
        start_tweets_str = "{:,.0f}".format(float(start_tweets))
        end_tweets = df.tail(1)['tweets'].values[0]
        percent_change_tweets = (end_tweets - start_tweets) / start_tweets * 100
        if percent_change_tweets > 0:
            percent_change_tweets_str = "+{:,.1f}%".format(float(percent_change_tweets))
        else:
            percent_change_tweets_str = "{:,.1f}%".format(float(percent_change_tweets))

        # Cards
        card_content1 = [
            dbc.CardHeader('Starting Price'),
            dbc.CardBody(
                [
                    html.H2(start_price_str, className="kpi"),
                    html.P(
                        "The closing price in the beginning of the period.",
                        className="card-text",
                    ),
                    html.Br()
                ]
            )
        ]
        card1 = dbc.Card(card_content1, color="secondary", outline=True)

        card_content2 = [
            dbc.CardHeader('Price Change'),
            dbc.CardBody(
                [
                    html.H2(percent_change_str, className="kpi"),
                    html.P(
                        "Closing Price change during the period.",
                        className="card-text",
                    ),
                    html.Br()
                ]
            )
        ]
        card2 = dbc.Card(card_content2, color="secondary", outline=True)

        card_content3 = [
            dbc.CardHeader('Starting Reddit Posts'),
            dbc.CardBody(
                [
                    html.H2(start_reddit_str, className="kpi"),
                    html.P(
                        "The number of Reddit posts in the beginning of the period.",
                        className="card-text",
                    ),
                    html.Br()
                ]
            )
        ]
        card3 = dbc.Card(card_content3, color="secondary", outline=True)

        card_content4 = [
            dbc.CardHeader('Reddit Posts Change'),
            dbc.CardBody(
                [
                    html.H2(percent_change_reddit_str, className="kpi"),
                    html.P(
                        "Reddit posts change during the period.",
                        className="card-text",
                    ),
                    html.Br()
                ]
            )
        ]
        card4 = dbc.Card(card_content4, color="secondary", outline=True)

        card_content5 = [
            dbc.CardHeader('Starting Tweets'),
            dbc.CardBody(
                [
                    html.H2(start_tweets_str, className="kpi"),
                    html.P(
                        "The number of tweets in the beginning of the period.",
                        className="card-text",
                    ),
                    html.Br()
                ]
            )
        ]
        card5 = dbc.Card(card_content5, color="secondary", outline=True)

        card_content6 = [
            dbc.CardHeader('Tweets Change'),
            dbc.CardBody(
                [
                    html.H2(percent_change_tweets_str, className="kpi"),
                    html.P(
                        "Tweets change during the period.",
                        className="card-text",
                    ),
                    html.Br()
                ]
            )
        ]
        card6 = dbc.Card(card_content6, color="secondary", outline=True)

    return fig_reddit, fig_tweet, fig_price, card1, card2, card3, card4, card5, card6


if __name__ == '__main__':
    app.server(host='0.0.0.0', port=8080, debug=True)
    #app.run_server(debug=True)
