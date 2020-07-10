from datetime import datetime

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels import regression
import data_scraping.excel_helpers as excel
import config

# period is 21 trading days for monthly, and 252 trading days for yearly


def mean(returns, period=252):
    return period * sum(returns) / len(returns)


def standard_deviation_asset(returns, period=252):
    var = sum(pow(x-mean(returns, period), 2) for x in returns) / len(returns)  # variance
    return np.math.sqrt(var) * np.sqrt(period)


def standard_deviation_portfolio(returns, weights, period=252):
    return np.sqrt(np.dot(weights.T, np.dot(returns.cov() * period, weights)))


def risk_free_rate(date: datetime, period=252):
    return excel.read_entry_from_csv(config.beta_factors_file_path,
                                     config.yearly_factors if period == 252 else config.monthly_factors,
                                     date,
                                     'RF')


def beta_coefficient_covariance(asset_returns, benchmark_returns):
    covariance = np.cov(asset_returns.values, benchmark_returns.values)
    return covariance[0, 1] / covariance[1, 1]


def beta_coefficient_regression(asset_returns, benchmark_returns):
    benchmark_returns = sm.add_constant(benchmark_returns)
    model = regression.linear_model.OLS(asset_returns.values(), benchmark_returns).fit()
    return model.params[1]


def treynor_ratio(portfolio_returns, benchmark_returns, risk_free_rate, period=252):
    portfolio_beta = beta_coefficient_covariance(portfolio_returns, benchmark_returns)
    return ((portfolio_returns.mean() - risk_free_rate.mean()) * period) / portfolio_beta


def sharpe_ratio(portfolio_returns, risk_free_rate, period=252):
    portfolio_volatility = portfolio_returns.std() * np.sqrt(period)
    return ((portfolio_returns.mean() - risk_free_rate.mean()) * period) / portfolio_volatility


def information_ratio(portfolio_returns, benchmark_returns, period=252):
    return_difference = portfolio_returns - benchmark_returns
    volatility = standard_deviation_asset(return_difference, period)
    return (return_difference.mean() * period) / volatility


def modigliani_ratio(portfolio_returns, benchmark_returns, risk_free_rate, days=252):
    benchmark_volatility = standard_deviation_asset(benchmark_returns.std(), days)
    sharpe = sharpe_ratio(portfolio_returns, risk_free_rate, days)
    return (sharpe * benchmark_volatility) + risk_free_rate.mean()
