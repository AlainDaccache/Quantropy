from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from scipy.optimize import Bounds, minimize
import scipy.interpolate as sci
import historical_data_collection.data_preparation_helpers as excel
import fundamental_analysis.macroeconomic_analysis as macro
from config import MarketIndices
from FactorBox.asset_pricing_models import FactorModelDataset, AssetPricingModel, TimeDataFrame
import numpy as np
import pandas as pd


class Portfolio(TimeDataFrame):
    def __init__(self, assets):
        if isinstance(assets, MarketIndices):
            assets = macro.companies_in_index(market_index=assets)[:5]
        super().__init__(assets)
        self.portfolio_tickers = self.df_returns.columns

    def get_volatility_returns(self):
        return self.df_returns.std(axis=0) * np.sqrt(self.freq_to_yearly[self.df_frequency[0]])

    def get_weighted_volatility_returns(self, weights):
        return np.sqrt(np.dot(weights, np.dot(weights, self.get_covariance_matrix())))

    def get_covariance_matrix(self):
        return self.df_returns.cov() * self.freq_to_yearly[self.df_frequency[0]]

    def get_mean_returns(self):
        return self.df_returns.mean(axis=0) * self.freq_to_yearly[self.df_frequency[0]]

    def get_weighted_mean_returns(self, weights):
        return np.dot(weights, self.get_mean_returns())


class CapitalAssetPricingModel(AssetPricingModel):
    def __init__(self, factor_dataset: FactorModelDataset, frequency: str = 'Monthly', to_date: datetime = None,
                 from_date=None):
        super().__init__(factor_dataset, ['MKT-RF'], frequency, to_date, from_date)
        self.excess_market_returns = self.factors_timedf.df_returns['MKT-RF']

    def beta_covariance_method(self, benchmark_returns):
        pass

    def capital_allocation_line(self, date: datetime = None):
        # From https://kevinvecmanis.io/finance/optimization/2019/04/02/Algorithmic-Portfolio-Optimization.html
        min_index = np.argmin(minimal_volatilities)
        ex_returns = target_returns[min_index:]
        ex_volatilities = minimal_volatilities[min_index:]

        var = sci.splrep(ex_returns, ex_volatilities)

        def func(x):
            # Spline approximation of the efficient frontier
            spline_approx = sci.splev(x, var, der=0)
            return spline_approx

        def d_func(x):
            # first derivative of the approximate efficient frontier function
            deriv = sci.splev(x, var, der=1)
            return deriv

        def eqs(p, rfr=0.01):
            # rfr = risk free rate

            eq1 = rfr - p[0]
            eq2 = rfr + p[1] * p[2] - func(p[2])
            eq3 = p[1] - d_func(p[2])
            return eq1, eq2, eq3

        # Initializing the weights can be tricky - I find taking the half-way point between your max return and max
        # variance typically yields good results.

        rfr = 0.01
        m = port_vols.max() / 2
        l = port_returns.max() / 2

        optimal = optimize.fsolve(eqs, [rfr, m, l])
        print(optimal)
        pass

    '''
    The Security Market Line (SML) graphically represents the relationship between the asset's return (on y-axis) and systematic risk (or beta, on x-axis).
    With E(R_i) = R_f + B_i * (E(R_m) - R_f), the y-intercept of the SML is equal to the risk-free interest rate, while the slope is equal to the market risk premium
    Plotting the SML for a market index (i.e. DJIA), individual assets that are correctly priced are plotted on the SML (in the ideal 'Efficient Market Hypothesis' world). 
    In real market scenarios, we are able to use the SML graph to determine if an asset being considered for a portfolio offers a reasonable expected return for the risk. 
    - If an asset is priced at a point above the SML, it is undervalued, since for a given amount of risk, it yields a higher return. 
    - Conversely, an asset priced below the SML is overvalued, since for a given amount of risk, it yields a lower return.
    '''

    def security_market_line(self, portfolio: Portfolio, date: datetime = None, regression_period: int = 36,
                             benchmark: pd.Series = None):

        frequency = self.factors_timedf.df_frequency
        portfolio_copy = portfolio.set_frequency(frequency, inplace=False) \
            .slice_dataframe(to_date=date, from_date=regression_period, inplace=False)

        betas = [
            self.regress_factor_loadings(portfolio=portfolio.df_returns[ticker], benchmark_returns=benchmark, date=date,
                                         regression_period=regression_period).params[1]
            for ticker in portfolio_copy.df_returns]

        mean_asset_returns = portfolio_copy.get_mean_returns()
        date = portfolio_copy.df_returns.index[-1] if date is None else date

        risk_free_rate = macro.risk_free_rates(lookback=regression_period, to_date=date, frequency=frequency).mean() \
                         * portfolio.freq_to_yearly[frequency[0]]

        risk_premium = macro.market_premiums(lookback=regression_period, to_date=date, frequency=frequency).mean() \
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

    def markowitz_efficient_frontier(self, portfolio: Portfolio, to_date: datetime, from_date,
                                     plot_frontier=True, plot_assets=True, plot_cal=True):

        len_p = len(portfolio.df_returns.columns)
        portfolio_cpy = portfolio.slice_dataframe(to_date=to_date, from_date=from_date, inplace=False)
        df = self.factors_timedf.merge([portfolio_cpy]).df_returns
        portfolio_returns = df.iloc[:, -len_p:].dropna(how='all')
        print(portfolio_returns)
        portfolio_cpy = Portfolio(portfolio_returns)
        covariance_matrix = portfolio_cpy.get_covariance_matrix()
        print(covariance_matrix)
        mean_returns = portfolio_cpy.get_mean_returns()
        print(mean_returns)
        target_returns = np.linspace(mean_returns.min(), mean_returns.max(), 50)
        minimal_volatilities, weights = [], []

        for target_return in target_returns:
            optimal = minimize(
                # objective function for portfolio volatility. We're optimizing for the weights
                fun=lambda w: np.sqrt(np.dot(w, np.dot(w, covariance_matrix))),
                # initial guess for weights (all equal)
                x0=np.ones(len_p) / len_p, method='SLSQP',
                # weighted sum should equal target return, and weights should sum to one
                constraints=({'type': 'eq', 'fun': lambda x: np.sum(mean_returns * x) - target_return},
                             {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}),
                # all weights should be between zero and one
                bounds=Bounds(0, 1))

            minimal_volatilities.append(optimal['fun'])
            weights.append(optimal.x)

        sharpe_arr = target_returns / minimal_volatilities

        fig, ax = plt.subplots(figsize=(10, 10))
        if plot_frontier:
            plt.scatter(minimal_volatilities, target_returns, c=sharpe_arr, cmap='viridis')
            plt.colorbar(label='Sharpe Ratio')
            plt.xlabel('Volatility')
            plt.ylabel('Return')
            max_sharpe_idx = sharpe_arr.argmax()
            plt.plot(minimal_volatilities[max_sharpe_idx], target_returns[max_sharpe_idx], 'r*', markersize=25.0)

            min_volatility_idx = np.asarray(minimal_volatilities).argmin()
            plt.plot(minimal_volatilities[min_volatility_idx], target_returns[min_volatility_idx], 'y*',
                     markersize=25.0)

        if plot_assets:
            volatilities = portfolio.get_volatility_returns()
            for i, txt in enumerate(portfolio_returns.columns):
                ax.annotate(txt, (volatilities[i], mean_returns[i]), xytext=(10, 10), textcoords='offset points')
                plt.scatter(volatilities[i], mean_returns[i], marker='x', color='red')

        if plot_cal:
            # self.capital_allocation_line()
            pass
        plt.show()

        return {'Target Return': target_returns, 'Minimum Volatilty': minimal_volatilities,
                'Sharpe Ratio': sharpe_arr, 'Optimal Weights': weights}


if __name__ == '__main__':
    capm = CapitalAssetPricingModel(factor_dataset=FactorModelDataset.FAMA_FRENCH_DATASET,
                                    frequency='Daily')
    capm.regress_factor_loadings(portfolio=Portfolio(assets='AAPL'))
    # capm.markowitz_efficient_frontier(portfolio=Portfolio(assets=MarketIndices.DOW_JONES))
    # capm.security_market_line(portfolio=Portfolio(assets=MarketIndices.DOW_JONES), date=datetime.now(),
    #                           regression_period=5 * 12)
