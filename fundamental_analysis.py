import robin_stocks.robinhood as r
import yahoo_fin.stock_info as yf
from datetime import date
from datetime import datetime
import pandas as pd
import argparse
from tqdm import tqdm
# from houskeeping import save_df, get_symbols_groups
import math
import time
import xlsxwriter

# from indicators import sigmas, moving_average_indicator, fractal_indicator
# from universe import sp500_list, nasdaq_list, dow_list

def rh_login():
    # construct the argument parse and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-e", "--email", required=True, help="robinhood email")
    ap.add_argument("-p", "--password", required=True,help="robinhood password")
    args = vars(ap.parse_args())
    r.login(args['email'],args['password'],expiresIn=86400,by_sms=True)

def get_stocks():
    table=pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    sp500 = list(table[0]['Symbol'])
    # symbol_groups = get_symbols_groups(sp500,n=75)
    return sp500

def get_symbols_groups(lst,n):
    """  
    used for api batch calls
    yield succesive n-sized chunks from list
    """
    for i in range(0, len(lst),n):
        yield lst[i:i+n]

def fundamental_data(symbol_groups,excel_subname='_stock_'):
    # create dataframe soon to be populated
    fundamental_df =  pd.DataFrame(columns=['Ticker',
                                            'Open' 
                                            # 'High',
                                            # 'Low',
                                            # 'Volume',
                                            # 'AvgVolume',
                                            # # 'OvernightVol',
                                            # # 'Avg2weekVol',
                                            # # 'Avg30weekVol',
                                            # '52weekHigh',
                                            # '52weekHighDate',
                                            # '52HighDelta',
                                            # '52weekLow',
                                            # '52weekLowDate',
                                            # '52LowDelta',
                                            # # 'DivYield',
                                            # # 'Float',
                                            # 'MarketCap',
                                            # 'pbRatio',
                                            # 'peRatio',
                                            # 'SharesOutstanding',
                                            # # 'Description',
                                            # # 'CEO',
                                            # 'Sector',
                                            # 'Industry',
                                            # # 'YearFounded',
                                            # # 'NumEmployees',
                                            # # 'City',
                                            # # 'State'
                                            ])

     # perfrom api batch call to get data and populate df                  
    for group in symbol_groups:
        '''
        Talk about the some of the data you can get from the Robinhood API
        '''
        fundamentals_group =  r.stocks.get_fundamentals(group)

        # iterate over each fundamental_group list and parse 
        # through each dictionary element. 
        for fund in fundamentals_group:
            print(fund)
            print('')
            try:
                # additional info for dataframe consider moving into another function. 
                high52 = fund['high_52_weeks_date']
                print('sup', high52)
                dhigh52 = datetime.strptime(high52, "%Y-%m-%d")
                low52 = fund['low_52_weeks_date']
                dlow52 = datetime.strptime(low52, "%Y-%m-%d")
                today = datetime.today()
                delta52high = today - dhigh52
                delta52low = today - dlow52

                print(fund['pb_ratio'])
                print(type(fund['pb_ratio']))
                print(None)

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
                pass
    return fundamental_df

def combine_df(df1,df2):
    combined_df = pd.concat([df1, df2],ignore_index=True)
    return combined_df

def filter_df(fundamental_df):
    filtered_df = fundamental_df.copy()
    ''' FILTER BY P/B Ratio 
    A p/b of 1 is indicative a fair price. 
    if p/b negative more liability
    # '''
    filtered_df = filtered_df[filtered_df['pbRatio']<=2]
    filtered_df = filtered_df[filtered_df['pbRatio']>=0]

    ''' FILTER BY P/E RATIO ''' # sign of profits if positive. if negative reporting loes. 
    filtered_df = filtered_df[filtered_df['peRatio']>0]

    ''' FILTER BY DIVIDEND RATE ''' # sign of profits if positive. if negative reporting loes. 
    filtered_df = filtered_df[filtered_df['DivYield']>0]

    # ''' FILTER BY PRICE '''
    # # filtered_df = filtered_df[fundamental_df['Open']<=200]

    # ''' FILTER BY MAXIMA / MINIMA ie 52week high or low'''
    # filtered_df = fundamental_df[filtered_df['52LowDelta']<=15] # what goes up must come down
    # # filtered_df = fundamental_df[fundamental_df['52HighDelta']<=15]

    # ''' FILTER BY MARKET CAP '''
    filtered_df = filtered_df[filtered_df['MarketCap']>=10000000000] # what goes up must come down


    # ''' FILTER BY VOLUME '''
    # # filtered_df = fundamental_df[fundamental_df['Volume']>=10000000000]
    # filtered_df = filtered_df[filtered_df['AvgVolume']>=3000000]

    ''' FILTER BY SECTOR'''
    # filtered_df = filtered_df[fundamental_df['Sector'].str.contains('Utilities')]
    # filtered_df = filtered_df[fundamental_df['Sector'].str.contains('Technology')]
    # filtered_df = filtered_df[fundamental_df['Sector'].str.contains('Retail')]
    # filtered_df = filtered_df[fundamental_df['Sector'].str.contains('Durables')]
    # filtered_df = filtered_df[fundamental_df['Sector'].str.contains('Non-Durables')]
    # filtered_df = filtered_df[fundamental_df['Sector'].str.contains('Transportation')]

    ''' FILTER BY INDUSTRY '''
    # filtered_df = filtered_df[fundamental_df['Industry'].str.contains('Aerospace')]
    # filtered_df = filtered_df[fundamental_df['Industry'].str.contains('Specialty')]
    # filtered_df = filtered_df[fundamental_df['Industry'].str.contains('Homebuilding')]
    # filtered_df = filtered_df[fundamental_df['Industry'].str.contains('Trucking')]
    # filtered_df = filtered_df[fundamental_df['Industry'].str.contains('Railroads')]
    # filtered_df = filtered_df[fundamental_df['Industry'].str.contains('Air')]
    # filtered_df = filtered_df[filtered_df['Industry'].str.contains('Oil')]
    # filtered_df = filtered_df[filtered_df['Industry'].str.contains('Oil & Gas Production')]
    # filtered_df = filtered_df[filtered_df['Industry'].str.contains('Pipelines')]
    # filtered_df = filtered_df[filtered_df['Industry'].str.contains('Forest')]

    # filtered_df = filtered_df[filtered_df['Industry'].str.contains('Vehicles')]

    # filtered_df = filtered_df[fundamental_df['Industry'].str.contains('Other')]
    # filtered_df = filtered_df[fundamental_df['Industry'].str.contains('Couriers')]
    # filtered_df = filtered_df[fundamental_df['Industry'].str.contains('Distributors')]
    # filtered_df = filtered_df[fundamental_df['Industry'].str.contains('Wholesale')]
    # filtered_df = filtered_df[fundamental_df['Industry'].str.contains('Water')]

    filtered_df.reset_index(inplace=True, drop=True)
    return filtered_df

def sort_df(fundamental_df,label='DivYield',ascending=True):
    sorted_df = fundamental_df.copy()
    sorted_df.sort_values(label, ascending = False, inplace = True)
    sorted_df.reset_index(inplace=True, drop=True)
    return sorted_df

def save_df(data_name, df):
    CURRENT_DATE = date.today()
    workbook_name = data_name + str(CURRENT_DATE)+'.xlsx'
    workbook = xlsxwriter.Workbook(workbook_name)
    worksheet = workbook.add_worksheet()

    row = 0
    col = 0
    for label in df.columns.array:
        worksheet.write(row, col, label)
        for i in range(0,len(df)): 
            worksheet.write(i+1,col,df[label][i]) 
        col +=1 
    workbook.close()

if __name__ == "__main__":
#   LOGIN
    rh_login()

#   GET LIST OF SP500 STOCKS
    table = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    sp500 = list(table[0]['Symbol'])

#   GET LIST OF NASDAQ STOCKS
    nasdaq_list = yf.tickers_nasdaq()

    # GET ETF LIST
    etf_list = pd.read_excel('ETF_list.xlsx')
    etf_list = list(etf_list['Ticker'])
    # print(etf_list)

#   GET SUBLIST OF STOCKS FOR 
    sp500_groups = get_symbols_groups(sp500,n=75)
    nasdaq_groups = get_symbols_groups(nasdaq_list,n=75)
    etf_groups = get_symbols_groups(etf_list,n=75)


# ##################################################################################################
#     # USING SUBLIST MAKE BATCH CALLS AND GET THE FUNDAMETNAL DF
#     # # THAT HAS MOSTLY
    sp500fundamental_df = fundamental_data(sp500_groups)
    # print(sp500fundamental_df)
    # nasdaqfundamental_df = fundamental_data(nasdaq_groups)
    # etffundamental_df = fundamental_data(etf_groups)
    # filteredfundamental_df = filter_df(etffundamental_df)
    # filteredsp500_df = filter_df(sp500fundamental_df)
    # print('-etf-')
    # print(etffundamental_df)
    # print("-sp500-")
    print(sp500fundamental_df)
    # print(nasdaqfundamental_df)

    # print('-filtered etf-')
    # print(filteredfundamental_df)

    # print('-filtered sp500-')
    # print(filteredsp500_df)
    # print(sort_df(filteredfundamental_df))
    
#     combinedfundamental_df =  combine_df(sp500fundamental_df, nasdaqfundamental_df)
#     # filteredfundamental_df = filter_df(combinedfundamental_df)


#     # print(sp500fundamental_df)
#     # print('')
#     # print(nasdaqfundamental_df)
#     # print(sort_df(combinedfundamental_df))
    # print(sort_df(filteredfundamental_df))
    # print(filteredfundamental_df)

#     # # save_df('_combined_fundmental_data',combinedfundamental_df)

    save_df('complete_sp500_fundmental_data',sp500fundamental_df)
    # save_df('complete_nasdaq_fundmental_data',nasdaqfundamental_df)
#     # save_df('_nasdaq_fundmental_data',nasdaqfundamental_df)
#     save_df('_combined_fundmental_data',combinedfundamental_df)
    # save_df('_ETF_fundmental_data',filteredfundamental_df)







