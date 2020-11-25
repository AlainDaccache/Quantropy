import os
from datetime import datetime
from bs4 import BeautifulSoup as bs
import re
import json
import pandas as pd
import requests
from zope.interface import implementer
import numpy as np

import config
from historical_data_collection import data_preparation_helpers
from pprint import pprint
from historical_data_collection.financial_statements_scraper.html_scraper_sec_edgar import HtmlParser
from historical_data_collection.stock_prices_scraper import save_stock_prices

regex_patterns = {
    'Balance Sheet': {
        'Assets': {
            'Current Assets': {
                'Cash and Short Term Investments': {
                    'Cash and Cash Equivalents': r'$^',
                    'Marketable Securities Current': r'$^',
                    'Cash and Short Term Investments': r'Cash on Hand',
                },
                'Accounts Receivable': {
                    'Allowance for Doubtful Accounts': r'$^',
                    'Net Accounts Receivable': r'^Receivables$',
                    'Vendor Nontrade Receivables, Current': r'$^'
                },
                'Prepaid Expense, Current': r'^Pre-Paid Expenses$',
                'Inventory, Net': r'^Inventory$',
                'Income Taxes Receivable, Current': r'$^',
                'Assets Held-for-sale': r'$^',
                'Deferred Tax Assets, Current': r'$^',
                'Other Current Assets': r'^Other Current Assets$',
                'Total Current Assets': r'^Total Current Assets$'
            },
            'Non Current Assets': {

                'Marketable Securities Non Current': r'^Long-Term Investments$',
                'Restricted Cash Non Current': r'$^',
                'Property, Plant and Equipment': {
                    'Gross Property, Plant and Equipment': r'$^',
                    'Accumulated Depreciation and Amortization': r'$^',
                    'Property, Plant and Equipment, Net': r'^Property, Plant, And Equipment$',
                },
                'Operating Lease Right-of-use Assets': r'$^',
                'Deferred Tax Assets Non Current': r'$^',
                'Intangible Assets': {
                    'Goodwill': r'$^',
                    'Intangible Assets, Net (Excluding Goodwill)': r'$^',
                    'Total Intangible Assets': r'^Goodwill And Intangible Assets$',
                },
                'Other Non Current Assets': r'^Other Long-Term Assets$',
                'Total Non Current Assets': r'^Total Long-Term Assets$'
            },
            'Total Assets': r'^Total Assets$'
        },
        "Liabilities and Shareholders\' Equity": {
            'Liabilities': {
                'Current Liabilities': {
                    'Long-term Debt, Current Maturities': r'$^',
                    'Accounts Payable': r'^Accounts Payable Current$',
                    'Other Accounts Payable': r'$^',
                    'Operating Lease, Liability, Current': r'$^',
                    'Employee-related Liabilities, Current': r'$^',
                    'Accrued Income Taxes': r'$^',
                    'Accrued Liabilities, Current': r'$^',
                    'Deferred Revenue, Current': r'$^',
                    'Commercial Paper': r'$^',
                    'Income Taxes Payable': r'$^',
                    'Other Current Liabilities': r'$^',
                    'Total Current Liabilities': r'^Total Current Liabilities$',
                },
                'Non Current Liabilities': {
                    'Deferred Tax Liabilities': r'$^',
                    'Long-term Debt, Noncurrent Maturities': r'^Long-Term Debt$',
                    'Operating Lease, Liability, Noncurrent': r'$^',
                    'Liability, Defined Benefit Plan, Noncurrent': r'$^',
                    'Accrued Income Taxes, Noncurrent': r'$^',
                    'Deferred Revenue, Noncurrent': r'$^',
                    'Long-Term Unearned Revenue': r'$^',
                    'Other Liabilities, Noncurrent': r'^Other Non-Current Liabilities$',
                    'Total Non Current Liabilities': r'^Total Long-Term Liabilities$'
                },
                'Total Liabilities': r'^Total Liabilities$'
            },
            "Shareholders' Equity": {
                'Preferred Stock, Value, Issued': r'$^',
                'Common Stock and Additional Paid in Capital': {
                    'Common Stock, Value, Issued': r'^Common Stock Net$',
                    'Additional Paid in Capital': r'^Additional Paid In Capital$',
                    'Common Stocks, Including Additional Paid in Capital': r'$^',
                    'Weighted Average Number of Shares Outstanding, Basic': r'^Basic Shares Outstanding$',
                    'Weighted Average Number Diluted Shares Outstanding Adjustment': r'$^',
                    'Weighted Average Number of Shares Outstanding, Diluted': r'^Shares Outstanding$',
                },

                'Treasury Stock, Value': r'$^',
                'Retained Earnings (Accumulated Deficit)': r'^Retained Earnings (Accumulated Deficit)$',
                'Accumulated Other Comprehensive Income (Loss)': r'^Comprehensive Income$',
                'Deferred Stock Compensation': r'$^',
                'Stockholders\' Equity Attributable to Parent': r'$^',
                'Minority Interest': r'$^',
                'Stockholders\' Equity, Including Portion Attributable to Noncontrolling Interest': '^Share Holder Equity$'
            },
            'Total Liabilities and Shareholders\' Equity': r'^Total Liabilities And Share Holders Equity$'
        },
    },
    'Income Statement': {
        'Revenues': {
            'Service Sales': r'$^',
            'Product Sales': r'$^',
            'Net Sales': r'^Revenue$'
        },
        'Cost of Goods and Services Sold': {
            'Cost of Products': r'$^',
            'Cost of Services': r'$^',
            'Cost of Goods and Services Sold': r'^Cost Of Goods Sold$',
            'Gross Margin': r'^Gross Profit$',
        },
        'Provision for Loan, Lease, and Other Losses': r'$^',
        'Operating Expenses': {
            'Research and Development Expense': r'^Research And Development Expenses$',
            'Selling, General and Administrative': {
                'Marketing Expense': r'$^',
                'Selling and Marketing Expense': r'$^',
                'General and Administrative Expense': r'$^',
                'Selling, General and Administrative Expense': r'^SG&A Expenses$'
            },
            'Other Operating Expenses': r'^Other Operating Income Or Expenses',
            'EBITDA': r'^EBITDA$',
            'Total Operating Expenses': r'^Operating Expenses$'
        },
        'Costs and Expenses': r'$^',
        'Operating Income (Loss) / EBIT': r'^Operating Income$',
        'Other (Non-Operating) Income (Expense)': {
            'Interest Income': r'$^',
            'Interest and Dividend Income': r'$^',
            'Interest Expense': r'^Interest Expense$',
            'Interest Income (Expense), Net': r'$^',
            'Foreign Currency Transaction Gain (Loss)': r'$^',
            'Other Nonoperating Income (Expense)': '$^',
            # below is for 'Interest and other income, net' and 'Total other income/(expense), net'
            'Non-Operating Income (Expense)': r'^Total Non-Operating Income/Expense$'
        },

        'Income (Loss) before Income Taxes, Noncontrolling Interest': r'^Pre-Tax Income$',
        'Income Tax Expense (Benefit)': r'^Income Taxes$',
        'Net Income (Loss), Including Portion Attributable to Noncontrolling Interest': r'^Income After Taxes$',
        'Net Income (Loss) Attributable to Noncontrolling (Minority) Interest': r'^Other Income$',
        'Net Income (Loss) Attributable to Parent': r'^Net Income$',
        'Undistributed Earnings (Loss) Allocated to Participating Securities, Basic': r'^Undistributed Earnings Loss Allocated To Participating Securities Basic$',
        'Preferred Stock Dividends': r'$^',
        'Net Income (Loss) Available to Common Stockholders, Basic': r'^Net Income Loss Available To Common Stockholders Basic$',
        'Other Comprehensive Income (Loss)': r'$^',
        'Comprehensive Income (Loss), Net of Tax, Attributable to Parent': r'$^',
        # 'Earnings Per Share, Basic': '^Basic EPS$',
        # 'Earnings Per Share, Diluted': '^EPS - Earnings Per Share$',

    },
    'Cash Flow Statement': {
        'Cash, Cash Equivalents, Restricted Cash and Restricted Cash Equivalents, Beginning Balance':
            '$^',
        'Operating Activities': {
            'Net Income (Loss) Attributable to Parent': r'$^',
            'Adjustments to Reconcile Net Income': {
                'Depreciation, Depletion and Amortization': r'^Total Depreciation And Amortization - Cash Flow',
                'Share-based Payment Arrangement, Noncash Expense': r'$^',
                'Deferred Income Tax Expense (Benefit)': r'$^',
                'Other Noncash Income (Expense)': r'$^'
            },
            'Change in Assets and Liabilities': {
                'Increase (Decrease) in Accounts Receivable': r'$^',
                'Increase (Decrease) in Inventories': r'$^',
                'Increase (Decrease) in Other Receivables': r'$^',
                'Increase (Decrease) in Prepaid Expense and Other Assets': r'$^',
                'Increase (Decrease) in Other Operating Assets': r'$^',
                'Increase (Decrease) in Accounts Payable': r'$^',
                'Increase (Decrease) in Other Accounts Payable': r'$^',
                'Increase (Decrease) in Accrued Liabilities': r'$^',
                'Increase (Decrease) in Deferred Revenue, Liability': r'$^',
                'Increase (Decrease) in Other Operating Liabilities': r'$^'
            },
            'Net Cash Provided by (Used in) Operating Activities': r'^Cash Flow From Operating Activities$'
        },
        'Investing Activities': {
            'Payments to Acquire Marketable Securities, Available-for-sale': r'$^',
            'Proceeds from Maturities, Prepayments and Calls of Debt Securities, Available-for-sale': r'$^',
            'Proceeds from Sale of Debt Securities, Available-for-sale': r'$^',
            'Payments to Acquire Property, Plant, and Equipment': r'$^',
            'Payments to Acquire Businesses, Net of Cash Acquired': r'$^',
            'Payments to Acquire Other Investments': r'$^',
            'Proceeds from Sale and Maturity of Other Investments': r'$^',
            'Payments for (Proceeds from) Other Investing Activities': r'$^',
            'Net Cash Provided by (Used in) Investing Activities': r'^Cash Flow From Investing Activities$'
        },
        'Financing Activities': {
            'Proceeds from Issuance of Common Stock': r'$^',
            'Payment, Tax Withholding, Share-based Payment Arrangement': r'$^',
            'Payments of Dividends': r'(^Total Common And Preferred Stock Dividends Paid$)|(Common Stock Dividends Paid)',
            'Payments for Repurchase of Common Stock': r'$^',
            'Proceeds from Issuance of Long-term Debt': r'$^',
            'Repayments of Long-term Debt': r'$^',
            'Finance Lease, Principal Payments': r'$^',
            'Proceeds from (Repayments of) Bank Overdrafts': r'$^',
            'Proceeds from (Repayments of) Commercial Paper': r'$^',
            'Proceeds from (Payments for) Other Financing Activities': r'$^',
            'Net Cash Provided by (Used in) Financing Activities': r'^Cash Flow From Financial Activities$'
        },
        'Effect of Exchange Rate on Cash, Cash Equivalents, Restricted Cash and Restricted Cash Equivalents': r'$^',
        'Cash, Cash Equivalents, Restricted Cash and Restricted Cash Equivalents, Period Increase (Decrease), Including Exchange Rate Effect': r'$^',
        'Cash, Cash Equivalents, Restricted Cash and Restricted Cash Equivalents, Ending Balance': r'$^',
        'Supplemental': {}
    }
}


def scrape_macrotrend(ticker):
    """
    Step 1: Load Data Source
    """
    name = requests.get('https://www.macrotrends.net/stocks/charts/{}'.format(ticker)).url.rsplit('/')[-2]
    urls = {'Yearly': {}, 'Quarterly': {}}
    for freq in ['A', 'Q']:
        for statement in ['cash-flow-statement', 'income-statement', 'balance-sheet']:
            urls['Yearly' if freq == 'A' else 'Quarterly'][statement.replace('-', ' ').title()] = \
                "https://www.macrotrends.net/stocks/charts/{}/{}/{}?freq={}".format(ticker, name, statement, freq)

    """
    Step 2: Collect Tables
    """
    main_dict = {'Yearly': {}, 'Quarterly': {}}
    for period, statement_and_links in urls.items():
        for statement, link in statement_and_links.items():
            r = requests.get(link)
            multiplier = 1000000 if 'Millions' in r.text else 1000 if 'Thousands' in r.text else 1
            p = re.compile(r' var originalData = (.*?);\r\n\r\n\r', re.DOTALL)
            table_data = json.loads(p.findall(r.text)[0])

            dates = list(table_data[0].keys())[2:]
            dictio = {}
            for row in table_data:
                soup = bs(row['field_name'], features="lxml")
                # field_name = '_'.join([statement, soup.select_one('a, span').text])
                field_name = soup.select_one('a, span').text
                row_values = list(row.values())[2:]
                try:
                    dictio[field_name] = [float(i) if i != '' else 0 for i in row_values]
                except:
                    pass
            df = pd.DataFrame.from_dict(dictio, orient='index', columns=dates)
            # df = df.apply(lambda x: x.mul(multiplier))
            for year in df.columns:
                main_dict[period][year] = {} if year not in main_dict[period].keys() else main_dict[period][year]
                main_dict[period][year].update(df[year])

    """
    Step 3: Normalize Tables
    """

    master_dict = {'Yearly': {}, 'Quarterly': {}}  # frequency -> year -> title_category_name -> value
    for period, year_table in main_dict.items():
        for year, table in year_table.items():
            master_dict[period][year] = {} if year not in master_dict[period].keys() else master_dict[period][year]
            for normalized_category, pattern_string in data_preparation_helpers.flatten_dict(regex_patterns).items():
                master_dict[period][year][normalized_category] = np.nan

    for period, year_table in main_dict.items():
        for year, table in year_table.items():
            for scraped_name, scraped_value in data_preparation_helpers.flatten_dict(table).items():
                for normalized_category, pattern_string in data_preparation_helpers.flatten_dict(
                        regex_patterns).items():
                    if re.search(pattern_string, scraped_name, re.IGNORECASE):
                        master_dict[period][year][normalized_category] = scraped_value
                        break

    path = '{}/{}.xlsx'.format(config.FINANCIAL_STATEMENTS_DIR_PATH_EXCEL, ticker)
    data_preparation_helpers.save_pretty_excel(path, financials_dictio=master_dict)

    master_dict = data_preparation_helpers.unflatten(data_preparation_helpers.flatten_dict(master_dict))
    pprint(master_dict)


if __name__ == '__main__':
    # path = os.path.join(config.MARKET_TICKERS_DIR_PATH, 'Dow-Jones-Stock-Tickers.xlsx')
    # tickers = data_preparation_helpers.read_df_from_csv(path=path).iloc[0, :]
    for ticker in ['AAPL', 'FB', 'AMZN']:
        scrape_macrotrend(ticker)
        # save_stock_prices(ticker)
