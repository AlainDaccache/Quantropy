import financial_statement_analysis.financial_metrics as me
from datetime import datetime, timedelta
from financial_modeling.equity_valuation_modeling.cost_of_capital import dividend_growth_rate, cash_flow_growth_rate, \
    weighted_average_cost_of_capital
import numpy as np

# TODO important to figure out whether the discount rate should account only for cost of equity, or WACC?

'''
Equity valuation models fall into two major categories: absolute or intrinsic valuation methods and relative valuation 
methods. Dividend discount models (including the Gordon growth model and multi-stage dividend discount model) belong to 
the absolute valuation category, along with the discounted cash flow (DCF) approach, residual income, and asset-based 
models. Relative valuation approaches include comparables models. These involve calculating multiples or ratios, such as 
the price-to-earnings or P/E multiple, and comparing them to the multiples of other comparable firms.
'''

'''Original model, with dividend initial growing at constant rate for a certain amount of periods,
discounted (along with the expected stock price at the last period), at a certain rate'''


def dividend_discount_model(discount_rate: float, current_dividend: float, growth_rate: float, stock_price: float,
                            periods: int):
    first_phase = np.sum(
        [(current_dividend * (1 + growth_rate) ** period) / (1 + discount_rate) ** period] for period in
        range(1, periods + 1))
    discounted_stock_price = (stock_price * (1 + discount_rate)) ** periods / (1 + discount_rate) ** periods
    return first_phase + discounted_stock_price


'''The Gordon Growth Model solves for the present value of an infinite series of future dividends. These dividends are 
assumed to grow at a constant rate in perpetuity. Generally only used for companies with stable growth rates, such as 
blue-chip companies. These companies are well established and consistently pay dividends to their shareholders at a 
regular pace, given their steady cash flows. '''


def gordon_growth_model(current_dividend: float, growth_rate: float, discount_rate: float):
    return current_dividend * (1 + growth_rate) / (discount_rate - growth_rate)


'''The two-stage model assumes unstable initial growth rate lasting for a specific time, before stabilizing at a long 
term growth rate at perpetuity (for which we use the Gordon Growth Model).
It is therefore more flexible and complex (thus more realistic and practical), considering fluctuation of the business 
cycle, constant and unexpected financial difficulties (or successes)...) thus can be used across most dividend-paying companies
'''


def dividend_discount_model_two_stage(current_dividend: float, discount_rate: float, growth_rate: float,
                                      long_term_growth_rate: float, periods_initial_growth: int):
    first_phase = np.sum(
        [(current_dividend * (1 + growth_rate) ** period) / (1 + discount_rate) ** period for period in
         range(1, periods_initial_growth + 1)])
    second_phase = gordon_growth_model(current_dividend=current_dividend * (1 + growth_rate) ** periods_initial_growth,
                                       growth_rate=long_term_growth_rate, discount_rate=discount_rate)
    return first_phase + (second_phase / ((1 + discount_rate) ** periods_initial_growth))


'''The two-stage model assumes that the growth rate from the initial phase will become stable overnight. 
The H-model solves this by having an initial growth rate that is already high, followed by a decline to a stable growth 
rate over a more gradual period (Gordon Growth Model). H is the half-life of the duration of that transitionary period
The model assumes that a company's dividend payout ratio and cost of equity remain constant.'''


def dividend_discount_model_H_model(current_dividend: float, discount_rate: float, initial_growth_rate: float,
                                    terminal_growth_rate: float, transition_periods: int):
    half_life = transition_periods / 2
    gradual_decrease_phase = (current_dividend * half_life * (initial_growth_rate - terminal_growth_rate)) / (
            discount_rate - terminal_growth_rate)
    stable_phase = gordon_growth_model(current_dividend=current_dividend, growth_rate=terminal_growth_rate,
                                       discount_rate=discount_rate)
    return gradual_decrease_phase + stable_phase


'''The three-stage model has an initial phase of stable high growth that lasts for a specified period. 
In the second phase, growth declines linearly until it reaches a final and stable growth rate. 
This model improves upon both previous models and can be applied to nearly all firms. '''


def dividend_discount_model_three_stage(current_dividend: float, discount_rate: float,
                                        initial_growth_rate: float, initial_growth_period: int,
                                        terminal_growth_rate: float, transition_growth_period: int):
    first_phase = np.sum(
        [(current_dividend * (1 + initial_growth_rate) ** period) / (1 + discount_rate) ** period for period in
         range(1, initial_growth_period + 1)])  # inclusive to initial_period
    second_phase = dividend_discount_model_H_model(
        current_dividend=(current_dividend * (1 + initial_growth_rate) ** initial_growth_period),
        # dividend at initial_period
        discount_rate=discount_rate,
        initial_growth_rate=initial_growth_rate,
        terminal_growth_rate=terminal_growth_rate,
        transition_periods=transition_growth_period)
    return first_phase + (second_phase / ((1 + discount_rate) ** initial_growth_period))


def preferred_stock_valuation(dividend, required_rate_of_return):
    return dividend / required_rate_of_return


'''
This model is used for companies that do not pay dividends
'''


def discounted_cash_flow_model(cash_flow: float, growth_rate: float, discount_rate: float, periods: int):
    total_cash_flow = 0
    for period in range(1, periods + 1):
        total_cash_flow = + (cash_flow * (1 + growth_rate)) ** period / (1 + discount_rate) ** period
    return total_cash_flow


def valuation_wrapper(model: str, stock: str, date: datetime = datetime.now(),
                      lookback_period: timedelta = timedelta(days=0),
                      lookback_model_periods: int = 3,  # to compute average change in growth rate for H-Model
                      high_growth_periods: int = 5,  # first phase for all models (except GGM)
                      transitionary_growth_periods: int = 3,  # second phase for three-stage model
                      annual=True, ttm=False, diluted_shares=False):
    current_free_cash_flow = me.free_cash_flow(stock=stock, date=date, lookback_period=lookback_period, annual=annual,
                                               ttm=ttm)
    current_dividend = me.dividend_per_share(stock=stock, date=date, lookback_period=lookback_period, annual=annual,
                                             ttm=ttm,
                                             diluted_shares=diluted_shares)
    discount_rate = weighted_average_cost_of_capital(stock=stock, date=date, lookback_period=lookback_period,
                                                     annual=annual, ttm=ttm)

    if 'DCF' in model.split(' '):
        if model == 'DCF FCF':
            growth_rate = cash_flow_growth_rate(stock=stock, date=date, lookback_period=lookback_period, annual=annual,
                                                ttm=ttm)
            return discounted_cash_flow_model(cash_flow=current_free_cash_flow, growth_rate=growth_rate,
                                              discount_rate=discount_rate,
                                              periods=high_growth_periods)
        # TODO same for levered vs unlevered and other metrics for cash flow...
    else:
        growth_rate = dividend_growth_rate(stock=stock, date=date, lookback_period=lookback_period, annual=annual,
                                           ttm=ttm, diluted_shares=diluted_shares)
        if model == 'DDM':
            stock_price = me.market_price(stock=stock, date=date, lookback_period=lookback_period)
            return dividend_discount_model(current_dividend=current_dividend, growth_rate=growth_rate,
                                           discount_rate=discount_rate,
                                           stock_price=stock_price, periods=high_growth_periods)
        elif model == 'GGM':
            return gordon_growth_model(current_dividend=current_dividend, growth_rate=growth_rate,
                                       discount_rate=discount_rate)
        elif model == 'DDM Two-Stage':
            long_term_growth_rate = 0
            return dividend_discount_model_two_stage(current_dividend=current_dividend, growth_rate=growth_rate,
                                                     discount_rate=discount_rate,
                                                     long_term_growth_rate=long_term_growth_rate,
                                                     periods_initial_growth=high_growth_periods)
        elif model == 'DDM H Model' or model == 'DDM Three-Stage':
            current_dividend_growth = growth_rate
            previous_dividend_growth = dividend_growth_rate(stock=stock, date=date,
                                                            lookback_period=lookback_period - timedelta(
                                                                days=lookback_model_periods * 365), annual=annual,
                                                            ttm=ttm, diluted_shares=diluted_shares)
            average_change_in_dividend_growth = (
                                                        current_dividend_growth - previous_dividend_growth) / lookback_model_periods
            terminal_growth_rate = growth_rate * (1 + average_change_in_dividend_growth) ** high_growth_periods
            if model == 'DDM H Model':
                return dividend_discount_model_H_model(current_dividend=current_dividend, discount_rate=discount_rate,
                                                       initial_growth_rate=growth_rate,
                                                       terminal_growth_rate=terminal_growth_rate,
                                                       transition_periods=high_growth_periods)
            elif model == 'DDM Three-Stage':
                return dividend_discount_model_three_stage(current_dividend=current_dividend,
                                                           discount_rate=discount_rate,
                                                           initial_growth_rate=growth_rate,
                                                           terminal_growth_rate=terminal_growth_rate,
                                                           initial_growth_period=high_growth_periods,
                                                           transition_growth_period=transitionary_growth_periods)
    return Exception


if __name__ == '__main__':
    print(gordon_growth_model(current_dividend=10, growth_rate=0.06, discount_rate=0.08))
    print(dividend_discount_model_two_stage(current_dividend=2, growth_rate=0.15, discount_rate=0.10,
                                            long_term_growth_rate=0.05, periods_initial_growth=3))
    print(dividend_discount_model_H_model(current_dividend=4.60, initial_growth_rate=0.165, terminal_growth_rate=0.072,
                                          transition_periods=4, discount_rate=0.10))
    print(dividend_discount_model_three_stage(current_dividend=2.28, initial_growth_rate=0.184, initial_growth_period=4,
                                              transition_growth_period=3, terminal_growth_rate=0.072,
                                              discount_rate=0.10))
