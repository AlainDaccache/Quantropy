import math
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import data_scraping.excel_helpers as excel
import config
import financial_modeling.asset_pricing_models as asset_pricing_models
from scipy.stats import norm
import numpy.random as nrand

'''
Risk Deviation Measures
'''


def standard_deviation_portfolio(returns, weights, period=252):
    return np.sqrt(np.dot(weights.T, np.dot(returns.cov() * period, weights)))


def average_absolute_deviation(portfolio_returns, period=252):
    return stats.median_absolute_deviation(portfolio_returns) * np.sqrt(period)


def lower_semi_standard_deviation(portfolio_returns, period=252):
    returns_below_mean = portfolio_returns[portfolio_returns < portfolio_returns.mean()]
    return np.std(returns_below_mean) * np.sqrt(period)


path = '{}/{}.xlsx'.format(config.STOCK_PRICES_DIR_PATH, 'AAPL')
portfolio_returns = excel.read_df_from_csv(path)['Adj Close'].pct_change()
print(lower_semi_standard_deviation(portfolio_returns))

'''
Value at Risk (VAR) answers this question — What is the minimum loss over the whole range of outcomes in the 1% tail?
'''


# Historical Simulation: calculating daily portfolio changes in value to determine the probability distribution of returns.
def value_at_risk_historical_simulation(portfolio_returns, confidence_level=0.05):
    portfolio_returns = portfolio_returns.dropna()
    plt.hist(portfolio_returns, bins=40)
    plt.xlabel('Returns')
    plt.ylabel('Frequency')
    plt.grid(True)
    plt.show()
    sorted_returns = np.sort(portfolio_returns)
    total_count = len(sorted_returns)
    index = int(confidence_level * total_count)
    return abs(sorted_returns[index])


# Variance Covariance: calculate the inverse of the normal cumulative distribution (PPF)
def value_at_risk_variance_covariance(portfolio_returns, confidence_level=0.05, period=252):
    return abs(norm.ppf(confidence_level,
                        np.mean(portfolio_returns) * period,
                        np.std(portfolio_returns) * np.sqrt(period)))


# Monte Carlo
def value_at_risk_monte_carlo(portfolio_returns):
    pass


'''
Expected Shortfall, otherwise known as CVaR, or conditional value at risk, is simply the expected loss of the worst case scenarios of returns.
ES answers this question — What is the average loss over the whole range of outcomes in the 1% tail?
For example, if your portfolio has a VaR(95) of -3%, then the CVaR(95) would be the average value of all losses exceeding -3%.
'''


def conditional_value_at_risk(portfolio_returns, confidence_level=0.05, period=252):
    var = value_at_risk_historical_simulation(portfolio_returns=portfolio_returns, confidence_level=confidence_level)
    returns_below_var = portfolio_returns[portfolio_returns < var]
    return returns_below_var.mean()


'''
Measures of risk-adjusted return based on vol treat all deviations from the mean as risk, whereas measures of 
risk-adjusted return based on lower partial moments consider only deviations below some predefined minimum return 
threshold, t as risk i.e. positive deviations aren't risky. var is a more probabilistic view of loss as the risk of a portfolio
'''


# this method returns a lower partial moment of the returns
def lpm(returns, threshold, order):
    # create an array the same length as returns containing the minimum return threshold
    threshold_array = np.empty(len(returns))
    threshold_array.fill(threshold)
    diff = threshold_array - returns  # calculate the difference between the threshold and the returns
    diff = diff.clip(min=0)  # set the minimum of each to 0
    # return the sum of the different to the power of order
    return np.sum(diff ** order) / len(returns)


# returns a higher partial moment of the returns
def hpm(returns, threshold, order):
    # create an array the same length as returns containing hte minimum return threshold
    threshold_array = np.empty(len(returns))
    threshold_array.fill(threshold)
    diff = returns - threshold_array  # calc the diff between the returns and the threshold
    diff = diff.clip(min=0)  # set min of each to 0
    # return sum of the different to the power of order
    return np.sum(diff ** order) / len(returns)


# example usage
r = nrand.uniform(-1, 1, 50)
print('hpm(0.0)_1 = ', hpm(r, 0.0, 1))
print('lpm(0.0)_1 = ', lpm(r, 0.0, 1))

'''
Drawdown risk is the maximum (or average) historical 'drawdown' of the portfolio. 
A drawdown is the percentage loss between peak and trough.
'''


def drawdown_risk(portfolio_returns, trailing_period=252, max=False):
    if max:
        trailing_period = len(portfolio_returns)
    # Calculate the max drawdown in the past window days for each day in the series.
    # Use min_periods=1 if you want to let the first 252 days data have an expanding window
    rolling_max = portfolio_returns.rolling(trailing_period, min_periods=1).max()
    daily_drawdown = portfolio_returns / rolling_max - 1.0

    # Next we calculate the minimum (negative) daily drawdown in that window.
    max_daily_drawdown = daily_drawdown.rolling(trailing_period, min_periods=1).min()

    # Plot the results
    daily_drawdown.plot()
    max_daily_drawdown.plot()
    plt.show()
    return {
        'daily_drawdown': daily_drawdown,
        'max_daily_drawdown': max_daily_drawdown,
        'average_daily_drawdown': np.mean(daily_drawdown)
    }


'''
Risk Adjusted Returns Measures Based on Volatility
'''


# calculates the excess returns generated by a portfolio E(r) - rf and discounts it by portfolio beta: (E(r) - rd )/ beta
def treynor_ratio(portfolio_returns, benchmark_returns, risk_free_rate, period=252):
    portfolio_beta = asset_pricing_models.capital_asset_pricing_model(portfolio_returns=portfolio_returns,
                                                                      benchmark_returns=benchmark_returns).params[1]
    return ((portfolio_returns.mean() - risk_free_rate) * period) / portfolio_beta


# extension of Traynor - discounts expected excess returns by vol
def sharpe_ratio(portfolio_returns, risk_free_rate, period=252):
    portfolio_volatility = portfolio_returns.std() * np.sqrt(period)
    return ((portfolio_returns.mean() - risk_free_rate) * period) / portfolio_volatility


# extension of Sharpe ratio - replaces risk-free rate of return with the scalar expected return of a benchmark portfolio E(rb)
def information_ratio(portfolio_returns, benchmark_returns, period=252):
    return_difference = portfolio_returns - benchmark_returns
    volatility = np.std(return_difference, period)
    return (return_difference.mean() * period) / volatility


# combination of the Sharpe and info ratios. Adjusts the expected excess returns of the portfolio above the risk free
# rate by the expected excess returns of a benchmark portfolio, above the risk free rate
def modigliani_ratio(portfolio_returns, benchmark_returns, risk_free_rate, period=252):
    benchmark_volatility = np.std(benchmark_returns.std(), period)
    sharpe = sharpe_ratio(portfolio_returns, risk_free_rate, period)
    return (sharpe * benchmark_volatility) + risk_free_rate.mean()


'''
Risk Adjusted Returns Measures Based on Value at Risk
'''


# discounts the excess return of the portfolio above the risk-free rate by the value at risk of the portfolio
def excess_return_value_at_risk(portfolio_returns, risk_free_rate: float, confidence_level: float = 0.05, period=252):
    return (portfolio_returns.mean() * period - risk_free_rate) / value_at_risk_historical_simulation(
        portfolio_returns=portfolio_returns,
        confidence_level=confidence_level)


# discounts the excess return of the portfolio above the risk-free rate by the conditional VaR of the portfolio
def conditional_sharpe_ratio(portfolio_returns, risk_free_rate: float, confidence_level: float = 0.05,
                             period: int = 252):
    return (portfolio_returns.mean() * period - risk_free_rate) / conditional_value_at_risk(
        portfolio_returns=portfolio_returns, confidence_level=confidence_level)


def jensens_alpha(portfolio_returns, benchmark_returns):
    return asset_pricing_models.capital_asset_pricing_model(portfolio_returns=portfolio_returns,
                                                            benchmark_returns=benchmark_returns).params[0]


'''
Risk Adjusted Returns Measures Based on Partial Moments
'''


def omega_ratio(portfolio_returns, risk_free_rate: float, target=0, period: int = 252):
    return (portfolio_returns.mean() * period - risk_free_rate) / lpm(portfolio_returns, target, 1)


def sortino_ratio(portfolio_returns, risk_free_rate: float, target=0, period: int = 252):
    return (portfolio_returns.mean() * period - risk_free_rate) / np.sqrt(lpm(portfolio_returns, target, 2))


def kappa_three_ratio(portfolio_returns, risk_free_rate: float, target=0, period: int = 252):
    return (portfolio_returns.mean() * period - risk_free_rate) / math.pow(lpm(portfolio_returns, target, 3),
                                                                           float(1 / 3))


def gain_loss_ratio(portfolio_returns, target=0):
    return hpm(portfolio_returns, target, 1) / lpm(portfolio_returns, target, 1)


def upside_potential_ratio(portfolio_returns, target=0):
    return hpm(portfolio_returns, target, 1) / math.sqrt(lpm(portfolio_returns, target, 2))

# h = 10. # horizon of 10 days
# mu_h = 0.1 # this is the mean of % returns over 10 days - 10%
# sig = 0.3 # this is the vol of returns over a year - 30%
# sig_h = 0.3 * np.sqrt(h/252) # this is the vol over the horizon
# alpha = 0.01
