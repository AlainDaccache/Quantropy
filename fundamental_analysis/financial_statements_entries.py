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

# def read_financial_statement_entry(stock, financial_statement: str, entry_name: list, period: str,
#                                    date=None, lookback_period: timedelta = timedelta(days=0)):
#     '''
#     Read an entry from a financial statement. By default, we read the most recent position for the balance sheet,
#     and the trailing twelve months for the IncomeStatement and cash flow statement.
# 
#     :param financial_statement: 'BalanceSheet', 'IncomeStatement', 'CashFlowStatement'
#     :param stock:
#     :param entry_name:
#     :param date:
#     :param lookback_period:
#     :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months
#     :return:
#     '''
#     # path = os.path.join(config.FINANCIAL_STATEMENTS_DIR_PATH, stock + '.xlsx')
# 
#     if period == 'FY':
#         path_period = config.yearly
#     elif period in ['Q', 'TTM', 'YTD']:
#         path_period = config.quarterly
#     else:
#         raise Exception
# 
#     if date is None:
#         date = datetime.now()
# 
#     # if period == 'FY':
#     #     sheet_name = config.balance_sheet_yearly if financial_statement == 'BalanceSheet' \
#     #         else config.income_statement_yearly if financial_statement == 'IncomeStatement' \
#     #         else config.cash_flow_statement_yearly if financial_statement == 'CashFlowStatement' \
#     #         else Exception
#     # elif period in ['Q', 'TTM', 'YTD']:
#     #     sheet_name = config.balance_sheet_quarterly if financial_statement == 'BalanceSheet' \
#     #         else config.income_statement_quarterly if financial_statement == 'IncomeStatement' \
#     #         else config.cash_flow_statement_quarterly if financial_statement == 'CashFlowStatement' \
#     #         else Exception
#     # else:
#     #     raise Exception
#     to_return = {}
#     stock_list = [stock] if isinstance(stock, str) else stock
#     date_list = [date] if isinstance(date, datetime) else date
#     for stock_ in stock_list:
#         # TODO perhaps diff multiples depending on year and statement
#         with open(os.path.join(config.FINANCIAL_STATEMENTS_DIR_PATH_PICKLE, 'multiples.pkl'), 'rb') as handle:
#             dictio = pickle.load(handle)
#             multiple = dictio[stock_]
# 
#         path = os.path.join(config.FINANCIAL_STATEMENTS_DIR_PATH_PICKLE, path_period, financial_statement,
#                             '{}.pkl'.format(stock_))
#         if period == 'TTM':
#             entries_for_ttm = {date: [excel.read_entry_from_pickle(path=path, y=entry_name, x=date,
#                                                                    lookback_index=math.floor(
#                                                                        i + (lookback_period.days / 90))) * multiple
#                                       for i in range(4)]
#                                for date in date_list}
# 
#             if financial_statement == 'BalanceSheet':
#                 entries_for_ttm = {k: np.mean(v) for k, v in entries_for_ttm.items()}
# 
#             else:  # IncomeStatement or cash flow statement, cumulative
#                 entries_for_ttm = {k: np.sum(v) for k, v in entries_for_ttm.items()}
# 
#             to_return[stock_] = pd.Series(entries_for_ttm)
#         elif period == 'YTD':
#             entries_for_ytd, i = {date: [] for date in date_list}, 0
#             for date in date_list:
#                 while datetime((date - lookback_period).year, 1, 1) + timedelta(days=i * 90) < date:
#                     entry = excel.read_entry_from_pickle(path=path,
#                                                          y=entry_name,
#                                                          x=datetime((date - lookback_period).year, 1, 1) + timedelta(
#                                                              days=i * 90),
#                                                          lookback_index=math.floor(
#                                                              lookback_period.days / 90)) * multiple
#                     i = i + 1
#                     entries_for_ytd[date].append(entry)
# 
#             if financial_statement == 'BalanceSheet':
#                 entries_for_ytd = {k: np.mean(v) for k, v in entries_for_ytd.items()}
# 
#             else:  # IncomeStatement or cash flow statement, cumulative
#                 entries_for_ytd = {k: np.sum(v) for k, v in entries_for_ytd.items()}
# 
#             to_return[stock_] = pd.Series(entries_for_ytd)
# 
#         else:
#             to_return[stock_] = excel.read_entry_from_pickle(path=path, y=entry_name, x=date,
#                                                              lookback_index=math.floor(
#                                                                  lookback_period.days / 90) if period == 'Q'
#                                                              else math.floor(lookback_period.days / 365)) * multiple
#     if isinstance(stock, str):
#         return_ = to_return[stock]
#         if isinstance(return_, pd.Series):
#             return_.name = stock
#         return return_
#     elif isinstance(date, datetime):
#         return pd.Series(to_return, name=date)
# 
#     elif isinstance(stock, list) and isinstance(date, list):
#         return pd.DataFrame.from_dict(to_return, orient='index')
#     else:
#         raise Exception


# def try_multiple_entries(stock, statement, entries, lookback_period: timedelta, period: str, date=None):
#     output = None
#     if date is None:  # don't delete, useful for when doing len(date)
#         date = datetime.now()
#     for el in entries:
#         try_ = read_financial_statement_entry(financial_statement=statement, stock=stock, entry_name=el,
#                                               date=date, lookback_period=lookback_period, period=period)
# 
#         if not (isinstance(try_, pd.Series) or isinstance(try_, pd.DataFrame)):
#             return try_
# 
#         elif isinstance(try_, pd.Series):
#             output = pd.concat([output, try_], axis=0) if output is not None else try_
#             if (isinstance(date, list) and len(date) == len(output)) \
#                     or isinstance(stock, list) and len(stock) == len(output):
#                 return output
# 
#         elif isinstance(try_, pd.DataFrame):
#             # TODO test when not all values are in same entry
#             output = pd.concat([output, try_], axis=0) if output is not None else try_
#             if output.shape == (len(stock), len(date)):
#                 return output
# 
#     return np.nan
from data.database.db_crud import read_financial_statement_entry, get_atlas_db_url, connect_to_mongo_engine

'''Balance Sheet Entries'''


def cash_and_cash_equivalents(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    """
    **Cash and Cash Equivalents** is the amount of money on deposit in the bank. It is composed of

    *   Cash: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).  t
        icker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']). ticker(s)
        in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']). ticker(s) in questio
        n. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']). ticker(s) in question.
        Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).

    *   Short-term investments:

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetime.now().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.

    :return:
    """
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['Assets', 'CurrentAssets', 'Cash and Cash Equivalents'],
                                          date=date, lookback_period=lookback_period, period=period)


def current_marketable_securities(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['Assets', 'CurrentAssets', 'CashAndShortTermInvestments',
                                                      'MarketableSecurities'],
                                          date=date, lookback_period=lookback_period, period=period)


def net_accounts_receivable(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['Assets', 'CurrentAssets', 'AccountsReceivable',
                                                      'NetAccountsReceivable'],
                                          date=date, lookback_period=lookback_period, period=period)


def allowances_for_doubtful_accounts(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                                     period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['Assets', 'CurrentAssets', 'AccountsReceivable',
                                                      'AllowanceForDoubtfulAccounts'],
                                          date=date, lookback_period=lookback_period, period=period)


def credit_sales(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    pass


def credit_purchases(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    pass


def current_prepaid_expenses(stock, date=None,
                             lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['Assets', 'CurrentAssets', 'PrepaidExpense'],
                                          date=date, lookback_period=lookback_period, period=period)


def net_inventory(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['Assets', 'CurrentAssets', 'InventoryNet'],
                                          date=date, lookback_period=lookback_period, period=period)


def current_income_taxes_receivable(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                                    period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['Assets', 'CurrentAssets', 'IncomeTaxesReceivable'],
                                          date=date, lookback_period=lookback_period, period=period)


def assets_held_for_sale(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['Assets', 'CurrentAssets', 'Assets Held-for-sale'],
                                          date=date, lookback_period=lookback_period, period=period)


def current_deferred_tax_assets(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['Assets', 'CurrentAssets', 'DeferredTaxAssets'],
                                          date=date, lookback_period=lookback_period, period=period)


def other_current_assets(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['Assets', 'CurrentAssets', 'Other Assets, Current'],
                                          date=date, lookback_period=lookback_period, period=period)


def total_current_assets(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['Assets', 'CurrentAssets', 'TotalCurrentAssets'],
                                          date=date, lookback_period=lookback_period, period=period)


def non_current_marketable_securities(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                                      period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['Assets', 'NonCurrentAssets', 'MarketableSecurities'],
                                          date=date, lookback_period=lookback_period, period=period)


def gross_property_plant_and_equipment(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                                       period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['Assets', 'NonCurrentAssets', 'PropertyPlantAndEquipment',
                                                      'GrossPropertyPlantAndEquipment'],
                                          date=date, lookback_period=lookback_period, period=period)


def accumulated_depreciation_amortization(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                                          period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['Assets', 'NonCurrentAssets', 'PropertyPlantAndEquipment',
                                                      'AccumulatedDepreciationAndAmortization'],
                                          date=date, lookback_period=lookback_period, period=period)


def net_property_plant_equipment(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['Assets', 'NonCurrentAssets', 'PropertyPlantAndEquipment',
                                                      'NetPropertyPlantAndEquipment'],
                                          date=date, lookback_period=lookback_period, period=period)


def operating_lease_right_of_use_assets(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                                        period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['Assets', 'NonCurrentAssets', 'OperatingLeaseRightOfUseAssets'],
                                          date=date, lookback_period=lookback_period, period=period)


def non_current_deferred_tax_assets(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                                    period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['Assets', 'NonCurrentAssets', 'DeferredTaxAssets'],
                                          date=date, lookback_period=lookback_period, period=period)


def goodwill(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['Assets', 'NonCurrentAssets', 'IntangibleAssets', 'Goodwill'],
                                          date=date, lookback_period=lookback_period, period=period)


def net_intangible_assets(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['Assets', 'NonCurrentAssets', 'IntangibleAssets',
                                                      'NetIntangibleAssetsExcludingGoodwill'],
                                          date=date, lookback_period=lookback_period, period=period)


def total_intangible_assets(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['Assets', 'NonCurrentAssets', 'IntangibleAssets',
                                                      'TotalIntangibleAssets'],
                                          date=date, lookback_period=lookback_period, period=period)


def other_non_current_assets(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['Assets', 'NonCurrentAssets', 'OtherNonCurrentAssets'],
                                          date=date, lookback_period=lookback_period, period=period)


def total_non_current_assets(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['Assets', 'NonCurrentAssets', 'TotalNonCurrentAssets'],
                                          date=date, lookback_period=lookback_period, period=period)


def total_assets(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['Assets', 'TotalAssets'],
                                          date=date, lookback_period=lookback_period, period=period)


def long_term_debt_current_maturities(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                                      period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['LiabilitiesAndShareholdersEquity', 'Liabilities',
                                                      'CurrentLiabilities', 'LongTermDebtCurrentMaturities'],
                                          date=date, lookback_period=lookback_period, period=period)


def accounts_payable(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['LiabilitiesAndShareholdersEquity', 'Liabilities',
                                                      'CurrentLiabilities', 'AccountsPayable'],
                                          date=date, lookback_period=lookback_period, period=period)


def current_deferred_revenues(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['LiabilitiesAndShareholdersEquity', 'Liabilities',
                                                      'CurrentLiabilities', 'DeferredRevenue'],
                                          date=date, lookback_period=lookback_period, period=period)


def current_operating_lease_liabilities(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                                        period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['LiabilitiesAndShareholdersEquity', 'Liabilities',
                                                      'CurrentLiabilities', 'OperatingLeaseLiability'],
                                          date=date, lookback_period=lookback_period, period=period)


def current_employee_related_liabilities(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                                         period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['LiabilitiesAndShareholdersEquity', 'Liabilities',
                                                      'CurrentLiabilities', 'EmployeeRelatedLiabilities'],
                                          date=date, lookback_period=lookback_period, period=period)


def current_accrued_income_taxes_liabilities(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                                             period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['LiabilitiesAndShareholdersEquity', 'Liabilities',
                                                      'CurrentLiabilities', 'AccruedIncomeTaxes'],
                                          date=date, lookback_period=lookback_period, period=period)


def current_income_taxes_payable(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                                 period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['LiabilitiesAndShareholdersEquity', 'Liabilities',
                                                      'CurrentLiabilities', 'IncomeTaxesPayable'],
                                          date=date, lookback_period=lookback_period, period=period)


def current_accrued_liabilities(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['LiabilitiesAndShareholdersEquity', 'Liabilities',
                                                      'CurrentLiabilities', 'AccruedLiabilities'],
                                          date=date, lookback_period=lookback_period, period=period)


def other_current_liabilities(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                              period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['LiabilitiesAndShareholdersEquity', 'Liabilities',
                                                      'CurrentLiabilities', 'OtherCurrentLiabilities'],
                                          date=date, lookback_period=lookback_period, period=period)


def total_current_liabilities(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['LiabilitiesAndShareholdersEquity', 'Liabilities',
                                                      'CurrentLiabilities', 'TotalCurrentLiabilities'],
                                          date=date, lookback_period=lookback_period, period=period)


def long_term_debt_excluding_current_portion(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                                             period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['LiabilitiesAndShareholdersEquity', 'Liabilities',
                                                      'NonCurrentLiabilities', 'LongTermDebtNonCurrentMaturities'],
                                          date=date, lookback_period=lookback_period, period=period)


def total_long_term_debt(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return long_term_debt_current_maturities(stock=stock, date=date, lookback_period=lookback_period, period=period) + \
           long_term_debt_excluding_current_portion(stock=stock, date=date, lookback_period=lookback_period,
                                                    period=period)


def defined_benefit_plan_non_current_liabilities(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                                                 period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['LiabilitiesAndShareholdersEquity', 'Liabilities',
                                                      'NonCurrentLiabilities', 'DefinedBenefitPlan'],
                                          date=date, lookback_period=lookback_period, period=period)


def accrued_income_taxes_non_current_liabilities(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                                                 period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['LiabilitiesAndShareholdersEquity', 'Liabilities',
                                                      'NonCurrentLiabilities', 'AccruedIncomeTaxes'],
                                          date=date, lookback_period=lookback_period, period=period)


def deferred_revenue_non_current_liabilities(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                                             period: str = 'Q'):
    """
    Also known as *long-term unearned revenue*
    
    :param stock: 
    :param date: 
    :param lookback_period: 
    :param period: 
    :return: 
    """
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['LiabilitiesAndShareholdersEquity', 'Liabilities',
                                                      'NonCurrentLiabilities', 'DeferredRevenue'],
                                          date=date, lookback_period=lookback_period, period=period)


def other_non_current_liabilities(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['LiabilitiesAndShareholdersEquity', 'Liabilities',
                                                      'NonCurrentLiabilities', 'OtherLiabilitiesNonCurrent'],
                                          date=date, lookback_period=lookback_period, period=period)


def total_non_current_liabilities(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['LiabilitiesAndShareholdersEquity', 'Liabilities',
                                                      'NonCurrentLiabilities', 'TotalNonCurrentLiabilities'],
                                          date=date, lookback_period=lookback_period, period=period)


def total_liabilities(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['LiabilitiesAndShareholdersEquity', 'Liabilities',
                                                      'TotalLiabilities'],
                                          date=date, lookback_period=lookback_period, period=period)


def preferred_stock_value(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['LiabilitiesAndShareholdersEquity',
                                                      'ShareholdersEquity', 'PreferredStockValueIssued'],
                                          date=date, lookback_period=lookback_period, period=period)


def common_stock_value_issued(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['LiabilitiesAndShareholdersEquity', 'ShareholdersEquity',
                                                      'CommonStockAndAdditionalPaidInCapital',
                                                      'CommonStockValueIssued'],
                                          date=date, lookback_period=lookback_period, period=period)


def additional_paid_in_capital(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['LiabilitiesAndShareholdersEquity', 'ShareholdersEquity',
                                                      'CommonStockAndAdditionalPaidInCapital',
                                                      'AdditionalPaidInCapital'],
                                          date=date, lookback_period=lookback_period, period=period)


def common_stocks_including_additional_paid_in_capital(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                                                       period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['LiabilitiesAndShareholdersEquity', 'ShareholdersEquity',
                                                      'CommonStockAndAdditionalPaidInCapital',
                                                      'CommonStocksIncludingAdditionalPaidInCapital'],
                                          date=date, lookback_period=lookback_period, period=period)


def retained_earnings(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['LiabilitiesAndShareholdersEquity',
                                                      'ShareholdersEquity', 'RetainedEarningsAccumulatedDeficit'],
                                          date=date, lookback_period=lookback_period, period=period)


def accumulated_other_comprehensive_income(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                                           period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['LiabilitiesAndShareholdersEquity', 'ShareholdersEquity',
                                                      'AccumulatedOtherComprehensiveIncomeLoss'],
                                          date=date, lookback_period=lookback_period, period=period)


def minority_interest(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['LiabilitiesAndShareholdersEquity', 'ShareholdersEquity',
                                                      'MinorityInterest'],
                                          date=date, lookback_period=lookback_period, period=period)


def total_shares_outstanding(stock, diluted_shares: bool = False, date=None,
                             lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    """

    :param stock:
    :param diluted_shares: Share dilution is when a company issues additional stock, reducing the ownership proportion
    of a current shareholder. Shares can be diluted through a conversion by holders of optionable securities, secondary
    offerings to raise additional capital, or offering new shares in exchange for acquisitions or services.
    :param date:
    :param lookback_period:
    :param period:
    :return:
    """
    entry = ['LiabilitiesAndShareholdersEquity', 'ShareholdersEquity', 'CommonStockAndAdditionalPaidInCapital',
             'WeightedAverageNumberOfSharesOutstandingDiluted'] if diluted_shares \
        else ['LiabilitiesAndShareholdersEquity', 'ShareholdersEquity', 'CommonStockAndAdditionalPaidInCapital',
              'WeightedAverageNumberOfSharesOutstandingBasic']
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock, entry_name=entry, date=date,
                                          lookback_period=lookback_period, period=period)


def total_shareholders_equity(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    # return try_multiple_entries(stock=stock, date=date, lookback_period=lookback_period, period=period,
    #                             statement='BalanceSheet',
    #                             entries=[['LiabilitiesAndShareholdersEquity',
    #                                       'ShareholdersEquity',
    #                                       'Stockholders\' Equity, Including Portion Attributable to Noncontrolling Interest'],
    #                                      ['LiabilitiesAndShareholdersEquity',
    #                                       'ShareholdersEquity',
    #                                       'Stockholders\' Equity Attributable to Parent']
    #                                      ])
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['LiabilitiesAndShareholdersEquity', 'ShareholdersEquity',
                                                      'StockholdersEquityAttributableToParent'],
                                          date=date, lookback_period=lookback_period, period=period)


'''IncomeStatement Entries'''


def net_sales(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'TTM'):
    return read_financial_statement_entry(financial_statement='IncomeStatement', stock=stock,
                                          entry_name=['Revenues', 'NetSales'],
                                          date=date, lookback_period=lookback_period, period=period)


def cost_of_goods_services(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'TTM'):
    return read_financial_statement_entry(financial_statement='IncomeStatement', stock=stock,
                                          entry_name=['CostOfGoodsAndServicesSold', 'CostOfGoodsAndServicesSold'],
                                          date=date, lookback_period=lookback_period, period=period)


def research_development_expense(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'TTM'):
    return read_financial_statement_entry(financial_statement='IncomeStatement', stock=stock,
                                          entry_name=['OperatingExpenses', 'ResearchAndDevelopmentExpense'],
                                          date=date, lookback_period=lookback_period, period=period)


def selling_general_administrative(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                                   period: str = 'TTM'):
    return read_financial_statement_entry(financial_statement='IncomeStatement', stock=stock,
                                          entry_name=['OperatingExpenses', 'SellingGeneralAndAdministrative'],
                                          date=date, lookback_period=lookback_period, period=period)


def total_operating_expenses(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'TTM'):
    return read_financial_statement_entry(financial_statement='IncomeStatement', stock=stock,
                                          entry_name=['OperatingExpenses', 'TotalOperatingExpenses'],
                                          date=date, lookback_period=lookback_period, period=period)


def operating_income(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'TTM'):
    """
    The **operating income** is the profit realized from a business's operations, after deducting operating expenses
    such as wages, depreciation, and cost of goods sold (COGS).

    :param stock:
    :param date:
    :param lookback_period:
    :param period:
    :return:
    """
    return read_financial_statement_entry(financial_statement='IncomeStatement', stock=stock,
                                          entry_name=['OperatingIncomeLoss'], date=date,
                                          lookback_period=lookback_period, period=period)


def interest_income(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'TTM'):
    # TODO try InterestAndDividendIncome also
    return read_financial_statement_entry(financial_statement='IncomeStatement', stock=stock,
                                          entry_name=['NonOperatingIncomeExpense', 'InterestIncome'], date=date,
                                          lookback_period=lookback_period, period=period)


def interest_expense(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'TTM'):
    return read_financial_statement_entry(financial_statement='IncomeStatement', stock=stock,
                                          entry_name=['NonOperatingIncomeExpense', 'InterestExpense'],
                                          date=date, lookback_period=lookback_period, period=period)


def interest_income_expense_net(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'TTM'):
    return read_financial_statement_entry(financial_statement='IncomeStatement', stock=stock,
                                          entry_name=['NonOperatingIncomeExpense', 'InterestIncomeExpenseNet'],
                                          date=date, lookback_period=lookback_period, period=period)


def non_operating_income(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'TTM'):
    return read_financial_statement_entry(financial_statement='IncomeStatement', stock=stock,
                                          entry_name=['NonOperatingIncomeExpense', 'NonOperatingIncomeExpense'],
                                          date=date, lookback_period=lookback_period, period=period)


def income_tax_expense(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'TTM'):
    return read_financial_statement_entry(financial_statement='IncomeStatement', stock=stock,
                                          entry_name=['IncomeTaxExpenseBenefit'],
                                          date=date, lookback_period=lookback_period, period=period)


def net_income(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'TTM'):
    return read_financial_statement_entry(financial_statement='IncomeStatement', stock=stock,
                                          entry_name=['NetIncomeLossAttributableToParent'],
                                          date=date, lookback_period=lookback_period, period=period)
    # return try_multiple_entries(stock=stock, statement='IncomeStatement', date=date, lookback_period=lookback_period,
    #                             period=period,
    #                             entries=[['NetIncomeLossAttributableToParent'],
    #                                      ['NetIncomeLossAvailableToCommonStockholdersBasic'],
    #                                      ['NetIncomeLossAttributableToMinorityInterest']])


def preferred_dividends(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'TTM'):
    return np.nan_to_num(read_financial_statement_entry(financial_statement='IncomeStatement', stock=stock,
                                                        entry_name=['PreferredStockDividends'],
                                                        date=date, lookback_period=lookback_period, period=period))


'''Cash Flow Statement Entries'''


def cash_flow_operating_activities(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                                   period: str = 'TTM'):
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
    return read_financial_statement_entry(financial_statement='CashFlowStatement', stock=stock,
                                          entry_name=['OperatingActivities',
                                                      'NetCashProvidedByUsedInOperatingActivities'],
                                          date=date, lookback_period=lookback_period, period=period)


def depreciation_and_amortization(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                                  period: str = 'TTM'):
    """
    This income statement expense reduces net income but has no effect on cash flow, so it must be added back
    when reconciling net income and cash flow from operations.

    :param stock:
    :param date:
    :param lookback_period:
    :param period:
    :return:
    """
    return read_financial_statement_entry(financial_statement='CashFlowStatement', stock=stock,
                                          entry_name=['AdjustmentsToReconcileNetIncome',
                                                      'DepreciationDepletionAndAmortization'],
                                          date=date, lookback_period=lookback_period, period=period)


def acquisition_property_plant_equipment(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                                         period: str = 'TTM'):
    return read_financial_statement_entry(financial_statement='CashFlowStatement', stock=stock,
                                          entry_name=['InvestingActivities',
                                                      'PaymentsToAcquirePropertyPlantAndEquipment'],
                                          date=date, lookback_period=lookback_period, period=period)


def cash_flow_investing_activities(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                                   period: str = 'TTM'):
    return read_financial_statement_entry(financial_statement='CashFlowStatement', stock=stock,
                                          entry_name=['InvestingActivities',
                                                      'NetCashProvidedByUsedInInvestingActivities'],
                                          date=date, lookback_period=lookback_period, period=period)


def cash_flow_financing_activities(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                                   period: str = 'TTM'):
    return read_financial_statement_entry(financial_statement='CashFlowStatement', stock=stock,
                                          entry_name=['FinancingActivities',
                                                      'NetCashProvidedByUsedInFinancingActivities'],
                                          date=date, lookback_period=lookback_period, period=period)


def payments_of_dividends(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'TTM'):
    return read_financial_statement_entry(financial_statement='CashFlowStatement', stock=stock,
                                          entry_name=['FinancingActivities', 'PaymentsOfDividends'],
                                          date=date, lookback_period=lookback_period, period=period)


def net_debt_issued(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'TTM'):
    proceeds_from_issuance_of_debt = read_financial_statement_entry(financial_statement='CashFlowStatement',
                                                                    stock=stock, entry_name=['Financing Activities',
                                                                                             'ProceedsFromIssuanceOfLongTermDebt'],
                                                                    date=date, lookback_period=lookback_period,
                                                                    period=period)
    repayment_of_debt = abs(read_financial_statement_entry(financial_statement='CashFlowStatement', stock=stock,
                                                           entry_name=['Financing Activities',
                                                                       'RepaymentsOfLongTermDebt'],
                                                           date=date, lookback_period=lookback_period, period=period))
    return proceeds_from_issuance_of_debt - repayment_of_debt


if __name__ == '__main__':
    # pprint(total_assets(stock='AAPL'))
    # pprint(total_assets(stock='AAPL', date=[datetime.now(), datetime(2019, 1, 1)]))
    # pprint(total_assets(stock=['AAPL', 'AMZN'], date=None))
    # pprint(total_assets(stock=['AAPL', 'AMZN'], date=[datetime.now(), datetime(2019, 1, 1)]))
    # pprint(net_income(stock='AMGN', period='TTM'))
    atlas_url = get_atlas_db_url(username='AlainDaccache', password='qwerty98', dbname='matilda-db')
    db = connect_to_mongo_engine(atlas_url)
    pprint(net_income(stock='AMGN', date=[datetime.now(), datetime(2019, 1, 1)], period='TTM'))
    pprint(net_income(stock=['AMGN', 'AXP'], date=datetime.now(), period='FY'))
    pprint(net_income(stock=['AMGN', 'MMM'], date=[datetime.now(), datetime(2019, 1, 1)]))
