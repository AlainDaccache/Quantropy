from datetime import datetime, timedelta
import financial_statement_analysis.financial_statements_entries as fi
import financial_statement_analysis.financial_metrics as me
import data_scraping.excel_helpers as excel
import financial_modeling.asset_pricing_models as required_rr
import financial_statement_analysis.macro_data as macro
import numpy as np
from functools import partial


def cash_flow_growth_rate(cash_flow_type: partial, stock, periods: int = 5, date=datetime.now(),
                          lookback_period=timedelta(days=0), annual=True,
                          ttm=False):
    ls = [cash_flow_type(stock=stock, date=date - timedelta(days=365 * i if annual else 90 * i),
                         lookback_period=lookback_period, annual=annual, ttm=ttm)
          for i in range(0, periods)]
    return excel.average_growth(ls[::-1])  # reverse


def cost_of_preferred_stock(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=True,
                            ttm=False):
    preferred_dividends = fi.preferred_dividends(stock=stock, date=date, lookback_period=lookback_period, annual=annual,
                                                 ttm=ttm)
    market_price_of_preferred = fi.preferred_stock_value(stock=stock, date=date, lookback_period=lookback_period,
                                                         annual=annual, ttm=ttm)
    return preferred_dividends / market_price_of_preferred


def cost_of_debt(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=True,
                 ttm=False):
    interest_rate = fi.interest_expense(stock=stock, date=date, lookback_period=lookback_period, annual=annual,
                                        ttm=ttm) / fi.total_long_term_debt(stock=stock, date=date,
                                                                           lookback_period=lookback_period,
                                                                           annual=annual,
                                                                           ttm=ttm)
    tax_rate = fi.income_tax_expense(stock=stock, date=date, lookback_period=lookback_period, annual=annual,
                                     ttm=ttm) / me.earnings_before_taxes(stock=stock, date=date,
                                                                         lookback_period=lookback_period,
                                                                         annual=annual,
                                                                         ttm=ttm)
    return abs(interest_rate * (1 - tax_rate))


def cost_of_equity_capm(stock: str, from_date: datetime = datetime.now() - timedelta(days=365 * 5),
                        to_date: datetime = datetime.now(),
                        beta_period='Monthly',
                        benchmark: str = '^GSPC'):
    beta = required_rr.asset_pricing_wrapper(model='CAPM', portfolio=stock, benchmark=benchmark, period=beta_period,
                                             from_date=from_date, to_date=to_date).params[1]
    risk_free_rate = macro.cumulative_risk_free_rate(from_date=to_date - timedelta(days=365), to_date=to_date)
    risk_premium = macro.cumulative_market_premium(from_date=to_date - timedelta(days=365), to_date=to_date)
    return risk_free_rate + beta * risk_premium


def cost_of_equity_ddm(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=True,
                       ttm=False, diluted_shares=True):
    stock_price = me.market_price(stock=stock, date=date, lookback_period=lookback_period)

    this_period_dividend = me.dividend_per_share(stock=stock, date=date, lookback_period=lookback_period, annual=annual,
                                                 ttm=ttm, diluted_shares=diluted_shares)
    growth_rate = cash_flow_growth_rate(cash_flow_type=me.dividend_per_share, stock=stock, date=date,
                                        lookback_period=lookback_period, annual=annual, ttm=ttm)
    next_period_dividend = this_period_dividend * (1 + growth_rate)
    return (next_period_dividend / stock_price) + growth_rate


"""
    Summary: Calculate the cost of equity for WACC using the Bond yield plus risk premium method.
    PARA bond_yield: The company's interest rate on long-term debt.
    PARA risk_premium: The company's risk premium usually 3% to 5%.
"""


def cost_of_equity_byprp(bond_yield: float, risk_premium: float):
    return bond_yield + risk_premium


def weighted_average_cost_of_capital(stock, date=datetime.now(), lookback_period: timedelta = timedelta(days=0),
                                     lookback_lookback_period: timedelta = timedelta(days=365 * 5),
                                     annual=True, ttm=False,
                                     beta_period='Monthly', benchmark: str = '^GSPC'):
    from_date = date - lookback_period - lookback_lookback_period
    to_date = date - lookback_period

    dictio = {'Common Equity': (cost_of_equity_capm(stock=stock, from_date=from_date, to_date=to_date,
                                                    beta_period=beta_period,
                                                    benchmark=benchmark),
                                fi.total_shareholders_equity(stock=stock, date=date, lookback_period=lookback_period,
                                                             annual=annual, ttm=ttm)),
              'Preferred Equity': (
                  cost_of_preferred_stock(stock=stock, date=date, lookback_period=lookback_period, annual=annual,
                                          ttm=ttm),
                  fi.preferred_stock_value(stock=stock, date=date, lookback_period=lookback_period,
                                           annual=annual, ttm=ttm)),
              'Debt': (cost_of_debt(stock=stock, date=date, lookback_period=lookback_period, annual=annual, ttm=ttm),
                       fi.total_long_term_debt(stock=stock, date=date, lookback_period=lookback_period, annual=annual,
                                               ttm=ttm))}

    capitals = [np.nan_to_num(v[1]) for k, v in dictio.items()]
    weights = [part / sum(capitals) for part in capitals]
    costs = [np.nan_to_num(v[0]) for k, v in dictio.items()]
    return np.sum([weight * cost for weight, cost in zip(weights, costs)])


if __name__ == '__main__':
    print(weighted_average_cost_of_capital('AAPL'))
