import argparse
import robin_stocks.robinhood as r
import yahoo_fin.stock_info as yf
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import mplfinance as mpf


'''
The purpose of this script is to extract fundamental data using the RobinHood API
'''

# from indicators import sigmas, moving_average_indicator, fractal_indicator
# from universe import sp500_list, nasdaq_list, dow_list

def rh_login():
    # construct the argument parse and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-e", "--email", required=True, help="robinhood email")
    ap.add_argument("-p", "--password", required=True,help="robinhood password")
    args = vars(ap.parse_args())

    r.login(args['email'],args['password'],expiresIn=86400,by_sms=True)

def candle_indicator(stock_df, view=False):

    print(stock_df.info)
    # stock_df['Candle Buy Signal'] = stock_df['close_price'][-1] > stock_df['close_price'][-2]
    # stock_df['Candle Sell Signal'] = stock_df['close_price'][-1] < stock_df['close_price'][-2]

    # if view == True:
    #     from matplotlib.dates import DateFormatter, date2num, WeekdayLocator, DayLocator, MONDAY
    #     import mplfinance
    #     from mplfinance.original_flavor import candlestick_ohlc
    #     stock_df = stock_df.reset_index()
    # # print(hist)
    #     print(stock_df.info)

    #     # print(hist['timestamp'])

    #     stock_df['date_ax'] = stock_df['timestamp'].apply(lambda date: date2num(date))

    #     # print(hist.head())

    #     list_of_cols = ['date_ax', 'open', 'high', 'low', 'close']

    #     hist_values = [tuple(vals) for vals in stock_df[list_of_cols].values]

    #     mondays = WeekdayLocator(MONDAY)
    #     alldays = DayLocator()
    #     weekFormatter = DateFormatter('%b %d')
    #     dayFormatter = DateFormatter('%d')

    #     fig, ax = plt.subplots()
    #     fig.subplots_adjust(bottom=0.2)
    #     ax.xaxis.set_major_locator(mondays)
    #     ax.xaxis.set_minor_locator(alldays)

    #     candlestick_ohlc(ax,hist_values,width=0.2,colorup='g',colordown='r')
    #     plt.show()

if __name__ == "__main__":
    stock = 'AAPL'

    # log into Robinhood so you can use the API to get fundamental data
    rh_login()

    # returns a list and each index has a dictionary with information


    # fundamental_data=  r.stocks.get_fundamentals(stock)
    # print(fundamental_data)
    """Takes any number of stock tickers and returns fundamental information
    about the stock such as what sector it is in, a description of the company, dividend yield, and market cap.

    :param inputSymbols: May be a single stock ticker or a list of stock tickers.
    :type inputSymbols: str or list
    :param info: Will filter the results to have a list of the values that correspond to key that matches info.
    :type info: Optional[str]
    :returns: [list] If info parameter is left as None then the list will contain a dictionary of key/value pairs for each ticker. \
    Otherwise, it will be a list of strings where the strings are the values of the key that corresponds to info.
    :Dictionary Keys: * open
                      * high
                      * low
                      * volume
                      * average_volume_2_weeks
                      * average_volume
                      * high_52_weeks
                      * dividend_yield
                      * float
                      * low_52_weeks
                      * market_cap
                      * pb_ratio
                      * pe_ratio
                      * shares_outstanding
                      * description
                      * instrument
                      * ceo
                      * headquarters_city
                      * headquarters_state
                      * sector
                      * industry
                      * num_employees
                      * year_founded
                      * symbol

    """ 


    # um = r.get_instruments_by_symbols(stock, info=None)
    # print(um)
    """Takes any number of stock tickers and returns information held by the market
    such as ticker name, bloomberg id, and listing date.

    :param inputSymbols: May be a single stock ticker or a list of stock tickers.
    :type inputSymbols: str or list
    :param info: Will filter the results to have a list of the values that correspond to key that matches info.
    :type info: Optional[str]
    :returns: [list] If info parameter is left as None then the list will a dictionary of key/value pairs for each ticker. \
    Otherwise, it will be a list of strings where the strings are the values of the key that corresponds to info.
    :Dictionary Keys: * id
                      * url
                      * quote
                      * fundamentals
                      * splits
                      * state
                      * market
                      * simple_name
                      * name
                      * tradeable
                      * tradability
                      * symbol
                      * bloomberg_unique
                      * margin_initial_ratio
                      * maintenance_ratio
                      * country
                      * day_trade_ratio
                      * list_date
                      * min_tick_size
                      * type
                      * tradable_chain_id
                      * rhs_tradability
                      * fractional_tradability
                      * default_collar_fraction

    """ 

    price = r.get_latest_price(stock)
    print(price)

    hist_df = pd.DataFrame(columns=['Datetime','Open', 'High', 'Low','Close',
                                    'Volume',
                                    'Symbol'
                                    # 'session',
                                    # 'interpolated'
                                    ])

 


    stock_history = r.get_stock_historicals(stock, interval='day', span='year', bounds='regular', info=None)

    for hist in stock_history:
        print(hist)
        date = hist['begins_at']
        date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
        print(date)
        print(type(date))
        df_new_row = pd.DataFrame({
            'Datetime':[date],
            'Symbol':[hist['symbol']],
            'Open':[float(hist['open_price'])],
            'High':[float(hist['high_price'])],
            'Low':[float(hist['low_price'])],
            'Close':[float(hist['close_price'])],
            'Volume':[float(hist['volume'])],
            # 'session':[hist['session']],
            # 'interpolated':[hist['interpolated']],
        })



        hist_df = pd.concat([hist_df, df_new_row],ignore_index=True)


    # Convert 'Datetime' column to datetime objects and set as index
    hist_df['Datetime'] = pd.to_datetime(hist_df['Datetime'])
    hist_df.set_index('Datetime',inplace=True)
    print(hist_df)

    # # Plot candlestick chart
    mpf.plot(hist_df, type='candle')


    # candle_indicator(hist_df,view=True)
    # PLOT with signals 
    # fig, ax = plt.subplots(figsize=(14,8))
    # ax.plot(hist_df['close_price'] , label = 'AAPL' ,linewidth=0.5, color='blue', alpha = 0.9)
    # # ax.plot(data['SMA 30'], label = 'SMA30', alpha = 0.85)
    # # ax.plot(data['SMA 100'], label = 'SMA100' , alpha = 0.85)
    # # ax.scatter(data.index , data['Buy_Signal_price'] , label = 'Buy' , marker = '^', color = 'green',alpha =1 )
    # # ax.scatter(data.index , data['Sell_Signal_price'] , label = 'Sell' , marker = 'v', color = 'red',alpha =1 )
    # # ax.set_title(stocksymbols[0] + " Price History with buy and sell signals",fontsize=10, backgroundcolor='blue', color='white')
    # # ax.set_xlabel(f'{startdate} - {end_date}' ,fontsize=18)
    # ax.set_ylabel('Close Price INR (₨)' , fontsize=18)
    # legend = ax.legend()
    # ax.grid()
    # plt.tight_layout()
    # plt.show()
    # # print(hist[0].keys())
    # # print(hist[0].values())
    # # print(len(hist))
