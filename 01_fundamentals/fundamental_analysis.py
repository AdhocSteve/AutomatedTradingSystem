import argparse
import robin_stocks.robinhood as r
import yahoo_fin.stock_info as yf
import pandas as pd
from datetime import datetime
from tqdm import tqdm

from df_cheats import save_df
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

def get_stock_list(universe):
    '''
    returns a tuple (stock_list, 'market_name_string')
    this functions uses different methods to get a list of stocks in an index
    '''
    if universe == 'sp500':
        table=pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
        sp500_list = list(table[0]['Symbol'])
        return (sp500_list,universe)
    
    if universe == 'nasdaq':
        nasdaq_list = yf.tickers_nasdaq()
        return (nasdaq_list,universe)
    
    if universe == 'ETF':
        ETF_list = pd.read_excel('list_of_ETF_securities.xlsx')
        ETF_list = list(ETF_list['Ticker'])
        return (ETF_list,universe)
    
    if universe == 'top_options':
        top_options_list = pd.read_excel('list_of_wb_top_options.xlsx')
        top_options_list = list(top_options_list['Ticker'])
        return (top_options_list,universe)

def get_symbols_groups(lst,n):
    """  
    used for api batch calls
    yield succesive n-sized chunks from list
    """
    for i in tqdm(range(0, len(lst),n)):
        yield lst[i:i+n]

def fundamental_data(stock_list):
    # create dataframe soon to be populated
    # helps if you already have an idea of what the API returns looks like
    fundamental_df =  pd.DataFrame(columns=['Ticker'
                                            ])
    
    # now you are ready to make API batch calls to download fundamental data
    print(f'Dowloading {stock_list[1]} fundamental data')

    # create batches of symbol groups, each limited to 75 securities
    symbol_groups = get_symbols_groups(stock_list[0],75)

     # perfrom api batch call to get data and populate df                  
    for group in symbol_groups:
        '''
        Talk about the some of the data you can get from the Robinhood API
        '''
        fundamentals_group =  r.stocks.get_fundamentals(group,)

        # iterate over each fundamental_group list and parse 
        # through each dictionary element. 
        for fund in fundamentals_group:

            try:
                # i think it wouuld be useful to see how far away
                high52 = fund['high_52_weeks_date']
                low52 = fund['low_52_weeks_date']

                dhigh52 = datetime.strptime(high52, "%Y-%m-%d")
                dlow52 = datetime.strptime(low52, "%Y-%m-%d")

                today = datetime.today()
                delta52high = today - dhigh52
                delta52low = today - dlow52

                # sometimes there is None data that is not too friendly to the rest of the code
                if(fund['open']==None):
                    fund['open']=0.0
                
                if(fund['high']==None):
                    fund['high']=0.0

                if(fund['low']==None):
                    fund['low']=0.0

                if(fund['pb_ratio']==None):
                    fund['pb_ratio']=0.0

                if(fund['pe_ratio']==None):
                    fund['pe_ratio']=0.0

                if(fund['dividend_yield']==None):
                    fund['dividend_yield']=0.0
                    
                # BUILD DATA FRAME TO ADD THE INFORMATION YOU WANT FROM THE DICTIONARY
                df_new_row = pd.DataFrame({ 
                                                'Ticker':[fund['symbol']],
                                                'Open':[float(fund['open'])],
                                                'High':[float(fund['high'])],
                                                'Low':[float(fund['low'])],
                                                'Volume':[float(fund['volume'])],
                                                # 'AvgVolume':[float(fund['average_volume'])],
                                                'OvernightVol':[float(fund['overnight_volume'])],
                                                # # 'Avg2weekVol':[float(fund['average_volume_2_weeks'])],
                                                # # 'Avg30weekVol':[float(fund['average_volume_2_weeks'])],
                                                '52weekHigh':[fund['high_52_weeks']],
                                                '52weekHighDate':[fund['high_52_weeks_date']],
                                                '52HighDelta':delta52high.days,
                                                '52weekLow':[fund['low_52_weeks']],
                                                '52weekLowDate':[fund['low_52_weeks_date']],
                                                '52LowDelta':delta52low.days,
                                                'DivYield':[float(fund['dividend_yield'])],
                                                # # 'Float':[math.floor(float(fund['float']))],
                                                'MarketCap':[float(fund['market_cap'])],
                                                'MarketCapBillions':[float(fund['market_cap'])/1000000000],
                                                'pbRatio':[float(fund['pb_ratio'])],
                                                'peRatio':[float(fund['pe_ratio'])],
                                                # 'SharesOutstanding':[math.floor(float(fund['shares_outstanding']))],
                                                # # 'Description':[fund['description']],
                                                # # 'CEO':[fund['ceo']],
                                                'Sector':[fund['sector']],
                                                'Industry':[fund['industry']],
                                                # # 'YearFounded':[fund['year_founded']],
                                                # # 'NumEmployees':[fund['num_employees']],
                                                # # 'City':[fund['headquarters_city']],
                                                'State':[fund['headquarters_state']]
                                            })
                fundamental_df = pd.concat([fundamental_df, df_new_row],ignore_index=True)
            except:
                unavailable_fund = fund['symbol']
                print(f'Looks  {unavailable_fund} not available')
                pass
    return fundamental_df

if __name__ == "__main__":

    # universe in which securities reside
    top_options = get_stock_list('top_options')
    sp_500 = get_stock_list('sp500')
    nasdaq = get_stock_list('nasdaq')
    ETFs = get_stock_list('ETF')

    # log into Robinhood so you can use the API to get fundamental data
    rh_login()
    sp500_fundamental_df = fundamental_data(sp_500)
    nasdaq_fundamental_df = fundamental_data(nasdaq)
    top_options_fundamental_df = fundamental_data(top_options)

    # save the fundamental data frames into excel sheets
    # save_df('fundamentals_for_' + sp_500[1], sp500_fundamental_df)
    # save_df('fundamentals_for_' + nasdaq[1], nasdaq_fundamental_df)
    save_df('fundamentals_for_' + top_options[1], top_options_fundamental_df)




