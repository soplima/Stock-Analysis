from eod import EodHistoricalData
import datetime as dt
import json
import os
import matplotlib.pyplot as plt
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



def main():
    key = open('api_token.txt').read()
    #print(get_security_type(get_exchange_data(key)))
    #print(get_sp(symbols=True, sector='Information Technology, Health, Financials'))
    #healthCare = get_sp(symbols=True, sector='Health Care')
    #get_data(*'AAPL', 'MCD', 'NKE', 'AMZN', 'GOOG', key= key, path= 'test')
    #get_closing_prices(folder='test')
    #print(returns_from_closes('test', '0-closes.csv'))
    #print(get_corr(returns_from_closes('healthCare', '0-closes.csv')))
    plot_closes('test/0-closes.csv')

if __name__ == '__main__':
    main()