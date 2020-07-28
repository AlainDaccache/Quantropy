import company_analysis.financial_statements_entries as fi
import company_analysis.financial_metrics as me
import financial_modeling.asset_pricing_models as required_rr
import data_scraping.excel_helpers as excel
import config

from datetime import datetime, timedelta


def free_cash_flow(stock: str, date: datetime, lookback_period: timedelta, annual: bool, ttm: bool):

    return fi.cash_flow_operating_activities(stock=stock, date=date, lookback_period=lookback_period, annual=annual,
                                             ttm=ttm) - me.capital_expenditures(stock=stock, date=date, lookback_period=lookback_period, annual=annual,
                                                                                ttm=ttm)


def cost_of_equity(type: str, stock: str, date: datetime, lookback_period: timedelta, period='Daily'):
    asset_returns = excel.read_df_from_csv('{}/{}.xlsx'.format(config.STOCK_PRICES_DIR_PATH, stock))['Adj Close'].pct_change()[1:]
    if type == 'capm':

        capm = required_rr.capm(asset_returns)
        risk_free_rate = me.risk_free_rate(date - lookback_period, )


ca = cost_of_equity('capm', 'AAPL')

def cost_of_debt(stock: str, date: datetime, lookback_period: timedelta, annual: bool, ttm: bool):
    pass


def weighted_average_cost_of_capital(stock: str, date: datetime, lookback_period: timedelta, annual: bool, ttm: bool):
    total_debt = fi.total_long_term_debt(stock=stock, date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)
    total_equity = fi.total_shareholders_equity(stock=stock, date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)
    cost_of_equity = cost_of_equity(type='capm', stock=stock, date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)
    cost_of_debt = cost_of_debt(stock=stock, date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)
    return (total_debt/(total_debt+total_equity)) * cost_of_debt + (total_equity/(total_debt+total_equity)) * cost_of_equity


def discount_rate():
    pass


def growth_rate():
    pass


# Absolute Value Models:
# Single-Period Models:
# Dividend Discount Models:
# Gordon Growth model,
# Multi-Period Models:
# Discounted Cash Flow Models:
# Dividend Discount Models:

# Multi-period model,
# Two-stage growth model,
# H model,
# Three-stage growth model,
# Relative Value Models:

def stock_valuation():
    pass
    # if stock pays dividends:
