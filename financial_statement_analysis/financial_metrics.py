import os
from datetime import datetime, timedelta
import financial_statement_analysis.financial_statements_entries as fi
import data_scraping.excel_helpers as excel
import config
import numpy as np

'''
Data outside financial statements for the company
'''


def market_price(stock, date=datetime.today(), lookback_period=timedelta(days=0)):
    path = os.path.join(config.STOCK_PRICES_DIR_PATH, '{}.xlsx'.format(stock))
    output = excel.read_entry_from_csv(path, config.stock_prices_sheet_name, 'Adj Close', date, lookback_period.days)
    print('Market Price for {} on the {} is: {}'.format(stock, date, output))
    return output


def get_stock_location(stock):
    return excel.read_entry_from_csv(config.COMPANY_META_DATA_FILE_PATH, 'Sheet1', 'Location', stock)


def get_stock_industry(stock):
    return excel.read_entry_from_csv(config.COMPANY_META_DATA_FILE_PATH, 'Sheet1', 'Industry', stock)


def get_stock_sector(stock):
    return excel.read_entry_from_csv(config.COMPANY_META_DATA_FILE_PATH, 'Sheet1', 'Sector', stock)


'''
Intermediary data from financial statements used in accounting ratios and financial modeling
'''


def dividend_per_share(stock, date=datetime.today(), lookback_period=timedelta(days=0), annual=True, ttm=False,
                       diluted_shares=True):
    dividends_paid = fi.payments_for_dividends(stock=stock, date=date, lookback_period=lookback_period,
                                               annual=annual, ttm=ttm)
    shares_outstanding = fi.total_shares_outstanding(stock=stock, date=date, lookback_period=lookback_period,
                                                     annual=annual, ttm=ttm, diluted=diluted_shares)
    return abs(dividends_paid) / shares_outstanding


def cash_flow_per_share(cash_flow_metric, stock, date=datetime.today(), lookback_period=timedelta(days=0),
                        annual=True, ttm=False, diluted_shares=True):
    cash_flow = cash_flow_metric(stock=stock, date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)
    shares_outstanding = fi.total_shares_outstanding(stock=stock, date=date, lookback_period=lookback_period,
                                                     annual=annual, ttm=ttm, diluted=diluted_shares)
    return cash_flow / shares_outstanding


def market_capitalization(stock, date=datetime.now(), lookback_period=timedelta(days=0), diluted_shares=True,
                          annual=False, ttm=False):
    shares_outstanding = fi.total_shares_outstanding(stock=stock, date=date, lookback_period=lookback_period,
                                                     annual=annual, ttm=ttm, diluted=diluted_shares)
    output = market_price(stock, date, lookback_period) * shares_outstanding
    print('Market Capitalization for {} on the {} is: {}'.format(stock, date, output))
    return output


def enterprise_value(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=True, ttm=False):
    output = market_capitalization(stock=stock, date=date, lookback_period=lookback_period, annual=annual, ttm=ttm) \
             + fi.total_liabilities(stock=stock, date=date, lookback_period=lookback_period, annual=annual, ttm=ttm) \
             - fi.cash_and_cash_equivalents(stock=stock, date=date, lookback_period=lookback_period, annual=annual,
                                            ttm=ttm)
    print('Enterprise Value for {} on the {} is: {}'.format(stock, date, output))
    return output


def gross_profit(stock, date=datetime.today(), lookback_period=timedelta(days=0), annual=True, ttm=False):
    return fi.net_sales(stock=stock, date=date, lookback_period=lookback_period, annual=annual,
                        ttm=ttm) - fi.cost_of_goods_services(stock=stock, date=date, lookback_period=lookback_period,
                                                             annual=annual, ttm=ttm)


# TODO Review
def debt_service(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=True, ttm=True):
    return fi.interest_expense(stock=stock, date=date, lookback_period=lookback_period, annual=annual,
                               ttm=ttm)


# TODO Review
def net_credit_sales(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=True, ttm=True):
    return fi.net_sales(stock=stock, date=date, lookback_period=lookback_period, annual=annual,
                        ttm=ttm) \
           - fi.net_accounts_receivable(stock=stock, date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)


def earnings_before_interest_and_taxes_and_depreciation_and_amortization(stock, date=datetime.today(),
                                                                         lookback_period=timedelta(days=0), annual=True,
                                                                         ttm=False):
    return earnings_before_interest_and_taxes(stock=stock, date=date, lookback_period=lookback_period, annual=annual,
                                              ttm=ttm) \
           + fi.depreciation_and_amortization(stock=stock, date=date, lookback_period=lookback_period,
                                              annual=annual, ttm=ttm)


def earnings_before_interest_and_taxes(stock, date=datetime.today(), lookback_period=timedelta(days=0), annual=True,
                                       ttm=False):
    return earnings_before_taxes(stock=stock, date=date, lookback_period=lookback_period, annual=annual, ttm=ttm) \
           + fi.income_tax_expense(stock, date, lookback_period, annual, ttm)


def earnings_before_taxes(stock, date=datetime.today(), lookback_period=timedelta(days=0), annual=True, ttm=False):
    directly_from_statement = fi.read_income_statement_entry(stock=stock,
                                                             entry_name=[
                                                                 'Income (Loss) from Continuing Operations before Income Taxes, Noncontrolling Interest',
                                                                 ' '],
                                                             date=date, lookback_period=lookback_period, annual=annual,
                                                             ttm=ttm)
    if not np.isnan(directly_from_statement):
        return directly_from_statement
    else:
        return fi.net_income(stock=stock, date=date, lookback_period=lookback_period, annual=annual, ttm=ttm) \
               + fi.income_tax_expense(stock=stock, date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)


def effective_tax_rate(stock, date, lookback_period=timedelta(days=0), annual=True, ttm=False):
    return fi.income_tax_expense(stock=stock, date=date, lookback_period=lookback_period, annual=annual,
                                 ttm=ttm) \
           / earnings_before_taxes(stock=stock, date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)


def capital_expenditures(stock, date, lookback_period=timedelta(days=0), annual=True, ttm=False):
    from_cash_flow_statement = fi.acquisition_property_plant_equipment(stock=stock, date=date,
                                                                       lookback_period=lookback_period,
                                                                       annual=annual, ttm=ttm)
    if not np.isnan(from_cash_flow_statement):
        return from_cash_flow_statement
    else:
        return fi.net_property_plant_equipment(stock=stock, date=date, lookback_period=lookback_period, annual=annual,
                                               ttm=ttm) \
               - fi.net_property_plant_equipment(stock=stock, date=date - timedelta(days=365 if annual else 90),
                                                 lookback_period=lookback_period, annual=annual, ttm=ttm) \
               + fi.depreciation_and_amortization(stock=stock, date=date, lookback_period=lookback_period,
                                                  annual=annual, ttm=ttm)


# NOPAT
def net_profit_after_tax(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=True, ttm=True):
    pass


def working_capital(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=True, ttm=True):
    return fi.current_total_assets(stock=stock, date=date, lookback_period=lookback_period, annual=annual,
                                   ttm=ttm) - fi.current_total_liabilities(stock=stock, date=date,
                                                                           lookback_period=lookback_period,
                                                                           annual=annual, ttm=ttm)


'''Free Cash Flow is the amount of cash flow available for discretionary spending by the company after the necessary capital invesment. 
            It builds on CFO but takes into account (deducts) Capital Expenditures. Unlike FCFE and FCFF, it is a generic measure of cash flow.'''


def free_cash_flow(stock: str, date: datetime, lookback_period: timedelta, annual: bool, ttm: bool):
    return fi.cash_flow_operating_activities(stock=stock, date=date, lookback_period=lookback_period, annual=annual,
                                             ttm=ttm) - abs(capital_expenditures(stock=stock, date=date,
                                                                                 lookback_period=lookback_period,
                                                                                 annual=annual,
                                                                                 ttm=ttm))


'''FCFE is the amount of cash flow available to equity investors after paying interest to debt holders, considering net debt issued (or repaid) and reinvesting capital in the business.
It is the Operating Cash Flow - Capital Expenditures + Net Debt Issued'''


def free_cash_flow_to_equity(stock: str, date: datetime, lookback_period: timedelta, annual: bool, ttm: bool):
    return free_cash_flow(stock=stock, date=date, lookback_period=lookback_period, annual=annual,
                          ttm=ttm) + fi.net_debt_issued(stock=stock, date=date, lookback_period=lookback_period,
                                                        annual=annual, ttm=ttm)


'''FCFF equires multi-step calculation and is used in DCF analysis to arrive at the enterprise value. 
It is a hypothetical figure to estimate the firm value if it has no debt (i.e. if it was completely equity financed).
It is the EBIT * (1 - Tax Rate) + Depreciation & Amortization - Increase in Non-Cash Working Capital - Capital Expenditures
'''


def free_cash_flow_to_firm(stock: str, date: datetime, lookback_period: timedelta, annual: bool, ttm: bool):
    return earnings_before_interest_and_taxes(stock=stock, date=date, lookback_period=lookback_period, annual=annual,
                                              ttm=ttm) \
           * (1 - effective_tax_rate(stock=stock, date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)) \
           + fi.depreciation_and_amortization(stock=stock, date=date, lookback_period=lookback_period,
                                              annual=annual, ttm=ttm) \
           - (working_capital(stock=stock, date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)
              - working_capital(stock=stock, date=date - timedelta(days=365 if annual else 90),
                                lookback_period=lookback_period, annual=annual, ttm=ttm)) \
           - capital_expenditures(stock=stock, date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)
