# https://tradewithpython.com/generating-buy-sell-signals-using-python

import numpy as np
import pandas as pd
import yfinance as yf
import pandas_datareader.data as web
import pandas_ta as ta
import matplotlib.pyplot as plt
from datetime import date

plt.style.use('fivethirtyeight')
yf.pdr_override()

stocksymbols = ['TATAMOTORS.NS']
startdate = date(2017,8,4)
end_date = date.today()
print(end_date)

def getMyPortfolio(stocks = stocksymbols ,start = startdate , end = end_date):
    # data = web.get_data_yahoo(stocks , data_source='yahoo' , start = start ,end= end )
    data = web.get_data_yahoo(stocks  , start = start ,end= end )
    return data


data = getMyPortfolio(stocksymbols)
print(data)


data['SMA 30'] = ta.sma(data['Close'],30)
data['SMA 100'] = ta.sma(data['Close'],100)

print(data)
#SMA BUY SELL
#Function for buy and sell signal
def buy_sell(data):
    signalBuy = []
    signalSell = []
    position = False 

    for i in range(len(data)):
        if data['SMA 30'][i] > data['SMA 100'][i]:
            if position == False :
                signalBuy.append(data['Adj Close'][i])
                signalSell.append(np.nan)
                position = True
            else:
                signalBuy.append(np.nan)
                signalSell.append(np.nan)
        elif data['SMA 30'][i] < data['SMA 100'][i]:
            if position == True:
                signalBuy.append(np.nan)
                signalSell.append(data['Adj Close'][i])
                position = False
            else:
                signalBuy.append(np.nan)
                signalSell.append(np.nan)
        else:
            signalBuy.append(np.nan)
            signalSell.append(np.nan)
    return pd.Series([signalBuy, signalSell])
