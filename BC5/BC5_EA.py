import numpy as np
import pandas as pd
import yfinance as yf
import plotly.graph_objs as go

# downloads data for last 7 years day by day
# data_btc = yf.download(tickers=['ETH-USD', 'BTC-USD'], period = '7y', interval = '1d')

# downloads data for each 15 min in the last 7 hours
data_btc = yf.download(tickers=['ETH-USD', 'BTC-USD'], period = '7h', interval = '15m')

#prints closing price for bitcoin - multi index - can be really usedful to not having too many DFs
print(data_btc["Close", "BTC-USD"])