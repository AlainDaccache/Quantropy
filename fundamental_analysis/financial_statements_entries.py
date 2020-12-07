import pickle
from datetime import datetime, timedelta
from itertools import chain
from pprint import pprint

import numpy as np
import config
import os
import historical_data_collection.data_preparation_helpers as excel
import math
import pandas as pd


def read_financial_statement_entry(stock, financial_statement: str, entry_name: list, period: str,
                                   date=None,
                                   lookback_period: timedelta = timedelta(days=0)):
    '''
    Read an entry from a financial statement. By default, we read the most recent position for the balance sheet,
    and the trailing twelve months for the income statement and cash flow statement.

    :param financial_statement: 'Balance Sheet', 'Income Statement', 'Cash Flow Statement'
    :param stock:
    :param entry_name:
    :param date:
    :param lookback_period:
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months
    :return:
    '''
    # path = os.path.join(config.FINANCIAL_STATEMENTS_DIR_PATH, stock + '.xlsx')

    if period == 'FY':
        path_period = config.yearly
    elif period in ['Q', 'TTM', 'YTD']:
        path_period = config.quarterly
    else:
        raise Exception

    if date is None:
        date = datetime.now()

    # if period == 'FY':
    #     sheet_name = config.balance_sheet_yearly if financial_statement == 'Balance Sheet' \
    #         else config.income_statement_yearly if financial_statement == 'Income Statement' \
    #         else config.cash_flow_statement_yearly if financial_statement == 'Cash Flow Statement' \
    #         else Exception
    # elif period in ['Q', 'TTM', 'YTD']:
    #     sheet_name = config.balance_sheet_quarterly if financial_statement == 'Balance Sheet' \
    #         else config.income_statement_quarterly if financial_statement == 'Income Statement' \
    #         else config.cash_flow_statement_quarterly if financial_statement == 'Cash Flow Statement' \
    #         else Exception
    # else:
    #     raise Exception
    to_return = {}
    stock_list = [stock] if isinstance(stock, str) else stock
    date_list = [date] if isinstance(date, datetime) else date
    for stock_ in stock_list:
        # TODO perhaps diff multiples depending on year and statement
        with open(os.path.join(config.FINANCIAL_STATEMENTS_DIR_PATH_PICKLE, 'multiples.pkl'), 'rb') as handle:
            dictio = pickle.load(handle)
            multiple = dictio[stock_]

        path = os.path.join(config.FINANCIAL_STATEMENTS_DIR_PATH_PICKLE, path_period, financial_statement,
                            '{}.pkl'.format(stock_))
        if period == 'TTM':
            entries_for_ttm = {date: [excel.read_entry_from_pickle(path=path, y=entry_name, x=date,
                                                                   lookback_index=math.floor(
                                                                       i + (lookback_period.days / 90))) * multiple
                                      for i in range(4)]
                               for date in date_list}

            if financial_statement == 'Balance Sheet':
                entries_for_ttm = {k: np.mean(v) for k, v in entries_for_ttm.items()}

            else:  # income statement or cash flow statement, cumulative
                entries_for_ttm = {k: np.sum(v) for k, v in entries_for_ttm.items()}

            to_return[stock_] = pd.Series(entries_for_ttm)
        elif period == 'YTD':
            entries_for_ytd, i = {date: [] for date in date_list}, 0
            for date in date_list:
                while datetime((date - lookback_period).year, 1, 1) + timedelta(days=i * 90) < date:
                    entry = excel.read_entry_from_pickle(path=path,
                                                         y=entry_name,
                                                         x=datetime((date - lookback_period).year, 1, 1) + timedelta(
                                                             days=i * 90),
                                                         lookback_index=math.floor(
                                                             lookback_period.days / 90)) * multiple
                    i = i + 1
                    entries_for_ytd[date].append(entry)

            if financial_statement == 'Balance Sheet':
                entries_for_ytd = {k: np.mean(v) for k, v in entries_for_ytd.items()}

            else:  # income statement or cash flow statement, cumulative
                entries_for_ytd = {k: np.sum(v) for k, v in entries_for_ytd.items()}

            to_return[stock_] = pd.Series(entries_for_ytd)

        else:
            to_return[stock_] = excel.read_entry_from_pickle(path=path, y=entry_name, x=date,
                                                             lookback_index=math.floor(
                                                                 lookback_period.days / 90) if period == 'Q'
                                                             else math.floor(lookback_period.days / 365)) * multiple
    if isinstance(stock, str):
        return_ = to_return[stock]
        if isinstance(return_, pd.Series):
            return_.name = stock
        return return_
    elif isinstance(date, datetime):
        return pd.Series(to_return, name=date)

    elif isinstance(stock, list) and isinstance(date, list):
        return pd.DataFrame.from_dict(to_return, orient='index')
    else:
        raise Exception


def try_multiple_entries(stock, statement, entries, lookback_period: timedelta, period: str, date=None):
    output = None
    if date is None:  # don't delete, useful for when doing len(date)
        date = datetime.now()
    for el in entries:
        try_ = read_financial_statement_entry(financial_statement=statement, stock=stock, entry_name=el,
                                              date=date, lookback_period=lookback_period, period=period)

        if not (isinstance(try_, pd.Series) or isinstance(try_, pd.DataFrame)):
            return try_

        elif isinstance(try_, pd.Series):
            output = pd.concat([output, try_], axis=0) if output is not None else try_
            if (isinstance(date, list) and len(date) == len(output)) \
                    or isinstance(stock, list) and len(stock) == len(output):
                return output

        elif isinstance(try_, pd.DataFrame):
            # TODO test when not all values are in same entry
            output = pd.concat([output, try_], axis=0) if output is not None else try_
            if output.shape == (len(stock), len(date)):
                return output

    return np.nan


'''Balance Sheet Entries'''


def cash_and_cash_equivalents(stock, date=None,
                              lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Assets', 'Current Assets', 'Cash and Cash Equivalents'],
                                          date=date, lookback_period=lookback_period, period=period)


def current_marketable_securities(stock, date=None,
                                  lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Assets', 'Current Assets', 'Marketable Securities Current'],
                                          date=date, lookback_period=lookback_period, period=period)


def gross_accounts_receivable(stock, date=None,
                              lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Assets', 'Current Assets', 'Gross Accounts Receivable'],
                                          date=date, lookback_period=lookback_period, period=period)


def allowances_for_doubtful_accounts(stock, date=None,
                                     lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Assets', 'Current Assets', 'Allowances for Doubtful Accounts'],
                                          date=date, lookback_period=lookback_period, period=period)


def net_accounts_receivable(stock, date=None,
                            lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Assets', 'Current Assets', 'Net Accounts Receivable'],
                                          date=date, lookback_period=lookback_period, period=period)


# TODO
def credit_sales(stock, date=None,
                 lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    pass


# TODO
def credit_purchases(stock, date=None,
                     lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    pass


def current_prepaid_expenses(stock, date=None,
                             lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Assets', 'Current Assets', 'Prepaid Expense, Current'],
                                          date=date, lookback_period=lookback_period, period=period)


def net_inventory(stock, date=None,
                  lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Assets', 'Current Assets', 'Inventory, Net'],
                                          date=date, lookback_period=lookback_period, period=period)


def current_income_taxes_receivable(stock, date=None,
                                    lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Assets', 'Current Assets',
                                                      'Income Taxes Receivable, Current'],
                                          date=date, lookback_period=lookback_period, period=period)


def assets_held_for_sale(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                         period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Assets', 'Current Assets', 'Assets Held-for-sale'],
                                          date=date, lookback_period=lookback_period, period=period)


def current_deferred_tax_assets(stock, date=None,
                                lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Assets', 'Current Assets', 'Deferred Tax Assets, Current'],
                                          date=date, lookback_period=lookback_period, period=period)


def other_current_assets(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                         period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Assets', 'Current Assets', 'Other Assets, Current'],
                                          date=date, lookback_period=lookback_period, period=period)


def current_total_assets(stock, date=None,
                         lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Assets', 'Current Assets', 'Total Current Assets'],
                                          date=date, lookback_period=lookback_period, period=period)


def non_current_marketable_securities(stock, date=None,
                                      lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Assets', 'Non Current Assets',
                                                      'Marketable Securities Non Current'],
                                          date=date, lookback_period=lookback_period, period=period)


def accumulated_depreciation_amortization(stock, date=None,
                                          lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Assets', 'Non Current Assets',
                                                      'Accumulated Depreciation and Amortization'],
                                          date=date, lookback_period=lookback_period, period=period)


def net_property_plant_equipment(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Assets', 'Non Current Assets',
                                                      'Property, Plant and Equipment, Net'],
                                          date=date, lookback_period=lookback_period, period=period)


def operating_lease_right_of_use_assets(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                                        period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Assets', 'Non Current Assets',
                                                      'Operating Lease Right-of-use Assets'],
                                          date=date, lookback_period=lookback_period, period=period)


def non_current_deferred_tax_assets(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                                    period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Assets', 'Non Current Assets',
                                                      'Deferred Tax Assets Non Current'],
                                          date=date, lookback_period=lookback_period, period=period)


def goodwill(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Assets', 'Non Current Assets', 'Goodwill'],
                                          date=date, lookback_period=lookback_period, period=period)


def net_intangible_assets(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                          period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Assets', 'Non Current Assets',
                                                      'Intangible Assets, Net (Excluding Goodwill)'],
                                          date=date, lookback_period=lookback_period, period=period)


def total_intangible_assets(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                            period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Assets', 'Non Current Assets', 'Total Intangible Assets'],
                                          date=date, lookback_period=lookback_period, period=period)


def other_non_current_assets(stock, date=None,
                             lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Assets', 'Non Current Assets', 'Other Non Current Assets'],
                                          date=date, lookback_period=lookback_period, period=period)


def total_non_current_assets(stock, date=None,
                             lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Assets', 'Non Current Assets', 'Total Non Current Assets'],
                                          date=date, lookback_period=lookback_period, period=period)


def total_assets(stock, date=None,
                 lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Assets', 'Total Assets', 'Total Assets'],
                                          date=date, lookback_period=lookback_period, period=period)


def long_term_debt_current_maturities(stock, date=None,
                                      lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Liabilities and Shareholders\' Equity', 'Liabilities',
                                                      'Long-term Debt, Current Maturities'],
                                          date=date, lookback_period=lookback_period, period=period)


def accounts_payable(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                     period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Liabilities and Shareholders\' Equity', 'Liabilities',
                                                      'Accounts Payable'],
                                          date=date, lookback_period=lookback_period, period=period)


def current_deferred_revenues(stock, date=None,
                              lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Liabilities and Shareholders\' Equity', 'Liabilities',
                                                      'Current Deferred Revenues'],
                                          date=date, lookback_period=lookback_period, period=period)


def current_accrued_liabilities(stock, date=None,
                                lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Liabilities and Shareholders\' Equity', 'Liabilities',
                                                      'Accrued Liabilities, Current'],
                                          date=date, lookback_period=lookback_period, period=period)


def current_total_liabilities(stock, date=None,
                              lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Liabilities and Shareholders\' Equity', 'Liabilities',
                                                      'Total Current Liabilities'],
                                          date=date, lookback_period=lookback_period, period=period)


def long_term_debt_excluding_current_portion(stock, date=None,
                                             lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Liabilities and Shareholders\' Equity', 'Liabilities',
                                                      'Long-term Debt, Noncurrent Maturities'],
                                          date=date, lookback_period=lookback_period, period=period)


def total_long_term_debt(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                         period: str = 'Q'):
    return long_term_debt_current_maturities(stock=stock, date=date, lookback_period=lookback_period,
                                             period=period) + \
           long_term_debt_excluding_current_portion(stock=stock, date=date, lookback_period=lookback_period,
                                                    period=period)


def total_non_current_liabilities(stock, date=None,
                                  lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Liabilities and Shareholders\' Equity', 'Liabilities',
                                                      'Total Non Current Liabilities'],
                                          date=date, lookback_period=lookback_period, period=period)


def total_liabilities(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                      period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Liabilities and Shareholders\' Equity', 'Liabilities',
                                                      'Total Liabilities'],
                                          date=date, lookback_period=lookback_period, period=period)


def preferred_stock_value(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                          period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Liabilities and Shareholders\' Equity',
                                                      'Shareholders\' Equity',
                                                      'Preferred Stock, Value, Issued'],
                                          date=date, lookback_period=lookback_period, period=period)


def additional_paid_in_capital(stock, date=None,
                               lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Liabilities and Shareholders\' Equity',
                                                      'Shareholders\' Equity',
                                                      'Additional Paid in Capital'],
                                          date=date, lookback_period=lookback_period, period=period)


def retained_earnings(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                      period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Liabilities and Shareholders\' Equity',
                                                      'Shareholders\' Equity',
                                                      'Retained Earnings (Accumulated Deficit)'],
                                          date=date, lookback_period=lookback_period, period=period)


def accumulated_other_comprehensive_income(stock, date=None,
                                           lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Liabilities and Shareholders\' Equity',
                                                      'Shareholders\' Equity',
                                                      'Accumulated Other Comprehensive Income (Loss)'],
                                          date=date, lookback_period=lookback_period, period=period)


def minority_interest(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                      period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Liabilities and Shareholders\' Equity',
                                                      'Shareholders\' Equity',
                                                      'Minority Interest'],
                                          date=date, lookback_period=lookback_period, period=period)


def total_shares_outstanding(stock, diluted_shares: bool = False, date=None,
                             lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    entry = ['Liabilities and Shareholders\' Equity', 'Shareholders\' Equity',
             'Weighted Average Number of Shares Outstanding, Diluted'] if diluted_shares \
        else ['Liabilities and Shareholders\' Equity', 'Shareholders\' Equity',
              'Weighted Average Number of Shares Outstanding, Basic']
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock, entry_name=entry, date=date,
                                          lookback_period=lookback_period, period=period)


def total_shareholders_equity(stock, date=None,
                              lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return try_multiple_entries(stock=stock, date=date, lookback_period=lookback_period, period=period,
                                statement='Balance Sheet',
                                entries=[['Liabilities and Shareholders\' Equity',
                                          'Shareholders\' Equity',
                                          'Stockholders\' Equity, Including Portion Attributable to Noncontrolling Interest'],
                                         ['Liabilities and Shareholders\' Equity',
                                          'Shareholders\' Equity',
                                          'Stockholders\' Equity Attributable to Parent']
                                         ])


'''Income Statement Entries'''


def net_sales(stock, date=None,
              lookback_period: timedelta = timedelta(days=0), period: str = 'TTM'):
    return read_financial_statement_entry(financial_statement='Income Statement', stock=stock,
                                          entry_name=['Revenues', 'Net Sales'],
                                          date=date, lookback_period=lookback_period, period=period)


def cost_of_goods_services(stock, date=None,
                           lookback_period: timedelta = timedelta(days=0), period: str = 'TTM'):
    return read_financial_statement_entry(financial_statement='Income Statement', stock=stock,
                                          entry_name=['Costs and Expenses', 'Cost of Goods and Services Sold'],
                                          date=date, lookback_period=lookback_period, period=period)


def research_development_expense(stock, date=None,
                                 lookback_period: timedelta = timedelta(days=0), period: str = 'TTM'):
    return read_financial_statement_entry(financial_statement='Income Statement', stock=stock,
                                          entry_name=['Costs and Expenses',
                                                      'Research and Development Expense'],
                                          date=date, lookback_period=lookback_period, period=period)


def selling_general_administrative(stock, date=None,
                                   lookback_period: timedelta = timedelta(days=0), period: str = 'TTM'):
    return read_financial_statement_entry(financial_statement='Income Statement', stock=stock,
                                          entry_name=['Costs and Expenses',
                                                      'Selling, General and Administrative'],
                                          date=date, lookback_period=lookback_period, period=period)


def total_operating_expenses(stock, date=None,
                             lookback_period: timedelta = timedelta(days=0), period: str = 'TTM'):
    return read_financial_statement_entry(financial_statement='Income Statement', stock=stock,
                                          entry_name=['Costs and Expenses', 'Total Operating Expenses'],
                                          date=date, lookback_period=lookback_period, period=period)


def operating_income(stock, date=None,
                     lookback_period: timedelta = timedelta(days=0), period: str = 'TTM'):
    return read_financial_statement_entry(financial_statement='Income Statement', stock=stock,
                                          entry_name=['Operating Income (Loss) / EBIT',
                                                      'Operating Income (Loss) / EBIT'],
                                          date=date,
                                          lookback_period=lookback_period, period=period)


def interest_income(stock, date=None,
                    lookback_period: timedelta = timedelta(days=0), period: str = 'TTM'):
    for el in ['Interest and Dividend Income', 'Interest Income']:
        ans = read_financial_statement_entry(financial_statement='Income Statement', stock=stock,
                                             entry_name=['Non-Operating Income (Expense)', el],
                                             date=date, lookback_period=lookback_period, period=period)
        if not np.isnan(ans):
            return ans
    return np.nan


def interest_expense(stock, date=None,
                     lookback_period: timedelta = timedelta(days=0), period: str = 'TTM'):
    return read_financial_statement_entry(financial_statement='Income Statement', stock=stock,
                                          entry_name=['Non-Operating Income (Expense)', 'Interest Expense'],
                                          date=date, lookback_period=lookback_period, period=period)


def interest_income_expense_net(stock, date=None,
                                lookback_period: timedelta = timedelta(days=0), period: str = 'TTM'):
    return read_financial_statement_entry(financial_statement='Income Statement', stock=stock,
                                          entry_name=['Non-Operating Income (Expense)',
                                                      'Interest Income (Expense), Net'],
                                          date=date, lookback_period=lookback_period, period=period)


def non_operating_income(stock, date=None,
                         lookback_period: timedelta = timedelta(days=0), period: str = 'TTM'):
    return read_financial_statement_entry(financial_statement='Income Statement', stock=stock,
                                          entry_name=['Non-Operating Income (Expense)',
                                                      'Non-Operating Income (Expense)'],
                                          date=date, lookback_period=lookback_period, period=period)


def income_tax_expense(stock, date=None,
                       lookback_period: timedelta = timedelta(days=0), period: str = 'TTM'):
    return read_financial_statement_entry(financial_statement='Income Statement', stock=stock,
                                          entry_name=['Income Tax Expense (Benefit)', 'Income Tax Expense (Benefit)'],
                                          date=date, lookback_period=lookback_period, period=period)


def net_income(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'TTM'):
    return try_multiple_entries(stock=stock, statement='Income Statement', date=date, lookback_period=lookback_period,
                                period=period,
                                entries=[['Net Income (Loss) Attributable to Parent',
                                          'Net Income (Loss) Attributable to Parent'],
                                         ['Net Income (Loss) Available to Common Stockholders, Basic',
                                          'Net Income (Loss) Available to Common Stockholders, Basic'],
                                         ['Net Income Loss Attributable to Noncontrolling (Minority) Interest',
                                          'Net Income Loss Attributable to Noncontrolling (Minority) Interest']
                                         ])


def preferred_dividends(stock, date=None,
                        lookback_period: timedelta = timedelta(days=0), period: str = 'TTM'):
    return np.nan_to_num(read_financial_statement_entry(financial_statement='Income Statement', stock=stock,
                                                        entry_name=['Preferred Stock Dividends', ' '],
                                                        date=date, lookback_period=lookback_period, period=period))


'''Cash Flow Statement Entries'''


def cash_flow_operating_activities(stock, date=None,
                                   lookback_period: timedelta = timedelta(days=0), period: str = 'TTM'):
    '''
    Operating cash flow is a measure of cash generated/consumed by a business from its operating activities

    Computed as Net Income + Depreciation & Amortization + Non-Cash Items (i.e. stock-based compensation, unrealized gains/losses...) - Changes in Net Working Capital

    Unlike EBITDA, cash from operations is adjusted all non-cash items and changes in net working capital. However, it excludes capital expenditures.

    :param stock:
    :param date:
    :param lookback_period:
    :param period:
    :return:
    '''
    return read_financial_statement_entry(financial_statement='Cash Flow Statement', stock=stock,
                                          entry_name=['Operating Activities',
                                                      'Net Cash Provided by (Used in) Operating Activities'],
                                          date=date, lookback_period=lookback_period, period=period)


def depreciation_and_amortization(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                                  period: str = 'TTM'):
    from_income_statement = read_financial_statement_entry(financial_statement='Income Statement', stock=stock,
                                                           entry_name=['Costs and Expenses',
                                                                       'Depreciation and Amortization'],
                                                           date=date, lookback_period=lookback_period, period=period)
    if not np.isnan(from_income_statement):
        return from_income_statement
    else:
        return read_financial_statement_entry(financial_statement='Cash Flow Statement', stock=stock,
                                              entry_name=['Operating Activities',
                                                          'Depreciation, Depletion and Amortization'],
                                              date=date, lookback_period=lookback_period, period=period)


def acquisition_property_plant_equipment(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                                         period: str = 'TTM'):
    return read_financial_statement_entry(financial_statement='Cash Flow Statement', stock=stock,
                                          entry_name=['Investing Activities',
                                                      'Payments to Acquire Property, Plant, and Equipment'],
                                          date=date, lookback_period=lookback_period, period=period)


def cash_flow_investing_activities(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                                   period: str = 'TTM'):
    return read_financial_statement_entry(financial_statement='Cash Flow Statement', stock=stock,
                                          entry_name=['Investing Activities',
                                                      'Net Cash Provided by (Used in) Investing Activities'],
                                          date=date, lookback_period=lookback_period, period=period)


def cash_flow_financing_activities(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                                   period: str = 'TTM'):
    return read_financial_statement_entry(financial_statement='Cash Flow Statement', stock=stock,
                                          entry_name=['Financing Activities',
                                                      'Net Cash Provided by (Used in) Financing Activities'],
                                          date=date, lookback_period=lookback_period, period=period)


def payments_for_dividends(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'TTM'):
    return read_financial_statement_entry(financial_statement='Cash Flow Statement', stock=stock,
                                          entry_name=['Financing Activities', 'Payments of Dividends'],
                                          date=date, lookback_period=lookback_period, period=period)


def net_debt_issued(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'TTM'):
    proceeds_from_issuance_of_debt = read_financial_statement_entry(financial_statement='Cash Flow Statement',
                                                                    stock=stock,
                                                                    entry_name=['Financing Activities',
                                                                                'Proceeds from Issuance of Long-term Debt'],
                                                                    date=date, lookback_period=lookback_period,
                                                                    period=period)
    repayment_of_debt = abs(read_financial_statement_entry(financial_statement='Cash Flow Statement', stock=stock,
                                                           entry_name=['Financing Activities',
                                                                       'Repayments of Long-term Debt'],
                                                           date=date, lookback_period=lookback_period, period=period))
    return proceeds_from_issuance_of_debt - repayment_of_debt


if __name__ == '__main__':
    # pprint(total_assets(stock='AAPL'))
    # pprint(total_assets(stock='AAPL', date=[datetime.now(), datetime(2019, 1, 1)]))
    # pprint(total_assets(stock=['AAPL', 'AMZN'], date=None))
    # pprint(total_assets(stock=['AAPL', 'AMZN'], date=[datetime.now(), datetime(2019, 1, 1)]))
    # pprint(net_income(stock='AMGN', period='TTM'))
    pprint(net_income(stock='AMGN', date=[datetime.now(), datetime(2019, 1, 1)], period='TTM'))
    pprint(net_income(stock=['AMGN', 'AXP'], date=datetime.now(), period='FY'))
    pprint(net_income(stock=['AMGN', 'MMM'], date=[datetime.now(), datetime(2019, 1, 1)]))
