import abc
import inspect
from datetime import datetime

import macroeconomic_analysis.macroeconomic_analysis as macro
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import typing
from functools import partial
from scipy.optimize import minimize, Bounds
from config import MarketIndices
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
    def solve_weights(self, leverage=1, long_short_exposure=1):
        """
        
        :param leverage: leverage constraints. By default, 1 (no leverage). leverage constraints. By default, 1 (no leverage).
        :param long_short_exposure: exposure between long and short positions. By default, 1 (long-only). exposure between long and short positions. By default, 1 (long-only).
        :return: 
        """
        pass


class EquallyWeightedPortfolio(PortfolioAllocationModel):
    def __init__(self, portfolio: Portfolio):
        super().__init__(portfolio)

    def solve_weights(self, leverage=0, long_short_exposure=0):
        output = pd.Series()
        for ticker, stock_return in self.portfolio.df_returns.iteritems():
            output[ticker] = 1 / len(self.portfolio.stocks)
        return output


class ValueWeightedPortfolio(PortfolioAllocationModel):
    def __init__(self, portfolio: Portfolio):
        super().__init__(portfolio)

    def solve_weights(self, leverage=0, long_short_exposure=0):
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

    The portfolio's *expected return* is the proportion-weighted combination of the constituents assets' returns.
    It is the weighted-average of the returns of the portfolio's constituents.

    .. math:: E(R_p) = \\sum_{i} w_i * E(R_i)

    where :math:`R_p` is the return of the portfolio, :math:`R_i` is the return of asset :math:`i`, and :math:`w_i` is
    the weighting of component asset :math:`i`.

    The portfolio's *return variance* is used as a proxy for risk. It is not simply a linear combination of individual
    risks, but a function of the correlations :math:`\\rho_{ij}` of the component assets, for all asset pairs :math:`(i, j)`.

    .. math:: \\sigma_p^2 = \\sum_{i} (w_i^2 + \\sigma_i^2) + \\sum_{i} \\sum_{i \\neq j} w_i * w_j * \\sigma_i * \\sigma_j * \\rho_{ij}

    where :math:`\\sigma` is the (sample) standard deviation of the periodic returns on an asset, and :math:`\\rho_{ij}`
    is the correlation coefficient between the returns on assets :math:`i` and :math:`j`.

    With the idea of **diversification**, an investor can reduce portfolio risk simply by holding combinations of
    instruments that are not perfectly positively correlated (correlation coefficient :math:`-1 <= \\rho_{ij} < 1`).
    In other words, investors can reduce their exposure to individual asset risk by holding a diversified portfolio of
    assets. Diversification may allow for the same portfolio expected return with reduced risk.
    """

    def __init__(self, portfolio: Portfolio):
        super().__init__(portfolio=portfolio)

    def solve_weights(self, use_sharpe=False, leverage=0, long_short_exposure=0):
        """
        :param use_sharpe: to optimize for Sharpe ratio, input True. By default minimizes volatility.

        :param leverage: leverage constraints. By default, 1 (no leverage).
        :param long_short_exposure: exposure between long and short positions. By default, 1 (long-only).
        :return:

        """

        def objective_function(weights):
            if use_sharpe:
                portfolio_returns = self.portfolio.df_returns.dropna()
                portfolio_returns = np.sum(weights * portfolio_returns, axis=1)
                rf = macro.risk_free_rates(to_date=self.portfolio.df_returns.index[-1],
                                           from_date=self.portfolio.df_returns.index[0],
                                           frequency=self.portfolio.frequency)
                from portfolio_management.risk_quantification import sharpe_ratio
                return - sharpe_ratio(portfolio_returns=portfolio_returns, risk_free_rates=rf)

            else:
                return np.sqrt(np.dot(weights, np.dot(weights, covariance_matrix)))

        covariance_matrix = self.portfolio.get_covariance_matrix()
        # TODO try solving using the Critical Line Algorithm of Markowitz!
        optimal = minimize(
            # objective function for portfolio volatility or Sharpe. We're optimizing for the weights
            fun=objective_function,
            # initial guess for weights (all equal)
            x0=np.ones((len(self.portfolio.stocks))) / (len(self.portfolio.stocks)),
            method='SLSQP',
            # weighted sum should equal target return, and weights should sum to one
            constraints=({'type': 'eq', 'fun': lambda x: np.sum(x) - 1}),
            # all weights should be between zero and one
            bounds=Bounds(0, 1))

        if not optimal.success:
            raise BaseException(optimal.message)
        return pd.Series(data=optimal.x, index=self.portfolio.stocks)  # Return optimized weights

    def markowitz_efficient_frontier(self, market_portfolio: Portfolio = None, plot_assets=True, plot_cal=False):
        """
        One can plot every possible combination of risky assets on the *risk-return space*, a graph with the horizontal axis
        representing the *variance* (a.k.a risk), and the vertical axis representing the *expected returns*.
        The left boundary of this region is parabolic, and the upper part of the parabolic boundary is the **efficient frontier**
        in the absence of a risk-free asset (sometimes called *the Markowitz bullet*). Combinations along this upper edge
        represent portfolios (including no holdings of the risk-free asset) for which there is lowest risk for a given
        level of expected return. Equivalently, a portfolio lying on the efficient frontier represents the combination
        offering the best possible expected return for given risk level.

        :param market_portfolio:
        :param plot_assets: Plot risk/return profile of each asset in the portfolio
        :param plot_cal: Plot the Capital Allocation Line
        :return: Pandas DataFrame representing optimal weights and minimun volatilities for each level of required return.
        """
        covariance_matrix = self.portfolio.get_covariance_matrix(to_freq='Y')
        mean_returns = self.portfolio.get_mean_returns(to_freq='Y')
        target_returns = np.linspace(mean_returns.min(), mean_returns.max(), 50)
        minimal_volatilities, weights = [], []

        for target_return in target_returns:
            optimal = minimize(
                # objective function for portfolio volatility. We're optimizing for the weights
                fun=lambda w: np.sqrt(np.dot(w, np.dot(w, covariance_matrix))),
                # initial guess for weights (all equal)
                x0=np.ones((len(self.portfolio.stocks))) / (len(self.portfolio.stocks)),
                method='SLSQP',
                # weighted sum should equal target return, and weights should sum to one
                constraints=({'type': 'eq', 'fun': lambda x: np.sum(mean_returns * x) - target_return},
                             {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}),
                # all weights should be between zero and one
                bounds=Bounds(0, 1))

            minimal_volatilities.append(optimal['fun'])
            weights.append(optimal.x)

        sharpe_arr = target_returns / minimal_volatilities

        fig, ax = plt.subplots(figsize=(10, 10))
        plt.scatter(minimal_volatilities, target_returns, c=sharpe_arr, cmap='viridis')
        plt.colorbar(label='Sharpe Ratio')
        plt.xlabel('Standard Deviation')
        plt.ylabel('Expected Returns')

        max_sharpe_idx = sharpe_arr.argmax()
        plt.plot(minimal_volatilities[max_sharpe_idx], target_returns[max_sharpe_idx], 'r*', markersize=15.0)
        ax.annotate(text='Max Sharpe', xy=(minimal_volatilities[max_sharpe_idx], target_returns[max_sharpe_idx]),
                    xytext=(10, 10), textcoords='offset points')

        min_volatility_idx = np.asarray(minimal_volatilities).argmin()
        plt.plot(minimal_volatilities[min_volatility_idx], target_returns[min_volatility_idx], 'y*', markersize=15.0)
        ax.annotate(text='Min Vol', xy=(minimal_volatilities[min_volatility_idx], target_returns[min_volatility_idx]),
                    xytext=(10, 10), textcoords='offset points')

        # Get yearly mean and std of market portfolio returns
        mkt_mean, mkt_std = market_portfolio.get_mean_returns(to_freq='Y'), market_portfolio.get_volatility_returns(to_freq='Y')
        if market_portfolio is not None and len(market_portfolio.df_returns.columns) == 1:
            plt.plot(mkt_std, mkt_mean, 'bo', markersize=15.0)
            ax.annotate(text=market_portfolio.df_returns.columns[0], xy=(mkt_std, mkt_mean),
                        xytext=(10, 10), textcoords='offset points')
        if plot_assets:
            volatilities = portfolio.get_volatility_returns()
            for i, txt in enumerate(self.portfolio.stocks):
                ax.annotate(txt, (volatilities[i], mean_returns[i]), xytext=(10, 10), textcoords='offset points')
                plt.scatter(volatilities[i], mean_returns[i], marker='x', color='red')

        if plot_cal:
            # self.capital_allocation_line()
            pass

        plt.show()

        return pd.DataFrame.from_dict({'Target Return': target_returns, 'Minimum Volatilty': minimal_volatilities,
                                       'Sharpe Ratio': sharpe_arr, 'Optimal Weights': weights})

    def capital_allocation_line(self, date: datetime = None):
        # # From https://kevinvecmanis.io/finance/optimization/2019/04/02/Algorithmic-Portfolio-Optimization.html
        # min_index = np.argmin(minimal_volatilities)
        # ex_returns = target_returns[min_index:]
        # ex_volatilities = minimal_volatilities[min_index:]
        #
        # var = sci.splrep(ex_returns, ex_volatilities)
        #
        # def func(x):
        #     # Spline approximation of the efficient frontier
        #     spline_approx = sci.splev(x, var, der=0)
        #     return spline_approx
        #
        # def d_func(x):
        #     # first derivative of the approximate efficient frontier function
        #     deriv = sci.splev(x, var, der=1)
        #     return deriv
        #
        # def eqs(p, rfr=0.01):
        #     # rfr = risk free rate
        #
        #     eq1 = rfr - p[0]
        #     eq2 = rfr + p[1] * p[2] - func(p[2])
        #     eq3 = p[1] - d_func(p[2])
        #     return eq1, eq2, eq3
        #
        # # Initializing the weights can be tricky - I find taking the half-way point between your max return and max
        # # variance typically yields good results.
        #
        # rfr = 0.01
        # m = port_vols.max() / 2
        # l = port_returns.max() / 2
        #
        # optimal = optimize.fsolve(eqs, [rfr, m, l])
        # print(optimal)
        pass

    def security_market_line(self, portfolio: Portfolio, date: datetime = None, regression_window: int = 36,
                             benchmark: pd.Series = None):
        """

        :param portfolio:
        :param date:
        :param regression_window:
        :param benchmark:
        :return:
        """
        # '''
        #     The Security Market Line (SML) graphically represents the relationship between the asset's return (on y-axis) and systematic risk (or beta, on x-axis).
        #     With E(R_i) = R_f + B_i * (E(R_m) - R_f), the y-intercept of the SML is equal to the risk-free interest rate, while the slope is equal to the market risk premium
        #     Plotting the SML for a market index (i.e. DJIA), individual assets that are correctly priced are plotted on the SML (in the ideal 'Efficient Market Hypothesis' world).
        #     In real market scenarios, we are able to use the SML graph to determine if an asset being considered for a portfolio offers a reasonable expected return for the risk.
        #     - If an asset is priced at a point above the SML, it is undervalued, since for a given amount of risk, it yields a higher return.
        #     - Conversely, an asset priced below the SML is overvalued, since for a given amount of risk, it yields a lower return.
        # '''
        frequency = self.factors_timedf.df_frequency
        portfolio_copy = portfolio.set_frequency(frequency, inplace=False) \
            .slice_dataframe(to_date=date, from_date=regression_window, inplace=False)

        betas = [
            self.regress_factor_loadings(portfolio=portfolio.df_returns[ticker], benchmark_returns=benchmark, date=date,
                                         regression_window=regression_window).params[1]
            for ticker in portfolio_copy.df_returns]

        mean_asset_returns = portfolio_copy.get_mean_returns()
        date = portfolio_copy.df_returns.index[-1] if date is None else date

        risk_free_rate = macro.risk_free_rates(lookback=regression_window, to_date=date, frequency=frequency).mean() \
                         * portfolio.freq_to_yearly[frequency[0]]

        risk_premium = macro.market_premiums(lookback=regression_window, to_date=date, frequency=frequency).mean() \
                       * portfolio.freq_to_yearly[frequency[0]]

        x = np.linspace(0, max(betas) + 0.1, 100)
        y = float(risk_free_rate) + x * float(risk_premium)
        fig, ax = plt.subplots(figsize=(10, 10))
        plt.plot(x, y)
        ax.set_xlabel('Betas', fontsize=14)
        ax.set_ylabel('Expected Returns', fontsize=14)
        ax.set_title('Security Market Line', fontsize=18)

        for i, txt in enumerate(portfolio.df_returns):
            ax.annotate(txt, (betas[i], mean_asset_returns[i]), xytext=(10, 10), textcoords='offset points')
            plt.scatter(betas[i], mean_asset_returns[i], marker='x', color='red')

        plt.show()


class PostModernPortfolioTheory(PortfolioAllocationModel):
    def __init__(self, portfolio: Portfolio):
        super().__init__(portfolio)

    def solve_weights(self, risk_metric=None, objective=None, leverage=0, long_short_exposure=0):
        """

        :param risk_metric: risk metric to optimize portfolio for. By default, volatility (standard deviation)
        :param objective: 'maximize' or 'minimize' the risk_metric. By default, minimizes.
        :param leverage: leverage constraints. By default, 1 (no leverage).
        :param long_short_exposure: exposure between long and short positions. By default, 1 (long-only).
        :return:
        """
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
        return pd.Series(data=optimal.x, index=self.portfolio.stocks)  # Return optimized weights


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
    assets = macro.companies_in_index(MarketIndices.DOW_JONES)
    portfolio = Portfolio(assets=assets)
    portfolio.set_frequency(frequency='M', inplace=True)
    portfolio.slice_dataframe(from_date=datetime(2016, 1, 1), to_date=datetime(2020, 1, 1), inplace=True)
    print(portfolio.df_returns.tail(10))

    MPT = ModernPortfolioTheory(portfolio)
    weights = MPT.solve_weights(use_sharpe=True)
    print(weights)

    market_portfolio = Portfolio(assets='^DJI')
    market_portfolio.set_frequency(frequency='M', inplace=True)
    market_portfolio.slice_dataframe(from_date=datetime(2016, 1, 1), to_date=datetime(2020, 1, 1), inplace=True)

    stats = MPT.markowitz_efficient_frontier(market_portfolio=market_portfolio, plot_assets=True, plot_cal=True)
    pd.set_option('display.max_columns', None)
    print(stats.head())

    # portfolio = Portfolio(assets=['AAPL', 'MSFT', 'CSCO'])
    #
    # w = mpt.solve_weights(risk_metric=sharpe_ratio, objective='maximize')
    # print(w)
    # postmodern = PostModernPortfolioTheoryOptimization(portfolio)
    # print(postmodern.solve_weights(objective=lambda w: sortino_ratio(portfolio_returns=portfolio.df_returns,
    #                                                                  risk_free_rates=risk_free_rates())))
