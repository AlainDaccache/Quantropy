import company_analysis.time_value_of_money as time_value

'''
Valuation Models
'''

"""
Summary: Given an array of dividends, estimate the stock price using an n-period model.
PARA discount_rate: The discount rate used to calculate the NPV & PV calculations
PARA LT_growth_rate: The long-term growth rate used to calculate the last dividend in perpetuity.
PARA dividends: A list of dividends where the last dividend is the one that is paid in perpetuity.
"""


def stock_valuation_n_period(discount_rate: float ,long_term_growth_rate: float, dividends: []):
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


def dividend_discount_model(discount_rate: float, dividends: float, growth_rate: float, stock_price: float, periods: int):
    total_cashflows = 0  # initalize our total cashflows
    for period in range(1, periods + 1):  # loop the number of periods and calculate the cash flows.

        # define the growth and discount factor
        growth_factor = (1 + growth_rate)
        discount_factor = (1 + discount_rate) ** period

        # calculate the cashflow
        cashflow = (dividends * growth_factor) ** period / discount_factor
        total_cashflows = total_cashflows + cashflow

    # calculate the terminal value, or the stock price at period n.
    terminal_val =  stock_price / (1 + discount_rate) ** periods

    return total_cashflows + terminal_val


#EXAMPLE
disc_rate = 0.132
grow_rate = 0.05
dividends = 1.0
stock_price = 14.12
periods = 5

dividend_discount_model(disc_rate, dividends, grow_rate, stock_price, periods)


def gordon_growth_model(dividend, dividend_growth_rate, required_rate_of_return):
    """
    Summary: Calculate the value of a stock using a Gordon Growth model.

    PARA dividend: The dividend earned over the life of the stock.
    PARA type: float

    PARA dividend_growth_rate: The growth rate in the value of the dividend every period.
    PARA type: float

    PARA required_rate_of_return: The required rate of return for the investor.
    PARA type: float

    """

    dividend_period_one = dividend * (1 + dividend_growth_rate)

    return dividend_period_one / (required_rate_of_return - dividend_growth_rate)

div = 2.00
gro = 0.05
rrr = 0.12

gordon_growth_model(div, gro, rrr)


def multistage_dividend_discount_model(dividend, discount_rate, growth_rate, constant_growth_rate, periods):
    """
    Summary: Calculate the value of a stock using a multistage growth model.

    PARA dividend: The dividend earned over the life of the stock.
    PARA type: float

    PARA discount_rate: The discount rate used to calculate the NPV & PV calcs.
    PARA type: float

    PARA growth_rate: The growth rate during the multistage period.
    PARA type: float

    PARA constant_growth: The growth rate in perpetuity.
    PARA type: float

    PARA periods: The number of periods.
    PARA type: int

    """
    total_value= 0


    for period in range(1, periods + 1):

        # if it's the last period calculate the terminal value
        if period == periods:

            # calculate the terminal dividend.
            terminal_dividend = (dividend * (1 + growth_rate) ** period)

            # calculate the terminal value and then discount it.
            terminal_value = terminal_dividend / (discount_rate - constant_growth_rate)
            terminal_value_disc = terminal_value / (1 + discount_rate) ** (period -1)

            # return the total value of the stock
            total_value += terminal_value_disc

        # otherwise calculate the cashflow for that period
        else:
            cashflow = (dividend * (1 + growth_rate) ** period) / (1 + discount_rate) ** period
            total_value += cashflow

    return total_value

# EXAMPLE
div = 1.00
gro = 0.20
cos = 0.05
dis = 0.10
per = 4

multistage_dividend_discount_model(div, dis, gro, cos, per)


def preferred_stock_valuation(dividend, required_rate_of_return):
    """
    Summary: Given a preferred dividend stock, calculate the value of that stock.

    PARA dividend: The dividend for each period, earned over an infinite period.
    PARA type: float

    PARA required_rate_of_return: The required rate of return desired for an investment.
    PARA type: float

    """

    return dividend / required_rate_of_return

# EXAMPLE
annual_div = 5.00
rrr = .08

preferred_stock_valuation(annual_div, rrr)
