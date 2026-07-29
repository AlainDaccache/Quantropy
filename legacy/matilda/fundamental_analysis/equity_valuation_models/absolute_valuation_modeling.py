'''
Equity valuation models fall into two major categories: absolute or intrinsic valuation methods and relative valuation 
methods. Dividend discount models (including the Gordon growth model and multi-stage dividend discount model) belong to 
the absolute valuation category, along with the discounted cash flow (DCF) approach, residual income, and asset-based 
models. Relative valuation approaches include comparables models. These involve calculating multiples or ratios, such as 
the price-to-earnings or P/E multiple, and comparing them to the multiples of other comparable firms.
'''
from datetime import datetime
from typing import Callable
from functools import partial

from matilda.fundamental_analysis.equity_valuation_models.cost_of_capital import weighted_average_cost_of_capital
from matilda.data_pipeline.db_crud import read_market_price
from matilda.fundamental_analysis.accounting_ratios import *
from matilda.fundamental_analysis.financial_statements import *

HISTORICAL_GDP_GROWTH_RATE = 0.04  # historically between 4% and 5%, assume lower bound (more conservative)
HISTORICAL_INFLATION_RATE = 0.03  # historically between 2% and 3%, assume upper bound (less conservative)

'''
Growth Measures
'''


# Also known as the Sustainable Growth Rate (SGR) Model
def growth_rate_PRAT_model(stock: str, date=None, lookback_period=timedelta(days=0), period='FY'):
    profit_margin = net_profit_margin(stock=stock, date=date, lookback_period=lookback_period, period=period)
    retention = retention_ratio(stock=stock, date=date, lookback_period=lookback_period, period=period)
    asset_turnover = asset_turnover_ratio(stock=stock, date=date, lookback_period=lookback_period, period=period)
    financial_leverage = asset_to_equity(stock=stock, date=date, lookback_period=lookback_period, period=period)
    return profit_margin * retention * asset_turnover * financial_leverage


def growth_rate_implied_by_ggm(stock: str, date=None, lookback_period=timedelta(days=0), period='FY',
                               diluted_shares=False):
    # current_price = read_market_price(stock=stock, date=date, lookback_period=lookback_period)
    # required_rate_of_return = weighted_average_cost_of_capital(stock=stock, date=date, lookback_period=lookback_period,
    #                                                            period=period)
    # dividend_per_share = dividend_per_share(stock=stock, date=date, lookback_period=lookback_period,
    #                                         period=period, diluted_shares=diluted_shares)
    # return (current_price * required_rate_of_return - dividend_per_share) / (current_price + dividend_per_share)
    pass


def growth_rate_implied_by_price_book(stock: str, date=datetime.today(),
                                      lookback_period=timedelta(days=0), period: str = 'FY',
                                      diluted_shares=False):
    pass


'''
Absolute Valuation Models
'''

'''The Gordon Growth Model solves for the present value of an infinite series of future dividends. These dividends are 
assumed to grow at a constant rate in perpetuity. Generally only used for companies with stable growth rates, such as 
blue-chip companies. These companies are well established and consistently pay dividends to their shareholders at a 
regular pace, given their steady cash flows. '''


def gordon_growth_model(current_cash_flow: float, terminal_growth_rate: float, discount_rate: float):
    return current_cash_flow * (1 + terminal_growth_rate) / (discount_rate - terminal_growth_rate)


'''The two-stage model assumes unstable initial growth rate lasting for a specific time, before stabilizing at a long 
term growth rate at perpetuity (for which we use the Gordon Growth Model).
It is therefore more flexible and complex (thus more realistic and practical), considering fluctuation of the business 
cycle, constant and unexpected financial difficulties (or successes)...) thus can be used across most dividend-paying companies
'''


def absolute_valuation_two_stage_model(current_cash_flow: float, discount_rate: float,
                                       initial_growth_rate: float, terminal_growth_rate: float,
                                       periods_initial_growth: int = 5):
    first_phase = np.sum(
        [(current_cash_flow * (1 + initial_growth_rate) ** period) / (1 + discount_rate) ** period for period in
         range(1, periods_initial_growth + 1)])
    second_phase = gordon_growth_model(
        current_cash_flow=current_cash_flow * (1 + initial_growth_rate) ** periods_initial_growth,
        terminal_growth_rate=terminal_growth_rate, discount_rate=discount_rate)
    return first_phase + (second_phase / ((1 + discount_rate) ** periods_initial_growth))


'''The two-stage model assumes that the growth rate from the initial phase will become stable overnight. 
The H-model solves this by having an initial growth rate that is already high, followed by a decline to a stable growth 
rate over a more gradual period (Gordon Growth Model). H is the half-life of the duration of that transitionary period
The model assumes that a company's dividend payout ratio and cost of equity remain constant.
'''


def absolute_valuation_H_model(current_cash_flow: float, discount_rate: float, initial_growth_rate: float,
                               terminal_growth_rate: float, transition_growth_periods: int = 5):
    half_life = transition_growth_periods / 2
    gradual_decrease_phase = (current_cash_flow * half_life * (initial_growth_rate - terminal_growth_rate)) / (
            discount_rate - terminal_growth_rate)
    stable_phase = gordon_growth_model(current_cash_flow=current_cash_flow, terminal_growth_rate=terminal_growth_rate,
                                       discount_rate=discount_rate)
    return gradual_decrease_phase + stable_phase


'''The three-stage model has an initial phase of stable high growth that lasts for a specified period. 
In the second phase, growth declines linearly until it reaches a final and stable growth rate. 
This model improves upon both previous models and can be applied to nearly all firms. '''


def absolute_valuation_three_stage_model(current_cash_flow: float, discount_rate: float,
                                         initial_growth_rate: float, terminal_growth_rate: float,
                                         transition_growth_periods: int, initial_growth_period: int = 5):
    first_phase = np.sum(
        [(current_cash_flow * (1 + initial_growth_rate) ** period) / (1 + discount_rate) ** period for period in
         range(1, initial_growth_period + 1)])  # inclusive to initial_period
    second_phase = absolute_valuation_H_model(
        current_cash_flow=(current_cash_flow * (1 + initial_growth_rate) ** initial_growth_period),
        discount_rate=discount_rate,
        initial_growth_rate=initial_growth_rate,
        terminal_growth_rate=terminal_growth_rate,
        transition_growth_periods=transition_growth_periods)
    return first_phase + (second_phase / ((1 + discount_rate) ** initial_growth_period))


def preferred_stock_valuation(dividend, required_rate_of_return):
    return dividend / required_rate_of_return


def valuation_wrapper(model_type: partial,  # Gordon Growth, Two Stage, H Model, Three Stage
                      # For Three-Stage Model, specify transitionary growth periods (5 by default)
                      # For all models except GGM, specify initial growth periods (5 by default)
                      model_metric: Callable,  # Dividend, EBITDA, OCF...
                      stock: str, date=datetime.now(),
                      lookback_period=timedelta(days=0),
                      period: str = 'FY', diluted_shares: bool = False):
    shares_outstanding = total_shares_outstanding(stock=stock, date=date, lookback_period=lookback_period,
                                                  period=period, diluted_shares=diluted_shares)

    discount_rate = weighted_average_cost_of_capital(stock=stock, date=date, lookback_period=lookback_period,
                                                     period=period)
    print('WACC is {}'.format(discount_rate))
    if model_metric == dividend_per_share:
        current_cash_flow = dividend_per_share(stock=stock, date=date, lookback_period=lookback_period,
                                               period=period, diluted_shares=diluted_shares)
    else:
        current_cash_flow = cash_flow_per_share(cash_flow_metric=model_metric,
                                                stock=stock, date=date, lookback_period=lookback_period,
                                                period=period, diluted_shares=diluted_shares)

    initial_growth_rate = cash_flow_growth_rate(cash_flow_type=partial(cash_flow_per_share, model_metric),
                                                stock=stock, date=date, lookback_period=lookback_period, period=period)
    print('Initial Growth Rate is {}'.format(initial_growth_rate))
    terminal_growth_rate = growth_rate_PRAT_model(stock, date=datetime.now(), lookback_period=timedelta(days=0),
                                                  period=period)
    print('PRAT Terminal Growth Rate is {}'.format(terminal_growth_rate))
    #  The perpetuity growth rate is typically between the historical inflation rate of 2-3% and the historical GDP growth rate of 4-5%.
    #  If you assume a perpetuity growth rate in excess of 5%, you are basically saying that you expect the company's growth to outpace the economy's growth forever.
    terminal_growth_rate = min(terminal_growth_rate, HISTORICAL_GDP_GROWTH_RATE)
    terminal_growth_rate = max(terminal_growth_rate, HISTORICAL_INFLATION_RATE)
    print('Adujsted Terminal Growth Rate is {}'.format(terminal_growth_rate))
    partial_function = partial(model_type,
                               current_cash_flow=current_cash_flow,
                               discount_rate=discount_rate,
                               terminal_growth_rate=terminal_growth_rate)

    if model_type.func == gordon_growth_model:
        if model_metric == dividend_per_share:
            return partial_function()
        else:
            return partial_function() / shares_outstanding

    else:
        if model_metric == dividend_per_share:
            return partial_function(initial_growth_rate=initial_growth_rate)
        else:
            return partial_function(initial_growth_rate=initial_growth_rate) \
                   / shares_outstanding


'''
How to use:
- For DDM, the model metric is Dividend per Share
- For DCF, the model metrics can be EBITDA, OCF, FCF, FCFE, FCFF
'''