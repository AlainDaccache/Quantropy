from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import config
import os
import data_scraping.excel_helpers as excel
import math

'''
We can read an entry
- at the start of fiscal year --> annual = True, ttm = False
- at the start of a quarter --> annual = False, ttm = False
- as an average (for balance sheet, since position) or sum (for income and cash flow statements, since cumulative) 
during a year --> annual = True, ttm = True
'''

# By default, we read the most recent position for balance sheets
def read_balance_sheet_entry(stock, entry_name, date=datetime.now(), lookback_period=timedelta(days=0),
                             annual=False, ttm=False):
    path = os.path.join(config.FINANCIAL_STATEMENTS_DIR_PATH, stock + '.xlsx')
    if ttm and annual:
        return np.mean([excel.read_entry_from_csv(path=path,
                                                  sheet_name=config.balance_sheet_quarterly,
                                                  y=entry_name,
                                                  x=date,
                                                  lookback_index=math.floor(i + (lookback_period.days / 90)))
                        for i in range(4)])

    return excel.read_entry_from_csv(path=path,  # if not (annual or ttm) means both annual and ttm should be false
                                     sheet_name=config.balance_sheet_quarterly if not (
                                             annual or ttm) else config.balance_sheet_yearly,
                                     y=entry_name,
                                     x=date,
                                     lookback_index=math.floor(lookback_period.days / 90) if not (
                                             annual or ttm) else math.floor(
                                         lookback_period.days / 365))


def read_income_statement_entry(stock, entry_name, date=datetime.now(), lookback_period=timedelta(days=0),
                                annual=True, ttm=False):
    path = os.path.join(config.FINANCIAL_STATEMENTS_DIR_PATH, stock + '.xlsx')
    if annual and ttm:
        return np.sum([excel.read_entry_from_csv(path=path,
                                                 sheet_name=config.income_statement_quarterly,
                                                 y=entry_name,
                                                 x=date,
                                                 lookback_index=math.floor(i + (lookback_period.days / 90)))
                       for i in range(4)])
    return excel.read_entry_from_csv(path=path,
                                     sheet_name=config.income_statement_quarterly if not annual else config.income_statement_yearly,
                                     y=entry_name,
                                     x=date,
                                     lookback_index=math.floor(lookback_period.days / 90) if not annual else math.floor(
                                         lookback_period.days / 365))


def read_cash_flow_statement_entry(stock, entry_name, date=datetime.now(),
                                   lookback_period=timedelta(days=0), annual=True, ttm=False):
    path = os.path.join(config.FINANCIAL_STATEMENTS_DIR_PATH, stock + '.xlsx')
    if annual and ttm:
        return np.sum([excel.read_entry_from_csv(path=path,
                                                 sheet_name=config.cash_flow_statement_quarterly,
                                                 y=entry_name,
                                                 x=date,
                                                 lookback_index=math.floor(i + (lookback_period.days / 90)))
                       for i in range(4)])
    return excel.read_entry_from_csv(path=path,
                                     sheet_name=config.cash_flow_statement_quarterly if not (
                                                 annual or ttm) else config.cash_flow_statement_yearly,
                                     x=date,
                                     y=entry_name,
                                     lookback_index=math.floor(lookback_period.days / 90) if not (
                                                 annual or ttm) else math.floor(
                                         lookback_period.days / 365))


'''
Balance Sheet: preferably get the most recent (because it's a statement of position), 
so quarterly instead of yearly by default, ttm false by default (otherwise would compute average)
'''


def cash_and_cash_equivalents(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=False,
                              ttm=False):
    return read_balance_sheet_entry(stock=stock,
                                    entry_name=['Assets', 'Current Assets', 'Cash and Cash Equivalents'],
                                    date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)


def current_marketable_securities(stock, date=datetime.now(), lookback_period=timedelta(days=0),
                                  annual=False, ttm=False):
    return read_balance_sheet_entry(stock=stock,
                                    entry_name=['Assets', 'Current Assets',
                                                'Marketable Securities Current'],
                                    date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)


def gross_accounts_receivable(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=False,
                              ttm=False):
    return read_balance_sheet_entry(stock=stock,
                                    entry_name=['Assets', 'Current Assets', 'Gross Accounts Receivable'],
                                    date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)


def allowances_for_doubtful_accounts(stock, date=datetime.now(), lookback_period=timedelta(days=0),
                                     annual=False, ttm=False):
    return read_balance_sheet_entry(stock=stock,
                                    entry_name=['Assets', 'Current Assets',
                                                'Allowances for Doubtful Accounts'],
                                    date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)


def net_accounts_receivable(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=False,
                            ttm=False):
    return read_balance_sheet_entry(stock=stock,
                                    entry_name=['Assets', 'Current Assets', 'Net Accounts Receivable'],
                                    date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)


def current_prepaid_expenses(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=False,
                             ttm=False):
    return read_balance_sheet_entry(stock=stock,
                                    entry_name=['Assets', 'Current Assets', 'Prepaid Expense, Current'],
                                    date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)


def net_inventory(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=False, ttm=False):
    return read_balance_sheet_entry(stock=stock,
                                    entry_name=['Assets', 'Current Assets', 'Inventory, Net'],
                                    date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)


def current_income_taxes_receivable(stock, date=datetime.now(), lookback_period=timedelta(days=0),
                                    annual=False, ttm=False):
    return read_balance_sheet_entry(stock=stock,
                                    entry_name=['Assets', 'Current Assets',
                                                'Income Taxes Receivable, Current'],
                                    date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)


def assets_held_for_sale(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=False,
                         ttm=False):
    return read_balance_sheet_entry(stock=stock,
                                    entry_name=['Assets', 'Current Assets', 'Assets Held-for-sale'],
                                    date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)


def current_deferred_tax_assets(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=False,
                                ttm=False):
    return read_balance_sheet_entry(stock=stock,
                                    entry_name=['Assets', 'Current Assets', 'Deferred Tax Assets, Current'],
                                    date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)


def other_current_assets(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=False,
                         ttm=False):
    return read_balance_sheet_entry(stock=stock,
                                    entry_name=['Assets', 'Current Assets', 'Other Assets, Current'],
                                    date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)


def current_total_assets(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=False,
                         ttm=False):
    return read_balance_sheet_entry(stock=stock,
                                    entry_name=['Assets', 'Current Assets', 'Total Current Assets'],
                                    date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)


def non_current_marketable_securities(stock, date=datetime.now(), lookback_period=timedelta(days=0),
                                      annual=False, ttm=False):
    return read_balance_sheet_entry(stock=stock,
                                    entry_name=['Assets', 'Non Current Assets',
                                                'Marketable Securities Non Current'],
                                    date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)


def net_property_plant_equipment(stock, date=datetime.now(), lookback_period=timedelta(days=0),
                                 annual=False, ttm=False):
    return read_balance_sheet_entry(stock=stock,
                                    entry_name=['Assets', 'Non Current Assets',
                                                'Property, Plant and Equipment, Net'],
                                    date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)


def operating_lease_right_of_use_assets(stock, date=datetime.now(), lookback_period=timedelta(days=0),
                                        annual=False, ttm=False):
    return read_balance_sheet_entry(stock=stock,
                                    entry_name=['Assets', 'Non Current Assets',
                                                'Operating Lease Right-of-use Assets'],
                                    date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)


def non_current_deferred_tax_assets(stock, date=datetime.now(), lookback_period=timedelta(days=0),
                                    annual=False, ttm=False):
    return read_balance_sheet_entry(stock=stock,
                                    entry_name=['Assets', 'Non Current Assets',
                                                'Deferred Tax Assets Non Current'],
                                    date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)


def goodwill(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=False, ttm=False):
    return read_balance_sheet_entry(stock=stock,
                                    entry_name=['Assets', 'Non Current Assets', 'Goodwill'],
                                    date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)


def net_intangible_assets(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=False,
                          ttm=False):
    return read_balance_sheet_entry(stock=stock,
                                    entry_name=['Assets', 'Non Current Assets',
                                                'Intangible Assets, Net (Excluding Goodwill)'],
                                    date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)


def total_intangible_assets(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=False,
                            ttm=False):
    return read_balance_sheet_entry(stock=stock,
                                    entry_name=['Assets', 'Non Current Assets', 'Total Intangible Assets'],
                                    date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)


def other_non_current_assets(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=False,
                             ttm=False):
    return read_balance_sheet_entry(stock=stock,
                                    entry_name=['Assets', 'Non Current Assets', 'Other Non Current Assets'],
                                    date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)


def total_non_current_assets(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=False,
                             ttm=False):
    return read_balance_sheet_entry(stock=stock,
                                    entry_name=['Assets', 'Non Current Assets', 'Total Non Current Assets'],
                                    date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)


def total_assets(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=False, ttm=False):
    return read_balance_sheet_entry(stock=stock,
                                    entry_name=['Assets', 'Total Assets', 'Total Assets'],
                                    date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)


def long_term_debt_current_maturities(stock, date=datetime.now(), lookback_period=timedelta(days=0),
                                      annual=False, ttm=False):
    return read_balance_sheet_entry(stock=stock,
                                    entry_name=['Liabilities and Shareholders\' Equity', 'Liabilities',
                                                'Long-term Debt, Current Maturities'],
                                    date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)


def current_accounts_payable(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=False,
                             ttm=False):
    return read_balance_sheet_entry(stock=stock,
                                    entry_name=['Liabilities and Shareholders\' Equity', 'Liabilities',
                                                'Accounts Payable, Current'],
                                    date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)


def current_deferred_revenues(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=False,
                              ttm=False):
    return read_balance_sheet_entry(stock=stock,
                                    entry_name=['Liabilities and Shareholders\' Equity', 'Liabilities',
                                                'Current Deferred Revenues'],
                                    date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)


def current_accrued_liabilities(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=False,
                                ttm=False):
    return read_balance_sheet_entry(stock=stock,
                                    entry_name=['Liabilities and Shareholders\' Equity', 'Liabilities',
                                                'Accrued Liabilities, Current'],
                                    date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)


def current_total_liabilities(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=False,
                              ttm=False):
    return read_balance_sheet_entry(stock=stock,
                                    entry_name=['Liabilities and Shareholders\' Equity', 'Liabilities',
                                                'Total Current Liabilities'],
                                    date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)


def long_term_debt_excluding_current_portion(stock, date=datetime.now(), lookback_period=timedelta(days=0),
                                             annual=False, ttm=False):
    return read_balance_sheet_entry(stock=stock,
                                    entry_name=['Liabilities and Shareholders\' Equity', 'Liabilities',
                                                'Long-term Debt, Noncurrent Maturities'],
                                    date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)


def total_long_term_debt(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=False,
                         ttm=False):
    return long_term_debt_current_maturities(stock=stock, date=date, lookback_period=lookback_period,
                                             annual=annual, ttm=ttm) + \
           long_term_debt_excluding_current_portion(stock=stock, date=date, lookback_period=lookback_period,
                                                    annual=annual, ttm=ttm)


def total_non_current_liabilities(stock, date=datetime.now(), lookback_period=timedelta(days=0),
                                  annual=False, ttm=False):
    return read_balance_sheet_entry(stock=stock,
                                    entry_name=['Liabilities and Shareholders\' Equity', 'Liabilities',
                                                'Total Non Current Liabilities'],
                                    date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)


def total_liabilities(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=False,
                      ttm=False):
    return read_balance_sheet_entry(stock=stock,
                                    entry_name=['Liabilities and Shareholders\' Equity', 'Liabilities',
                                                'Total Liabilities'],
                                    date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)


def preferred_stock_value(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=False,
                          ttm=False):
    return read_balance_sheet_entry(stock=stock,
                                    entry_name=['Liabilities and Shareholders\' Equity',
                                                'Shareholders\' Equity',
                                                'Preferred stock=stock, Value, Issued'],
                                    date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)


def additional_paid_in_capital(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=False,
                               ttm=False):
    return read_balance_sheet_entry(stock=stock,
                                    entry_name=['Liabilities and Shareholders\' Equity',
                                                'Shareholders\' Equity',
                                                'Additional Paid in Capital'],
                                    date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)


def retained_earnings(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=False,
                      ttm=False):
    return read_balance_sheet_entry(stock=stock,
                                    entry_name=['Liabilities and Shareholders\' Equity',
                                                'Shareholders\' Equity',
                                                'Retained Earnings (Accumulated Deficit)'],
                                    date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)


def accumulated_other_comprehensive_income(stock, date=datetime.now(), lookback_period=timedelta(days=0),
                                           annual=False, ttm=False):
    return read_balance_sheet_entry(stock=stock,
                                    entry_name=['Liabilities and Shareholders\' Equity',
                                                'Shareholders\' Equity',
                                                'Accumulated Other Comprehensive Income (Loss)'],
                                    date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)


def total_shares_outstanding(stock, date=datetime.now(), lookback_period=timedelta(days=0),
                             diluted=True, annual=False, ttm=False):
    entry = ['Liabilities and Shareholders\' Equity', 'Shareholders\' Equity',
             'Weighted Average Number of Shares Outstanding, Diluted'] if diluted \
        else ['Liabilities and Shareholders\' Equity', 'Shareholders\' Equity',
              'Weighted Average Number of Shares Outstanding, Basic']
    return read_balance_sheet_entry(stock=stock, entry_name=entry, date=date,
                                    lookback_period=lookback_period, annual=annual, ttm=ttm)


def total_shareholders_equity(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=False,
                              ttm=False):
    return read_balance_sheet_entry(stock=stock,
                                    entry_name=['Liabilities and Shareholders\' Equity',
                                                'Shareholders\' Equity',
                                                'Stockholders\' Equity Attributable to Parent'],
                                    date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)


def net_sales(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=True, ttm=False):
    return read_income_statement_entry(stock=stock,
                                       entry_name=['Revenues', 'Net Sales'],
                                       date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)


def cost_of_goods_services(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=True,
                           ttm=False):
    return read_income_statement_entry(stock=stock,
                                       entry_name=['Costs and Expenses', 'Cost of Goods and Services Sold'],
                                       date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)


def research_development_expense(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=True,
                                 ttm=False):
    return read_income_statement_entry(stock=stock,
                                       entry_name=['Costs and Expenses',
                                                   'Research and Development Expense'],
                                       date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)


def selling_general_administrative(stock, date=datetime.now(), lookback_period=timedelta(days=0),
                                   annual=True, ttm=False):
    return read_income_statement_entry(stock=stock,
                                       entry_name=['Costs and Expenses',
                                                   'Selling, General and Administrative'],
                                       date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)


def accumulated_depreciation_amortization(stock, date=datetime.now(), lookback_period=timedelta(days=0),
                                          annual=True, ttm=False):
    return read_income_statement_entry(stock=stock,
                                       entry_name=['Costs and Expenses',
                                                   'Depreciation, Depletion and Amortization, Nonproduction'],
                                       date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)


def total_operating_expenses(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=True,
                             ttm=False):
    return read_income_statement_entry(stock=stock,
                                       entry_name=['Costs and Expenses', 'Total Operating Expenses'],
                                       date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)


def operating_income(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=True, ttm=False):
    return read_income_statement_entry(stock=stock,
                                       entry_name=['Operating Income (Loss) / EBIT', ' '], date=date,
                                       lookback_period=lookback_period, annual=annual, ttm=ttm)


def interest_income(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=True, ttm=False):
    for el in ['Interest and Dividend Income', 'Interest Income']:
        ans = read_income_statement_entry(stock=stock,
                                          entry_name=['Non-Operating Income (Expense)', el],
                                          date=date, lookback_period=lookback_period, annual=annual,
                                          ttm=ttm)
        if not np.isnan(ans):
            return ans
    return np.nan


def interest_expense(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=True, ttm=False):
    return read_income_statement_entry(stock=stock,
                                       entry_name=['Non-Operating Income (Expense)', 'Interest Expense'],
                                       date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)


def interest_income_expense_net(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=True,
                                ttm=False):
    return read_income_statement_entry(stock=stock,
                                       entry_name=['Non-Operating Income (Expense)',
                                                   'Interest Income (Expense), Net'],
                                       date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)


def non_operating_income(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=True,
                         ttm=False):
    return read_income_statement_entry(stock=stock,
                                       entry_name=['Non-Operating Income (Expense)',
                                                   'Non-Operating Income (Expense)'],
                                       date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)


def income_before_tax_minority_interest(stock, date=datetime.now(), lookback_period=timedelta(days=0),
                                        annual=True, ttm=False):
    return read_income_statement_entry(stock=stock,
                                       entry_name=[
                                           'Income (Loss) from Continuing Operations before Income Taxes, Noncontrolling Interest',
                                           ' '],
                                       date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)


def income_tax_expense(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=True,
                       ttm=False):
    return read_income_statement_entry(stock=stock,
                                       entry_name=['Income Tax Expense (Benefit)', 'Income Tax Expense (Benefit)'],
                                       date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)


def net_income(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=True, ttm=False):
    for el in ['Net Income (Loss)',
               'Net Income (Loss) Available to Common Stockholders, Basic',
               'Net Income Loss Attributable to Noncontrolling (Minority) Interest']:
        ans = read_income_statement_entry(stock=stock,
                                          entry_name=[el, el],
                                          date=date, lookback_period=lookback_period, annual=annual,
                                          ttm=ttm)
        if not np.isnan(ans):
            return ans
    return np.nan


def preferred_dividends(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=True,
                        ttm=False):
    return read_income_statement_entry(stock=stock,
                                       entry_name=['Preferred stock=stock Dividends', ' '],
                                       date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)


def cash_flow_operating_activities(stock, date=datetime.now(), lookback_period=timedelta(days=0),
                                   annual=True, ttm=False):
    return read_cash_flow_statement_entry(stock=stock,
                                          entry_name=['Operating Activities',
                                                      'Net Cash Provided by (Used in) Operating Activities'],
                                          date=date, lookback_period=lookback_period, annual=annual,
                                          ttm=ttm)


def change_in_depreciation_and_amortization(stock, date=datetime.now(), lookback_period=timedelta(days=0),
                                            annual=True, ttm=False):
    from_income_statement = read_income_statement_entry(stock=stock,
                                                        entry_name=['Costs and Expenses',
                                                                    'Depreciation and Amortization'],
                                                        date=date, lookback_period=lookback_period, annual=annual,
                                                        ttm=ttm)
    if not np.isnan(from_income_statement):
        return from_income_statement
    else:
        return read_cash_flow_statement_entry(stock=stock,
                                              entry_name=['Operating Activities',
                                                          'Depreciation and Amortization'],
                                              date=date, lookback_period=lookback_period, annual=annual,
                                              ttm=ttm)


def cash_flow_investing_activities(stock, date=datetime.now(), lookback_period=timedelta(days=0),
                                   annual=True, ttm=False):
    return read_cash_flow_statement_entry(stock=stock,
                                          entry_name=['Investing Activities',
                                                      'Net Cash Provided by (Used in) Investing Activities'],
                                          date=date, lookback_period=lookback_period, annual=annual,
                                          ttm=ttm)


def cash_flow_financing_activities(stock, date=datetime.now(), lookback_period=timedelta(days=0),
                                   annual=True, ttm=False):
    return read_cash_flow_statement_entry(stock=stock,
                                          entry_name=['Financing Activities',
                                                      'Net Cash Provided by (Used in) Financing Activities'],
                                          date=date, lookback_period=lookback_period, annual=annual,
                                          ttm=ttm)

