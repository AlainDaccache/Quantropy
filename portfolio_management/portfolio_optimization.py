import abc
import inspect
from functools import partial
import macroeconomic_analysis.macroeconomic_analysis as macro

import numpy as np
import pandas as pd
import typing
from scipy.optimize import minimize, Bounds
from fundamental_analysis.supporting_metrics import market_capitalization
from portfolio_management.Portfolio import Portfolio

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
    def solve_weights(self, risk_metric=None, objective=None, leverage=0, long_short_exposure=0):
        pass


class EquallyWeightedPortfolio(PortfolioAllocationModel):
    def __init__(self, portfolio: Portfolio):
        super().__init__(portfolio)

    def solve_weights(self, risk_metric=None, objective=None, leverage=0, long_short_exposure=0):
        output = pd.Series()
        for ticker, stock_return in self.portfolio.df_returns.iteritems():
            output[ticker] = 1 / len(self.portfolio.stocks)
        return output


class ValueWeightedPortfolio(PortfolioAllocationModel):
    def __init__(self, portfolio: Portfolio):
        super().__init__(portfolio)

    def solve_weights(self, risk_metric=None, objective=None, leverage=0, long_short_exposure=0):
        output = pd.Series()
        for ticker, stock_return in self.portfolio.df_returns.iteritems():
            output[ticker] = market_capitalization(stock=str(ticker), date=self.portfolio.df_returns.index[-1])
        return output.divide(output.sum())


class InverseVolatilityWeightedPortfolio():
    pass


class InverseBetaWeightedPortfolio():
    pass


class ModernPortfolioTheory(PortfolioAllocationModel):
    """

    In **Markowitz's mean-variance framework**:

    The portfolio's *expected return* is the proportion-weighted combination of the constituents assets' returns.
    It is the weighted-average of the returns of the portfolio's constituents.

    .. math:: E(R_p) = \\sum_{i} w_i * E(R_i)

    where :math:`R_p` is the return of the portfolio, :math:`R_i` is the return of asset :math:`i`, and :math:`w_i` is
    the weighting of component asset :math:`i`.

    The portfolio's *return variance* is used as a proxy for risk. It is not simply a linear combination of individual
    risks, but a function of the correlations :math:`\\rho_{ij}` of the component assets, for all asset pairs :math:`(i, j)`.

    .. math:: \\sigma_p^2 = \\sum_{i} (w_i^2 + \\sigma_i^2) + \\sum_{i} \\sum_{i \\neq j} w_i * w_j * \\sigma_i * \\sigma_j * \\rho_{ij}

    where :math:`\\sigma` is the (sample) standard deviation of the periodic returns on an asset, and :math:`\\rho_{ij}`:
    is the correlation coefficient between the returns on assets :math:`i` and :math:`j`.

    With the idea of **diversification**, an investor can reduce portfolio risk simply by holding combinations of
    instruments that are not perfectly positively correlated (correlation coefficient :math:`-1 <= \\rho_{ij} < 1`).
    In other words, investors can reduce their exposure to individual asset risk by holding a diversified portfolio of
    assets. Diversification may allow for the same portfolio expected return with reduced risk.
    """
    def __init__(self, portfolio: Portfolio):
        super().__init__(portfolio=portfolio)

    def solve_weights(self, risk_metric=None, objective=None, leverage=0, long_short_exposure=0):
        """
        :param risk_metric: risk metric to optimize portfolio for. By default, volatility (standard deviation)
        :param objective: 'maximize' or 'minimize' the risk_metric. By default, minimizes.
        :param leverage:
        :param long_short_exposure:
        :return:

        """

        # TODO try solving using the Critical Line Algorithm of Markowitz!
        covariance_matrix = self.portfolio.get_covariance_matrix()

        def risk_measures_wrapper(weights: typing.List):
            nonlocal risk_metric

            if risk_metric is None:  # by default, minimize volatility of portfolio
                return np.sqrt(np.dot(weights, np.dot(weights, covariance_matrix)))

            elif isinstance(risk_metric, partial):
                fn_args_names = inspect.signature(risk_metric.func)

            else:
                fn_args_names = inspect.signature(risk_metric)

            portfolio_returns = self.portfolio.df_returns.dropna()
            portfolio_returns = np.sum(weights * portfolio_returns, axis=1)
            risk_metric = partial(risk_metric, portfolio_returns=portfolio_returns)

            if 'risk_free_rates' in fn_args_names.parameters.keys():
                rf = macro.risk_free_rates(to_date=self.portfolio.df_returns.index[-1],
                                           from_date=self.portfolio.df_returns.index[0],
                                           frequency=self.portfolio.frequency)
                risk_metric = partial(risk_metric, risk_free_rates=rf)

            if objective == 'maximize':
                # Since our optimization functions naturally seek to minimize,
                # we can minimize one of two quantities: the negative or the inverse
                return - risk_metric()
            else:
                return risk_metric()

        optimal = minimize(
            # objective function for portfolio volatility. We're optimizing for the weights
            fun=risk_measures_wrapper,
            # initial guess for weights (all equal)
            x0=np.ones((len(self.portfolio.stocks))) / (len(self.portfolio.stocks)),
            method='SLSQP',
            # weighted sum should equal target return, and weights should sum to one
            constraints=({'type': 'eq', 'fun': lambda x: np.sum(x) - 1}),
            # all weights should be between zero and one
            bounds=Bounds(0, 1))

        if not optimal.success:
            raise BaseException(optimal.message)
        return optimal.x  # Return optimized weights


class PostModernPortfolioTheory(PortfolioAllocationModel):
    def __init__(self, portfolio: Portfolio):
        super().__init__(portfolio)

    def expected_returns(self):
        pass

    def covariance_matrix(self):
        pass

    def objective_function(self, weights):
        pass

    def solve_weights(self, risk_metric=None, objective=None, leverage=0, long_short_exposure=0):
        pass


class TreynorBlackModel(PortfolioAllocationModel):
    """
    Under the **Treynor-Black model**, an investor considers that most securities are priced efficiently,
    but believes they have information that can be used to predict the abnormal performance (captured by the alpha
    of some factor model) of a few of them. The model combines an actively managed portfolio built with a few mispriced
    securities and a passively managed market index fund. As such, the overall portfolio consists of an active portfolio of weight :math:`w_A` and a passive portfolio
    with weight :math:`w_P = 1 - w_A`.

    - The higher the :math:`\\alpha` of a security, the higher the weight we assign to it.
    - The more risky the security is (unsystematic risk), the lower the weight we assign to it.

    The weight we assign to a security *i* should therefore be proportional to :math:`\\frac{\\alpha_i}{\\sigma(\\epsilon_i)^2}`.
    By default, we take the :math:`\\alpha` of the Capital Asset Pricing Model, :math:`r_i + \\beta_i * (R_M - R_F) + \\alpha_i + \\epsilon_i`.

    Then it was shown by Treynor and Black that the active portfolio is constructed using the weights
    :math:`w_i = \\frac{\\frac{\\alpha_i}{\\sigma_i^2}}{\\sum_{j=1}^{N} \\frac{\\alpha_j}{\\sigma_j^2}}`.
    Using these weights, we can construct the active portfolio and calculate the following:

    .. math::
        \\alpha_A = \\sum_{i=1}^{N} w_i * \\alpha_i ,
        \\beta_A = \\sum_{i=1}^{N} w_i * \\beta_i ,
        \\sigma(\\epsilon_A)^2 = \\sum_{i=1}^{N} w_i^2 * \\sigma(\\epsilon_i)^2

    They then determine the size of the active portfolio in the overall portfolio,

    .. math:: w_A = \\frac{\\frac{\\alpha_A}{\\sigma_A^2}}{\\frac{E(r_P) - r_f}{\\sigma_P^2}}

    where :math:`r_p` is the return of the passive portfolio, :math:`r_f` is the risk-free rate, and
    :math:`\\sigma_P^2` is the volatility of the passive portfolio.

    To avoid the overall portfolio from exhibiting a lot of unsystematic risk, we correct the formula
    to ensure the beta of the overall portfolio doesn't change.

    .. math:: w_A = \\frac{w_A}{1 + (1 - \\beta_A) * w_A}

    The model is not bounded :math:`0 ≤ w_A ≤ 1` and :math:`0 ≤ w_M ≤ 0` i.e short positions in the market portfolio or active portfolio
    could be initiated to leverage a position in the other portfolio. This is often regarded as the major flaw of the
    model, as it often yields an unrealistic weight in the active portfolio. Imposing lower and upper bounds for
    :math:`w_A` is a measure to counter this.

    """
    def __init__(self, portfolio: Portfolio):
        super().__init__(portfolio)

    def solve_weights(self, risk_metric=None, objective=None, leverage=0, long_short_exposure=0):
        pass


class BlackLittermanModel(PortfolioAllocationModel):
    def __init__(self, portfolio: Portfolio):
        super().__init__(portfolio)

    def solve_weights(self, risk_metric=None, objective=None, leverage=0, long_short_exposure=0):
        pass


class RiskParityModel(PortfolioAllocationModel):
    def __init__(self, portfolio: Portfolio):
        super().__init__(portfolio)

    def solve_weights(self, risk_metric=None, objective=None, leverage=0, long_short_exposure=0):
        pass


class HierarchicalRiskParityModel(PortfolioAllocationModel):
    def __init__(self, portfolio: Portfolio):
        super().__init__(portfolio)

    def solve_weights(self, risk_metric=None, objective=None, leverage=0, long_short_exposure=0):
        pass


class NestedClusteredOptimization(PortfolioAllocationModel):
    def __init__(self, portfolio: Portfolio):
        super().__init__(portfolio)

    def solve_weights(self, risk_metric=None, objective=None, leverage=0, long_short_exposure=0):
        pass


if __name__ == '__main__':
    pass
    # portfolio = Portfolio(assets=['AAPL', 'MSFT', 'CSCO'])
    # mpt = ModernPortfolioTheory(portfolio)
    # w = mpt.solve_weights(risk_metric=sharpe_ratio, objective='maximize')
    # print(w)
    # postmodern = PostModernPortfolioTheoryOptimization(portfolio)
    # print(postmodern.solve_weights(objective=lambda w: sortino_ratio(portfolio_returns=portfolio.df_returns,
    #                                                                  risk_free_rates=risk_free_rates())))
