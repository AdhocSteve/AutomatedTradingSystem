
from matplotlib.pyplot import get
from custom_strategy03 import buy_stocks, get_buy_list
from numpy.core.fromnumeric import trace
from numpy.lib.function_base import select
from scipy.stats.stats import sigmaclip
from save_excel import save_excel_bought_yesterday
from numpy.lib.npyio import save
from webull import paper_webull
from universe import set_universe
from momentum import hqm_stocks
import pandas as pd 
from fractals import fractal_indicator
from visual import RSI, moving_average_indicator, bollinger_indicator, candle_indicator
from fibonnaci import fibonnaci_retracement
import math
import schedule
import time
from time import ctime


def login_webull():
    global wb
    wb = paper_webull()
    wb.refresh_login() # 7/23/2021 Will eventually have to change this 3 months from now
    result = wb.login('svalenzuela8@miners.utep.edu', 'Svelty+Car0+2o16!', 'comp', '044604', '1001', '0905') 
    if result:
        print('logged in')

def size_of_portfolio():
    global portfolio_size
    portfolio = wb.get_portfolio()
    portfolio_size = float(portfolio['usableCash'])
    print(portfolio_size)

def excel_portfolio_to_dic():
    global stocks_in_portfolio_dic
    stocks_in_portfolio_dic = {}
    print('read yesterdays stocks and saved into dictionary for faster iteration')
    print('')
    stocks_in_portfolio_excel = r'stocks_in_portfolio.xlsx'
    stocks_in_portfolio_df = pd.read_excel(stocks_in_portfolio_excel)
    stocks_in_portfolio_dic = {}
    for row in stocks_in_portfolio_df.index:
        stock = stocks_in_portfolio_df.loc[row,'Ticker']
        price = stocks_in_portfolio_df.loc[row,'Price']
        quant = stocks_in_portfolio_df.loc[row,'Quant']
        stocks_in_portfolio_dic.update({stock:(price,quant)})

    print('stocks in portfolio ',stocks_in_portfolio_dic)

def portfolio_check1():
    print('checking if yesterdays stocks reached  their target price ')
    print('if so save in dictionary to remove later ')
    print('')
    remove_stocks_from_portfolio = {}
    for key in stocks_in_portfolio_dic:
        stock = key 

        if stock in stocks_bought_today_dic:
            print(stock, 'bought today continue')
            continue

        stock_df = wb.get_bars(stock=stock, interval='d1', count=200 ,extendTrading=0)
        current_price = stock_df['close'][-1]
        stock_price_quant_tuple = stocks_in_portfolio_dic[stock]
        old_price, quant_bought = stock_price_quant_tuple
        target_price = old_price * 1.02
        stop_price = old_price * 0.96

        print(quant_bought, 'shares  of stock', stock, ' in portfolio since yesterday checking if target price reached')
        print('current_price ', current_price ,' old price ', old_price, ' target price ', target_price, ' stop_price ', stop_price)
        print('')
        if current_price >= target_price:
            try:
                wb.get_trade_token('022197')
                wb.place_order(stock=stock, action='SELL', orderType='MKT', enforce='DAY', quant=quant_bought)
                stocks_bought_today_dic.update({key:about_to_buy_dic[key]})
                remove_stocks_from_portfolio.update({stock:'sell'})
            except:
                print('unable to place order \n')

        if current_price <= stop_price:
            try:
                wb.get_trade_token('022197')
                wb.place_order(stock=stock, action='SELL', orderType='MKT', enforce='DAY', quant=quant_bought)
                stocks_bought_today_dic.update({key:about_to_buy_dic[key]})
                remove_stocks_from_portfolio.update({stock:'sell'})
            except:
                print('unable to place order \n')

    print('')

    # actaully sell and remvoe stocks from portfolio
    for key in remove_stocks_from_portfolio:
        # wb.get
        print(key, 'reached target remvoing from portofilio')
        stocks_in_portfolio_dic.pop(key)

    print('')


def get_quality_stocks():
    global quality_stocks_df
    universe='sp500'
    universe = set_universe(universe) 
    quality_stocks_df1 = hqm_stocks(universe,portfolio_size)

    universe2='nasdaq'
    universe2 = set_universe(universe2) 
    quality_stocks_df2 = hqm_stocks(universe2,portfolio_size)

    frames = [quality_stocks_df1,quality_stocks_df2]
    quality_stocks_df = pd.concat(frames, axis=0)

    quality_stocks_df = quality_stocks_df[quality_stocks_df['Price']<=20]
    quality_stocks_df = quality_stocks_df[quality_stocks_df['HQM Score']>=89.0]
    quality_stocks_df.reset_index(inplace=True, drop=True)
    print(quality_stocks_df)


def get_day_signal_df():
    global day_signal_df
    print('getting day signal dataframe  ')



    # build day signal dataframe
    day_signals = [
                'Ticker', 
                'Price', 
                'volume',
                'rsi', 
                'change',
                'gain',
                'loss',
                'avgGain',
                'avgLoss',
                'bull_frac',
                'bear_frac',
                '50MA > 200MA',
                '$ < 20MA',
                '$ < lvl1 fib',
                '$ > lvl3 fib']

    day_signal_df = pd.DataFrame(columns = day_signals)

    # set up dictionaries to save special stocks
    fractal_day_list = {}
    gappers_day_list = {}

    for row in quality_stocks_df.index:
        stock = quality_stocks_df.loc[row,'Ticker']

        if stock in stocks_in_portfolio_dic:
            print('')
            print(f'{stock} already in portfolio so not getting day signals for')
            print('')
            time.sleep(0.3)
            continue


        try:
            stock_df = wb.get_bars(stock=stock, interval='d1', count=200 ,extendTrading=0)
            willing_to_loose = portfolio_size * 0.045
            quant = math.floor(willing_to_loose/stock_df['close'][-1])
            if quant == 0:
                # print('cannot buy', stock, ' shares able to buy', quant)
                print('.')
                continue

            stock_df['volume'] = stock_df['volume']/1000000
            if stock_df['volume'][-1] < 0.9:
                # print(f'{stock}  passed because it had low volume', stock_df['volume'][-1])
                print('.')
                continue

            moving_average_indicator(stock_df)  
            RSI(stock_df)
            fractal_indicator(stock_df)
            fibonnaci_retracement(stock_df)


            # print(stock_df)

            # populate day signal dataframe 
            day_signal_df = day_signal_df.append(pd.Series( 
                                    [
                                    stock, 
                                    stock_df['close'][-1],
                                    round(stock_df['volume'][-1],2),
                                    int(stock_df['rsi'][-1]),
                                    stock_df['change'][-1],
                                    stock_df['gain'][-1],
                                    stock_df['loss'][-1],
                                    stock_df['avgGain'][-1], 
                                    stock_df['avgLoss'][-1], 
                                    stock_df['bull_fractal'][-1],
                                    stock_df['bear_fractal'][-1],
                                    stock_df['50MA > 200MA'][-1],
                                    stock_df['$ < 20MA'][-1],
                                    stock_df['$ < lvl2'][-1],
                                    stock_df['$ > lvl3'][-1]
                                    ],
                                    index = day_signals ),
                                    ignore_index = True)

            time.sleep(0.2)
        except:
            print('skipped', stock)
            print(stock_df.tail())
            time.sleep(0.2)
            print('')
    # # maybe filter out high rsi, MA50<200, 
    # # maybe save fractals, fib levels, gappers
    print(day_signal_df)
    return day_signal_df

stocks_bought_today_dic = {}
def get_buy_list():
    global about_to_buy_dic
    print('====================getting buy list')

    print(day_signal_df)

    print('stocsk bought alreayd', stocks_bought_today_dic)
    about_to_buy_dic = {}
    #     # stocks_bought_today_dic = {}
    for row in day_signal_df.index:
        print(day_signal_df.loc[row,'Ticker'])
        stock_to_buy = day_signal_df.loc[row,'Ticker']

        if stock_to_buy in stocks_bought_today_dic:
            print('just bought today',stock_to_buy)
            continue

        if stock_to_buy in stocks_in_portfolio_dic:
            print('bought yesterday still havent sold',stock_to_buy)
            continue

        if stock_to_buy in about_to_buy_dic:
            print('already in possible buy list', stock_to_buy)
            continue
        stock_df = wb.get_bars(stock=stock_to_buy, interval='m5', count=200 ,extendTrading=0)
        bollinger_indicator(stock_df)
        candle_indicator(stock_df)
        
        # print(stock_df)

        try:

            
            print(stock_to_buy,' bollinger signal ', stock_df['price < LB'][-1], ' candle signal ',stock_df['Candle Buy Signal'][-1] )
            if (stock_df['price < LB'][-1] == True) and (stock_df['Candle Buy Signal'][-1]==True):
                # print('BUYING ', stock_to_buy)
                price = stock_df['close'][-1]
                willing_to_loose = portfolio_size * 0.045
                quant = math.floor(willing_to_loose/price)

                print('bollinger signal ', stock_df['price < LB'][-1], ' candle signal ')
                if quant != 0:
                    about_to_buy_dic.update({stock_to_buy:(price,quant)})
                    print('BUYING ', quant,' of ', stock_to_buy, ' at ',price )
                    print('bollinger signal ', stock_df['price < LB'][-1], ' candle signal ')
        except:
            print('sipp', stock_to_buy)
            print('')

            # print(stock_df)
    print('')

    print('stocks about to be purchased ',about_to_buy_dic)
    print('')

    print('===============finished getting buy list======================')
    print('')

def buy_stocks():
        
    global stocks_to_remove,stocks_bought_today_dic

    print('===============buying stocks and saving them on an excel  ============')
    print('')

    stocks_to_remove = {}
        # still not sure if another dataframe for todays bought stoughs should be inlcuded
        # i guess so so i can still iterate throught the stocks bought yesterday and today 
        # and exclude the stocks that were bought toda


    for key in about_to_buy_dic:
            # check if stock already bought
            # print(key)
            # print(buy_dic[key])

        buying_stock = key
        pri, qua = about_to_buy_dic[key]

        if buying_stock in stocks_bought_today_dic:
            print(buying_stock,' already purchased')
            continue

        if buying_stock in stocks_in_portfolio_dic:
                print(buying_stock,' already owned since yesterday')
                continue

        try:

            wb.get_trade_token('022197')
            wb.place_order(stock=buying_stock, action='BUY', orderType='MKT', enforce='DAY', quant=qua)
            stocks_bought_today_dic.update({key:about_to_buy_dic[key]})
            stocks_to_remove.update({key:'sell'})
        except:
            print('market not open')

    print('about to buy',about_to_buy_dic)
    print('stocks bought today ', stocks_bought_today_dic)
    

    for key in stocks_to_remove:
        stock = key
        print(stock, 'removed from buy cidtionary ')
        about_to_buy_dic.pop(stock)

    stocks_to_remove.clear()

    print('stocks about to buy', about_to_buy_dic)

def save_excel_of_stocks_portfolio_new():
    global portfolio_stocks_and_bought_today_stocks

    stocks_in_portfolio_columns = [
                'Ticker', 
                'Price', 
                'Quant'
    ]

    stocks_in_portfolio = pd.DataFrame(columns =stocks_in_portfolio_columns)


    def Merge(dict1, dict2):
        dic = {**dict1, **dict2}
        return dic

    portfolio_stocks_and_bought_today_stocks = Merge(stocks_in_portfolio_dic, stocks_bought_today_dic)
    print('portfolio +  bought today ', portfolio_stocks_and_bought_today_stocks)

    for key in portfolio_stocks_and_bought_today_stocks:
        stock = key
        price , quant = portfolio_stocks_and_bought_today_stocks[stock]
        stocks_in_portfolio = stocks_in_portfolio.append(pd.Series( 
                            [stock, 
                            price,
                            quant
                            ],

                            index = stocks_in_portfolio_columns ),
                            ignore_index = True)

    print('')
    print('stocks bought and ready to be remvoved from today buy list ',stocks_to_remove)
    print('yesterdays stocks still not sold ', stocks_in_portfolio_dic)
    print('today bought', stocks_bought_today_dic)
    # print('stocks in portoflio now', portfolio_stocks_and_bought_today_stocks)
    print('')
    for key in stocks_to_remove:
        stock = key
        print(stock, 'removed from buy cidtionary ')
        about_to_buy_dic.pop(stock)

    stocks_to_remove.clear()


    day = 'AssTest'
    print('this will be saved on exdcel bought list ')
    print(stocks_in_portfolio)
    print('')

    save_excel_bought_yesterday(df=stocks_in_portfolio)


sell_pesky_stocks = {}
def check_portfolio2():
    for key in portfolio_stocks_and_bought_today_stocks:# that way yesterdays stocks can be just one excel read and overwriten through each loop 
        stock = key                         # and avoids day trades
        if stock in stocks_bought_today_dic:
            print(stock, ' bought today ')
            continue

        print(stock, 'still pending sale')
        stock_df = wb.get_bars(stock=stock, interval='m5', count=200 ,extendTrading=0)

        old_price, quant_bought = portfolio_stocks_and_bought_today_stocks[stock]
        current_price = stock_df['close'][-1]

        target_price = old_price * 1.02
        stop_price = old_price * 0.96

        if current_price >=  target_price:
            print('target reached ')
            try:
                wb.get_trade_token('022197')
                wb.place_order(stock=stock, action='SELL', orderType='MKT', enforce='DAY', quant=quant_bought)
                stocks_bought_today_dic.update({key:about_to_buy_dic[key]})
                sell_pesky_stocks.update({stock:quant_bought})
            except:
                print('unable to place order \n')

        if current_price <=  stop_price:
            print('target reached ')
            try:
                wb.get_trade_token('022197')
                wb.place_order(stock=stock, action='SELL', orderType='MKT', enforce='DAY', quant=quant_bought)
                stocks_bought_today_dic.update({key:about_to_buy_dic[key]})
                sell_pesky_stocks.update({stock:quant_bought})
            except:
                print('unable to place order \n')


    for key in sell_pesky_stocks:
        stock = key
        print(stock, 'removed from portfolioS ')
        stocks_in_portfolio_dic.pop(stock)

    sell_pesky_stocks.clear()
    print('stokcks left')
    print(stocks_in_portfolio_dic)

if __name__ == "__main__":
    # stocks_bought_today_dic = {}

    def part1():
        print(ctime(time.time()))
        start = time.time()
        login_webull()
        size_of_portfolio()
        excel_portfolio_to_dic()
        portfolio_check1()
        get_quality_stocks()
        get_day_signal_df()
        size_of_portfolio()
        end = time.time()
        print((end-start),'time for part 1')
        print('')
        # time.sleep(0.)

    def part2():
        print(ctime(time.time()))
        start = time.time()
        get_buy_list()
        buy_stocks()
        save_excel_of_stocks_portfolio_new()
        check_portfolio2()
        size_of_portfolio()
        end = time.time()
        print((end-start),'time for part 2')
        print('')

    # print maybe in later time looks for stocks with low rsi like post 130

    schedule.every().day.at("07:27").do(part1)
    schedule.every().day.at("07:32").do(part2)
    schedule.every().day.at("07:37").do(part2)
    schedule.every().day.at("07:52").do(part2)
    schedule.every().day.at("07:57").do(part1)

    schedule.every().day.at("08:02").do(part2)
    schedule.every().day.at("08:07").do(part2)
    schedule.every().day.at("08:12").do(part2)
    schedule.every().day.at("08:17").do(part2)
    schedule.every().day.at("08:22").do(part2)
    schedule.every().day.at("08:27").do(part2)
    schedule.every().day.at("08:32").do(part1)
    schedule.every().day.at("08:37").do(part2)
    schedule.every().day.at("08:42").do(part2)
    schedule.every().day.at("08:47").do(part2)
    schedule.every().day.at("08:52").do(part2)
    schedule.every().day.at("08:57").do(part1)

    schedule.every().day.at("09:02").do(part2)
    schedule.every().day.at("09:07").do(part2)
    schedule.every().day.at("09:12").do(part2)
    schedule.every().day.at("09:17").do(part2)
    schedule.every().day.at("09:22").do(part2)
    schedule.every().day.at("09:27").do(part2)
    schedule.every().day.at("09:32").do(part1)
    schedule.every().day.at("09:37").do(part2)
    schedule.every().day.at("09:42").do(part2)
    schedule.every().day.at("09:47").do(part2)
    schedule.every().day.at("09:52").do(part2)
    schedule.every().day.at("09:57").do(part1)

    schedule.every().day.at("10:02").do(part2)
    schedule.every().day.at("10:07").do(part2)
    schedule.every().day.at("10:12").do(part2)
    schedule.every().day.at("10:17").do(part2)
    schedule.every().day.at("10:22").do(part2)
    schedule.every().day.at("10:27").do(part2)
    schedule.every().day.at("10:32").do(part1)
    schedule.every().day.at("10:37").do(part2)
    schedule.every().day.at("10:42").do(part2)
    schedule.every().day.at("10:47").do(part2)
    schedule.every().day.at("10:52").do(part2)
    schedule.every().day.at("10:57").do(part1)

    schedule.every().day.at("11:02").do(part2)
    schedule.every().day.at("11:07").do(part2)
    schedule.every().day.at("11:12").do(part2)
    schedule.every().day.at("11:17").do(part2)
    schedule.every().day.at("11:22").do(part2)
    schedule.every().day.at("11:27").do(part2)
    schedule.every().day.at("11:32").do(part1)
    schedule.every().day.at("11:37").do(part2)
    schedule.every().day.at("11:42").do(part2) # change back to part2 asap
    schedule.every().day.at("11:47").do(part2)
    schedule.every().day.at("11:52").do(part2)
    schedule.every().day.at("11:57").do(part1)

    schedule.every().day.at("12:02").do(part2)
    schedule.every().day.at("12:07").do(part2)
    schedule.every().day.at("12:12").do(part2)
    schedule.every().day.at("12:17").do(part2)
    schedule.every().day.at("12:22").do(part2)
    schedule.every().day.at("12:27").do(part2)
    schedule.every().day.at("12:32").do(part1)
    schedule.every().day.at("12:37").do(part2)
    schedule.every().day.at("12:42").do(part2)
    schedule.every().day.at("12:47").do(part2) #
    schedule.every().day.at("12:52").do(part2)
    schedule.every().day.at("12:57").do(part1)

    schedule.every().day.at("13:02").do(part2)
    schedule.every().day.at("13:07").do(part2)
    schedule.every().day.at("13:12").do(part2)
    schedule.every().day.at("13:17").do(part2)
    schedule.every().day.at("13:22").do(part2)
    schedule.every().day.at("13:27").do(part2)
    schedule.every().day.at("13:32").do(part1)
    schedule.every().day.at("13:37").do(part2)
    schedule.every().day.at("13:42").do(part2)
    schedule.every().day.at("13:47").do(part2)
    schedule.every().day.at("13:52").do(part2)
    schedule.every().day.at("13:57").do(part1)
    
    


#    while time != sometime:
        

#    part1() # takes about 5 minutes to cycle over
    part1()
    part2()


    while True:
        schedule.run_pending()
        time.sleep(1)
