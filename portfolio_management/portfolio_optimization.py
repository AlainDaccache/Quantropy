from functools import partial

import numpy as np
import matplotlib.pyplot as plt
from cvxpy import *
import pandas as pd
import portfolio_management.risk_quantification as risk_measures

np.random.seed(123)


def optimal_portfolio_allocation(portfolio_returns: pd.DataFrame, risk_measure, longs=None, shorts=None,
        objective_function: str = 'Mean-Variance',
        constraints: dict = {'Sum of All Weights Equal to': 1,
                             'Maximum Allocation to': {'Stock': 0.2,
                                                       'Industry': {},
                                                       'Sector': {},
                                                       'Asset Class': {}}}):
    '''

    * Objective Function: Mean-Variance, Beta Neutral, Risk Parity...

    * Constraints:

        - Sum of all weights equal to one,
        - Maximum allocation to a stock or industry or sector or asset class is x %, ...

    :param portfolio_returns: Series of series
    :param longs:
    :param shorts:
    :param risk_measure:
    :return:
    '''
    weighted_portfolio_returns_list, weighted_portfolio_risk_list, stock_weights_list, portfolio_volatilities_list = \
        [], [], [], []

    for i in range(5000):
        weights = np.array(np.random.random(len(portfolio_returns)))  # select random weights for portfolio holdings
        weights /= np.sum(weights)  # rebalance weights to sum to 1
        stock_weights_list.append(weights)

        # calculate return and risk of the whole portfolio
        weighted_portfolio_returns = np.sum(portfolio_returns * weights)
        weighted_portfolio_returns_list.append(weighted_portfolio_returns)

        portfolio_volatility = risk_measures.standard_deviation_portfolio(returns=portfolio_returns, weights=weights,
                                                                          period=252)
        portfolio_volatilities_list.append(portfolio_volatility)

        weighted_portfolio_risk = risk_measure(portfolio_returns=weighted_portfolio_returns)

        weighted_portfolio_risk_list.append(weighted_portfolio_risk)

    # a dictionary for Returns and Risk values of each portfolio
    portfolio = {'Returns': weighted_portfolio_returns_list,
                 'Volatility': portfolio_volatilities_list,
                 'Risk Ratio': weighted_portfolio_risk_list}

    # extend original dictionary to accomodate each ticker and weight in the portfolio
    for counter, (symbol, returns) in enumerate(enumerate(portfolio_returns)):
        portfolio['{} {}'.format(symbol, 'Weight')] = [Weight[counter] for Weight in stock_weights_list]

    results_frame = pd.DataFrame(portfolio)
    print(results_frame.head())

    # locate position of portfolio with highest Risk Adjusted Return Ratio
    max_risk_ratio_port = results_frame.iloc[results_frame['Risk Ratio'].idxmax()]
    # locate positon of portfolio with minimum standard deviation
    min_vol_port = results_frame.iloc[results_frame['Volatility'].idxmin()]

    # create scatter plot coloured by Sharpe Ratio
    plt.scatter(results_frame['Volatility'], results_frame['Returns'], c=results_frame['Sharpe Ratio'], cmap='RdYlGn')
    plt.xlabel('Volatility (Std. Deviation)')
    plt.ylabel('Expected Returns')
    plt.title('Efficient Frontier')
    plt.colorbar()

    # plot red star to highlight position of portfolio with highest Sharpe Ratio
    plt.scatter(max_risk_ratio_port[1], max_risk_ratio_port[0], marker='D', color='r', s=100)
    # plot green star to highlight position of minimum variance portfolio
    plt.scatter(min_vol_port[1], min_vol_port[0], marker='D', color='g', s=100)

    print("The portfolio weight allocation that maximizes the risk adjusted returns ratio is \n {}".format(
        max_risk_ratio_port))
    print("The portfolio weight allocation that minimizes the volatility is \n {}".format(min_vol_port))
    return max_risk_ratio_port
