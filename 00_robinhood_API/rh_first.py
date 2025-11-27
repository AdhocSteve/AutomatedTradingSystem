import argparse
import robin_stocks.robinhood as r
import yahoo_fin.stock_info as yf
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import mplfinance as mpf



import pyotp
totp  = pyotp.TOTP("My2factorAppHere").now()
print("Current OTP:", totp)