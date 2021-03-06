import os
import pickle
from bs4 import BeautifulSoup as bs
import re
import json
import pandas as pd
import requests
from matilda import config
from pprint import pprint

from matilda.database.data_preparation_helpers import flatten_dict

regex_patterns = {
    'Balance Sheet': {
        'Assets': {
            'Current Assets': {
                'Cash and Short Term Investments': {
                    'Cash and Cash Equivalents': r'$^',
                    'Marketable Securities': r'$^',
                    'Cash and Short Term Investments': r'Cash on Hand',
                },
                'Accounts Receivable': {
                    'Allowance for Doubtful Accounts': r'$^',
                    'Net Accounts Receivable': r'^Receivables$',
                    'Vendor Non-trade Receivables': r'$^'
                },
                'Prepaid Expense': r'^Pre-Paid Expenses$',
                'Inventory Net': r'^Inventory$',
                'Income Taxes Receivable': r'$^',
                'Assets Held For Sale': r'$^',
                'Deferred Tax Assets': r'$^',
                'Other Current Assets': r'^Other Current Assets$',
                'Total Current Assets': r'^Total Current Assets$'
            },
            'Non Current Assets': {

                'Marketable Securities': r'^Long-Term Investments$',
                'Restricted Cash': r'$^',
                'Property Plant And Equipment': {
                    'Gross Property, Plant and Equipment': r'$^',
                    'Accumulated Depreciation and Amortization': r'$^',
                    'Net Property, Plant, and Equipment': r'^Property, Plant, And Equipment$',
                },
                'Operating Lease Right-of-use Assets': r'$^',
                'Deferred Tax Assets': r'$^',
                'Intangible Assets': {
                    'Goodwill': r'$^',
                    'Net Intangible Assets Excluding Goodwill': r'$^',
                    'Total Intangible Assets': r'^Goodwill And Intangible Assets$',
                },
                'Other Non Current Assets': r'^Other Long-Term Assets$',
                'Total Non Current Assets': r'^Total Long-Term Assets$'
            },
            'Total Assets': r'^Total Assets$'
        },
        "Liabilities and Shareholders Equity": {
            'Liabilities': {
                'Current Liabilities': {
                    'Long-Term Debt, Current Maturities': r'$^',
                    'Accounts Payable': r'^Accounts Payable Current$',
                    'Other Accounts Payable': r'$^',
                    'Operating Lease Liability': r'$^',
                    'Employee-Related Liabilities': r'$^',
                    'Accrued Income Taxes': r'$^',
                    'Accrued Liabilities': r'$^',
                    'Deferred Revenue': r'$^',  # TODO also known as long term unearned revenue
                    'Commercial Paper': r'$^',
                    'Income Taxes Payable': r'$^',
                    'Other Current Liabilities': r'$^',
                    'Total Current Liabilities': r'^Total Current Liabilities$',
                },
                'Non Current Liabilities': {
                    'Deferred Tax': r'$^',
                    'Long-Term Debt Non Current Maturities': r'^Long-Term Debt$',
                    'Operating Lease': r'$^',
                    'Defined Benefit Plan': r'$^',
                    'Accrued Income Taxes': r'$^',
                    'Deferred Revenue': r'$^',
                    'Long-Term Unearned Revenue': r'$^',
                    'Other Liabilities Non Current': r'^Other Non-Current Liabilities$',
                    'Total Non Current Liabilities': r'^Total Long-Term Liabilities$'
                },
                'Total Liabilities': r'^Total Liabilities$'
            },
            "Shareholders Equity": {
                'Preferred Stock Value Issued': r'$^',
                'Common Stock and Additional Paid in Capital': {
                    'Common Stock Value Issued': r'^Common Stock Net$',
                    'Additional Paid in Capital': r'^Additional Paid In Capital$',
                    'Common Stocks Including Additional Paid In Capital': r'$^',
                    'Weighted Average Number of Shares Outstanding Basic': r'^Basic Shares Outstanding$',
                    'Weighted Average Number Diluted Shares Outstanding Adjustment': r'$^',
                    'Weighted Average Number of Shares Outstanding Diluted': r'^Shares Outstanding$',
                },

                'Treasury Stock Value': r'$^',
                'Retained Earnings Accumulated Deficit': r'^Retained Earnings (Accumulated Deficit)$',
                'Accumulated Other Comprehensive Income (Loss)': r'^Comprehensive Income$',
                'Deferred Stock Compensation': r'$^',
                'Stockholders Equity Attributable to Parent': r'^Share Holder Equity$',
                'Minority Interest': r'$^',
                'Stockholders Equity Including Portion Attributable to Minority Interest': '$^'
            },
            'Total Liabilities and Shareholders Equity': r'^Total Liabilities And Share Holders Equity$'
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
        'Provision for Loan Lease and Other Losses': r'$^',
        'Operating Expenses': {
            'Research and Development Expense': r'^Research And Development Expenses$',
            'Selling, General and Administrative': {
                'Marketing Expense': r'$^',
                'Selling and Marketing Expense': r'$^',
                'General and Administrative Expense': r'$^',
                'Selling General and Administrative Expense': r'^SG&A Expenses$'
            },
            'Other Operating Expenses': r'^Other Operating Income Or Expenses',
            'Earnings Before Interest, Taxes, Depreciation, and Amortization,': r'^EBITDA$',
            'Total Operating Expenses': r'^Operating Expenses$'
        },
        'Costs and Expenses': r'$^',
        'Operating Income (Loss)': r'^Operating Income$',
        'Non-Operating Income (Expense)': {
            'Interest Income': r'$^',
            'Interest and Dividend Income': r'$^',
            'Interest Expense': r'^Interest Expense$',
            'Interest Income (Expense), Net': r'$^',
            'Foreign Currency Transaction Gain (Loss)': r'$^',
            'Other Non-Operating Income (Expense)': '$^',
            # below is for 'Interest and other income, net' and 'Total other income/(expense), net'
            'Non-Operating Income (Expense)': r'^Total Non-Operating Income/Expense$'
        },

        'Income (Loss) before Income Taxes, Minority Interest': r'^Pre-Tax Income$',
        'Income Tax Expense (Benefit)': r'^Income Taxes$',
        'Net Income (Loss), Including Portion Attributable to Minority Interest': r'^Income After Taxes$',
        'Net Income (Loss) Attributable to Minority Interest': r'^Other Income$',
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
            'Net Income (Loss) Attributable to Parent': r'^Net Income/Loss$',
            'Adjustments to Reconcile Net Income': {
                'Depreciation, Depletion and Amortization': r'^Total Depreciation And Amortization - Cash Flow',
                'Share-based Payment Arrangement, Non-Cash Expense': r'$^',
                'Deferred Income Tax Expense (Benefit)': r'$^',
                'Other Non-Cash Income (Expense)': r'^Other Non-Cash Items$'
            },
            'Change in Assets and Liabilities': {
                'Increase (Decrease) in Accounts Receivable': r'^Change In Accounts Receivable$',
                'Increase (Decrease) in Inventories': r'^Change In Inventories$',
                'Increase (Decrease) in Other Receivables': r'$^',
                'Increase (Decrease) in Prepaid Expense and Other Assets': r'$^',
                'Increase (Decrease) in Other Operating Assets': r'$^',
                'Increase (Decrease) in Accounts Payable': r'^Change In Accounts Payable$',
                'Increase (Decrease) in Other Accounts Payable': r'$^',
                'Increase (Decrease) in Accrued Liabilities': r'$^',
                'Increase (Decrease) in Deferred Revenue': r'$^',
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


def scrape_macrotrend(tickers, save_to_excel=True, save_to_pickle=True):
    multiples_dictio = {}

    if not os.path.exists(config.FINANCIAL_STATEMENTS_DIR_PATH_EXCEL):
        os.makedirs(config.FINANCIAL_STATEMENTS_DIR_PATH_EXCEL)
    if not os.path.exists(config.FINANCIAL_STATEMENTS_DIR_PATH_PICKLE):
        os.makedirs(config.FINANCIAL_STATEMENTS_DIR_PATH_PICKLE)
    if not os.path.exists(config.FINANCIAL_STATEMENTS_DIR_PATH_PICKLE_UNFLATTENED):
        os.makedirs(config.FINANCIAL_STATEMENTS_DIR_PATH_PICKLE_UNFLATTENED)

    for period in ['Quarterly', 'Yearly']:
        for sheet in ['Balance Sheet', 'Cash Flow Statement', 'Income Statement']:
            path = os.path.join(config.FINANCIAL_STATEMENTS_DIR_PATH_PICKLE, period, sheet)
            if not os.path.exists(path):
                os.makedirs(path)

    for ticker in tickers:
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
                if ticker not in multiples_dictio.keys():
                    multiples_dictio[ticker] = multiplier

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
                for normalized_category, pattern_string in flatten_dict(
                        regex_patterns).items():
                    # master_dict[period][year][normalized_category] = np.nan
                    master_dict[period][year][normalized_category] = 0

        # fill values based on match
        for period, year_table in main_dict.items():
            for year, table in year_table.items():
                for scraped_name, scraped_value in flatten_dict(table).items():
                    for normalized_category, pattern_string in flatten_dict(
                            regex_patterns).items():
                        if re.search(pattern_string, scraped_name, re.IGNORECASE):
                            master_dict[period][year][normalized_category] = scraped_value
                            break

        unflattened_master_dict = {period:
                                       {date: unflatten(filings)
                                        for date, filings in date_dict.items()
                                        } for period, date_dict in master_dict.items()
                                   }
        # pprint(unflattened_master_dict)
        pprint(master_dict)

        path = '{}/{}.pkl'.format(config.FINANCIAL_STATEMENTS_DIR_PATH_PICKLE_UNFLATTENED, ticker)
        with open(path, 'wb') as handle:
            pickle.dump(unflattened_master_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)

        path = '{}/{}.xlsx'.format(config.FINANCIAL_STATEMENTS_DIR_PATH_EXCEL, ticker)
        save_pretty_excel(path, financials_dictio=master_dict, with_pickle=save_to_pickle)
        master_dict = unflatten(flatten_dict(master_dict))
        pprint(master_dict)

    multiple_pickle_path = os.path.join(config.FINANCIAL_STATEMENTS_DIR_PATH_PICKLE, 'multiples.pkl')

    try:
        with open(multiple_pickle_path, 'rb') as handle:
            existing_dictio = pickle.load(handle)
    except:
        existing_dictio = {}

    with open(multiple_pickle_path, 'wb') as handle:
        existing_dictio.update(multiples_dictio)
        pickle.dump(existing_dictio, handle, protocol=pickle.HIGHEST_PROTOCOL)
