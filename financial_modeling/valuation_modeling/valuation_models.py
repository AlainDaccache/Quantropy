import financial_modeling.valuation_modeling.time_value_of_money as time_value
import financial_statement_analysis.financial_statements_entries as fi
import financial_statement_analysis.financial_metrics as me
import financial_modeling.asset_pricing_models as required_rr
import data_scraping.excel_helpers as excel
import config
from datetime import datetime, timedelta

'''
Absolute Value Models:
    Single-Period Models:
        Dividend Discount Models:
            Gordon Growth Model
    Multi-Period Models:
        Discounted Cash Flow Models:
            
        Dividend Discount Models:
            N-Period Model
            Two-stage Growth Model
            H Dividend Discount Model
            Three-Stage Growth Model
Relative Value Models:
    P/E
'''

'''
Part I. Dividend Discount Models
'''

"""
Summary: Given an array of dividends, estimate the stock price using an n-period model.
PARA discount_rate: The discount rate used to calculate the NPV & PV calculations
PARA LT_growth_rate: The long-term growth rate used to calculate the last dividend in perpetuity.
PARA dividends: A list of dividends where the last dividend is the one that is paid in perpetuity.
"""


def stock_valuation_n_period(discount_rate: float, long_term_growth_rate: float, dividends: []):
    div_array, div_last = dividends[:-1], dividends[-1]  # get the dividend array & the last dividend
    num_pers = len(dividends) - 1  # define the number of periods.
    pres_val_dividends = time_value.net_present_value(discount_rate, div_array) * (1 + discount_rate)

    # calculate late the terminal value, which is a dividend in perpituity.
    last_div_n = div_last / (discount_rate - long_term_growth_rate)

    # calulate the the total value which is the pv of the dividends cashflow
    # and the present value of the dividend in perpituity.
    total_val = pres_val_dividends + time_value.present_value(last_div_n, discount_rate, num_pers)

    return total_val


'''
Summary: Given an array of dividends, estimate the stock price using an n-period model.

    PARA discount_rate: The discount rate used to calculate the NPV & PV calculations.
    PARA dividends: The period 0 dividend.
    PARA growth_rate: The growth rate that will be applied to the dividend every period.
    PARA stock_price: The stock price at period n
    PARA periods: The number of periods.
'''


def dividend_discount_model(discount_rate: float, dividends: float, growth_rate: float, stock_price: float,
                            periods: int):
    total_cashflows = 0  # initalize our total cashflows
    for period in range(1, periods + 1):  # loop the number of periods and calculate the cash flows.

        # define the growth and discount factor
        growth_factor = (1 + growth_rate)
        discount_factor = (1 + discount_rate) ** period

        # calculate the cashflow
        cashflow = (dividends * growth_factor) ** period / discount_factor
        total_cashflows = total_cashflows + cashflow

    # calculate the terminal value, or the stock price at period n.
    terminal_val = stock_price / (1 + discount_rate) ** periods

    return total_cashflows + terminal_val


"""
    Summary: Calculate the value of a stock using a Gordon Growth model.
    PARA dividend: The dividend earned over the life of the stock.
    PARA dividend_growth_rate: The growth rate in the value of the dividend every period.
    PARA required_rate_of_return: The required rate of return for the investor.
"""


def gordon_growth_model(dividend: float, dividend_growth_rate: float, required_rate_of_return: float):
    dividend_period_one = dividend * (1 + dividend_growth_rate)

    return dividend_period_one / (required_rate_of_return - dividend_growth_rate)


"""
    Summary: Calculate the value of a stock using a multistage growth model.
    PARA dividend: The dividend earned over the life of the stock.
    PARA discount_rate: The discount rate used to calculate the NPV & PV calcs.
    PARA growth_rate: The growth rate during the multistage period.
    PARA constant_growth: The growth rate in perpetuity.
    PARA periods: The number of periods.
"""


def multistage_dividend_discount_model(dividend: float, discount_rate: float,
                                       growth_rate: float, constant_growth_rate: float,
                                       periods: int):
    total_value = 0

    for period in range(1, periods + 1):

        if period == periods:  # if it's the last period calculate the terminal value

            terminal_dividend = (dividend * (1 + growth_rate) ** period)
            terminal_value = terminal_dividend / (discount_rate - constant_growth_rate)
            terminal_value_disc = terminal_value / (1 + discount_rate) ** (period - 1)
            total_value += terminal_value_disc

        else:  # otherwise calculate the cashflow for that period
            cashflow = (dividend * (1 + growth_rate) ** period) / (1 + discount_rate) ** period
            total_value += cashflow

    return total_value


"""
    Summary: Given a preferred dividend stock, calculate the value of that stock.
    PARA dividend: The dividend for each period, earned over an infinite period.
    PARA required_rate_of_return: The required rate of return desired for an investment.
"""


def preferred_stock_valuation(dividend, required_rate_of_return):
    return dividend / required_rate_of_return


'''
Part II. Discounted Cash Flow Models
'''
