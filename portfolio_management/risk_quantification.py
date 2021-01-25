import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from scipy.stats import norm
from quantitative_analysis.risk_factor_modeling import CapitalAssetPricingModel

'''
Risk Deviation Measures
'''


def standard_deviation(portfolio_returns, period=252):
    """

    :param portfolio_returns: Pandas series representing percentage changes of the security (or portfolio) returns over time. It should be same time range and frequency as risk free rates
    :param period: period to compute statistics of returns for. For instance, to compute yearly, then input 252, and to compute monthly, then input 21.
    :return:
    """
    return portfolio_returns.std() * np.sqrt(period)


# def standard_deviation_portfolio(returns, weights, period=252):
#     return np.sqrt(np.dot(weights.T, np.dot(returns.cov() * period, weights)))


def average_absolute_deviation(portfolio_returns, period=252):
    return stats.median_absolute_deviation(portfolio_returns) * np.sqrt(period)


def lower_semi_standard_deviation(portfolio_returns, period=252):
    returns_below_mean = portfolio_returns[portfolio_returns < portfolio_returns.mean()]
    return np.std(returns_below_mean) * np.sqrt(period)


'''
Value at Risk (VAR) quantifies the minimum loss over the whole range of outcomes in the 1% tail?
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


def conditional_value_at_risk(portfolio_returns, confidence_level=0.05, period=252):
    """
    Expected Shortfall, otherwise known as CVaR, or conditional value at risk, is simply the expected loss of the worst case scenarios of returns.
    ES answers this question — What is the average loss over the whole range of outcomes in the 1% tail?
    For example, if your portfolio has a VaR(95) of -3%, then the CVaR(95) would be the average value of all losses exceeding -3%.

    :param portfolio_returns: Pandas series representing percentage changes of the security (or portfolio) returns over time. It should be same time range and frequency as risk free rates
    :param confidence_level:
    :param period: period to compute statistics of returns for. For instance, to compute yearly, then input 252, and to compute monthly, then input 21.
    :return:
    """
    var = value_at_risk_historical_simulation(portfolio_returns=portfolio_returns, confidence_level=confidence_level)
    returns_below_var = portfolio_returns[portfolio_returns < var]
    return returns_below_var.mean()


def lpm(returns, threshold, order):
    """
    Returns a lower partial moment of the returns. Example usage:

    >>>  r = nrand.uniform(-1, 1, 50)
    >>>  print('lpm(0.0)_1 = ', lpm(r, 0.0, 1))

    :param returns:
    :param threshold:
    :param order:
    :return:
    """
    # create an array the same length as returns containing the minimum return threshold
    threshold_array = np.empty(len(returns))
    threshold_array.fill(threshold)
    diff = threshold_array - returns  # calculate the difference between the threshold and the returns
    diff = diff.clip(min=0)  # set the minimum of each to 0
    # return the sum of the different to the power of order
    return np.sum(diff ** order) / len(returns)


def hpm(returns, threshold, order):
    """
    Returns a higher partial moment of the returns. Example usage:

    >>> r = nrand.uniform(-1, 1, 50)
    >>> print('hpm(0.0)_1 = ', hpm(r, 0.0, 1))

    :param returns:
    :param threshold:
    :param order:
    :return:
    """
    # create an array the same length as returns containing hte minimum return threshold
    threshold_array = np.empty(len(returns))
    threshold_array.fill(threshold)
    diff = returns - threshold_array  # calc the diff between the returns and the threshold
    diff = diff.clip(min=0)  # set min of each to 0
    # return sum of the different to the power of order
    return np.sum(diff ** order) / len(returns)


def drawdown_risk(portfolio_returns, trailing_period=252, max=False):
    """
    Drawdown risk is the maximum (or average) historical 'drawdown' of the portfolio.
    A drawdown is the percentage loss between peak and trough.

    :param portfolio_returns: Pandas series representing percentage changes of the security (or portfolio) returns over time. It should be same time range and frequency as risk free rates
    :param trailing_period:
    :param max:
    :return:
    """
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


def treynor_ratio(portfolio_returns, risk_free_rates, benchmark_returns=None, period=252):
    """
    The **Treynor reward to volatility model** is a measurement of the returns earned in excess of that which could have
    been earned on an investment that has no diversifiable risk (e.g., Treasury bills or a completely diversified portfolio),
    per unit of market risk assumed. In other words, it calculates the excess returns generated by a portfolio
    :math:`r_i - r_f`, where :math:`r_i` is the portfolio :math:`i`'s returns and :math:`r_f` is the risk-free
    rate, then discounts it by portfolio :math:`i`'s beta, :math:`\\beta_i`.

    Like the Sharpe ratio, the Treynor ratio (T) does not quantify the value added, if any, of active portfolio
    management. It is a ranking criterion only. A ranking of portfolios based on the Treynor Ratio is only useful if
    the portfolios under consideration are sub-portfolios of a broader, fully diversified portfolio.
    If this is not the case, portfolios with identical systematic risk, but different total risk, will be rated the same.
    But the portfolio with a higher total risk is less diversified and therefore has a higher unsystematic risk which is
    not priced in the market.

    An alternative method of ranking portfolio management is Jensen's alpha, which quantifies the added return as the
    excess return above the security market line in the capital asset pricing model. As these two methods both determine
    rankings based on systematic risk alone, they will rank portfolios identically.

    :param portfolio_returns: Pandas series representing percentage changes of the security (or portfolio) returns over time. It should be same time range and frequency as risk free rates
    :param benchmark_returns: Pandas series representing percentage changes of the benchmark (i.e. S&P500) returns over time.
    :param risk_free_rates: Pandas series representing percentage changes of a risk-free asset's returns over time. It should be same time range and frequency as portfolio_returns
    :param period: period to compute statistics of returns for. For instance, to compute yearly, then input 252, and to compute monthly, then input 21.
    :return: :math:`T = \\frac{r_i - r_f}{\\beta_i}`
    """
    portfolio_beta = capm_beta(benchmark_returns=benchmark_returns, portfolio_returns=portfolio_returns)
    return ((portfolio_returns.mean() - risk_free_rates.mean()) * period) / portfolio_beta


def sharpe_ratio(portfolio_returns, risk_free_rates, period=252):
    """
    The **Sharpe ratio** was developed by William F. Sharpe in 1966. It is an extension of the *Traynor ratio*, as
    it discounts expected excess returns by the volatility. It measures the performance of an investment
    (e.g., a security or portfolio) compared to a risk-free asset, after adjusting for its risk.
    In other words, it is the difference between the returns of the investment  and the risk-free return, divided by
    the standard deviation of the investment (i.e., its volatility). It represents the additional amount of return
    that an investor receives per unit of increase in risk.

    The *ex-ante* ratio is defined as :math:`\\frac{E[R_a - R_b]}{\\sigma_a}` where :math:`R_{a}` is the asset return,
    :math:`R_b` is the risk-free return (such as a U.S. Treasury security). :math:`E[R_{a}-R_{b}]` is the expected
    value of the excess of the asset return over the benchmark return, and :math:`\\sigma _{a}` is the standard deviation
    of the asset excess return. The *ex-post* ratio uses the same equation as the one above but with realized returns
    of the asset and benchmark rather than expected returns

    :param portfolio_returns: Pandas series representing percentage changes of the security (or portfolio) returns over time. It should be same time range and frequency as risk free rates Pandas series representing percentage changes of the security (or portfolio) returns over time. It should be same time range and frequency as risk free rates
    :param risk_free_rates: Pandas series representing percentage changes of a risk-free asset's returns over time. It should be same time range and frequency as portfolio_returns Pandas series representing percentage changes of a risk-free asset's returns over time. It should be same time range and frequency as portfolio_returns
    :param period: period to compute statistics of returns for. For instance, to compute yearly, then input 252, and to compute monthly, then input 21. Period to compute statistics of returns for. For instance, to compute yearly, then input 252, and to compute monthly, then input 21.
    :return: :math:`S = \\frac{E[R_a - R_b]}{\\sigma_a}`
    """
    portfolio_volatility = portfolio_returns.std() * np.sqrt(period)
    return ((portfolio_returns.mean() - risk_free_rates.mean()) * period) / portfolio_volatility


def information_ratio(portfolio_returns, benchmark_returns, period=252):
    """
    The **information ratio** is similar to the Sharpe ratio, the main difference being that the Sharpe ratio uses a
    risk-free return as benchmark whereas the information ratio uses a risky index as benchmark (such as the S&P500).

    :param portfolio_returns: Pandas series representing percentage changes of the security (or portfolio) returns over time. It should be same time range and frequency as risk free rates
    :param benchmark_returns: Pandas series representing percentage changes of the benchmark (i.e. S&P500) returns over time. Pandas series representing percentage changes of the benchmark (i.e. S&P500) returns over time.
    :param period: period to compute statistics of returns for. For instance, to compute yearly, then input 252, and to compute monthly, then input 21.
    :return:
    """
    return_difference = portfolio_returns - benchmark_returns
    return (return_difference.mean() * period) / (return_difference.std() * np.sqrt(period))


def modigliani_ratio(portfolio_returns, benchmark_returns, risk_free_rates, period=252):
    """
    The **Modigliani risk-adjusted performance** is a combination of the Sharpe and info ratios.
    It adjusts the expected excess returns of the portfolio above the risk free rate by the expected excess
    returns of a benchmark portfolio, above the risk free rate.

    :param portfolio_returns: Pandas series representing percentage changes of the security (or portfolio) returns over time. It should be same time range and frequency as risk free rates
    :param benchmark_returns: Pandas series representing percentage changes of the benchmark (i.e. S&P500) returns over time.
    :param risk_free_rates: Pandas series representing percentage changes of a risk-free asset's returns over time. It should be same time range and frequency as portfolio_returns
    :param period: period to compute statistics of returns for. For instance, to compute yearly, then input 252, and to compute monthly, then input 21.
    :return:
    """
    benchmark_volatility = np.std(benchmark_returns.std(), period)
    sharpe = sharpe_ratio(portfolio_returns, risk_free_rates, period)
    return (sharpe * benchmark_volatility) + (risk_free_rates.mean() * period)


def excess_return_value_at_risk(portfolio_returns, risk_free_rates, confidence_level: float = 0.05, period=252):
    """
    Discounts the excess return of the portfolio above the risk-free rate by the value at risk of the portfolio

    :param portfolio_returns: Pandas series representing percentage changes of the security (or portfolio) returns over time. It should be same time range and frequency as risk free rates
    :param risk_free_rates: Pandas series representing percentage changes of a risk-free asset's returns over time. It should be same time range and frequency as portfolio_returns
    :param confidence_level:
    :param period: period to compute statistics of returns for. For instance, to compute yearly, then input 252, and to compute monthly, then input 21.
    :return:
    """
    return ((portfolio_returns.mean() - risk_free_rates.mean()) * period) / \
           value_at_risk_historical_simulation(portfolio_returns=portfolio_returns, confidence_level=confidence_level)


def conditional_sharpe_ratio(portfolio_returns, risk_free_rates, confidence_level: float = 0.05, period: int = 252):
    """
    Discounts the excess return of the portfolio above the risk-free rate by the conditional VaR of the portfolio

    :param portfolio_returns: Pandas series representing percentage changes of the security (or portfolio) returns over time. It should be same time range and frequency as risk free rates
    :param risk_free_rates: Pandas series representing percentage changes of a risk-free asset's returns over time. It should be same time range and frequency as portfolio_returns
    :param confidence_level:
    :param period: period to compute statistics of returns for. For instance, to compute yearly, then input 252, and to compute monthly, then input 21.
    :return:
    """
    return ((portfolio_returns.mean() - risk_free_rates.mean()) * period) / \
           conditional_value_at_risk(portfolio_returns=portfolio_returns, confidence_level=confidence_level)


def capm_beta(portfolio_returns, benchmark_returns=None):
    """

    :param portfolio_returns: Pandas series representing percentage changes of the security (or portfolio) returns over time. It should be same time range and frequency as risk free rates
    :param benchmark_returns: Pandas series representing percentage changes of the benchmark (i.e. S&P500) returns over time.
    :return:
    """
    return CapitalAssetPricingModel(from_date=portfolio_returns.index[0], to_date=portfolio_returns.index[-1],
                                    factor_dataset=benchmark_returns) \
        .regress_factor_loadings(portfolio=portfolio_returns).params[1]


def jensens_alpha(portfolio_returns, benchmark_returns):
    """
    The **Jensen's alpha** determines the abnormal return of a security or portfolio of securities over the theoretical
    expected return. It is a version of the standard alpha based on a theoretical performance index instead of a market index.
    The theoretical return is predicted by a market model, most commonly the capital asset pricing model (CAPM).
    The market model uses statistical methods to predict the appropriate risk-adjusted return of an asset.

    The CAPM for instance uses beta as a multiplier. The CAPM return is supposed to be 'risk adjusted',
    which means it takes account of the relative riskiness of the asset. This is based on the concept that riskier
    assets should have higher expected returns than less risky assets. If an asset's return is even higher than the
    risk adjusted return, that asset is said to have "positive alpha" or "abnormal returns".
    Investors are constantly seeking investments that have higher alpha.

    Since Eugene Fama, many academics believe financial markets are too efficient to allow for repeatedly earning
    positive Alpha, unless by chance.

    :param portfolio_returns: Pandas series representing percentage changes of the security (or portfolio) returns over time. It should be same time range and frequency as risk free rates
    :param benchmark_returns: Pandas series representing percentage changes of the benchmark (i.e. S&P500) returns over time.
    :return:
    """
    return CapitalAssetPricingModel(from_date=portfolio_returns.index[0], to_date=portfolio_returns.index[-1],
                                    factor_dataset=benchmark_returns) \
        .regress_factor_loadings(portfolio=portfolio_returns).params[0]


def omega_ratio(portfolio_returns, risk_free_rates, target=0, period: int = 252):
    """
    Notice the denominator is power of 1/1.

    :param portfolio_returns: Pandas series representing percentage changes of the security (or portfolio) returns over time. It should be same time range and frequency as risk free rates
    :param risk_free_rates: Pandas series representing percentage changes of a risk-free asset's returns over time. It should be same time range and frequency as portfolio_returns
    :param target: minimum acceptable return, below which the returns are less desirable.
    :param period: period to compute statistics of returns for. For instance, to compute yearly, then input 252, and to compute monthly, then input 21.
    :return:
    """
    return ((portfolio_returns.mean() - risk_free_rates.mean()) * period) / lpm(portfolio_returns, target, 1)


def sortino_ratio(portfolio_returns, risk_free_rates, target=0, period: int = 252):
    """
    Notice the denominator is power of 1/2.

    :param portfolio_returns: Pandas series representing percentage changes of the security (or portfolio) returns over time. It should be same time range and frequency as risk free rates
    :param risk_free_rates: Pandas series representing percentage changes of a risk-free asset's returns over time. It should be same time range and frequency as portfolio_returns
    :param target: minimum acceptable return, below which the returns are less desirable.
    :param period: period to compute statistics of returns for. For instance, to compute yearly, then input 252, and to compute monthly, then input 21.
    :return:
    """
    return ((portfolio_returns.mean() - risk_free_rates.mean()) * period) / np.sqrt(lpm(portfolio_returns, target, 2))


def kappa_three_ratio(portfolio_returns, risk_free_rates, target=0, period: int = 252):
    """
    Notice the denominator is power of 1/3.

    :param portfolio_returns: Pandas series representing percentage changes of the security (or portfolio) returns over time. It should be same time range and frequency as risk free rates
    :param risk_free_rates: Pandas series representing percentage changes of a risk-free asset's returns over time. It should be same time range and frequency as portfolio_returns
    :param target: minimum acceptable return, below which the returns are less desirable.
    :param period: period to compute statistics of returns for. For instance, to compute yearly, then input 252, and to compute monthly, then input 21.
    :return:
    """
    return ((portfolio_returns.mean() - risk_free_rates.mean()) * period) / math.pow(lpm(portfolio_returns, target, 3),
                                                                                     float(1 / 3))


def gain_loss_ratio(portfolio_returns, target=0):
    """

    :param portfolio_returns: Pandas series representing percentage changes of the security (or portfolio) returns over time. It should be same time range and frequency as risk free rates
    :param target: minimum acceptable return, below which the returns are less desirable.
    :return:
    """
    return hpm(portfolio_returns, target, 1) / lpm(portfolio_returns, target, 1)


def upside_potential_ratio(portfolio_returns, target=0):
    """
    The **upside-potential ratio** is a measure of a return of an investment asset relative to the minimal acceptable
    return. The measurement allows a firm or individual to choose investments which have had relatively good upside
    performance, per unit of downside risk.

    :param portfolio_returns: Pandas series representing percentage changes of the security (or portfolio) returns over time. It should be same time range and frequency as risk free rates
    :param target: minimum acceptable return, below which the returns are less desirable. minimum acceptable return, below which the returns are less desirable.
    :return:
    """
    return hpm(portfolio_returns, target, 1) / math.sqrt(lpm(portfolio_returns, target, 2))


def roys_safety_first_criterion(portfolio_returns: pd.Series, minimum_threshold=0.02, period=252):
    """

    :param portfolio_returns: Pandas series representing percentage changes of the security (or portfolio) returns over time. It should be same time range and frequency as risk free rates
    :param minimum_threshold: minimum acceptable return, below which the returns are less desirable.
    :param period: period to compute statistics of returns for. For instance, to compute yearly, then input 252, and to compute monthly, then input 21.
    :return:
    """
    return (portfolio_returns.mean() * period - minimum_threshold) / (portfolio_returns.std() * math.sqrt(period))


if __name__ == '__main__':
    from portfolio_management.Portfolio import Portfolio
    from datetime import datetime

    assets = ['AAPL', 'V', 'KO', 'CAT']
    portfolio = Portfolio(assets=assets)
    portfolio.slice_dataframe(to_date=datetime(2021, 1, 1), from_date=datetime(2016, 1, 1))
    portfolio_returns = portfolio.get_weighted_sum_returns(weights=np.ones(len(assets)) / len(assets))
    print(portfolio_returns.head())
    print(roys_safety_first_criterion(portfolio_returns=portfolio_returns, minimum_threshold=0.02, period=252))
