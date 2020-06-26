import os
from datetime import datetime, timedelta
import pandas as pd
import company_analysis.financial_statements_entries as fi
import data_scraping.excel_helpers as excel
import config


def market_price(stock, date=datetime.today()):
    output = excel.read_entry_from_csv(stock, config.stock_prices_sheet_name, date, 'Adj Close')
    print('Market Price for {} on the {} is: {}'.format(stock, date, output))
    return output


def gross_profit(stock, date=datetime.today(), annual=True, ttm=False):
    return fi.net_sales(stock, date, annual, ttm) - fi.cost_of_goods_services(stock, date, annual, ttm)


def ebit(stock, date=datetime.today(), annual=True, ttm=False):
    try:
        return fi.net_income(stock, date) + fi.interest_expense(stock, date) + fi.income_tax_expense(stock, date)
    except:
        return fi.net_sales(stock, date) - fi.cost_of_goods_services(stock, date) - fi.total_operating_expenses(stock, date) - fi.accumulated_depreciation_amortization(stock, date)


def ebitda(stock, date, annual=True, ttm=False):
    output = ebit(stock, date) + fi.accumulated_depreciation_amortization(stock, date)
    print('EBITDA for {} on the {} is: {}'.format(stock, date, output))
    return output


def capex(stock, date, annual=True, ttm=False):
    ppe_delta = (fi.net_property_plant_equipment(stock, date, annual, ttm)
                 - fi.net_property_plant_equipment(stock, date - timedelta(days=365), annual, ttm))
    return ppe_delta + fi.accumulated_depreciation_amortization(stock, date, annual, ttm)


def debt_service(stock, date=datetime.now(), annual=True, ttm=True):
    return fi.interest_expense(stock, date, annual, ttm)  # TODO Review


def net_credit_sales(stock, date=datetime.now(), annual=True, ttm=True):
    return fi.net_sales(stock, date, annual, ttm) - fi.net_accounts_receivable(stock, date, annual, ttm)  # TODO Review


def working_capital(stock, date=datetime.now(), annual=True, ttm=True):
    return fi.current_total_assets(stock, date, annual, ttm) - fi.current_total_liabilities(stock, date, annual, ttm)


def market_capitalization(stock, date=datetime.now(), diluted_shares=True):
    shares_outstanding = fi.total_shares_outstanding(stock, date, diluted_shares)
    output = market_price(stock, date) * shares_outstanding
    print('Market Capitalization for {} on the {} is: {}'.format(stock, date, output))
    return output


def enterprise_value(stock, date=datetime.now(), annual=True, ttm=False):
    output = market_capitalization(stock, date) \
             + fi.total_liabilities(stock, date, annual, ttm) \
             - fi.cash_and_cash_equivalents(stock, date, annual, ttm)
    print('Enterprise Value for {} on the {} is: {}'.format(stock, date, output))
    return output


def cost_of_debt(stock, date=datetime.now(), pretax=True):
    output = fi.interest_expense(stock, date) / fi.total_liabilities(stock, date)
    if not pretax:
        pass # output *= tax_rate TODO
enterprise_value('FB')

