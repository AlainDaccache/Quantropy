import urllib
import unicodedata
import config
import pandas as pd
import requests
from bs4 import BeautifulSoup
import pickle
import os


def save_nasdaq():
    urls = ['ftp://ftp.nasdaqtrader.com/symboldirectory/nasdaqlisted.txt',
            'ftp://ftp.nasdaqtrader.com/symboldirectory/nasdaqtraded.txt']
    main_df = pd.DataFrame()
    for url in urls:
        path = os.path.join(config.ROOT_DIR, config.DATA_DIR_NAME, config.MARKET_TICKERS_DIR_NAME, 'NASDAQ_Listed.txt')
        urllib.request.urlretrieve(url, path)
        if main_df.empty:
            main_df = pd.read_csv(path, sep="|")[:-1]
        else:
            cur_df = pd.read_csv(path, sep="|")[:-1]
            main_df = pd.concat([main_df, cur_df], axis=0, ignore_index=True)
            main_df = main_df.drop_duplicates('Symbol').reset_index(drop=True)
            # main_df['feedback_id'].fillna(main_df['Symbol'])
            # main_df = main_df.drop_duplicates().reset_index(drop=True)
            # main_df.set_index(list(main_df)[0], inplace=True)
            main_df.set_index('Symbol', inplace=True)
            main_df = main_df[['Security Name', 'Financial Status', 'ETF']]
            main_df.sort_index(inplace=True)
    with open(os.path.join(config.ROOT_DIR, config.DATA_DIR_NAME, config.MARKET_TICKERS_DIR_NAME, "nasdaq_df.pickle"),
              "wb") as f:
        pickle.dump(main_df, f)
    os.remove(os.path.join(config.ROOT_DIR, config.DATA_DIR_NAME, config.MARKET_TICKERS_DIR_NAME, 'NASDAQ_Listed.txt'))
    print(main_df.head())
    return


def save_dow_jones_tickers():
    url = 'https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average'
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'lxml')
    table = soup.find('table', {'class': 'wikitable sortable'})
    tickers = []
    for row in table.findAll('tr')[1:]:
        ticker = unicodedata.normalize("NFKD", row.findAll('td')[2].text).split(': ')[-1]
        ticker = ticker.strip()
        tickers.append(ticker)

    with open(os.path.join(config.ROOT_DIR, config.DATA_DIR_NAME, config.MARKET_TICKERS_DIR_NAME,
                           "djia30_tickers.pickle"), "wb") as f:
        pickle.dump(tickers, f)

    return tickers


def save_sp500_tickers():
    url = 'http://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'lxml')
    table = soup.find('table', {'class': 'wikitable sortable'})
    tickers = []
    for row in table.findAll('tr')[1:]:
        ticker = row.findAll('td')[0].text
        ticker = ticker.strip()
        tickers.append(ticker)

    with open(
            os.path.join(config.ROOT_DIR, config.DATA_DIR_NAME, config.MARKET_TICKERS_DIR_NAME, "sp500_tickers.pickle"),
            "wb") as f:
        pickle.dump(tickers, f)

    return tickers


def save_russell_3000_tickers():
    url = "http://www.beatthemarketanalyzer.com/blog/wp-content/uploads/2016/10/Russell-3000-Stock-Tickers-List.xlsx"
    path = os.path.join(config.ROOT_DIR, config.DATA_DIR_NAME, config.MARKET_TICKERS_DIR_NAME,
                        'Russell-3000-Stock-Tickers-List.xlsx')
    urllib.request.urlretrieve(url, path)
    df = pd.read_excel(pd.ExcelFile(path), index_col=0, skiprows=3)
    print(df.to_string())
    tickers = list(df.index)
    with open(os.path.join(config.ROOT_DIR, config.DATA_DIR_NAME, config.MARKET_TICKERS_DIR_NAME,
                           "russell3000_tickers.pickle"), "wb") as f:
        pickle.dump(tickers, f)
    os.remove(path)
