import os
from datetime import datetime
import pandas as pd
import config
import data_scraping.financial_data_scraper as scraper
from openpyxl import load_workbook
import numpy as np
import xlrd
from sxl import Workbook


def get_date_index(df, date, date_axis):
    dates_values = df.columns if date_axis == 'column' else df.index.values
    if isinstance(dates_values[0], str):
        dates_values = [datetime.strptime(x, '%Y-%m-%d') for x in dates_values]
    elif isinstance(dates_values[0], np.datetime64):
        dates_values = [datetime.utcfromtimestamp(x.tolist()/1e9) for x in dates_values]
    if len(dates_values) > 1:
        if dates_values[0] > dates_values[1]:
            return next((index for (index, item) in enumerate(dates_values) if item <= date), 0)
        else:
            return next((index for (index, item) in enumerate(dates_values) if item >= date), -1)
    else:
        return 0


def save_into_csv(stock, df, sheet_name):
    financials_path = '{}/{}.xlsx'.format(config.financial_statements_folder_path, stock)

    with pd.ExcelWriter(financials_path, engine='openpyxl') as writer:
        if os.path.exists(financials_path):
            excel_book = load_workbook(financials_path)
            writer.book = load_workbook(financials_path)
            writer.sheets = dict((ws.title, ws) for ws in excel_book.worksheets)
        df.to_excel(writer, sheet_name)
        writer.save()
        writer.close()


def read_df_from_csv(stock, sheet_name):
    financials_path = '{}/{}.xlsx'.format(config.financial_statements_folder_path, stock)
    if os.path.exists(financials_path):
        workbook = xlrd.open_workbook(financials_path, on_demand=True)
        sheets = workbook.sheet_names()
        if sheet_name not in sheets:
            return pd.DataFrame()
        else:
            xls = pd.ExcelFile(financials_path)
            return pd.read_excel(xls, sheet_name, index_col=0)
    return pd.DataFrame()


def read_entry_from_csv(stock, sheet_name, date, entry):
    financials_path = '{}/{}.xlsx'.format(config.financial_statements_folder_path, stock)

    if os.path.exists(financials_path):
        sheets = xlrd.open_workbook(financials_path, on_demand=True).sheet_names()
        if sheet_name not in sheets:
            if sheet_name == config.stock_prices_sheet_name:
                scraper.scrape_stock_prices(stock)
            elif sheet_name in config.quarterly_statements:
                # scraper.scrape_financial_statements(stock, '10-Q')
                return Exception
            elif sheet_name in config.yearly_statements:
                scraper.scrape_financial_statements(stock, '10-K')
    else:
        scraper.scrape_stock_prices(stock)
        scraper.scrape_financial_statements(stock, '10-K')
        # scraper.scrape_financial_statements(stock, '10-Q')

    xls = pd.ExcelFile(financials_path)
    df = pd.read_excel(xls, sheet_name, index_col=0)

    if sheet_name != config.stock_prices_sheet_name:
        date_index = get_date_index(df, date, date_axis='column')
        return df.iloc[:, date_index].loc[entry]
    else:
        date_index = get_date_index(df, date, date_axis='row')
        return df[entry].iloc[date_index]


def read_dates_from_csv(ticker, sheet_name):
    financials_path = "{}/{}.xlsx".format(config.financial_statements_folder_path, ticker)
    if os.path.exists(financials_path):
        sheets = xlrd.open_workbook(financials_path, on_demand=True).sheet_names()
        if sheet_name not in sheets:
            return []
        with open(financials_path, "r") as csv:
            xls = pd.ExcelFile(financials_path)
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