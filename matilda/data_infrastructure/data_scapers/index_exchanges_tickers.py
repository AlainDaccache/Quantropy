import unicodedata
import requests
from matilda import config
import pandas as pd
import os
import urllib
from bs4 import BeautifulSoup
from datetime import datetime


def store_to_csv(file_path, tickers):
    current_date = datetime.now().strftime('%Y-%m-%d')
    if not os.path.exists(file_path):
        df = pd.DataFrame.from_dict({current_date: tickers})
        df.to_csv(file_path)
    else:
        df = pd.read_csv(file_path, index_col=0)
        df[current_date] = tickers
        df = df.T
        df.to_csv(file_path)


def save_current_nasdaq():
    urls = ['ftp://ftp.nasdaqtrader.com/symboldirectory/nasdaqlisted.txt',
            'ftp://ftp.nasdaqtrader.com/symboldirectory/nasdaqtraded.txt']
    main_df = pd.DataFrame()
    for url in urls:
        path = os.path.join(config.MARKET_EXCHANGES_DIR_PATH, 'NASDAQ_Listed.txt')
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

    df = pd.DataFrame.from_dict({datetime.now(): main_df.index})
    pd.DataFrame.to_pickle(df, path=os.path.join(config.MARKET_INDICES_DIR_PATH, 'NASDAQ-Historical-Constituents.pkl'))

    return main_df.index


def save_historical_dow_jones_tickers(save_pickle=True):
    url = 'https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average'
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'lxml')
    table = soup.find('table', {'class': 'wikitable sortable'})
    tickers = []
    for row in table.findAll('tr')[1:]:
        ticker = unicodedata.normalize("NFKD", row.findAll('td')[1].text).split(': ')[-1]
        ticker = ticker.strip()
        tickers.append(ticker)

    if save_pickle:
        df = pd.DataFrame.from_dict({datetime.today(): tickers}, orient='index')
        pd.DataFrame.to_pickle(df, path=os.path.join(config.DATA_DIR_PATH, 'test_data',
                                                     'Dow-Jones-Historical-Constituents.pkl'))

    return {datetime.today(): tickers}


def save_historical_sp500_tickers(save_pickle=True):
    resp = requests.get('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    soup = BeautifulSoup(resp.text, 'lxml')
    current_tickers_table, historical_tickers_table = soup.findAll('table', {'class': 'wikitable sortable'})

    current_tickers = [row.findAll('td')[0].text.strip() for row in current_tickers_table.findAll('tr')[1:]]

    historical_changes_dictio = {}
    for row in historical_tickers_table.findAll('tr')[2:]:
        row_data = row.findAll('td')
        date = datetime.strptime(row_data[0].text.rstrip(), '%B %d, %Y')
        ticker_added, ticker_removed = row_data[1].text.rstrip(), row_data[3].text.rstrip()
        if date not in historical_changes_dictio.keys():
            historical_changes_dictio[date] = {'Added': [], 'Removed': []}
        historical_changes_dictio[date]['Added'].append(ticker_added)
        historical_changes_dictio[date]['Removed'].append(ticker_removed)

    cumulative_dictio = {}

    # TODO Not perfectly accurate, as ticker names can change with time (i.e. SAIC = SAI)
    for date, added_removed in historical_changes_dictio.items():

        cumulative_dictio[date] = current_tickers
        for added in added_removed['Added']:
            if len(added) > 0:  # before this date, the ticker wasn't there
                try:
                    current_tickers.remove(added)
                except:
                    print(f'Manual check needed for added ticker {added} on {date}')
        for removed in added_removed['Removed']:
            if len(removed) > 0:  # before this date, the ticker was there
                current_tickers.append(removed)

    if save_pickle:
        cumulative_df = pd.DataFrame.from_dict(cumulative_dictio, orient='index')
        pd.DataFrame.to_pickle(cumulative_df,
                               path=os.path.join(config.MARKET_INDICES_DIR_PATH, 'S&P-500-Historical-Constituents.pkl'))
    return cumulative_dictio


def url_to_pickle_clean_to_df(url: str, output_name: str, skiprows: int = 0):
    path = os.path.join(config.MARKET_INDICES_DIR_PATH, output_name)
    urllib.request.urlretrieve(url, path)
    try:
        df = pd.read_excel(pd.ExcelFile(path), index_col=0, skiprows=skiprows)
    except:
        df = pd.read_html(path, index_col=0, skiprows=skiprows)
    os.remove(path)
    # print(df.to_string())
    tickers = list(df.index)
    file_path = os.path.join(config.MARKET_INDICES_DIR_PATH, output_name)
    cumulative_df = pd.DataFrame.from_dict({datetime.now(): tickers}, orient='index')
    pd.DataFrame.to_pickle(cumulative_df, path=file_path)
    return tickers


def save_current_russell_3000_tickers():
    return url_to_pickle_clean_to_df(
        url="http://www.beatthemarketanalyzer.com/blog/wp-content/uploads/2016/10/Russell-3000-Stock-Tickers-List.xlsx",
        output_name='Russell-3000-Stock-Tickers.csv',
        skiprows=3)


def save_total_us_stock_market_tickers():
    return url_to_pickle_clean_to_df(
        url='https://www.ishares.com/us/products/239724/ishares-core-sp-total-us-stock-market-etf/1521942788811.ajax?fileType=xls&fileName=iShares-Core-SP-Total-US-Stock-Market-ETF_fund&dataType=fund',
        output_name='US-Stock-Market-Tickers.xls', skiprows=7)


# if __name__ == '__main__':
    # save_current_dow_jones_tickers()
    # save_current_nasdaq()
    # save_current_russell_3000_tickers()
    # save_total_us_stock_market_tickers()
    # save_historical_sp500_tickers()
