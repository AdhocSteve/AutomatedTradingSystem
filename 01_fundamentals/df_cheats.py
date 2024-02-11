import pandas as pd
import xlsxwriter
from datetime import date

def save_df(data_name, df):
    '''
    be proud of this one, I believe this is your first real piece of self written code. 
    '''
    CURRENT_DATE = date.today()
    workbook_name = data_name + '_' + str(CURRENT_DATE) + '.xlsx'
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
