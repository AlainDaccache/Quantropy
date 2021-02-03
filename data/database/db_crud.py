import os
from collections import defaultdict
from pprint import pprint

from numpy import mean
from pymongo import MongoClient
from mongoengine import *
from datetime import datetime, timedelta

from data.database import object_model
from historical_data_collection import data_preparation_helpers
from macroeconomic_analysis.macroeconomic_analysis import companies_in_index
import pickle
import config

'''
0. Connect to MongoDB Atlas and Mongo Engine using our URL
'''


def get_atlas_db_url(username, password, dbname):
    return f"mongodb+srv://{username}:{password}@cluster0.ptrie.mongodb.net/{dbname}?retryWrites=true&w=majority&" \
           f"ssl=true"


def connect_to_mongo_atlas(atlas_url: str):
    client = MongoClient(atlas_url)
    return client.get_database()


def connect_to_mongo_engine(atlas_url: str):
    return connect(host=atlas_url)


'''
I. `Create` Routines for Company Info, Financial Statements, Asset Prices, Risk Factors, Macroeconomic Indicators
'''


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
                    unflattened = data_preparation_helpers.unflatten(multiplied)

                    def reformat_str(str_):
                        return str_.replace('-', ' ').replace(',', '').replace('(', '').replace(')',
                                                                                                '').title().strip().replace(
                            ' ', '')

                    statement_dictio[statement] = {reformat_str(k): v if not isinstance(v, dict)
                    else {reformat_str(kk): vv if not isinstance(vv, dict) else {
                        reformat_str(kkk): vvv if not isinstance(vvv, dict) else {
                            reformat_str(kkkk): vvvv
                            for kkkk, vvvv in vvv.items()} for kkk, vvv in vv.items()}
                          for kk, vv in v.items()} for k, v in unflattened.items()}

                filing = object_model.Filing(company=ticker, date=date_formatted, period=filing_period,
                                             BalanceSheet=statement_dictio['Balance Sheet'],
                                             IncomeStatement=statement_dictio['Income Statement'],
                                             CashFlowStatement=statement_dictio['Cash Flow Statement'])
                filing.save()


def db_time_series_helper(file_path, from_date=None, to_date=None):
    with open(file_path, 'rb') as handle:
        df = pickle.load(handle)

    from_ = 0 if from_date is None else data_preparation_helpers.get_date_index(date=from_date,
                                                                                dates_values=df.index)

    to_ = -1 if to_date is None else data_preparation_helpers.get_date_index(date=to_date, dates_values=df.index)
    df = df.iloc[from_:to_, ]
    df_conv = {key: [{'date': date, 'price': price} for date, price in zip(df.index, df[key])]
               for key in df.columns}
    return df_conv


def populate_db_asset_prices(tickers=None, from_date=None, to_date=None):
    if tickers is None:
        tickers = next(os.walk(config.STOCK_PRICES_DIR_PATH))[2]
        tickers = [ticker.strip('.pkl') for ticker in tickers]

    for ticker in tickers:
        df_conv = db_time_series_helper(file_path=f'{config.STOCK_PRICES_DIR_PATH}/{ticker}.pkl',
                                        from_date=from_date, to_date=to_date)

        object_model.AssetPrices(company=ticker, open=df_conv['Open'], high=df_conv['High'], low=df_conv['Low'],
                                 close=df_conv['Close'], adj_close=df_conv['Adj Close']).save()


def populate_db_risk_factors(from_date=None, to_date=None):
    dir_path = f'{config.FACTORS_DIR_PATH}/pickle/'
    for factor_model in os.listdir(path=dir_path):
        df_conv = db_time_series_helper(file_path=f'{dir_path}/{factor_model}', from_date=from_date, to_date=to_date)

        risk_factors = [object_model.RiskFactor(name=key, series=df_conv[key]) for key, value in df_conv.items()]
        object_model.RiskFactorModel(name=factor_model.replace('.pkl', ''), risk_factors=risk_factors).save()


def populate_db_routine(db_username, db_password, db_name,
                        tickers=None, from_date=None, to_date=None, reset_db=False,
                        populate_company_info=True, populate_financial_statements=True,
                        populate_asset_prices=True, populate_risk_factors=True):
    atlas_url = get_atlas_db_url(username=db_username, password=db_password, dbname=db_name)
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


'''
II. `Read` routines
'''


def read_financial_statement_entry(stock, financial_statement: str, entry_name: list, period: str,
                                   date=None, lookback_period: timedelta = timedelta(days=0)):
    """
    Read an entry from a financial statement. By default, we read the most recent position for the balance sheet,
    and the trailing twelve months for the income statement and cash flow statement.

    :param financial_statement: 'BalanceSheet', 'IncomeStatement', 'CashFlowStatement'
    :param stock:
    :param entry_name:
    :param date:
    :param lookback_period:
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months
    :return:

    """

    if date is None:
        date = datetime.now()

    if not isinstance(date, list):
        date = [date]

    if not isinstance(stock, list):
        stock = [stock]

    date.sort()  # for peace of mind

    filings = object_model.Filing.objects(company__in=object_model.Company.objects(ticker__in=stock),
                                          date__gte=date[0] - timedelta(days=100) if period == 'Q'
                                          else date[0] - timedelta(days=400),
                                          date__lte=date[-1], period='Yearly' if period == 'FY' else 'Quarterly')

    # .as_pymongo()  # .only(financial_statement).as_pymongo()[financial_statement]
    #     pipeline = [{'$sort': {'date': 1}},
    #                 {'$group': {
    #                     '_id': '$company',
    #                     'date': {'$last': '$date'},
    #                 }}]
    # agg = filings.aggregate(*pipeline)
    # for a in agg:
    #     print(a)

    # TODO This is noob. Should try aggregation https://stackoverflow.com/questions/25151042/moving-averages-with-mongodbs-aggregation-framework

    output = defaultdict(dict)
    for date_ in date:
        for stock_ in stock:

            # get the closest filing from this date for this stock's filings
            filings_for_stock = filings.filter(company=stock_).order_by('date').as_pymongo()
            # logic for 'while the next filing has a date less than the date we want, keep iterating'
            # so we stop when the next filing has a greater date, so we should stop at that current filing.
            for idx, filing in enumerate(filings_for_stock):
                if idx + 1 < len(filings_for_stock) and filings_for_stock[idx + 1]['date'] < date_:
                    continue

                # now can get corresponding entry
                def get_entry(filing_):
                    entry = filing_[financial_statement]
                    for e in entry_name:
                        entry = entry[e]
                    return entry

                if period in ['Q', 'FY']:
                    output[date_][stock_] = get_entry(filing_=filing)

                elif period in ['TTM', 'YTD']:
                    entries = []
                    for i in range(4):
                        filing = filings_for_stock[idx - i]
                        if period == 'YTD' and filing['date'] < datetime(date_.year, 1, 1):
                            break
                        entries.append(get_entry(filing_=filing))

                    if financial_statement == 'BalanceSheet':  # do average since it's a statement of position
                        output[date_][stock_] = sum(entries)

                    elif financial_statement in ['IncomeStatement', 'CashFlowStatement']:
                        output[date_][stock_] = mean(entries)

                    else:
                        raise Exception('Please enter a valid `financial_statement`')

                else:
                    raise Exception('Please enter a valid `period`')

                break

    return dict(output)


'''
III. `Update` routines
'''

'''
IV. `Delete` routines
'''

if __name__ == '__main__':
    # populate_db_routine(db_username='AlainDaccache', db_password='qwerty98', db_name='matilda-db',
    #                     tickers=companies_in_index(config.MarketIndices.DOW_JONES)[:5],
    #                     from_date=datetime(2000, 1, 1), reset_db=True)

    atlas_url = get_atlas_db_url(username='AlainDaccache', password='qwerty98', dbname='matilda-db')
    db = connect_to_mongo_engine(atlas_url)
    pprint(read_financial_statement_entry(stock=companies_in_index(config.MarketIndices.DOW_JONES)[:5],
                                          financial_statement='BalanceSheet',
                                          period='TTM', date=[datetime(2016, 1, 1), datetime.now()],
                                          entry_name=['Assets', 'CurrentAssets', 'TotalCurrentAssets']))
