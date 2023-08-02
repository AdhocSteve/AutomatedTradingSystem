import numpy as np
import pandas as pd
import yfinance as yf
import pandas_datareader.data as web
import pandas_ta as ta
import matplotlib.pyplot as plt
from dateime import date

plt.style.use('fivethirtyeight')
yf.pdr_override()

stocksymbols = ['TATAMOTORS.NS']