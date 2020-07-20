from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import config
import os
import data_scraping.excel_helpers as excel


# for balance sheets, when doing trailing twelve months, we compute the mean
def read_balance_sheet_entry(stock_ticker, entry_name, date=datetime.now(), annual=False, ttm=True):
    path = os.path.join(config.FINANCIAL_STATEMENTS_DIR_PATH, stock_ticker + '.xlsx')
    if ttm:
        return np.mean([excel.read_entry_from_csv(path,
                                                  config.balance_sheet_quarterly,
                                                  date - timedelta(days=i * 90),
                                                  entry_name)
                        for i in range(4)])
    return excel.read_entry_from_csv(path,
                                     config.balance_sheet_quarterly if not annual else config.balance_sheet_yearly,
                                     date,
                                     entry_name)


def read_income_statement_entry(stock_ticker, entry_name, date=datetime.now(), annual=True, ttm=False):
    path = os.path.join(config.FINANCIAL_STATEMENTS_DIR_PATH, stock_ticker + '.xlsx')
    if ttm:
        return np.sum([excel.read_entry_from_csv(path,
                                                 config.income_statement_quarterly,
                                                 date - timedelta(days=i * 90),
                                                 entry_name)
                       for i in range(4)])
    return excel.read_entry_from_csv(path,
                                     config.income_statement_quarterly if not annual else config.income_statement_yearly,
                                     date,
                                     entry_name)


def read_cash_flow_statement_entry(stock_ticker, entry_name, date=datetime.now(), annual=True, ttm=False):
    path = os.path.join(config.FINANCIAL_STATEMENTS_DIR_PATH, stock_ticker + '.xlsx')
    if ttm:
        return np.sum([excel.read_entry_from_csv(path,
                                                 config.income_statement_quarterly,
                                                 date - timedelta(days=i * 90),
                                                 entry_name)
                       for i in range(4)])
    return excel.read_entry_from_csv(path,
                                     config.cash_flow_statement_quarterly if not annual else config.cash_flow_statement_yearly,
                                     date,
                                     entry_name)


'''
Balance Sheet: preferably get the most recent (because it's a statement of position), 
so quarterly instead of yearly by default, and ttm if yearly by default
'''


def cash_and_cash_equivalents(stock_ticker, date=datetime.now(), annual=False, ttm=True):
    return read_balance_sheet_entry(stock_ticker,
                                    ['Assets', 'Current Assets', 'Cash and Cash Equivalents'],
                                    date, annual, ttm)


cash_and_cash_equivalents('AAPL', annual=True, ttm=False)


def current_marketable_securities(stock_ticker, date=datetime.now(), annual=False, ttm=True):
    return read_balance_sheet_entry(stock_ticker,
                                    ['Assets', 'Current Assets', 'Marketable Securities Current'],
                                    date, annual, ttm)


def gross_accounts_receivable(stock_ticker, date=datetime.now(), annual=False, ttm=True):
    return read_balance_sheet_entry(stock_ticker,
                                    ['Assets', 'Current Assets', 'Gross Accounts Receivable'],
                                    date, annual, ttm)


def allowances_for_doubtful_accounts(stock_ticker, date=datetime.now(), annual=False, ttm=True):
    return read_balance_sheet_entry(stock_ticker,
                                    ['Assets', 'Current Assets', 'Allowances for Doubtful Accounts'],
                                    date, annual, ttm)


def net_accounts_receivable(stock_ticker, date=datetime.now(), annual=False, ttm=True):
    return read_balance_sheet_entry(stock_ticker,
                                    ['Assets', 'Current Assets', 'Net Accounts Receivable'],
                                    date, annual, ttm)


def current_prepaid_expenses(stock_ticker, date=datetime.now(), annual=False, ttm=True):
    return read_balance_sheet_entry(stock_ticker,
                                    ['Assets', 'Current Assets', 'Prepaid Expense, Current'],
                                    date, annual, ttm)


def net_inventory(stock_ticker, date=datetime.now(), annual=False, ttm=True):
    return read_balance_sheet_entry(stock_ticker,
                                    ['Assets', 'Current Assets', 'Inventory, Net'],
                                    date, annual, ttm)


def current_income_taxes_receivable(stock_ticker, date=datetime.now(), annual=False, ttm=True):
    return read_balance_sheet_entry(stock_ticker,
                                    ['Assets', 'Current Assets', 'Income Taxes Receivable, Current'],
                                    date, annual, ttm)


def assets_held_for_sale(stock_ticker, date=datetime.now(), annual=False, ttm=True):
    return read_balance_sheet_entry(stock_ticker,
                                    ['Assets', 'Current Assets', 'Assets Held-for-sale'],
                                    date, annual, ttm)


def current_deferred_tax_assets(stock_ticker, date=datetime.now(), annual=False, ttm=True):
    return read_balance_sheet_entry(stock_ticker,
                                    ['Assets', 'Current Assets', 'Deferred Tax Assets, Current'],
                                    date, annual, ttm)


def other_current_assets(stock_ticker, date=datetime.now(), annual=False, ttm=True):
    return read_balance_sheet_entry(stock_ticker,
                                    ['Assets', 'Current Assets', 'Other Assets, Current'],
                                    date, annual, ttm)


def current_total_assets(stock_ticker, date=datetime.now(), annual=False, ttm=True):
    return read_balance_sheet_entry(stock_ticker,
                                    ['Assets', 'Current Assets', 'Total Assets, Current'],
                                    date, annual, ttm)


def non_current_marketable_securities(stock_ticker, date=datetime.now(), annual=False, ttm=True):
    return read_balance_sheet_entry(stock_ticker,
                                    ['Assets', 'Non Current Assets', 'Marketable Securities Non Current'],
                                    date, annual, ttm)


def net_property_plant_equipment(stock_ticker, date=datetime.now(), annual=False, ttm=True):
    return read_balance_sheet_entry(stock_ticker,
                                    ['Assets', 'Non Current Assets', 'Property, Plant and Equipment, Net'],
                                    date, annual, ttm)


def operating_lease_right_of_use_assets(stock_ticker, date=datetime.now(), annual=False, ttm=True):
    return read_balance_sheet_entry(stock_ticker,
                                    ['Assets', 'Non Current Assets', 'Operating Lease Right-of-use Assets'],
                                    date, annual, ttm)


def non_current_deferred_tax_assets(stock_ticker, date=datetime.now(), annual=False, ttm=True):
    return read_balance_sheet_entry(stock_ticker,
                                    ['Assets', 'Non Current Assets', 'Deferred Tax Assets Non Current'],
                                    date, annual, ttm)


def goodwill(stock_ticker, date=datetime.now(), annual=False, ttm=True):
    return read_balance_sheet_entry(stock_ticker,
                                    ['Assets', 'Non Current Assets', 'Goodwill'],
                                    date, annual, ttm)


def net_intangible_assets(stock_ticker, date=datetime.now(), annual=False, ttm=True):
    return read_balance_sheet_entry(stock_ticker,
                                    ['Assets', 'Non Current Assets', 'Intangible Assets, Net (Excluding Goodwill)'],
                                    date, annual, ttm)


def total_intangible_assets(stock_ticker, date=datetime.now(), annual=False, ttm=True):
    return read_balance_sheet_entry(stock_ticker,
                                    ['Assets', 'Non Current Assets', 'Total Intangible Assets'],
                                    date, annual, ttm)


def other_non_current_assets(stock_ticker, date=datetime.now(), annual=False, ttm=True):
    return read_balance_sheet_entry(stock_ticker,
                                    ['Assets', 'Non Current Assets', 'Other Non Current Assets'],
                                    date, annual, ttm)


def total_non_current_assets(stock_ticker, date=datetime.now(), annual=False, ttm=True):
    return read_balance_sheet_entry(stock_ticker,
                                    ['Assets', 'Non Current Assets', 'Total Non Current Assets'],
                                    date, annual, ttm)


def total_assets(stock_ticker, date=datetime.now(), annual=False, ttm=True):
    return read_balance_sheet_entry(stock_ticker,
                                    ['Assets', 'Total Assets', 'Total Assets'],
                                    date, annual, ttm)


def long_term_debt_current_maturities(stock_ticker, date=datetime.now(), annual=False, ttm=True):
    return read_balance_sheet_entry(stock_ticker,
                                    ['Liabilities and Shareholders\' Equity', 'Liabilities',
                                     'Long-term Debt, Current Maturities'],
                                    date, annual, ttm)


def current_accounts_payable(stock_ticker, date=datetime.now(), annual=False, ttm=True):
    return read_balance_sheet_entry(stock_ticker,
                                    ['Liabilities and Shareholders\' Equity', 'Liabilities',
                                     'Accounts Payable, Current'],
                                    date, annual, ttm)


def current_deferred_revenues(stock_ticker, date=datetime.now(), annual=False, ttm=True):
    return read_balance_sheet_entry(stock_ticker,
                                    ['Liabilities and Shareholders\' Equity', 'Liabilities',
                                     'Current Deferred Revenues'],
                                    date, annual, ttm)


def current_accrued_liabilities(stock_ticker, date=datetime.now(), annual=False, ttm=True):
    return read_balance_sheet_entry(stock_ticker,
                                    ['Liabilities and Shareholders\' Equity', 'Liabilities',
                                     'Accrued Liabilities, Current'],
                                    date, annual, ttm)


def current_total_liabilities(stock_ticker, date=datetime.now(), annual=False, ttm=True):
    return read_balance_sheet_entry(stock_ticker,
                                    ['Liabilities and Shareholders\' Equity', 'Liabilities',
                                     'Total Current Liabilities'], date, annual, ttm)


def total_non_current_liabilities(stock_ticker, date=datetime.now(), annual=False, ttm=True):
    return read_balance_sheet_entry(stock_ticker,
                                    ['Liabilities and Shareholders\' Equity', 'Liabilities',
                                     'Total Long-Term Liabilities'],
                                    date, annual, ttm)


def total_liabilities(stock_ticker, date=datetime.now(), annual=False, ttm=True):
    return read_balance_sheet_entry(stock_ticker,
                                    ['Liabilities and Shareholders\' Equity', 'Liabilities', 'Total Liabilities'],
                                    date, annual, ttm)


def preferred_stock_value(stock_ticker, date=datetime.now(), annual=False, ttm=True):
    return read_balance_sheet_entry(stock_ticker,
                                    ['Liabilities and Shareholders\' Equity', 'Shareholders\' Equity',
                                     'Preferred Stock, Value, Issued'],
                                    date, annual, ttm)


def additional_paid_in_capital(stock_ticker, date=datetime.now(), annual=False, ttm=True):
    return read_balance_sheet_entry(stock_ticker,
                                    ['Liabilities and Shareholders\' Equity', 'Shareholders\' Equity',
                                     'Additional Paid in Capital'],
                                    date, annual, ttm)


def retained_earnings(stock_ticker, date=datetime.now(), annual=False, ttm=True):
    return read_balance_sheet_entry(stock_ticker,
                                    ['Liabilities and Shareholders\' Equity', 'Shareholders\' Equity',
                                     'Retained Earnings (Accumulated Deficit)'],
                                    date, annual, ttm)


def accumulated_other_comprehensive_income(stock_ticker, date=datetime.now(), annual=False, ttm=True):
    return read_balance_sheet_entry(stock_ticker,
                                    ['Liabilities and Shareholders\' Equity', 'Shareholders\' Equity',
                                     'Accumulated Other Comprehensive Income (Loss)'],
                                    date, annual, ttm)


def total_shares_outstanding(stock_ticker, date=datetime.now(), diluted=True, annual=False, ttm=True):
    entry = ['Liabilities and Shareholders\' Equity', 'Shareholders\' Equity',
             'Weighted Average Number of Shares Outstanding, Diluted'] if diluted \
        else ['Liabilities and Shareholders\' Equity', 'Shareholders\' Equity',
              'Weighted Average Number of Shares Outstanding, Basic']
    return read_balance_sheet_entry(stock_ticker, entry, date, annual, ttm)


def total_shareholders_equity(stock_ticker, date=datetime.now(), annual=False, ttm=True):
    return read_balance_sheet_entry(stock_ticker,
                                    ['Liabilities and Shareholders\' Equity', 'Shareholders\' Equity',
                                     'Stockholders\' Equity Attributable to Parent'],
                                    date, annual, ttm)


# print(cash_and_cash_equivalents('FB'))

# for income statements and cash flow statements, when doing trailing twelve months, we compute the sum
# by default, we use annual because its accumulation instead of position (unlike balance sheet)
def net_sales(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    return read_income_statement_entry(stock_ticker,
                                       ['Revenues', 'Net Sales'],
                                       date, annual, ttm)


def cost_of_goods_services(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    return read_income_statement_entry(stock_ticker,
                                       ['Costs and Expenses', 'Cost of Goods and Services Sold'],
                                       date, annual, ttm)


def research_development_expense(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    return read_income_statement_entry(stock_ticker,
                                       ['Costs and Expenses', 'Research and Development Expense'],
                                       date, annual, ttm)


def selling_general_administrative(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    return read_income_statement_entry(stock_ticker,
                                       ['Costs and Expenses', 'Selling, General and Administrative'],
                                       date, annual, ttm)


def accumulated_depreciation_amortization(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    return read_income_statement_entry(stock_ticker,
                                       ['Costs and Expenses',
                                        'Depreciation, Depletion and Amortization, Nonproduction'],
                                       date, annual, ttm)


def total_operating_expenses(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    return read_income_statement_entry(stock_ticker,
                                       ['Costs and Expenses', 'Total Operating Expenses'],
                                       date, annual, ttm)


def operating_income(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    return read_income_statement_entry(stock_ticker,
                                       ['Operating Income (Loss) / EBIT', ''], date, annual, ttm)


def interest_income(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    for el in ['Interest and Dividend Income', 'Interest Income']:
        ans = read_income_statement_entry(stock_ticker,
                                          ['Non-Operating Income (Expense)', el],
                                          date, annual, ttm)
        if not np.isnan(ans):
            return ans
    return np.nan


def interest_expense(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    return read_income_statement_entry(stock_ticker,
                                       ['Non-Operating Income (Expense)', 'Interest Expense'],
                                       date, annual, ttm)


def interest_income_expense_net(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    return read_income_statement_entry(stock_ticker,
                                       ['Non-Operating Income (Expense)', 'Interest Income (Expense), Net'],
                                       date, annual, ttm)


def non_operating_income(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    return read_income_statement_entry(stock_ticker,
                                       ['Non-Operating Income (Expense)', 'Non-Operating Income (Expense)'],
                                       date, annual, ttm)


def income_before_tax_minority_interest(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    return read_income_statement_entry(stock_ticker,
                                       [
                                           'Income (Loss) from Continuing Operations before Income Taxes, Noncontrolling Interest',
                                           ''],
                                       date, annual, ttm)


def income_tax_expense(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    return read_income_statement_entry(stock_ticker,
                                       ['Income Tax Expense (Benefit)', ''],
                                       date, annual, ttm)


def net_income(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    for el in ['Net Income (Loss)',
               'Net Income (Loss) Available to Common Stockholders, Basic',
               'Net Income Loss Attributable to Noncontrolling (Minority) Interest']:
        ans = read_income_statement_entry(stock_ticker,
                                          [el, ''],
                                          date, annual, ttm)
        if not np.isnan(ans):
            return ans
    return np.nan


def preferred_dividends(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    return read_income_statement_entry(stock_ticker,
                                       ['Preferred Stock Dividends', ''],
                                       date, annual, ttm)


def cash_flow_operating_activities(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    return read_cash_flow_statement_entry(stock_ticker,
                                          ['Operating Activities',
                                           'Net Cash Provided by (Used in) Operating Activities'],
                                          date, annual, ttm)


def cash_flow_investing_activities(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    return read_cash_flow_statement_entry(stock_ticker,
                                          ['Investing Activities',
                                           'Net Cash Provided by (Used in) Investing Activities'],
                                          date, annual, ttm)


def cash_flow_financing_activities(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    return read_cash_flow_statement_entry(stock_ticker,
                                          ['Financing Activities',
                                           'Net Cash Provided by (Used in) Financing Activities'],
                                          date, annual, ttm)
