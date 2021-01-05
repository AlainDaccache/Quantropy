from datetime import datetime, timedelta

import config
import historical_data_collection.data_preparation_helpers as excel
import pandas as pd
import os
import numpy as np

from portfolio_management.Portfolio import TimeDataFrame


def gross_national_product_price_index(date):
    return float(excel.read_entry_from_csv(config.MACRO_DATA_FILE_PATH, 'Yearly', 'GNP Price Index', date))


def risk_free_rates(to_date: datetime, from_date=None, frequency: str = 'Yearly'):
    df = pd.read_pickle('{}/pickle/Fama-French 3 Factors Data.pkl'.format(config.FACTORS_DIR_PATH))['RF']
    time_df = TimeDataFrame(df)
    time_df.slice_dataframe(to_date=to_date, from_date=from_date, inplace=True)
    time_df.set_frequency(frequency=frequency, inplace=True)
    return time_df.df_returns


def market_premiums(to_date: datetime, from_date: datetime = None, lookback=None, frequency: str = 'Yearly'):
    df = excel.read_df_from_csv(path='{}/Fama-French Factors Data.xlsx'.format(config.FACTORS_DIR_PATH),
                                sheet_name='Daily')['MKT-RF']
    return excel.slice_resample_merge_returns(returns=[df], lookback=lookback, from_date=from_date, to_date=to_date,
                                              frequency=frequency)


def companies_in_industry(industry, date=datetime.now()):
    if isinstance(industry, config.SIC_Sectors):
        entry = 'SIC Industry'
    elif isinstance(industry, config.GICS_Sectors):
        entry = 'GICS Industry'
    else:
        raise Exception('Ensure arg for industry is an instance of config.SIC_Sectors or config.GICS_Sectorsll')

    df = pd.read_pickle(config.TOTAL_MARKET_PATH)

    return df[df[entry] == industry.value].index


def companies_in_sector(sector, date=datetime.now()):
    if isinstance(sector, config.SIC_Sectors):
        entry = 'SIC Sector'
    elif isinstance(sector, config.GICS_Sectors):
        entry = 'GICS Sector'
    else:
        raise Exception

    df = pd.read_pickle(config.TOTAL_MARKET_PATH)
    return df[df[entry] == sector.value].index


def companies_in_location(location: config.Regions, date=datetime.now()):
    if not isinstance(location, config.Regions):
        raise Exception('Ensure arg for location is an instance of config.Regions')
    df = pd.read_pickle(config.TOTAL_MARKET_PATH)
    return df[df['Location'].str.contains(location)].index


def companies_in_exchange(exchange: config.Exchanges, date=datetime.now()):
    if not isinstance(exchange, config.Exchanges):
        raise Exception('Ensure arg for exchange is an instance of config.Exchanges')
    path = os.path.join(config.MARKET_EXCHANGES_DIR_PATH, '{}.txt'.format(exchange.value))
    df = pd.read_csv(filepath_or_buffer=path, sep='\t', header=0)
    return list(df['Symbol'])


def companies_in_index(market_index: config.MarketIndices, date=datetime.now()):
    path = os.path.join(config.MARKET_INDICES_DIR_PATH, '{}-Historical-Constituents.pkl'.format(market_index.value))
    df = pd.read_pickle(path)
    idx = excel.get_date_index(date, df.index)
    return list(df.iloc[idx, :])


def company_cik(ticker: str):
    df = pd.read_pickle(config.TOTAL_MARKET_PATH)
    return df['CIK'].loc[ticker]


def company_industry(ticker: str, type: str = 'SIC', date: datetime = datetime.now()):
    '''

    :param ticker:
    :param type: SIC, GICS
    :return:
    '''
    df = pd.read_pickle(config.TOTAL_MARKET_PATH)
    return df['{} Industry'.format(type)].loc[ticker]


def company_sector(ticker: str, type: str = 'GICS', date: datetime = datetime.now()):
    '''

    :param ticker:
    :param type: SIC, GICS
    :return:
    '''
    df = pd.read_pickle(config.TOTAL_MARKET_PATH)
    return df['{} Sector'.format(type)].loc[ticker]


def company_location(ticker: str, date: datetime = datetime.now()):
    df = pd.read_pickle(config.TOTAL_MARKET_PATH)
    return df['Location'].loc[ticker]


def company_index(ticker: str, date: datetime = datetime.now()):
    df = pd.read_pickle(config.TOTAL_MARKET_PATH)
    return df['Location'].loc[ticker]


def company_exchange(ticker: str):
    df = pd.read_pickle(config.TOTAL_MARKET_PATH)
    return df['Location'].loc[ticker]


if __name__ == '__main__':
    print(companies_in_index(config.MarketIndices.SP_500))
