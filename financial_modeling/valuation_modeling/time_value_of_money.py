def compounded_rate(current_pct, periods):
    return (1 + current_pct) ** periods - 1


def present_value(future_value, discount_rate, periods):
    return future_value / ( 1 + discount_rate) ** periods


def future_value(present_value, discount_rate, periods):
    return present_value * ( 1 + discount_rate) ** periods


def net_present_value(discount_rate, cashflows):
    total_value = 0.0
    for index, cashflow in enumerate(cashflows):
        total_value += cashflow / (1 + discount_rate)**index
    return total_value


def present_value_perpetuity(cashflow, discount_rate):
    return cashflow / discount_rate


def present_value_perpetuity_due(cashflow, discount_rate):
    return cashflow / discount_rate * (1 + discount_rate)


def present_value_annuity(cashflow, discount_rate, periods):
    return cashflow / discount_rate * (1 - 1 / ( 1 + discount_rate )** periods)


def present_value_annuity_due(cashflow, discount_rate, periods):
    return cashflow / discount_rate * (1 - 1 / ( 1 + discount_rate )** periods) * (1 + discount_rate)


def present_value_growing_annuity(cashflow, discount_rate, periods, growth_rate):
    return cashflow / discount_rate * (1 - (1 + growth_rate) ** periods / (1 + discount_rate) ** periods)


def future_value_annuity(cashflow, discount_rate, periods):
    return cashflow / discount_rate * (( 1 + discount_rate )** periods - 1)


def future_value_annuity_due(cashflow, discount_rate, periods):
    return cashflow / discount_rate * (( 1 + discount_rate )** periods - 1) * (1 + discount_rate)


def effective_annual_rate(annual_percentage_rate, compounding_frequency):
    return (1 + annual_percentage_rate / compounding_frequency) ** compounding_frequency - 1
