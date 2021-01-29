import os

from pymongo import MongoClient
from mongoengine import *
from datetime import datetime

from data.database import object_model
from historical_data_collection import data_preparation_helpers
from macroeconomic_analysis.macroeconomic_analysis import companies_in_index
import pickle
import config


def get_atlas_db_url(username, password, dbname):
    return f"mongodb+srv://{username}:{password}@cluster0.ptrie.mongodb.net/{dbname}?retryWrites=true&w=majority"


def connect_to_mongo_atlas(atlas_url: str):
    client = MongoClient(atlas_url)
    return client.get_database()


def connect_to_mongo_engine(atlas_url: str):
    return connect(host=atlas_url)


def populate_db_company_info(tickers=None):
    """

    :param tickers: if None, then populate all
    :return:
    """
    with open(config.TOTAL_MARKET_PATH, 'rb') as handle:
        company_classifications = pickle.load(handle)

    for ticker, company in company_classifications.iterrows():
        if tickers is not None and ticker not in tickers:
            continue
        object_model.Company(name=company['Company Name'], ticker=ticker, cik=company['CIK'],
                             sic_sector=company['SIC Sector'], sic_industry=company['SIC Industry'],
                             gics_sector=company['GICS Sector'],
                             location=company['Location'], exchange=company['Exchange']).save()


def populate_db_financial_statements(tickers, from_date=None, to_date=None, statements=None, refresh=False):
    """

    :param tickers:
    :param from_date: by default, all
    :param to_date: by default, all
    :param statements: by default, all
    :param refresh: re-scrape the data
    :return:
    """
    for ticker in tickers:
        path = '{}/{}.pkl'.format(config.FINANCIAL_STATEMENTS_DIR_PATH_PICKLE_UNFLATTENED, ticker)

        with open(path, 'rb') as handle:
            filings_dictio = pickle.load(handle)

        multiple_pickle_path = f'{config.FINANCIAL_STATEMENTS_DIR_PATH_PICKLE}/multiples.pkl'
        with open(multiple_pickle_path, 'rb') as handle:
            multiple = pickle.load(handle)[ticker]

        for filing_period, filing_dates in filings_dictio.items():
            for filing_date, statement_dictio in filing_dates.items():
                date_formatted = datetime.strptime(filing_date, '%Y-%m-%d')
                for statement, keys_dict in statement_dictio.items():

                    # TODO hot fix, find better way
                    flattened = data_preparation_helpers.flatten_dict(keys_dict)
                    multiplied = {k: v * multiple for k, v in flattened.items()}
                    keys_dict = data_preparation_helpers.unflatten(multiplied)

                    if statement == 'BalanceSheet':  # test
                        filing = object_model.Filing(company=ticker, date=date_formatted, period=filing_period,
                                                     BalanceSheet=keys_dict)
                        filing.save()


def populate_db_asset_prices(tickers=None, from_date=None, to_date=None):
    if tickers is None:
        tickers = next(os.walk(config.STOCK_PRICES_DIR_PATH))[2]
        tickers = [ticker.strip('.pkl') for ticker in tickers]

    for ticker in tickers:
        asset_prices_path = f'{config.STOCK_PRICES_DIR_PATH}/{ticker}.pkl'

        with open(asset_prices_path, 'rb') as handle:
            df = pickle.load(handle)

        from_ = 0 if from_date is None else data_preparation_helpers.get_date_index(date=from_date,
                                                                                    dates_values=df.index)

        to_ = -1 if to_date is None else data_preparation_helpers.get_date_index(date=to_date, dates_values=df.index)
        df = df.iloc[from_:to_, ]

        df_conv = {key: [{'date': date, 'price': price} for date, price in zip(df.index, df[key])]
                   for key in df.columns}

        object_model.AssetPrices(company=ticker, open=df_conv['Open'], high=df_conv['High'], low=df_conv['Low'],
                                 close=df_conv['Close'], adj_close=df_conv['Adj Close']).save()


def populate_db_risk_factors(from_date, to_date):
    for factor_model in os.listdir(path=config.FACTORS_DIR_PATH):
        with open(f'{config.FACTORS_DIR_PATH}/{factor_model}.pkl', 'rb') as handle:
            df = pickle.load(handle)

        from_ = 0 if from_date is None else data_preparation_helpers.get_date_index(date=from_date,
                                                                                    dates_values=df.index)

        to_ = -1 if to_date is None else data_preparation_helpers.get_date_index(date=to_date, dates_values=df.index)
        df = df.iloc[from_:to_, ]
        df_conv = {key: [{'date': date, 'price': price} for date, price in zip(df.index, df[key])]
                   for key in df.columns}

        risk_factors = [object_model.RiskFactor(name=key, series=df[key]) for key, value in df_conv.items()]
        object_model.RiskFactorModel(name=factor_model, risk_factors=risk_factors).save()


def populate_db_routine(tickers=None, from_date=None, to_date=None, reset_db=True,
                        populate_company_info=True, populate_financial_statements=True,
                        populate_asset_prices=True, populate_risk_factors=True):
    atlas_url = get_atlas_db_url(username='AlainDaccache', password='qwerty98', dbname='matilda-db')
    db = connect_to_mongo_engine(atlas_url)
    if reset_db:
        db.drop_database('matilda-db')
        connect_to_mongo_engine(atlas_url)
    if populate_company_info:
        populate_db_company_info(tickers)
    if populate_financial_statements:
        populate_db_financial_statements(tickers, from_date, to_date)
    if populate_asset_prices:
        populate_db_asset_prices(tickers, from_date, to_date)
    if populate_risk_factors:
        populate_db_risk_factors(from_date, to_date)


if __name__ == '__main__':
    # populate_db_routine(tickers=companies_in_index(config.MarketIndices.DOW_JONES))
    atlas_url = get_atlas_db_url(username='AlainDaccache', password='qwerty98', dbname='matilda-db')
    db = connect_to_mongo_engine(atlas_url)
    db.drop_database('matilda-db')
    connect_to_mongo_engine(atlas_url)
    populate_db_asset_prices(from_date=datetime(2000, 1, 1), to_date=datetime.now())
