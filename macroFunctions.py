from eod import EodHistoricalData
import datetime as dt
import json
import os
import math
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import pandas as pd
import numpy as np
import requests

DEFAULT_DATA = dt.date.today() - dt.timedelta(365)
TODAY = dt.date.today()




def get_exchange_data(key, exchange='NYSE'):
    '''
    returns documentation for a specific exchange
    '''
    if not key:
        print("Token could not be found :(")
        return None
    endpoint = f"https://eodhistoricaldata.com/api/exchange-symbol-list/"
    endpoint += f"{exchange}?api_token={key}&fmt=json"
    print("Downloading data -_-")
    call =requests.get(endpoint).text
    exchange_data = pd.DataFrame(json.loads(call))
    print("Completed :)")
    return exchange_data

def get_security_type(exchange_data, type="Common Stock"):
    """
    Returns a list of filtered security types
    Types available: Common Stock, ETF, Fund, Preferred Stock
    """
    symbols = exchange_data[exchange_data.Type == type]
    return symbols.Code.to_list()

def get_sp(symbols =True, sector= False):
    """
    Returns S&P 500 metadata
    Sectors: Communication Services, Consumer Discretionary, Consumer Staples, Energy, Financials, Health Care, Industrials, Information Technology, Materials, Real Estate, Utilities
    """
    sp = pd.read_csv('sp500.csv')
    if sector:
        sp = sp[sp.Sector == sector]
    if symbols:
        return sp['Symbol']
    else:
        return sp


def get_data(*tickers, key, path='data_files', data=DEFAULT_DATA):
    """
    Downloads and stores as a CSV file prices and data for selected stocks
    """
    if not os.path.exists(f"{os.getcwd()}/{path}"):
        os.mkdir(path)
        print(f"Directory '{path}' created successfully :)")
    else:
        print(f"Directory '{path}' already exists ;)")


    downloaded = 0
    skipped = 0
    tickers_skipped = []

    client = EodHistoricalData(key)
    for ticker in tickers:
        try:
            print(f"Downloading... {ticker}")
            df = pd.DataFrame(client.get_prices_eod(ticker, from_=data))
            df.index = pd.DatetimeIndex(df.date)
            df.drop(columns=['date'], inplace=True)
            df.to_csv(f"{path}/{ticker}.csv")
            downloaded += 1
        except:
            print(f"{ticker} not found :( skipping...")
            skipped += 1
            tickers_skipped.append(ticker) 
        print("Downloaded Completed :)")
        print(f"Data downloaded for {downloaded} stocks")
        print(f"{skipped} tickers were skipped")
        if tickers_skipped:
            print("Tickers skipped ".center(30, "="))
            for ticker in tickers_skipped:
                print(ticker)


def get_closing_prices(folder= 'data_files', adj_close= False):
    """
    Return file with closing prices for selected stocks
    """
    files = [file for file in os.listdir(folder) if not file.startswith('0')]

    closes = pd.DataFrame()

    for file in files:
        if adj_close:
            df = pd.DataFrame(pd.read_csv(f"{folder}/{file}",
                            index_col= 'date')['adjusted_close'])
            df.rename(columns={'adjusted_close': file[:-4]}, inplace=True)    
        else:
            df = pd.DataFrame(pd.read_csv(f"{folder}/{file}",
                            index_col= 'date')['close'])
            df.rename(columns={'close': file[:-4]}, inplace=True)  

        if closes.empty:
            closes = df
        else: 
            closes = pd.concat([closes, df], axis= 1)
    closes.to_csv(f"{folder}/0-closes.csv")
    return closes          

def returns_from_closes(folder, filename):
    """
    returns instantaneous results for selected stocks
    """
    try: 
        data = pd.read_csv(f"{folder}/{filename}", index_col=['date'])

    except Exception as e:
        print(f"there was a problem: {e}")
    return np.log(data).diff().dropna()


def get_corr(data):
    """
    returns stocks correlation
    """
    return data.corr()


def plot_closes(closes, relative=False):
    """
    plot absolute  or relative closes for stocks    
    """
    if closes.endswith('.csv'):
        closes = pd.read_csv(closes, index_col=['date'])
    else:
        closes = pd.read_csv(closes, index_col=['date'])
    if relative:
        relative_change = closes / closes.iloc[0] 
        relative_change.plot()
        plt.axhline(0, c='r', ls='--')
        plt.grid(axis='y')
        plt.show()
    else:
        closes.plot()
        plt.grid(axis='y')
        plt.show()


def get_return_data(*tickers, date=DEFAULT_DATA, adj_close=False, key):
    """
    saves closes and returns results to excel file
    """
    client = EodHistoricalData(key)
    temp = pd.DataFrame()

    for ticker in tickers:
        try:
            if adj_close:
                temp[ticker] = pd.DataFrame(client.get_prices_eod(ticker,
                from_=date))['adjusted_close']
            else:
                temp[ticker] = pd.DataFrame(client.get_prices_eod(ticker,
                from_=date))['close']
        except Exception as e:
            print(f"{ticker} had a problem: {e}")
    data = temp
    data_instanteous = np.log(data).diff().dropna()
    data.pct_change()

    with pd.ExcelWriter('returns.xlsx', date_format='yyyy-mm-dd') as writer:
        data.to_excel(writer, sheet_name='closes')
        data_instanteous.to_excel(writer, sheet_name='returns')
        data_pct.to_excel(writer, sheet_name='pct change')

    print(f"Data retrieved and saved to returns.xlsx in {os.getcwd()}")
    return data, data_instanteous, data_pct


def plot_performance(folder):
    """
    returns figures containing relative performace of all stocks in folder
    """
    files = [file for file in os.listdir(folder) if not file.startswith('0')]
    fig, ax = plt.subplots(math.ceil(len(files)/ 4), 4, figsize=(16,16))
    count = 0
    for row in range(math.ceil(len(files)/ 4)):
        for column in range(4):
            try:
                data = pd.read_csv(f"{folder}/{files[count]}")['close']
                data = (data/data[0] -1) * 100
                ax[row,column].plot(data, label= files[count][:-4])
                ax[row,column].legend()
                ax[row,column].yaxis.set_major_formatter(mtick.PercentFormatter())
                ax[row,column].axhline(0, c='r', ls='--')
            except:
                pass
            count +=1
    plt.show()

""" Only possible to get the data using paid API
def screen_example(symbols, key):
     
    #Dataframe with current price, 52-week high and ratio of high to current price. 
    #Symbols is list-like 
    
    high = {}

    # Loop to request data for each symbol individually
    for ticker in symbols:
        try:
            # Making individual requests for each symbol
            call = f'https://eodhd.com/api/eod-last-day/{ticker}.US?api_token={key}&fmt=json'
            response = requests.get(call)
            print(f"Response status code for {ticker}: {response.status_code}")
            
            if response.status_code == 200:
                data = pd.DataFrame(response.json())
                if not data.empty:
                    # Assuming 'Technicals' contains 52-week high data
                    high[ticker] = data['Technicals']['52WeekHigh']
                else:
                    print(f"No data returned for {ticker}.")
            else:
                print(f"Error fetching data for {ticker}: {response.text}")

        except requests.exceptions.RequestException as e:
            print(f"Request failed for {ticker}: {e}")

    # Fetching the stock prices (kept the same as before)
    call = f'https://eodhd.com/api/eod-bulk-last-day/US?api_token={key}&fmt=json'
    try:
        response = requests.get(call)
        print(f"Response status code: {response.status_code}")
        if response.status_code == 200 and response.text:
            data = pd.DataFrame(response.json())
            data.reset_index(drop=True)
            mask = data.code.isin(symbols)
            prices = data[['code', 'close']][mask]
            high = pd.Series(high, name='high')
            prices = prices.merge(high, left_on='code', right_index=True)
            prices['ratio'] = prices['close'] / prices['high']
            return prices
        else:
            print("Failed to fetch price data.")
            return pd.DataFrame()

    except requests.exceptions.RequestException as e:
        print(f"Request failed for price data: {e}")
        return pd.DataFrame()  # Return an empty DataFrame in case of request failure

    data.reset_index(drop=True)
    
    client = EodHistoricalData(key)
    
    for ticker in symbols:
        try:
            high[ticker] = client.get_fundamental_equity(f"{ticker}.US")['Technicals']['52WeekHigh']
        except KeyError:
            print(f"52WeekHigh data not found for {ticker}. Skipping...")
            continue
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
    
    mask = data.code.isin(symbols)
    prices = data[['code', 'close']][mask]
    high = pd.Series(high, name='high')
    prices = prices.merge(high, left_on='code', right_index=True)
    prices['ratio'] = prices['close'] / prices['high']
    
    return prices
"""




def main():
    key = open('api_token.txt').read()
    #print(get_security_type(get_exchange_data(key)))
    #print(get_sp(symbols=True, sector='Information Technology, Health, Financials'))
    #healthCare = get_sp(symbols=True, sector='Health Care')
    #get_data(*'AAPL', 'MCD', 'NKE', 'AMZN', 'GOOG', key= key, path= 'test')
    #get_closing_prices(folder='test')
    #print(returns_from_closes('test', '0-closes.csv'))
    #print(get_corr(returns_from_closes('healthCare', '0-closes.csv')))
    #plot_closes('test/0-closes.csv', relative=True)
    #tickers = "AMZN GOOG MCD NKE".split()
    #returns = get_return_data(*tickers, key=key)
    #print(returns[0])
    #plot_performance('healthCare')
    #sp = get_sp()[:10]
    #print(screen_example(sp,key))




if __name__ == '__main__':
    main()