from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import config
import os
import data_scraping.excel_helpers as excel


# for balance sheets, when doing trailing twelve months, we compute the mean
def read_balance_sheet_entry(stock_ticker, entry_name, date=datetime.now(), annual=True, ttm=False): # ttm false for now till I do Quarterly scraping
    if annual:
        if ttm:
            return np.mean([excel.read_entry_from_csv(stock_ticker,
                                                 config.balance_sheet_quarterly,
                                                 date - timedelta(days=i*90),
                                                 entry_name)
                            for i in range(4)])
    return excel.read_entry_from_csv(stock_ticker,
                                config.balance_sheet_quarterly if not annual else config.balance_sheet_yearly,
                                date,
                                entry_name)


def read_income_statement_entry(stock_ticker, entry_name, date=datetime.now(), annual=True, ttm=False):
    if annual:
        if ttm:
            return np.sum([excel.read_entry_from_csv(stock_ticker,
                                                config.income_statement_quarterly,
                                                date - timedelta(days=i*90),
                                                entry_name)
                           for i in range(4)])
    return excel.read_entry_from_csv(stock_ticker,
                                config.income_statement_quarterly if not annual else config.income_statement_yearly,
                                date,
                                entry_name)


def read_cash_flow_statement_entry(stock_ticker, entry_name, date=datetime.now(), annual=True, ttm=False):
    if annual:
        if ttm:
            return np.sum([excel.read_entry_from_csv(stock_ticker,
                                                config.cash_flow_statement_quarterly,
                                                date - timedelta(days=i*90),
                                                entry_name)
                           for i in range(4)])
    return excel.read_entry_from_csv(stock_ticker,
                                config.cash_flow_statement_quarterly if not annual else config.cash_flow_statement_yearly,
                                date,
                                entry_name)


def cash_and_cash_equivalents(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    return read_balance_sheet_entry(stock_ticker, 'Cash and Cash Equivalents', date, annual, ttm)


def current_marketable_securities(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    return read_balance_sheet_entry(stock_ticker, 'Marketable Securities Current', date, annual, ttm)


def gross_accounts_receivable(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    return read_balance_sheet_entry(stock_ticker, 'Gross Accounts Receivable', date, annual, ttm)


def allowances_for_doubtful_accounts(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    return read_balance_sheet_entry(stock_ticker, 'Allowances for Doubtful Accounts', date, annual, ttm)


def net_accounts_receivable(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    return read_balance_sheet_entry(stock_ticker, 'Net Accounts Receivable', date, annual, ttm)


def current_prepaid_expenses(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    return read_balance_sheet_entry(stock_ticker, 'Prepaid Expense, Current', date, annual, ttm)


def net_inventory(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    return read_balance_sheet_entry(stock_ticker, 'Inventory, Net', date, annual, ttm)


def current_income_taxes_receivable(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    return read_balance_sheet_entry(stock_ticker, 'Income Taxes Receivable, Current', date, annual, ttm)


def assets_held_for_sale(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    return read_balance_sheet_entry(stock_ticker, 'Assets Held-for-sale', date, annual, ttm)


def current_deferred_tax_assets(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    return read_balance_sheet_entry(stock_ticker, 'Deferred Tax Assets, Current', date, annual, ttm)


def other_current_assets(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    return read_balance_sheet_entry(stock_ticker, 'Other Assets, Current', date, annual, ttm)


def current_total_assets(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    return read_balance_sheet_entry(stock_ticker, 'Total Assets, Current', date, annual, ttm)


def non_current_marketable_securities(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    return read_balance_sheet_entry(stock_ticker, 'Marketable Securities Non Current', date, annual, ttm)


def net_property_plant_equipment(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    return read_balance_sheet_entry(stock_ticker, 'Property, Plant and Equipment, Net', date, annual, ttm)


def operating_lease_right_of_use_assets(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    return read_balance_sheet_entry(stock_ticker, 'Operating Lease Right-of-use Assets', date, annual, ttm)


def non_current_deferred_tax_assets(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    return read_balance_sheet_entry(stock_ticker, 'Deferred Tax Assets Non Current', date, annual, ttm)


def goodwill(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    return read_balance_sheet_entry(stock_ticker, 'Goodwill', date, annual, ttm)


def net_intangible_assets(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    return read_balance_sheet_entry(stock_ticker, 'Intangible Assets, Net (Excluding Goodwill)', date, annual, ttm)


def total_intangible_assets(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    return read_balance_sheet_entry(stock_ticker, 'Total Intangible Assets', date, annual, ttm)


def other_non_current_assets(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    return read_balance_sheet_entry(stock_ticker, 'Other Non Current Assets', date, annual, ttm)


def total_non_current_assets(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    return read_balance_sheet_entry(stock_ticker, 'Total Non Current Assets', date, annual, ttm)


def total_assets(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    return read_balance_sheet_entry(stock_ticker, 'Total Assets', date, annual, ttm)


def long_term_debt_current_maturities(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    return read_balance_sheet_entry(stock_ticker, 'Long-term Debt, Current Maturities', date, annual, ttm)


def current_accounts_payable(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    return read_balance_sheet_entry(stock_ticker, 'Accounts Payable, Current', date, annual, ttm)


def current_deferred_revenues(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    return read_balance_sheet_entry(stock_ticker, 'Current Deferred Revenues', date, annual, ttm)


def current_accrued_liabilities(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    return read_balance_sheet_entry(stock_ticker, 'Accrued Liabilities, Current', date, annual, ttm)


def current_total_liabilities(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    return read_balance_sheet_entry(stock_ticker, 'Total Current Liabilities', date, annual, ttm)


def total_non_current_liabilities(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    return read_balance_sheet_entry(stock_ticker, 'Total Long-Term Liabilities', date, annual, ttm)


def total_liabilities(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    return read_balance_sheet_entry(stock_ticker, 'Total Liabilities', date, annual, ttm)


def preferred_stock_value(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    return read_balance_sheet_entry(stock_ticker, 'Preferred Stock, Value, Issued', date, annual, ttm)


def additional_paid_in_capital(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    return read_balance_sheet_entry(stock_ticker, 'Additional Paid in Capital', date, annual, ttm)


def retained_earnings(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    return read_balance_sheet_entry(stock_ticker, 'Retained Earnings (Accumulated Deficit)', date, annual, ttm)


def accumulated_other_comprehensive_income(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    return read_balance_sheet_entry(stock_ticker, 'Accumulated Other Comprehensive Income (Loss)', date, annual, ttm)


def total_shares_outstanding(stock_ticker, date=datetime.now(), diluted=True, annual=True, ttm=False):
    entry = 'Weighted Average Number of Shares Outstanding, Diluted' if diluted else 'Weighted Average Number of Shares Outstanding, Basic'
    return read_balance_sheet_entry(stock_ticker, entry, date, annual, ttm)


def total_shareholders_equity(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    return read_balance_sheet_entry(stock_ticker, 'Stockholders\' Equity Attributable to Parent', date, annual, ttm)


# print(cash_and_cash_equivalents('FB'))

# for income statements and cash flow statements, when doing trailing twelve months, we compute the sum
# by default, we use annual because its accumulation instead of position (unlike balance sheet)
def net_sales(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    return read_income_statement_entry(stock_ticker, 'Net Sales', date, annual, ttm)


def cost_of_goods_services(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    return read_income_statement_entry(stock_ticker, 'Cost of Goods and Services Sold', date, annual, ttm)


def research_development(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    return read_income_statement_entry(stock_ticker, 'Research and Development Expense', date, annual, ttm)


def selling_general_administrative(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    return read_income_statement_entry(stock_ticker, 'Selling, General and Administrative', date, annual, ttm)


def accumulated_depreciation_amortization(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    return read_income_statement_entry(stock_ticker, 'Depreciation, Depletion and Amortization, Nonproduction', date, annual, ttm)


def total_operating_expenses(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    return read_income_statement_entry(stock_ticker, 'Total Operating Expenses', date, annual, ttm)


def operating_income(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    return read_income_statement_entry(stock_ticker, 'Operating Income (Loss) / EBIT', date, annual, ttm)


def interest_income(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    return read_income_statement_entry(stock_ticker, 'Investment Income, Interest', date, annual, ttm)


def interest_expense(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    return read_income_statement_entry(stock_ticker, 'Interest Expense', date, annual, ttm)


def interest_income_expense_net(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    return read_income_statement_entry(stock_ticker, 'Interest Income (Expense), Net', date, annual, ttm)


def non_operating_income(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    return read_income_statement_entry(stock_ticker, 'Non-Operating Income (Expense)', date, annual, ttm)


def income_before_tax_minority_interest(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    return read_income_statement_entry(stock_ticker, 'Income (Loss) from Continuing Operations before Income Taxes, Noncontrolling Interest', date, annual, ttm)


def income_tax_expense(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    return read_income_statement_entry(stock_ticker, 'Income Tax Expense (Benefit)', date, annual, ttm)


def minority_interest(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    return read_income_statement_entry(stock_ticker, 'Income Tax Expense (Benefit)', date, annual, ttm)


def net_income(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    return read_income_statement_entry(stock_ticker, 'Net Income (Loss)', date, annual, ttm)


def net_income_attributable_to_shareholders(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    return read_income_statement_entry(stock_ticker, 'Net Income (Loss) Available to Common Stockholders, Basic', date, annual, ttm)


def preferred_dividends(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    return 0 # TODO


def cash_flow_operating_activities(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    return read_cash_flow_statement_entry(stock_ticker, 'Operating Activities', date, annual, ttm)


def cash_flow_investing_activities(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    return read_cash_flow_statement_entry(stock_ticker, 'Investing Activities', date, annual, ttm)


def cash_flow_financing_activities(stock_ticker, date=datetime.now(), annual=True, ttm=False):
    return read_cash_flow_statement_entry(stock_ticker, 'Financing Activities', date, annual, ttm)

