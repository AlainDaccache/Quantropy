import urllib
from datetime import datetime
import unicodedata
import config
import pandas as pd
import requests
from bs4 import BeautifulSoup
import os


def store_to_excel(file_path, tickers):
    current_date = datetime.now().strftime('%Y-%m-%d')
    if not os.path.exists(file_path):
        df = pd.DataFrame.from_dict({current_date: tickers}, orient='index')
        df.to_excel(file_path)
    else:
        df = pd.read_excel(file_path, index_col=0)
        df[current_date] = tickers
        df.to_excel(file_path)


def save_current_nasdaq():
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
            main_df = main_df[main_df['ETF'] == 'N']  # remove etfs
            main_df = main_df.drop_duplicates('Symbol').reset_index(drop=True)
            main_df.set_index('Symbol', inplace=True)
            main_df.sort_index(inplace=True)
            main_df = main_df[~main_df.index.str.contains('\$')]  # this is to remove derived asset classes
        os.remove(path)
    store_to_excel(file_path=os.path.join(config.MARKET_TICKERS_DIR_PATH, 'Nasdaq-Stocks-Tickers.xlsx'),
                   tickers=main_df.index)

    return main_df.index


def save_current_dow_jones_tickers():
    url = 'https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average'
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'lxml')
    table = soup.find('table', {'class': 'wikitable sortable'})
    tickers = []
    for row in table.findAll('tr')[1:]:
        ticker = unicodedata.normalize("NFKD", row.findAll('td')[1].text).split(': ')[-1]
        ticker = ticker.strip()
        tickers.append(ticker)

    store_to_excel(file_path=os.path.join(config.MARKET_TICKERS_DIR_PATH, 'Dow-Jones-Stock-Tickers.xlsx'),
                   tickers=tickers)

    return tickers


def save_current_sp500_tickers():
    url = 'http://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'lxml')
    table = soup.find('table', {'class': 'wikitable sortable'})
    tickers = []
    for row in table.findAll('tr')[1:]:
        ticker = row.findAll('td')[0].text
        ticker = ticker.strip()
        tickers.append(ticker)
    store_to_excel(file_path=os.path.join(config.MARKET_TICKERS_DIR_PATH, 'S&P-500-Stock-Tickers.xlsx'),
                   tickers=tickers)
    return tickers


def url_to_excel_clean_to_df(url: str, output_name: str, skiprows: int = 0):
    path = os.path.join(config.MARKET_TICKERS_DIR_PATH, output_name)
    urllib.request.urlretrieve(url, path)
    df = pd.read_excel(pd.ExcelFile(path), index_col=0, skiprows=skiprows, warn_bad_lines=False, error_bad_lines=False)
    os.remove(path)
    print(df.to_string())
    tickers = list(df.index)
    file_path = os.path.join(config.MARKET_TICKERS_DIR_PATH, output_name)
    store_to_excel(file_path=file_path, tickers=tickers)
    return tickers


def save_current_russell_3000_tickers():
    return url_to_excel_clean_to_df(
        url="http://www.beatthemarketanalyzer.com/blog/wp-content/uploads/2016/10/Russell-3000-Stock-Tickers-List.xlsx",
        output_name='Russell-3000-Stock-Tickers.xlsx',
        skiprows=3)


def save_total_us_stock_market_tickers():
    return url_to_excel_clean_to_df(
        url='https://www.ishares.com/us/products/239724/ishares-core-sp-total-us-stock-market-etf/1521942788811.ajax?fileType=xls&fileName=iShares-Core-SP-Total-US-Stock-Market-ETF_fund&dataType=fund',
        output_name='US-Stock-Market-Tickers.xls',
        skiprows=7)


def historical_sp500_ticker():
    pass


if __name__ == '__main__':
    # save_current_sp500_tickers()
    save_current_dow_jones_tickers()
    # save_current_nasdaq()
    # save_current_russell_3000_tickers()
    # save_total_us_stock_market_tickers()
