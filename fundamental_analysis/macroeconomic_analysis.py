from datetime import datetime

import config
import historical_data_collection.excel_helpers as excel
import pandas as pd
import os


def gross_national_product_price_index(date):
    return float(excel.read_entry_from_csv(config.MACRO_DATA_FILE_PATH, 'Yearly', 'GNP Price Index', date))


def cumulative_factors_helper(df, from_date, to_date):
    frm = excel.get_date_index(date=from_date, dates_values=df.index)
    to = excel.get_date_index(date=to_date, dates_values=df.index)
    sliced_df = df[to:] if frm == -1 else df[frm:to]
    cum_prod = (sliced_df + 1).cumprod() - 1
    return cum_prod[-1]


def risk_free_rate(date, freq: str = 'Yearly'):
    df = excel.read_df_from_csv(path='{}/{}.xlsx'.format(config.FACTORS_DIR_PATH, 'CAPM'), sheet_name=freq)['RF']
    date_index = excel.get_date_index(date, df.index)
    return df.iloc[date_index]


def risk_free_rates(from_date, to_date, freq: str = 'Yearly'):
    df = excel.read_df_from_csv(path='{}/{}.xlsx'.format(config.FACTORS_DIR_PATH, 'CAPM'), sheet_name=freq)['RF']
    frm = excel.get_date_index(date=from_date, dates_values=df.index)
    to = excel.get_date_index(date=to_date, dates_values=df.index)
    sliced_df = df[to:] if frm == -1 else df[frm:to]
    return sliced_df


def cumulative_risk_free_rate(from_date, to_date):
    df = excel.read_df_from_csv(path='{}/{}.xlsx'.format(config.FACTORS_DIR_PATH, 'CAPM'), sheet_name='Daily')['RF']
    return cumulative_factors_helper(df=df, from_date=from_date, to_date=to_date)


def market_premium(date, freq: str = 'Yearly'):
    df = excel.read_df_from_csv(path='{}/{}.xlsx'.format(config.FACTORS_DIR_PATH, 'CAPM'), sheet_name=freq)['Mkt-RF']
    date_index = excel.get_date_index(date, df.index)
    return df.iloc[date_index]


def cumulative_market_premium(from_date, to_date):
    df = excel.read_df_from_csv(path='{}/{}.xlsx'.format(config.FACTORS_DIR_PATH, 'CAPM'), sheet_name='Daily')['Mkt-RF']
    return cumulative_factors_helper(df=df, from_date=from_date, to_date=to_date)




def companies_in_industry(industry: str, date=datetime.now()):
    df = pd.read_excel(config.MARKET_INDICES_TOTAL_US_STOCK_MARKET, index_col=0)
    return df[df['Industry'] == industry].index


def companies_in_sector(sector: str, date=datetime.now()):
    df = pd.read_excel(config.MARKET_INDICES_TOTAL_US_STOCK_MARKET, index_col=0)
    return df[df['Sector'] == sector].index


def companies_in_location(location: str, date=datetime.now()):
    df = pd.read_excel(config.MARKET_INDICES_TOTAL_US_STOCK_MARKET, index_col=0)
    return df[df['Location'].str.contains(location)].index


def companies_in_exchange(exchange: str, date=datetime.now()):
    path = os.path.join(config.MARKET_EXCHANGES_DIR_PATH, '{}.txt'.format(exchange))
    df = pd.read_csv(filepath_or_buffer=path, sep='\t', header=0)
    return list(df['Symbol'])


def companies_in_index(market_index: str, date=datetime.now()):
    path = os.path.join(config.MARKET_INDICES_DIR_PATH, '{}-Stock-Tickers.csv'.format(market_index))
    df = pd.read_csv(path, parse_dates=True, index_col=0)
    idx = excel.get_date_index(date, df.columns)
    return list(df.iloc[:, idx])


def company_cik(ticker: str):
    df = pd.read_excel(config.MARKET_INDICES_TOTAL_US_STOCK_MARKET, index_col=0)
    return df['CIK'].loc[ticker]


def company_industry(ticker: str):
    df = pd.read_excel(config.MARKET_INDICES_TOTAL_US_STOCK_MARKET, index_col=0)
    return df['Industry'].loc[ticker]


def company_sector(ticker: str, type: str = 'GICS'):
    df = pd.read_excel(config.MARKET_INDICES_TOTAL_US_STOCK_MARKET, index_col=0)
    return df['{} Sector'.format(type)].loc[ticker]


def company_location(ticker: str):
    df = pd.read_excel(config.MARKET_INDICES_TOTAL_US_STOCK_MARKET, index_col=0)
    return df['Location'].loc[ticker]


if __name__ == '__main__':
    print(companies_in_index('S&P-500'))
