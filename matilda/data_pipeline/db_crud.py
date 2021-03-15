import os
import pickle

import typing

from matilda import config
import pandas as pd

from collections import defaultdict
from numpy import mean
from pymongo import MongoClient
from mongoengine import *
from datetime import datetime, timedelta

from matilda.data_pipeline.data_scapers.company_classification import scrape_company_classification
from matilda.data_pipeline.data_scapers.financial_statements_scraper.macrotrend_scraper import scrape_macrotrend
from matilda.data_pipeline.data_scapers.index_exchanges_tickers import save_historical_dow_jones_tickers, \
    save_historical_sp500_tickers
from matilda.data_pipeline import object_model, data_preparation_helpers
from matilda.data_pipeline.data_scapers.stock_prices_scraper import YahooFinance

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
    if not os.path.exists(config.TOTAL_MARKET_PATH):
        scrape_company_classification(tickers=tickers)

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

        if not os.path.exists(path):
            scrape_macrotrend(tickers=[ticker])

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


def db_time_series_helper(df, from_date=None, to_date=None):
    """

    :param data: data can be a path or a dataframe
    :param from_date:
    :param to_date:
    :return:
    """

    from_ = 0 if from_date is None else data_preparation_helpers.get_date_index(date=from_date,
                                                                                dates_values=df.index)

    to_ = -1 if to_date is None else data_preparation_helpers.get_date_index(date=to_date, dates_values=df.index)
    df = df.iloc[from_:to_, ]
    df_conv = {key: [{'date': date, 'price': price} for date, price in zip(df.index, df[key])]
               for key in df.columns}
    return df_conv


def populate_db_asset_prices(tickers: typing.List = None, from_date: datetime = None, to_date: datetime = None):
    if tickers is None:  # takes all stocks currently in stock prices directory
        tickers = next(os.walk(config.STOCK_PRICES_DIR_PATH))[2]
        tickers = [ticker.strip('.pkl') for ticker in tickers]

    if not isinstance(tickers, list):
        tickers = [tickers]

    for ticker in tickers:
        path = f'{config.STOCK_PRICES_DIR_PATH}/{ticker}.pkl'
        if not os.path.exists(path):
            data = YahooFinance(ticker=ticker, from_date=from_date, to_date=to_date).convert_format('pandas')
        else:
            with open(path, 'rb') as handle:
                data = pickle.load(handle)

        df_conv = db_time_series_helper(df=data, from_date=from_date, to_date=to_date)

        object_model.AssetPrices(company=ticker, open=df_conv['Open'], high=df_conv['High'], low=df_conv['Low'],
                                 close=df_conv['Close'], volume=df_conv['Volume']).save()


def populate_db_risk_factors(from_date=None, to_date=None):
    dir_path = f'{config.FACTORS_DIR_PATH}/pickle/'
    scrape_Fama_French_factors()
    scrape_AQR_factors()
    for factor_model in os.listdir(path=dir_path):
        path = f'{dir_path}/{factor_model}'
        with open(path, 'rb') as handle:
            df = pickle.load(handle)
        df_conv = db_time_series_helper(df=df, from_date=from_date, to_date=to_date)

        risk_factors = [object_model.RiskFactor(name=key, series=df_conv[key]) for key, value in df_conv.items()]
        object_model.RiskFactorModel(name=factor_model.replace('.pkl', ''), risk_factors=risk_factors).save()


def populate_db_routine(db_name,
                        db_username=config.ATLAS_DB_USERNAME, db_password=config.ATLAS_DB_PASSWORD,
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


def populate_indices(from_file=False):
    for (name, path, fun) in [('Dow Jones', 'Dow-Jones-Historical-Constituents', save_historical_dow_jones_tickers),
                              ('S&P 500', 'S&P-500-Historical-Constituents', save_historical_sp500_tickers)]:
        if from_file:
            with open(os.path.join(config.DATA_DIR_PATH, path), 'rb') as handle:
                dictio = pickle.load(handle)

        else:
            dictio = fun(save_pickle=False)

        output = [{'date': date, 'companies': companies} for date, companies in dictio.items()]
        object_model.Index(name=name, evolution=output).save()


'''
II. `Read` routines
'''


def format_input(stock, date):
    if date is None:
        date = datetime.now()
    if not (isinstance(date, list) or isinstance(date, tuple)):
        date = [date]
    if not isinstance(stock, list):
        stock = [stock]
    date.sort()  # for peace of mind
    return stock, date


def format_output(output: dict):
    output = pd.DataFrame.from_dict(output, orient='index')
    if len(output) == 1:
        if len(output.columns) > 1:  # one date, many stocks
            return output.iloc[0, :]
        return float(output.values[0])  # one date, one stock
    if len(output.columns) == 1:
        return output.iloc[:, 0]  # many dates, one stock
    return output  # many dates, many stocks


def read_financial_statement_entry(stock, financial_statement: str, entry_name: list, period: str,
                                   date=None, lookback_period: timedelta = timedelta(days=0)):
    # TODO also try multiple entries (allow entry_name to be list of list)
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

    stock, date = format_input(stock, date)
    filings = object_model.Filing.objects(company__in=object_model.Company.objects(ticker__in=stock),
                                          # date__gte=date[0] - lookback_period - timedelta(days=100) if period == 'Q'
                                          # else date[0] - lookback_period - timedelta(days=400),
                                          # date__lte=date[-1] - lookback_period,
                                          period='Yearly' if period == 'FY' else 'Quarterly')

    # TODO Try aggregation https://stackoverflow.com/questions/25151042/moving-averages-with-mongodbs-aggregation-framework

    # .as_pymongo()  # .only(financial_statement).as_pymongo()[financial_statement]
    #     pipeline = [{'$sort': {'date': 1}},
    #                 {'$group': {
    #                     '_id': '$company',
    #                     'date': {'$last': '$date'},
    #                 }}]
    # agg = filings.aggregate(*pipeline)
    # for a in agg:
    #     print(a)

    output = defaultdict(dict)
    for stock_ in stock:
        filings_for_stock = filings.filter(company=stock_).order_by('date').as_pymongo()
        for date_ in date:

            # get the closest filing from this date for this stock's filings
            for idx, filing in enumerate(filings_for_stock):

                # if date is instance of tuple, then it's a range and we need to consider all filings queried.
                if isinstance(date, list) and \
                        idx + 1 < len(filings_for_stock) and \
                        filings_for_stock[idx + 1]['date'] < date_ - lookback_period:
                    continue

                def get_entry(filing_):  # now can get corresponding entry
                    entry = filing_[financial_statement]
                    for e in entry_name:
                        entry = entry[e]
                    return entry

                if period in ['Q', 'FY']:
                    output[date_][stock_] = get_entry(filing_=filing)

                elif period in ['TTM', 'YTD']:
                    entries = []
                    for i in range(min(4, len(filings_for_stock))):
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

    return format_output(dict(output))


def read_prices_series(stock, from_date=None, to_date=datetime.now(),
                       lookback_period=timedelta(days=5 * 365), spec='close'):
    if from_date is None:
        from_date = to_date - lookback_period

    if not isinstance(stock, list):
        stock = [stock]

    objects = object_model.AssetPrices.objects.get(company__in=object_model.Company.objects(ticker__in=stock),
                                                   close__date__lte=to_date, close__date__gte=from_date)
    dictios = objects.to_mongo().to_dict()[spec]
    dates, prices = [dictio['date'] for dictio in dictios], [dictio['price'] for dictio in dictios]
    series = pd.Series(data=prices, index=dates, name=stock[0])  # TODO quick fix

    return series


def read_market_price(stock, date=None, lookback_period=timedelta(days=0), spec='close'):
    """

    :param stock:
    :param date:
    :param lookback_period:
    :param spec: 'open', 'high', 'low', 'close', 'adj_close'
    :return:
    """
    stock, date = format_input(stock, date)

    objects = object_model.AssetPrices.objects(company__in=object_model.Company.objects(ticker__in=stock),
                                               close__date__lte=date[0])  # TODO read date list
    output = defaultdict(dict)
    for obj in objects:
        output[date[0]][obj.company.name] = obj.close[-1].price
    return format_output(dict(output))
    # output = objects.filter(date__lte=date)

    # pipeline = [ {"$group": {'_id': {"date"}}}
    #     {"date": {"$company": {"$toUpper": "$name"}}}
    # ]
    # data = objects.aggregate(pipeline)

    # return output


def get_company_classification(stock):
    return object_model.Company.objects.get(ticker=stock).to_mongo().to_dict()


def company_industry(stock, classification: str):
    if classification not in ['SIC', 'GICS']:
        raise Exception

    return object_model.Company.objects(ticker=stock).values_list('sic_industry' if classification == 'SIC'
                                                                  else 'gics_industry')[0]


def company_sector(stock, classification: str):
    return object_model.Company.objects(ticker=stock).values_list('sic_sector' if classification == 'SIC'
                                                                  else 'gics_sector')[0]


def company_location(stock):
    return object_model.Company.objects(ticker=stock).values_list('location')[0]


def company_indices(stock, date):
    # TODO
    for index in object_model.Index.objects:
        if index.evolution:
            pass
    return ()


def companies_in_classification(class_, date=datetime.now()):
    if isinstance(class_, config.SIC_Industries):
        companies = object_model.Company.objects(sic_industry=class_.value)
    elif isinstance(class_, config.GICS_Industries):
        companies = object_model.Company.objects(gics_industry=class_.value)
    elif isinstance(class_, config.SIC_Sectors):
        companies = object_model.Company.objects(sic_sector=class_.value)
    elif isinstance(class_, config.GICS_Sectors):
        companies = object_model.Company.objects(gics_sector=class_.value)
    elif isinstance(class_, config.Regions):
        companies = object_model.Company.objects(location=class_.value)
    elif isinstance(class_, config.Exchanges):
        companies = object_model.Company.objects(exchange=class_.value)
    elif isinstance(class_, config.MarketIndices):  # TODO do better query
        query = object_model.Index.objects(name=class_.value).first().to_mongo()
        for item in query['evolution']:
            if item['date'] > date:
                continue
            return item['companies']
        return []
    else:
        raise Exception('Ensure arg for classification is an instance of config.SIC_Industries, '
                        'config.GICS_Industries, config.SIC_Sectors, config.GICS_Sectors,'
                        'config.Regions, config.Exchanges, or config.MarketIndices')

    return [company.ticker for company in companies]


def read_factor_returns(factor_model, factor, from_date, to_date, frequency):
    pass


def read_gross_national_product(from_date, to_date, frequency):
    pass


'''
III. `Update` routines
'''

'''
IV. `Delete` routines
'''

if __name__ == '__main__':
    # atlas_url = get_atlas_db_url(username='AlainDaccache', password='qwerty98', dbname='matilda-db')
    # db = connect_to_mongo_engine(atlas_url)

    # populate_db_financial_statements(tickers=stocks[0], from_date=datetime(2016, 1, 1), to_date=datetime.today())

    # populate_db_routine(db_username='AlainDaccache', db_password='qwerty98', db_name='matilda-db',
    #                     tickers=None, from_date=datetime(2016, 1, 1), to_date=datetime.today(), reset_db=True,
    #                     populate_company_info=True, populate_financial_statements=True,
    #                     populate_asset_prices=True, populate_risk_factors=True)

    atlas_url = get_atlas_db_url(username='AlainDaccache', password='qwerty98', dbname='matilda-db')
    db = connect_to_mongo_engine(atlas_url)
    # print(get_company_classification(stock='AAPL'))
    
    object_model.AssetPrices.drop_collection()
    stocks = companies_in_classification(class_=config.MarketIndices.DOW_JONES)
    populate_db_asset_prices(stocks)
    # populate_db_financial_statements(stocks)
    # populate_db_asset_prices('AAPL')
    # populate_db_risk_factors()
    # populate_db_company_info(tickers=stocks)

    # object_model.Index.drop_collection()
    # populate_indices(from_file=False)
    # object_model.User.drop_collection()
    # print(companies_in_classification(class_=config.MarketIndices.SP_500, date=datetime(2016, 1, 1)))

    # for period in ['YTD']:
    #     pprint(read_financial_statement_entry(stock=companies_in_classification(config.MarketIndices.DOW_JONES)[:5],
    #                                           financial_statement='BalanceSheet',
    #                                           period=period, date=datetime(2018, 6, 6),
    #                                           entry_name=['Assets', 'CurrentAssets', 'TotalCurrentAssets']))
    # pprint(read_market_price(stock=['MMM', 'AMGN'], date=datetime.now()))
    # nasdaq_tickers = object_model.Company.objects(exchange='NASDAQ').values_list('name')
    # print(nasdaq_tickers)
    # pprint(companies_in_classification(class_=config.Exchanges.NASDAQ))

    # print(company_industry('AAPL', classification='SIC'))
    print(read_prices_series(stock='AAPL'))
