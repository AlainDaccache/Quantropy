from datetime import datetime, timedelta
import numpy as np
from functools import partial


def cost_of_preferred_stock(stock, date=datetime.now(), lookback_period=timedelta(days=0), period: str = 'FY'):
    preferred_dividends = preferred_dividends(stock=stock, date=date, lookback_period=lookback_period, period=period)
    market_price_of_preferred = preferred_stock_value(stock=stock, date=date, lookback_period=lookback_period,
                                                      period=period)
    return preferred_dividends / market_price_of_preferred


def cost_of_debt(stock, date=datetime.now(), lookback_period=timedelta(days=0), period: str = 'FY'):
    interest_rate = interest_expense(stock=stock, date=date, lookback_period=lookback_period,
                                     period=period) / total_long_term_debt(stock=stock, date=date,
                                                                           lookback_period=lookback_period,
                                                                           period=period)
    tax_rate = income_tax_expense(stock=stock, date=date, lookback_period=lookback_period,
                                  period=period) / earnings_before_taxes(stock=stock, date=date,
                                                                         lookback_period=lookback_period,
                                                                         period=period)
    return abs(interest_rate * (1 - tax_rate))


def cost_of_equity_capm(stock: str, from_date: datetime = datetime.now() - timedelta(days=365 * 5),
                        to_date: datetime = datetime.now(),
                        beta_period='Monthly',
                        benchmark: str = '^GSPC'):
    beta = capital_asset_pricing_model(portfolio=stock, benchmark=benchmark, period=beta_period,
                                       from_date=from_date, to_date=to_date).params[1]
    risk_free_rate = cumulative_risk_free_rate(from_date=to_date - timedelta(days=365), to_date=to_date)
    risk_premium = cumulative_market_premium(from_date=to_date - timedelta(days=365), to_date=to_date)
    return risk_free_rate + beta * risk_premium


def cost_of_equity_ddm(stock, date=datetime.now(), lookback_period=timedelta(days=0), period: str = 'FY',
                       diluted_shares=True):
    stock_price = market_price(stock=stock, date=date, lookback_period=lookback_period)

    this_period_dividend = dividend_per_share(stock=stock, date=date, lookback_period=lookback_period, period=period,
                                              diluted_shares=diluted_shares)
    growth_rate = FundamentalMetricsHelpers(metric=partial(dividend_per_share), stock=stock, date=date) \
        .metric_growth_rate(lookback_period=lookback_period, period=period)

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
                                     period: str = 'FY', beta_period='Monthly', benchmark: str = '^GSPC'):
    from_date = date - lookback_period - lookback_lookback_period
    to_date = date - lookback_period

    dictio = {'Common Equity': (cost_of_equity_capm(stock=stock, from_date=from_date, to_date=to_date,
                                                    beta_period=beta_period,
                                                    benchmark=benchmark),
                                total_shareholders_equity(stock=stock, date=date, lookback_period=lookback_period,
                                                          period=period)),
              'Preferred Equity': (
                  cost_of_preferred_stock(stock=stock, date=date, lookback_period=lookback_period, period=period),
                  preferred_stock_value(stock=stock, date=date, lookback_period=lookback_period,
                                        period=period)),
              'Debt': (cost_of_debt(stock=stock, date=date, lookback_period=lookback_period, period=period),
                       total_long_term_debt(stock=stock, date=date, lookback_period=lookback_period, period=period))}

    capitals = [np.nan_to_num(v[1]) for k, v in dictio.items()]
    weights = [part / sum(capitals) for part in capitals]
    costs = [np.nan_to_num(v[0]) for k, v in dictio.items()]
    return np.sum([weight * cost for weight, cost in zip(weights, costs)])


if __name__ == '__main__':
    print(weighted_average_cost_of_capital('AAPL'))
