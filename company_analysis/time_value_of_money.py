'''
Time Value of Money
'''


def present_value(future_value, discount_rate, periods):
    '''
    Summary: Given a future value cash flow, estimate the present value of that cash flow.

    PARA future_value: The future value cash flow.
    PARA type: float

    PARA discount_rate: The discount rate
    PARA type: float

    PARA periods: The number of periods.
    PARA type: int

    '''

    return future_value / ( 1 + discount_rate) ** periods

# EXAMPLE
fut_val = 1000.0
rate = 0.2
per = 10

present_value(fut_val, rate, per)


def future_value(present_value, discount_rate, periods):
    '''
    Summary: Given a present value cash flow, estimate the future value of that cash flow.

    PARA present_value: The present value cash flow.
    PARA type: float

    PARA discount_rate: The discount rate
    PARA type: float

    PARA periods: The number of periods.
    PARA type: int

    '''

    return present_value * ( 1 + discount_rate) ** periods

# EXAMPLE
pres_val = 1000.0
rate = 0.2
per = 10

future_value(pres_val, rate, per)


def net_present_value(discount_rate, cashflows):
    '''
    Summary: Given a series of cash flows, calculate the net present value of those cash flows.

    PARA discount_rate: The discount rate
    PARA type: float

    PARA cashflows: A series of cash flows.
    PARA type: list

    '''

    # initalize result
    total_value = 0.0

    # loop through cashflows and calculate discounted value.
    for index, cashflow in enumerate(cashflows):
        total_value += cashflow / (1 + discount_rate)**index

    return total_value

# EXAMPLE
rate = 0.2
cashflows = [100, 100, 100, 100, 100]

net_present_value(rate, cashflows)


def present_value_perpetuity(cashflow, discount_rate):
    '''
    Summary: Given a cash flow, calculate the present value in perpetuity.

    PARA cashflow: A single cash flow.
    PARA type: float

    PARA discount_rate: The discount rate
    PARA type: float

    '''

    return cashflow / discount_rate

# EXAMPLE
cf = 1000.0
rate = 0.01

present_value_perpetuity(cf, rate)


def present_value_perpetuity_due(cashflow, discount_rate):
    '''
    Summary: Given a cash flow, calculate the present value in perpetuity due.

    PARA cashflow: A single cash flow.
    PARA type: float

    PARA discount_rate: The discount rate
    PARA type: float

    '''

    return cashflow / discount_rate * (1 + discount_rate)

# EXAMPLE
cf = 1000.0
rate = 0.01

present_value_perpetuity_due(cf, rate)


def present_value_annuity(cashflow, discount_rate, periods):
    '''
    Summary: Given a cash flow, calculate the present value of an annuity.

    PARA cashflow: A single cash flow.
    PARA type: float

    PARA discount_rate: The discount rate
    PARA type: float

    PARA periods: The number of periods.
    PARA type: int

    '''
    return cashflow / discount_rate * (1 - 1 / ( 1 + discount_rate )** periods)

# EXAMPLE
cf = 1000.0
rate = 0.01
per = 10

present_value_annuity(cf, rate, per)


def present_value_annuity_due(cashflow, discount_rate, periods):
    '''
    Summary: Given a cash flow, calculate the present value of an annuity due.

    PARA cashflow: A single cash flow.
    PARA type: float

    PARA discount_rate: The discount rate
    PARA type: float

    PARA periods: The number of periods.
    PARA type: int

    '''

    return cashflow / discount_rate * (1 - 1 / ( 1 + discount_rate )** periods) * (1 + discount_rate)

# EXAMPLE
cf = 1000.0
rate = 0.01
per = 10
present_value_annuity_due(cf, rate, per)


def present_value_growing_annuity(cashflow, discount_rate, periods, growth_rate):
    '''
    Summary: Given a cash flow, calculate the present value of a growing annuity. The assumption is that the
             discount rate > growth rate, otherwise a negative value will be returned.

    PARA cashflow: A single cash flow.
    PARA type: float

    PARA discount_rate: The discount rate
    PARA type: float

    PARA periods: The number of periods.
    PARA type: int

    PARA growth_rate: The growth rate
    PARA type: float

    '''

    return cashflow / discount_rate * (1 - (1 + growth_rate) ** periods / (1 + discount_rate) ** periods)

# EXAMPLE
cf = 1000.0
rate = 0.05
per = 10
gr = 0.03

present_value_growing_annuity(cf, rate, per, gr)


def future_value_annuity(cashflow, discount_rate, periods):
    '''
    Summary: Given a cash flow, calculate the future value of an annuity.

    PARA cashflow: A single cash flow.
    PARA type: float

    PARA discount_rate: The discount rate
    PARA type: float

    PARA periods: The number of periods.
    PARA type: int

    '''
    return cashflow / discount_rate * (( 1 + discount_rate )** periods - 1)

# EXAMPLE
cf = 1000.0
rate = 0.01
per = 10

future_value_annuity(cf, rate, per)


def future_value_annuity_due(cashflow, discount_rate, periods):
    '''
    Summary: Given a cash flow, calculate the future value of an annuity due.

    PARA cashflow: A single cash flow.
    PARA type: float

    PARA discount_rate: The discount rate
    PARA type: float

    PARA periods: The number of periods.
    PARA type: int

    '''

    return cashflow / discount_rate * (( 1 + discount_rate )** periods - 1) * (1 + discount_rate)

# EXAMPLE
cf = 1000.0
rate = 0.01
per = 10

future_value_annuity_due(cf, rate, per)


def eff_annual_rate(apr, frequency):
    '''
    Summary: Given an APR (Annual Percentage Rate) calculate the EAR (Effective Annual Rate)

    PARA apr: The Annual Percentage Rate.
    PARA type: float

    PARA frequency: The compounding frequency.
    PARA type: int
    '''

    return (1 + apr / frequency) ** frequency - 1

# EXAMPLE
annual_rate = .03
comp_freq = 10

eff_annual_rate(annual_rate, comp_freq)
