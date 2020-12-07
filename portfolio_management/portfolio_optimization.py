import abc
import numpy as np
import pandas as pd
import typing
from cvxpy import *
import scipy.optimize
from scipy.optimize import minimize, Bounds

import historical_data_collection.data_preparation_helpers as excel
from macroeconomic_analysis.macroeconomic_analysis import risk_free_rates
from fundamental_analysis.supporting_metrics import market_capitalization
from portfolio_management import Portfolio

np.random.seed(123)


class ExpectedReturnsMethods:
    def __init__(self, df_returns: pd.DataFrame):
        self.df_returns = df_returns

    def mean_historical_returns(self, exponentially_weighted=False):
        pass

    def log_historical_returns(self):
        pass

    def returns_capm(self):
        pass


class RiskModels:
    def __init__(self, df_returns: pd.DataFrame):
        self.df_returns = df_returns

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


class PortfolioAllocationModel(metaclass=abc.ABCMeta):
    def __init__(self, portfolio: Portfolio):
        self.portfolio = portfolio

    @abc.abstractmethod
    def solve_weights(self, objective=None, leverage=0, long_short_exposure=0):
        pass


class EquallyWeightedPortfolio(PortfolioAllocationModel):
    def __init__(self, portfolio: Portfolio):
        super().__init__(portfolio)

    def solve_weights(self, objective=None, leverage=0, long_short_exposure=0):
        output = pd.Series()
        for ticker, stock_return in self.portfolio.df_returns.iteritems():
            output[ticker] = 1 / len(self.portfolio.portfolio_tickers)
        return output


class ValueWeightedPortfolio(PortfolioAllocationModel):
    def __init__(self, portfolio: Portfolio):
        super().__init__(portfolio)

    def solve_weights(self, objective=None, leverage=0, long_short_exposure=0):
        output = pd.Series()
        for ticker, stock_return in self.portfolio.df_returns.iteritems():
            output[ticker] = market_capitalization(stock=str(ticker), date=self.portfolio.df_returns.index[-1])
        return output.divide(output.sum())


class InverseVolatilityWeightedPortfolio():
    pass


class InverseBetaWeightedPortfolio():
    pass


class MeanVarianceModel(PortfolioAllocationModel):
    # Global Minimum Variance Portfolio (GMVP)
    def __init__(self, portfolio: Portfolio):
        super().__init__(portfolio=portfolio)

    def solve_weights(self, objective=None, leverage=0, long_short_exposure=0):
        # TODO would be fun to try solving using the Critical Line Algorithm of Markowitz!
        covariance_matrix = self.portfolio.get_covariance_matrix()
        optimal = minimize(
            # objective function for portfolio volatility. We're optimizing for the weights
            fun=lambda w: np.sqrt(np.dot(w, np.dot(w, covariance_matrix))),
            # initial guess for weights (all equal)
            x0=np.ones((len(self.portfolio.portfolio_tickers))) / (len(self.portfolio.portfolio_tickers)),
            method='SLSQP',
            # weighted sum should equal target return, and weights should sum to one
            constraints=({'type': 'eq', 'fun': lambda x: np.sum(x) - 1}),
            # all weights should be between zero and one
            bounds=Bounds(0, 1))

        if not optimal.success:
            raise BaseException(optimal.message)
        return optimal.x  # Return optimized weights


class PostModernPortfolioTheoryOptimization(PortfolioAllocationModel):
    def __init__(self, portfolio: Portfolio):
        super().__init__(portfolio)

    def expected_returns(self):
        pass

    def covariance_matrix(self):
        pass

    def objective_function(self, weights):
        pass

    def solve_weights(self, objective=None, leverage=0, long_short_exposure=0):
        optimal = minimize(
            # objective function for portfolio volatility. We're optimizing for the weights
            fun=lambda w: self.objective_function(w),
            # initial guess for weights (all equal)
            x0=np.ones(len(self.portfolio.portfolio_tickers)) / len(self.portfolio.portfolio_tickers), method='SLSQP',
            # weighted sum should equal target return, and weights should sum to one
            constraints=({'type': 'eq', 'fun': lambda x: np.sum(x) - 1}),
            # all weights should be between zero and one
            bounds=Bounds(0, 1))
        if not optimal.success:
            raise BaseException(optimal.message)
        return optimal.x  # Return optimized weights


class FactorModel(PortfolioAllocationModel):
    def __init__(self, df_returns: pd.DataFrame, factors_returns: pd.DataFrame):
        super().__init__(df_returns)
        self.risk_free_rates = risk_free_rates(from_date=df_returns.index[0], to_date=df_returns.index[1],
                                               freq='Daily')
        self.factors_returns = factors_returns


class BlackLittermanModel(PortfolioAllocationModel):
    def __init__(self, df_returns: pd.DataFrame):
        super().__init__(df_returns)


class RiskParityModel(PortfolioAllocationModel):
    pass


class HierarchicalRiskParityModel(PortfolioAllocationModel):
    # De Padro
    pass


class NestedClusteredOptimization(PortfolioAllocationModel):
    pass


if __name__ == '__main__':
    pass
