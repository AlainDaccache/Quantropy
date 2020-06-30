'''
Weighted Average Cost of Capital
'''

def cost_of_preferred_stock(preferred_dividends, market_price_of_preferred):
    """
    Summary: Calculate the cost of preferred stock in the WACC formula.

    PARA preferred_dividends: The amount of a preferred dividend paid in that period.
    PARA type: float

    PARA market_price_of preferred: The price of a share of preferred stock during the period.
    PARA type: float

    """

    return preferred_dividends / market_price_of_preferred


# EXAMPLE
dividend = 8
price = 100
cost_of_preferred_stock( dividend, price)


def cost_of_debt(interest_rate, tax_rate):
    """
    Summary: Calculate the cost of debt in the WACC formula.

    PARA interest_rate: The interest rate charged on the debt.
    PARA type: float

    PARA tax_rate: The company's marginal federal plus state tax rate.
    PARA type: float

    """

    return interest_rate * (1 - tax_rate)

# EXAMPLE
interest_rate = .08
tax_rate = .4
cost_of_debt(interest_rate, tax_rate)


def cost_of_equity_capm(risk_free_rate, market_return, beta):
    """
    Summary: Calculate the cost of equity for WACC using the CAPM method.

    PARA risk_free_rate: The risk-free rate for the market, usually a treasury note.
    PARA type: float

    PARA market_return: The required rate of return for the company.
    PARA type: float

    PARA beta: The company's estimated stock beta.
    PARA type: float

    """

    return risk_free_rate + (beta * (market_return - risk_free_rate))

# EXAMPLE
beta = 1.1
rfr = .06
mkt = .11
cost_of_equity_capm(rfr, mkt, beta)


def cost_of_equity_ddm(stock_price, next_year_dividend, growth_rate):
    """
    Summary: Calculate the cost of equity for WACC using the DMM method.

    PARA stock_price: The company's current price of a share.
    PARA type: float

    PARA next_year_dividend: The expected dividend to be paid next year.
    PARA type: float

    PARA growth_rate: Firm's expected constant growth rate.
    PARA type: float

    """
    return (next_year_dividend / stock_price) + growth_rate

# EXAMPLE
p = 21
d = 1
g = .072
cost_of_equity_ddm(p, d, g)


def cost_of_equity_bond(bond_yield, risk_premium):
    """
    Summary: Calculate the cost of equity for WACC using the Bond yield plus risk premium method.

    PARA bond_yield: The company's interest rate on long-term debt.
    PARA type: float

    PARA risk_premium: The company's risk premium usually 3% to 5%.
    PARA type: float

    """
    return bond_yield + risk_premium

# EXAMPLE
y = .08
p = .05
cost_of_equity_bond(y, p)


def capital_weights(preferred_stock, total_debt, common_stock):
    """
    Summary: Given a firm's capital structure, calculate the weights of each group.

    PARA total_capital: The company's total capital.
    PARA type: float

    PARA preferred_stock: The company's preferred stock outstanding.
    PARA type: float

    PARA common_stock: The company's common stock outstanding.
    PARA type: float

    PARA total_debt: The company's total debt.
    PARA type: float

    RTYP weights_dict: A dictionary of all the weights.
    RTYP weights_dict: dictionary

    """
    # initalize the dictionary
    weights_dict = {}

    # calculate the total capital
    total_capital = preferred_stock + common_stock + total_debt

    # calculate each weight and store it in the dictionary
    weights_dict['preferred_stock'] = preferred_stock / total_capital
    weights_dict['common_stock'] = common_stock / total_capital
    weights_dict['total_debt'] = total_debt / total_capital

    return weights_dict

# EXAMPLE
debt = 8000000
preferred_stock = 2000000
common_stock = 10000000
capital_weights(preferred_stock, debt, common_stock)


def weighted_average_cost_of_capital(cost_of_common, cost_of_debt, cost_of_preferred, weights_dict):
    """
    Summary: Calculate a firm's WACC.

    PARA cost_of_common: The firm's cost of common equity.
    PARA type: float

    PARA cost_of_debt: The firm's cost of debt.
    PARA type: float

    PARA cost_of_preferred: The firm's cost of preferred equity.
    PARA type: float

    PARA weights_dict: The capital weights for each capital structure.
    PARA type: dictionary

    """

    weight_debt = weights_dict['total_debt']
    weight_common = weights_dict['common_stock']
    weight_preferred = weights_dict['preferred_stock']

    return (weight_debt * cost_of_debt) + (weight_common * cost_of_common) + (weight_preferred * cost_of_preferred)

# Cost of Equity
y = .08
p = .05
ke = cost_of_equity_bond(y, p)

# Cost of Debt
interest_rate = .08
tax_rate = .4
kd = cost_of_debt(interest_rate, tax_rate)

# Cost of Preferred
dividend = 8
price = 100
kp = cost_of_preferred_stock( dividend, price)

# Capital Weights
debt = 8000000
preferred_stock = 2000000
common_stock = 10000000
weights = capital_weights(preferred_stock, debt, common_stock)

weighted_average_cost_of_capital(ke, kd, kp, weights)