import abc
from functools import partial
import numpy as np
import pandas as pd
import typing
from cvxpy import *
import scipy.optimize
import historical_data_collection.excel_helpers as excel
import portfolio_management.risk_quantification as risk_measures
from fundamental_analysis.macroeconomic_analysis import risk_free_rates
from fundamental_analysis.supporting_metrics import market_capitalization

np.random.seed(123)


class ExpectedReturnsMethods:
    def __init__(self, portfolio_returns: pd.DataFrame):
        self.portfolio_returns = portfolio_returns

    def mean_historical_returns(self, exponentially_weighted=False):
        pass

    def log_historical_returns(self):
        pass

    def returns_capm(self):
        pass


class RiskModels:
    def __init__(self, portfolio_returns: pd.DataFrame):
        self.portfolio_returns = portfolio_returns

    def sample_covariance(self):
        pass

    def semi_covariance(self):
        pass

    def exponential_covariance(self):
        pass

    def theory_implied_correlation(self):
        '''
        https://mlfinlab.readthedocs.io/en/latest/portfolio_optimisation/theory_implied_correlation.html
        :return:
        '''
        pass


class PortfolioOptimizationModel(metaclass=abc.ABCMeta):
    def __init__(self, portfolio_returns: pd.DataFrame):
        self.portfolio_returns = portfolio_returns

    def expected_returns(self, weights):
        pass

    def covariance_matrix(self, weights):
        pass

    def objective_function(self, weights):
        '''
        Typically, maximize Sharpe Ratio, minimize variance...
        :param weights:
        :return:
        '''
        pass

    def solve_weights(self, fitness: typing.Callable, objective: str, leverage=0, long_short_exposure=0):
        n = len(self.portfolio_returns.columns)
        W = np.ones([n]) / n  # start with equal weights
        exp_returns = self.expected_returns(weights=W)
        cov_matrix = self.covariance_matrix(weights=W)

        b_ = [(0., 1.) for _ in range(n)]  # weights between 0%..100%.
        # No leverage, no shorting
        c_ = ({'type': 'eq', 'fun': lambda w: sum(w) - 1.})  # Sum of weights = 100%

        optimized = scipy.optimize.minimize(fun=fitness, args=[exp_returns, cov_matrix], x0=W,
                                            method='SLSQP', constraints=c_,
                                            bounds=b_)
        if not optimized.success:
            raise BaseException(optimized.message)
        return optimized.x  # Return optimized weights


class EquallyWeightedPortfolio(PortfolioOptimizationModel):
    def __init__(self, portfolio_returns: pd.DataFrame):
        super().__init__(portfolio_returns)

    def solve_weights(self, fitness: typing.Callable = lambda x: x, objective: str = '0', leverage=0,
                      long_short_exposure=0):
        output = pd.Series()
        for ticker, stock_return in self.portfolio_returns.iteritems():
            output[ticker] = 1 / len(self.portfolio_returns)
        return output


class MarketCapitalizationWeightedPortfolio(PortfolioOptimizationModel):
    def __init__(self, portfolio_returns: pd.DataFrame):
        super().__init__(portfolio_returns)

    def solve_weights(self, fitness: typing.Callable, objective: str, leverage=0, long_short_exposure=0):
        output = pd.Series()
        for ticker, stock_return in self.portfolio_returns.iteritems():
            output[ticker] = market_capitalization(stock=str(ticker), date=self.portfolio_returns.index[-1])
        return output / sum(output)


class InverseVolatilityPortfolio():
    pass


class InverseBetaPortfolio():
    pass


class MeanVarianceModel(PortfolioOptimizationModel):
    # Global Minimum Variance Portfolio (GMVP)
    def __init__(self, portfolio_returns: pd.DataFrame):
        super().__init__(portfolio_returns)

    def expected_returns(self, weights):
        return np.mean(self.portfolio_returns * weights)

    def covariance_matrix(self, weights):
        return np.cov(self.portfolio_returns)

    def objective_function(self, weights):
        pass

    def efficient_frontier(self):
        frontier_mean, frontier_var, frontier_weights = [], [], []
        n = len(self.portfolio_returns)  # Number of assets in the portfolio
        for r in np.linspace(min(R), max(R), num=20):  # Iterate through the range of returns on Y axis
            W = np.ones([n]) / n  # start optimization with equal weights
            b_ = [(0, 1) for i in range(n)]
            c_ = ({'type': 'eq', 'fun': lambda W: sum(W) - 1.})
            optimized = scipy.optimize.minimize(self.objective_function, W, (R, C, r), method='SLSQP', constraints=c_,
                                                bounds=b_)
            if not optimized.success:
                raise BaseException(optimized.message)

            # add point to the efficient frontier [x,y] = [optimized.x, r]
            frontier_mean.append(r)
            frontier_var.append(port_var(optimized.x, C))
            frontier_weights.append(optimized.x)

        return array(frontier_mean), array(frontier_var), frontier_weights


class CriticalLineAlgorithm(PortfolioOptimizationModel):
    pass


class FactorModel(PortfolioOptimizationModel):
    def __init__(self, portfolio_returns: pd.DataFrame, factors_returns: pd.DataFrame):
        super().__init__(portfolio_returns)
        self.risk_free_rates = risk_free_rates(from_date=portfolio_returns.index[0], to_date=portfolio_returns.index[1],
                                               freq='Daily')
        self.factors_returns = factors_returns


class BlackLittermanModel(PortfolioOptimizationModel):
    def __init__(self, portfolio_returns: pd.DataFrame):
        super().__init__(portfolio_returns)


class RiskParityModel():
    pass


class HierarchicalRiskParityModel(PortfolioOptimizationModel):
    # De Padro
    pass


class NestedClusteredOptimization(PortfolioOptimizationModel):
    pass


if __name__ == '__main__':
    portfolio_returns = excel.slice_resample_merge_returns(returns=['AAPL', 'FB', 'MSFT' 'RF'])
    mean_variance_optimization = MeanVarianceModel(portfolio_returns=portfolio_returns[['AAPL', 'FB', 'MSFT']])
    risk_free_rates = portfolio_returns['RF']
    # optimized = mean_variance_optimization.solve_weights(
    #     fitness=partial(risk_measures.sharpe_ratio, risk_free_rates=risk_free_rates), objective='maximize')
    # print(optimized)
    optimized = mean_variance_optimization.solve_weights(
        fitness=lambda W, exp_ret, cov: -((W.T @ exp_ret) / (W.T @ cov @ W) ** 0.5), objective='maximize')
