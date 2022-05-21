import numpy as np
import pandas as pd
import yfinance as yf
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
import dash
from dash import dcc, Dash, html
from dash.dependencies import Input, Output
import base64
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings("ignore")

# ----------------------------------------------------------------------------------------------------------------------
# Calling the app
app = Dash(external_stylesheets=[dbc.themes.GRID])

dropdown_leaderboard = dcc.Dropdown(
    id='leaderboard_drop',
    className = "dropdown",
    options={"1d":"Last Day", "5d":"Last Five Days", "1mo":"Last Month", "2mo":"Last Two Months", "3mo":"Last Quarter", "1y":"Last Year"},
    value='1y',
    multi=False,
    clearable = False,
    style={"box-shadow" : "1px 1px 3px lightgray", "background-color" : "white"}
    )

# ----------------------------------------------------------------------------------------------------------------------
# Functions to create plots

image_filename = 'ims_logo.png' # replace with your own image
encoded_image = base64.b64encode(open(image_filename, 'rb').read())

coins_bc4 = ['ADA-USD', 'ATOM-USD', 'AVAX-USD', 'AXS-USD', 'LUNA1-USD', 'MATIC-USD', 'BTC-USD', 'ETH-USD', 'SOL-USD', "LINK-USD"]
coins_added = ["DOGE-USD", "DOT-USD", "TRX-USD", "SHIB-USD", "LTC-USD", "XMR-USD", "FLOW-USD", "HNT-USD", "QNT-USD", "PAXG-USD"]
coins = coins_bc4 + coins_added

def create_leaderboard(lb_range = "1d"):
    """creates a leaderboard of the most performing coins in a time range 
    possible values for argument: one day 1d, five days 5d, one month 1mo, 2months 2mo, one quarter 3mo, one year 1y"""
    if (lb_range == "1d"):
        data_lb = yf.download(tickers=coins, period = "2d", interval = "15m")
    elif (lb_range == "5d"):
        data_lb = yf.download(tickers=coins, period = "2d", interval = "60m")
    else:
        data_lb = yf.download(tickers=coins, period = lb_range, interval = "1d")
    # creating empty df
    leaderboard = pd.DataFrame(columns = ["Percentage"])
    # appending percentage change in the timeframe for each coin into leaderboard df
    for coin in coins:
        prc = ((data_lb["Close", coin].iloc[-1] - data_lb["Close", coin].iloc[0]) / data_lb["Close", coin].iloc[-1]) * 100
        prc = np.round(prc, 2)
        leaderboard.loc[coin] = prc
    leaderboard.sort_values("Percentage", ascending=False, inplace=True)
    return data_lb, leaderboard

def get_linegraph(close_price, coin_name):
    #layout
    fig = go.Scatter(
        x = close_price.index,
        y = close_price.values,
        name = coin_name,
    )
    return fig


def get_top_bot(data_lb, leaderboard):
    """returns the linegraph figures for the two top and bottom performancers for the range specified in create_leaderboard() function """
    leaderboard.dropna(inplace=True)
    fig1 = get_linegraph(data_lb["Close", leaderboard.iloc[0].name], leaderboard.iloc[0].name)
    fig2 = get_linegraph(data_lb["Close", leaderboard.iloc[1].name], leaderboard.iloc[1].name)
    fig3 = get_linegraph(data_lb["Close", leaderboard.iloc[-2].name], leaderboard.iloc[-2].name)
    fig4 = get_linegraph(data_lb["Close", leaderboard.iloc[-1].name], leaderboard.iloc[-1].name)
    return fig1, fig2, fig3, fig4



def plot_leaderboard(leaderboard):
    """returns the table leaderboard figure"""
    leaderboard.dropna(inplace=True)
    fig = go.Figure(data=[go.Table(
    header=dict(values=["Coins", "Percentage change in closing price"],
                fill_color='lightgray',
                align='center'),
    cells=dict(values=[leaderboard.index, leaderboard],
               fill_color='white',
               align='center'))
    ])
    fig.update_layout(
        title = 'Leaderboard'
    )
    return fig


def plot_technical_analyis(coin="BTC-USD", boll_window = 30):
    """returning technical analysis plots for a certain coin over the time of existence of the coin"""

    df = yf.download(tickers=coin, period = "max", interval = "1d")
    #bollinger window parameters
    df['sma'] = df['Close'].rolling(boll_window).mean()
    df['std'] = df['Close'].rolling(boll_window).std(ddof = 0)
    df.reset_index(inplace=True)
    layout = go.Layout(
        autosize=False,
        xaxis= go.layout.XAxis(linecolor = 'black',
                              linewidth = 1,
                              mirror = True),

        yaxis= go.layout.YAxis(linecolor = 'black',
                              linewidth = 1,
                              mirror = True),
        margin=go.layout.Margin(
            l=50,
            r=50,
            b=100,
            t=100,
            pad = 4
        )
    )
    fig = go.Figure(
        data=[go.Candlestick(
        x=df.index,
        open=df['Open'], high=df['High'],
        low=df['Low'], close=df['Close'],
        increasing_line_color= 'Green', decreasing_line_color= 'Red'
    ), 
                go.Scatter(
                    x = df.index, 
                    y = df["Close"].rolling(window=21).mean(),
                    mode = 'lines', 
                    name = '21SMA',
                    line = {'color': '#ffff00'}
                ),
                go.Scatter(
                    x = df.index, 
                    y = df["Close"].rolling(window=50).mean(),
                    mode = 'lines',
                    name = '50SMA',
                    line = {'color': '#00ff11'}
                ), 
                go.Scatter(
                    x = df.index, 
                    y = df["Close"].rolling(window=200).mean(),
                    mode = 'lines', 
                    name = '200SMA',
                    line = {'color': '#ff0008'}
                ), 
                go.Scatter(
                    x = df.index, 
                    y = df["sma"],
                    mode = 'lines', 
                    name = '30SMA',
                    line = {'color': '#b300ff'}
                ),
                 go.Scatter(
                    x = df.index, 
                    y = df['sma'] + (df['std'] * 2),
                    line_color = 'gray',
                    line = {'dash': 'dash'},
                    name = 'upper band',
                    opacity = 0.5
                ),
                go.Scatter(
                    x = df.index, 
                    y = df['sma'] - (df['std'] * 2),
                    line_color = 'gray',
                    line = {'dash': 'dash'},
                    fill = 'tonexty',
                    name = 'lower band',
                    opacity = 0.5
                ),
            ]
        ,layout=layout)
    fig2 = go.Figure(
                data = go.Bar(
                    x = df.index,
                    y = df["Volume"],
                    marker_color = "black"
                )
    )
    fig.update_layout(
        title = f'The Candlestick graph for {coin}',
        xaxis_title = 'Date',
        yaxis_title = f'{coin}',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis_rangeslider_visible = False
    )
    fig.update_yaxes(tickprefix='$')
    fig2.update_layout(
        title = f'The Barchart graph showing volume for {coin}',
        xaxis_title = 'Date',
        yaxis_title = 'Amount of asset traded during the day',
        xaxis_rangeslider_visible = False,
        autosize=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig, fig2

# ----------------------------------------------------------------------------------------------------------------------
# App Layout

# ----------------------------------------------------------------------------------------------------------------------
# App layout
app.layout = dbc.Container([

    # 1st Row
    dbc.Row([
        dbc.Col(html.Div(html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()))),width=1),
        dbc.Col([html.H1("Crypto Currencies Dashboard",style={'letter-spacing': '1.5px','font-weight': 'bold','text-transform': 'uppercase'}),
                 html.H2("Business Case n. 5  -  Group I", style={'margin-bottom': '5px'})],
                width=9)
    ]),

    # Intermediate Row - Story telling
    dbc.Row(dbc.Col(html.H2("Discover the coins that performed better in a specified range of time by comparing their percentage changes over the course of the chosen range", style={'margin-bottom': '5px'}))),
    # Intermediate Row - DropDown Menu
    dbc.Row(dbc.Col(html.Div(dropdown_leaderboard),width=6, style={'padding': '0px 15px 0px'})),

    # 2nd Row
    dbc.Row([
        dbc.Col(html.Div(
            dcc.Graph(id="leaderboard", style={'box-shadow':'1px 1px 3px lightgray', "background-color" : "white"})),
            width=6,
            style={'padding':'2px 15px 15px 15px'}),
        dbc.Col(html.Div(
            dcc.Graph(id="leaderboard_coins", style={'box-shadow':'1px 1px 3px lightgray', "background-color" : "white"})),
            width=6,
            style={'padding':'2px 15px 15px 15px'}),
    ]),
],
#Container
fluid=True,
style={'background-color':'#F2F2F2',
       'font-family': 'sans-serif',
       'color': '#606060',
       'font-size':'14px'
})

# ----------------------------------------------------------------------------------------------------------------------
# Callbacks
@app.callback(
    [Output(component_id='leaderboard', component_property='figure'),
     Output(component_id='leaderboard_coins', component_property='figure')],
    [Input('leaderboard_drop', 'value')])

def plot(range):
    data_lb, leaderboard = create_leaderboard(range)
    top1, top2, bot1, bot2 = get_top_bot(data_lb, leaderboard)
    plt_coins = make_subplots(rows = 2, cols = 2, start_cell="bottom-left")
    plt_coins.add_trace(top1, row = 1, col = 1)
    plt_coins.add_trace(top2, row = 1, col = 2)
    plt_coins.add_trace(bot1, row = 2, col = 1)
    plt_coins.add_trace(bot2, row = 2, col = 2)
    plt_lb = plot_leaderboard(leaderboard)
    plt_coins.update_layout(
        title = "Top 2 and Worst 2 coins in the leaderboard",
        # title_xanchor="center",
        xaxis_title = 'Date',
        xaxis = {"color" : "black"},
        yaxis_title = f'Close Price',
        # title_yanchor="center",
        yaxis = {"color" : "black"},
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    plt_coins.update_yaxes(tickprefix='$')
    
    return plt_lb, plt_coins

# ----------------------------------------------------------------------------------------------------------------------
# Running the app
if __name__ == '__main__':
    app.run_server(debug=True)
