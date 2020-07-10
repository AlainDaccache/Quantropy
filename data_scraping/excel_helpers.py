import os
from datetime import datetime
from pathlib import Path
import pandas as pd
import config
import data_scraping.financial_data_scraper as scraper
from openpyxl import load_workbook
import numpy as np
import xlrd
from typing import Callable


def get_date_index(df, date, date_axis):
    dates_values = df.index.values if date_axis == 'y-axis' else df.columns
    if isinstance(dates_values[0], str):
        dates_values = [datetime.strptime(x, '%Y-%m-%d') for x in dates_values]
    elif isinstance(dates_values[0], np.datetime64):
        dates_values = [x.astype('M8[ms]').astype('O') for x in dates_values]
    if len(dates_values) > 1:
        if dates_values[0] > dates_values[1]: # if dates decreasing rightwards or downwards
            return next((index for (index, item) in enumerate(dates_values) if item <= date), 0)
        else: # if dates increasing rightwards or downwards
            return next((index for (index, item) in enumerate(dates_values) if item >= date), -1)
    else:
        return 0


def save_into_csv(path, df, sheet_name, overwrite_sheet=True, overwrite_file=True):

    with pd.ExcelWriter(path, engine='openpyxl') as writer:
        if os.path.exists(path):
            excel_book = load_workbook(path)
            writer.book = load_workbook(path)
            writer.sheets = dict((ws.title, ws) for ws in excel_book.worksheets)
            if overwrite_sheet and sheet_name in [ws.title for ws in excel_book.worksheets]:
                excel_book.remove(excel_book[sheet_name])
                excel_book.save(path)
        df.to_excel(writer, sheet_name=sheet_name)
        writer.save()
        writer.close()


def read_df_from_csv(path, sheet_name):

    if os.path.exists(path):
        workbook = xlrd.open_workbook(path, on_demand=True)
        sheets = workbook.sheet_names()
        if sheet_name not in sheets:
            return pd.DataFrame()
        else:
            xls = pd.ExcelFile(path)
            return pd.read_excel(xls, sheet_name, index_col=0)
    return pd.DataFrame()


def read_entry_from_csv(path, sheet_name, date, entry):

    if os.path.exists(path):
        # maybe the file exists, but the sheet is not in the file
        if config.financial_statements_folder_path in path:
            stock = Path(path).stem
            sheets = xlrd.open_workbook(path, on_demand=True).sheet_names()
            if sheet_name not in sheets:
                if sheet_name == config.stock_prices_sheet_name:
                    scraper.get_stock_prices(stock)
                elif sheet_name in config.quarterly_statements:
                    # scraper.scrape_financial_statements(stock, '10-Q')
                    return Exception
                elif sheet_name in config.yearly_statements:
                    scraper.scrape_financial_statements(stock, '10-K')

    # if the file doesn't exist
    else:
        if config.financial_statements_folder_path in path:
            stock = Path(path).stem
            scraper.get_stock_prices(stock)
            scraper.scrape_financial_statements(stock, '10-K')
            # scraper.scrape_financial_statements(stock, '10-Q')
        elif path == config.beta_factors_file_path:
            scraper.get_beta_factors()

    xls = pd.ExcelFile(path)
    df = pd.read_excel(xls, sheet_name, index_col=0)

    if isinstance(df.index, pd.DatetimeIndex): # if there is a column for dates
        date_index = get_date_index(df, date, date_axis='y-axis')
        return df[entry].iloc[date_index]
    else: # if there is a row for dates
        date_index = get_date_index(df, date, date_axis='x-axis')
        return df.iloc[:, date_index].loc[entry]


def read_dates_from_csv(path, sheet_name):
    if os.path.exists(path):
        sheets = xlrd.open_workbook(path, on_demand=True).sheet_names()
        if sheet_name not in sheets:
            return []
        with open(path, "r") as csv:
            xls = pd.ExcelFile(path)
            df = pd.read_excel(xls, '{}'.format(sheet_name), index_col=0)
            return [datetime.strptime(x, '%Y-%m-%d') for x in df.columns]
    else:
        return []


def get_stock_universe():
    tickers = []
    directory = config.financial_statements_folder_path
    for root, dirs, files in os.walk(directory):
        for file in files:
            tickers.append(os.path.splitext(file)[0])
    return tickers


def get_industry(stock: str):
    pass


def companies_in_industry(industry: str):
    df = pd.read_csv('companies_overview.csv', index_col='Ticker')
    ind = df['Industry'] == industry
    tickers_in_industry = [ticker for ticker, boolean in ind.iteritems() if boolean]
    return tickers_in_industry


def metric_in_industry(metric: Callable, industry: str) -> pd.Series(dtype="float64"):
    output = pd.Series(dtype='float64')
    tickers_in_industry = companies_in_industry(industry)
    for ticker in tickers_in_industry:
        output[ticker] = metric(ticker)
    return output


# get companies greater or lower than a certain percentile regarding metrics
# for Q1, percentile is 25, for Q2, percentile is 50, for Q3, percentile is 75
# comparator: '>', '<'
def companies_comparative_metrics(metrics_series: pd.Series(dtype='float64'), percentile: int, comparator: str):
    quantile = np.percentile(metrics_series, percentile)
    if comparator == '>':
        output = [ticker for ticker, metric_value in metrics_series.iteritems() if metric_value > quantile]
    else:
        output = [ticker for ticker, metric_value in metrics_series.iteritems() if metric_value < quantile]
    return output

if __name__ == '__main__':
    # metrics_series = metric_in_industry(partial(fi.earnings_per_share, ttm=False), 'SERVICES-COMPUTER PROGRAMMING, DATA PROCESSING, ETC.')
    # companies = companies_comparative_metrics(metrics_series, percentile=25, comparator='>')
    # print(companies)
    financial_path = '{}/{}.xlsx'.format(config.FINANCIAL_STATEMENTS_DIR_NAME, 'TSLA')
    # print(read_entry_from_csv(financial_path, config.stock_prices_sheet_name, datetime.now(), 'Adj Close'))
    # print(read_entry_from_csv(financial_path, config.balance_sheet_yearly, datetime(2018, 4, 4), 'Restricted Cash Non Current'))
    print(read_entry_from_csv(config.beta_factors_file_path, config.yearly_factors, datetime(2001, 1, 1), 'RF'))