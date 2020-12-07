import abc
import os
from math import ceil, floor

import pandas as pd
import statsmodels.formula.api as sm
import typing
import matplotlib.pyplot as plt
from statsmodels.regression.rolling import RollingOLS

import historical_data_collection.data_preparation_helpers as excel
import config
import macroeconomic_analysis.macroeconomic_analysis as macro
import scipy.interpolate as sci
import numpy as np
from enum import Enum
from datetime import timedelta, datetime
from functools import partial
from scipy.optimize import Bounds, minimize
from sklearn import preprocessing
from scipy.stats import mstats, stats
from statsmodels.iolib.summary2 import summary_col
from datetime import datetime
from enum import Enum
from config import MarketIndices, RebalancingFrequency
import fundamental_analysis.accounting_ratios as ratios
import fundamental_analysis.supporting_metrics as metrics
from portfolio_management.Portfolio import TimeDataFrame, Portfolio
from portfolio_management.portfolio_optimization import PortfolioAllocationModel, ValueWeightedPortfolio

'''
https://alphaarchitect.com/2011/08/01/how-to-use-the-fama-french-model/
https://www.sciencedirect.com/topics/economics-econometrics-and-finance/capm
https://hackernoon.com/using-capital-asset-pricing-model-capm-versus-black-scholes-model-to-value-stocks-a-how-to-guide-r53032tc
http://content.moneyinstructor.com/948/capm.html

BlackRock: https://www.blackrock.com/us/partner/tools/factor-box-360-evaluator-methodology
https://www.ishares.com/us/resources/tools/factor-box-resources#methodology
MorningStar: https://www.morningstar.com/InvGlossary/morningstar_style_box.aspx
http://news.morningstar.com/pdfs/FactSheet_StyleBox_Final.pdf

TODO Big concern as to how to consider edge cases for company universe, like
 Bankruptcy,
 Mergers, and Acquisition,
 and stock split -> maybe in simulator consider only pct returns of adj close, but perform transactions with actual close

# TODO Sector Specific Factors

Achieve diversification by combining factors; some compensating when others are not doing well and vice versa --> less/inversely correlated?
Would Principal Component Analysis help?

Shouldn't calculate every date in iterations, instead should do once and for all. So input can't be (stock, date) to factor
TODO First abstraction: https://www.quantopian.com/posts/how-to-define-a-custom-factor-using-fundamental-data-of-morningstar-dataset
TODO Second abstraction: http://alphacompiler.com/
'''


class AssetPricingModel:

    def __init__(self, *args):
        '''

        :param args:
        Import a dataframe
            * factor_df: pd.DataFrame   for your own dataframe
        Or for an already computed factors historical returns, like CAPM, Fama-French, AQR...
            * factor_model_type: FactorModelDataset.
            * factors: list[str]        the factors in that model you want to use. By default all.
            * frequency: str optional, Monthly default.
            * to_date: datetime optional, otherwise keeps all dates available for no information loss.
            * lookback_period or from_date: timedelta, datetime, or int.
        Or for even more customization
            * factor_model_dict: { factor_model: factors }
            * frequency: str optional, Monthly default
            * to_date: datetime optional
            * lookback_period or from_date: timedelta, datetime, or int.

        '''
        # argspec = inspect.signature(self.__init__)
        # we keep an internal granular df to resample from (it's Daily)
        frequency, from_date, to_date, lookback = 'Monthly', None, None, None

        if isinstance(args[0], pd.DataFrame) and len(args) == 1:
            self.factor_timedf = TimeDataFrame([args])
            self.granular_df = self.factor_timedf
        elif isinstance(args[0], FactorModelDataset) and len(args) >= 2:
            self.factor_model_type = args[0]
            path = os.path.join(config.FACTORS_DIR_PATH, 'pickle', '{}.pkl'.format(args[0].value))
            self.granular_df = pd.read_pickle(path)
            if isinstance(args[1], list):
                factors = args[1] + ['RF']
                self.granular_df = self.granular_df[factors]

            if len(args) >= 3 and isinstance(args[2], str):
                frequency = args[2]

            self.factors_timedf = TimeDataFrame(self.granular_df)
            if self.factors_timedf.frequency != frequency[0]:
                self.factors_timedf = self.factors_timedf.set_frequency(frequency=frequency, inplace=False)
            self.factors_timedf.df_returns = self.factors_timedf.df_returns.dropna(how='all')

            if len(args) >= 4 and isinstance(args[3], datetime):
                to_date = args[3]
            if len(args) >= 5 and (isinstance(args[4], datetime)
                                   or isinstance(args[4], timedelta) or isinstance(args[4], int)):
                from_date = args[4]

            self.factors_timedf.slice_dataframe(to_date=to_date, from_date=from_date, inplace=True)

    def regress_factor_loadings(self, portfolio, benchmark_returns: pd.Series = None,
                                date: datetime = None, regression_window: int = 36, rolling=False):
        '''

        :param portfolio: str, pd.Series, TimeDataFrame, Portfolio... If more than an asset, we compute an equal weighted returns
        :param benchmark_returns:
        :param date:
        :param regression_window:
        :param plot:
        :return:
        '''
        if not (isinstance(portfolio, TimeDataFrame) or isinstance(portfolio, Portfolio)):
            portfolio = TimeDataFrame(portfolio)

        if len(portfolio.df_returns.columns) > 1:
            # TODO actually, do an equal weighting
            raise TypeError('Inappropriate argument type for portfolio')

        if portfolio.frequency != self.factors_timedf.frequency:
            portfolio_copy = portfolio.set_frequency(self.factors_timedf.frequency, inplace=False) \
                .slice_dataframe(to_date=date, inplace=False)
        else:
            portfolio_copy = portfolio

        if benchmark_returns is None:  # if no benchmark specified, just use the one in the model
            timedf_merged = portfolio_copy.merge([self.factors_timedf], inplace=False)
        else:
            timedf_merged = portfolio_copy.merge([self.factors_timedf, benchmark_returns], inplace=False)
            timedf_merged.df_returns.drop(['MKT-RF'], axis=1, inplace=True)
            timedf_merged.df_returns.rename(columns={benchmark_returns: 'MKT-RF'}, inplace=True)
            timedf_merged.df_returns['MKT-RF'] = timedf_merged.df_returns['MKT-RF'] - timedf_merged.df_returns['RF']

        portfolio_returns, factors_df = timedf_merged.df_returns.iloc[:, 0] - timedf_merged.df_returns['RF'], \
                                        timedf_merged.df_returns.iloc[:, 1:]

        portfolio_returns.rename('XsRet', inplace=True)
        factors_df.drop(['RF'], axis=1, inplace=True)  # don't need it anymore

        if rolling:
            # endogenous is the portfolio returns (y, dependent), exogenous is the factors (x, explanatory, independent)
            rols = RollingOLS(endog=portfolio_returns, exog=factors_df, window=regression_window)
            rres = rols.fit()
            params = rres.params.dropna()
            print(params.tail())
            rres.plot_recursive_coefficient(variables=factors_df.columns, figsize=(10, 6))
            plt.show()
            return rres
        else:
            # need to merge again to run regression on dataframe (with y being XsRet)
            df_stock_factor = pd.merge(portfolio_returns, factors_df, left_index=True, right_index=True)
            df_stock_factor = df_stock_factor.iloc[-regression_window:, :]
            # rename because will give syntax error with '-' when running regression
            df_stock_factor.rename(columns={'MKT-RF': 'MKT'}, inplace=True)
            reg = sm.ols(formula='XsRet ~ {}'.format(' + '.join(factors_df.columns)),
                         data=df_stock_factor).fit(cov_type='HAC', cov_kwds={'maxlags': 1})
            print(reg.summary())

            nrows, ncols = ceil(len(factors_df.columns) / 3), min(len(factors_df.columns), 3)
            fig, axs = plt.subplots(nrows=nrows, ncols=ncols, figsize=(12, 5))
            plt.tight_layout()

            for i, factor in enumerate(df_stock_factor.iloc[:, 1:]):

                idx_x, idx_y = floor(i / 3), floor(i % 3)
                ax = axs
                if nrows > 1:
                    ax = axs[idx_x,]
                if ncols > 1:
                    ax = ax[idx_y]

                X = np.linspace(df_stock_factor[factor].min(), df_stock_factor[factor].max())
                Y = reg.params[i + 1] * X + reg.params[0]  # beta * x + alpha
                ax.plot(X, Y)

                ax.scatter(df_stock_factor[factor], df_stock_factor.iloc[:, 0], alpha=0.3)
                ax.grid(True)
                ax.axis('tight')
                ax.set_xlabel(factor if factor != 'MKT' else 'MKT-RF')
                ax.set_ylabel('Portfolio Excess Returns')

            plt.show()

            return reg


class Factor(metaclass=abc.ABCMeta):
    def __init__(self, weights=None, factors_names=None, winsorize_bounds=(0.05, 0.95), sort_direction='desc',
                 rank_split=(0.30, 0.70)):
        if factors_names is None:
            factors_names = ['Factor']
        if weights is None:
            weights = [1]
        self.weights = weights
        self.factors_names = factors_names
        self.winsorize_bounds = winsorize_bounds
        self.sort_direction = sort_direction
        self.rank_split = rank_split

    @abc.abstractmethod
    def factor_formula(self, stock, date):
        pass

    def compute_returns(self, stocks_returns, factor_scores, percentile_breakpoints):
        '''

        By default, go short on bottom percentile breakpoint, and long on top percentile breakpoint,
        :param stocks_returns:
        :param factor_scores:
        :return:
        '''

        pass

    def evaluate_factor(self, buckets: int):
        '''
        When evaluating a factor, you need to see a clear linear relationship between the rankings and the returns

        :param factor:
        :param buckets:
        :return:
        '''

        pass


class CustomAssetPricingModel(AssetPricingModel):
    """

    How to identify the factor profile of a company or fundamental_analysis?

    --------------------------------------------------------

    * **Factors choice:**
        * We specify factors, such as Value, Growth, Quality etc.
        * Each of those factors will be an aggregate of some metrics
        * Each of those metrics is assigned a weight (so for each category, weights sum to 1).
        For example, Value is an aggregate of P/E (75%) and P/B (25%).

    * **Ranking scheme:**
        * For each stock, we compute and normalize those metrics (can winsorize first, apply different methods like min-max, z-score).
        * Then, we compute the weighted sum of the metrics for each stock, to make a score for each factor
        * Now, we sum those factors once again, so each stock will have one score, and we can rank based on that

    * **Portfolio construction:** We cross-split the portfolio based on factors and percentiles, and pick the
    resulting portfolios to go long and short on. For example:

                                        Median ME
                                            |
                            Small Value     |   Big Value
    70th BE/ME Percentile ------------------|-------------
                            Small Neutral   |   Big Neutral
    30th BE/ME Percentile ------------------|--------------
                            Small Growth    |   Big Growth


    As an extra step, we can find the Beta exposures by regressing to the factors in asset pricing models
    --------------------------------------------------------------------------------------
    """

    def __init__(self, factors: typing.List, securities_universe, start_date: datetime,
                 end_date: datetime, rebalancing_frequency: RebalancingFrequency):
        # super().__init__()
        self.factors = factors
        self.asset_returns = Portfolio(assets=securities_universe).df_returns
        self.securities_universe = list(self.asset_returns.columns)
        self.start_date = start_date
        self.end_date = end_date
        self.rebalancing_frequency = rebalancing_frequency

    def pre_filter_universe(self) -> bool:
        pass

    def compute_raw_factors(self) -> pd.DataFrame:
        '''
        :param securities_universe
        :param factors: dict    The dict should be of depth 2: {'Factor Category': {Factor: (Computation, Loading)}}
                                If last depth is not tuple, then assuming equal loadings
        :param start_date:
        :param end_date:
        :param rebalancing_frequency:
        :param portfolio_allocation_policy:
        :param long_short_exposure:
        :return:
        '''

        # Generate range of dates to rebalance, between start and end date
        range_dates, i = [], 0
        while self.start_date + timedelta(days=round(i * self.rebalancing_frequency.value)) < self.end_date:
            range_dates.append(self.start_date + timedelta(days=round(i * self.rebalancing_frequency.value)))
            i = i + 1

        # Compute Raw Scores
        factors_dict = {
            (date, factor.__class__.__name__, factor_name, stock): computation
            for date in range_dates
            for stock in self.securities_universe
            for factor in self.factors
            for factor_name, computation in zip(factor.factors_names, factor.factor_formula(stock=stock, date=date))
        }
        pipeline_df = pd.Series(factors_dict).unstack(level=[1, 2])

        return pipeline_df

    def normalize_factors(self, pipeline_df: pd.DataFrame, winsorize_bounds=(0.05, 0.95), method='min-max'):
        '''

        :param pipeline_df:

        :param winsorize_bounds: to take care of outliers, specify bounds, or lambda function

        :param normalization_method: 'min-max', 'z-score', or lambda function
        Normalization makes training less sensitive to the scale of features, so we can better solve for coefficients.

        :return:
        '''

        def winsorize_group(group):

            def _sub(sub):
                # winsorize returns an numpy array, sub is a dataframe; sub[:] replaces the "values" of the dataframe,
                # not the dataframe itself
                sub[:] = mstats.winsorize(a=sub.values, limits=winsorize_bounds, axis=0)
                return sub

            # Return the result of the processing on the nested group
            return group.groupby(level=1, axis=1).apply(_sub)

        # First, we winsorize. For each date, apply winsorization to each column
        # So first, split by date along rows (level=0, axis=0), then split by factor category along columns
        if winsorize_bounds is not None:
            pipeline_df = pipeline_df.groupby(level=0, axis=0).apply(winsorize_group)

        print('Winsorized dataframe becomes\n', pipeline_df)

        # Then, normalize each factor according to some scheme
        def normalize_group(group):
            def _sub(sub):
                if method == 'z-score':
                    sub[:] = stats.zscore(sub, axis=0)
                elif method == 'min-max':
                    sub[:] = preprocessing.normalize(X=sub, axis=0)

                elif isinstance(method, typing.Callable):
                    sub[:] = method(sub)
                else:
                    raise AttributeError

                return sub

            return group.groupby(level=1, axis=1).apply(_sub)

        pipeline_df = pipeline_df.groupby(level=0, axis=0).apply(normalize_group)

        return pipeline_df

    def factor_weighted_sum(self, pipeline_df):
        '''
        Then, do a weighted sum of the factors for each category
        :param pipeline_df:
        :return:
        '''

        def weight_group(group):
            def _sub(sub):
                def weight_column(column_df):
                    # That's to multiply weight of one column

                    # Find the associated weight, filtering from factor, then metric within factor
                    associated_weight = 0
                    for f in self.factors:
                        if f.__class__.__name__ == column_df.columns[0][0]:
                            for i, m in enumerate(f.factors_names):
                                if m == column_df.columns[0][1]:
                                    associated_weight = f.weights[i]
                                    break
                    column_df[:] = column_df[:] * associated_weight
                    return column_df

                # Multiply each column with its associated weight
                weighted_columns_df = sub.groupby(level=1, axis=1).apply(weight_column)

                # Sum to get the weighted sum of each factor category
                return weighted_columns_df.groupby(level=0, axis=1).sum()

            return _sub(sub=group)  # group for each column group

        pipeline_df = pipeline_df.groupby(level=0, axis=0).apply(weight_group)  # group for each date

        return pipeline_df

    def portfolio_cross_section(self, pipeline_df: pd.DataFrame,
                                allocation_method: PortfolioAllocationModel = ValueWeightedPortfolio):
        '''
        :param pipeline_df
        :param rank:        List of factor directions to sort (asc, desc). Descending by default.
                            If list consists of one element, it's univariate sort. If it consists of two, it's bivariate, etc.
        :param percentile_split List of tuples, each of two floats

        :return:
        '''

        def split_stocks_quantile(df: pd.DataFrame, factor: str):
            factor_rank = None
            for factor_ in self.factors:
                if factor_.__class__.__name__ == factor:
                    factor_rank = factor_.rank_split

            bottom_quantile = df[df[factor] <= df[factor].quantile(factor_rank[0])]
            bottom_quantile_stocks = [stock for date, stock in bottom_quantile.index.values]

            top_quantile = df[df[factor] >= df[factor].quantile(factor_rank[1])]
            top_quantile_stocks = [stock for date, stock in top_quantile.index.values]

            return bottom_quantile_stocks, top_quantile_stocks

        def select_stocks(group):
            returns_df = pd.DataFrame()
            from_date = group.index.values[0][0]
            from_date_idx = group.index.levels[0].to_list().index(from_date)
            try:
                # TODO think about inclusive at rebalancing day
                to_date = group.index.levels[0][from_date_idx + 1] - timedelta(days=1)
            except:
                to_date = self.end_date
            if 'SMB' in group.columns:
                # Do the Fama French / AQR Way
                small_size_stocks, large_size_stocks = split_stocks_quantile(df=group, factor='SMB')

                for factor in group.columns:
                    if factor != 'SMB':
                        bottom_quantile_stocks, top_quantile_stocks = split_stocks_quantile(df=group, factor=factor)

                        small_top_stocks = set.intersection(set(small_size_stocks), set(top_quantile_stocks))
                        big_top_stocks = set.intersection(set(large_size_stocks), set(top_quantile_stocks))

                        small_bottom_stocks = set.intersection(set(small_size_stocks), set(bottom_quantile_stocks))
                        big_bottom_stocks = set.intersection(set(large_size_stocks), set(bottom_quantile_stocks))

                        cross_section_returns = {}
                        for name, stocks in zip(['Small Top', 'Big Top', 'Small Bottom', 'Big Bottom'],
                                                [small_top_stocks, big_top_stocks, small_bottom_stocks,
                                                 big_bottom_stocks]):
                            if len(stocks) > 0:
                                portfolio = self.asset_returns[stocks]
                                # To allocate weight, need history of returns up to now
                                weights = allocation_method(Portfolio(portfolio.loc[:from_date])).solve_weights()
                                returns = np.sum(weights * portfolio.loc[from_date:to_date], axis=1)
                                cross_section_returns[name] = returns
                            else:
                                dates = pd.date_range(start=from_date + timedelta(days=1) - timedelta(seconds=1),
                                                      end=to_date + timedelta(days=1) - timedelta(seconds=1)).to_list()
                                cross_section_returns[name] = pd.Series(np.zeros((to_date - from_date).days + 1),
                                                                        index=dates)
                        # HML = 1/2 (Small Value + Big Value) - 1/2 (Small Growth + Big Growth).
                        returns = 0.5 * (
                            cross_section_returns['Small Top'].add(cross_section_returns['Big Top'], fill_value=0)) \
                                  - 0.5 * (
                                      cross_section_returns['Small Bottom'].add(cross_section_returns['Big Bottom'],
                                                                                fill_value=0))
                        returns.name = factor
                        returns_df = returns_df.join([returns],
                                                     how='inner') if not returns_df.empty else returns.to_frame()
            return returns_df

        factor_returns = pipeline_df.groupby(level=0, axis=0).apply(select_stocks)
        factor_returns.index = factor_returns.index.droplevel(0)
        return factor_returns


class FactorModelDataset(Enum):
    AQR_DATASET = 'AQR Factors Data'
    FAMA_FRENCH_3_DATASET = 'Fama-French 3 Factors Data'
    CARHART_4_DATASET = 'Carhart 4 Factors Data'
    FAMA_FRENCH_5_DATASET = 'Fama-French 5 Factors Data'
    Q_FACTOR_DATASET = 'Q Factors Data'


class CapitalAssetPricingModel(AssetPricingModel):
    def __init__(self, factor_dataset=FactorModelDataset.FAMA_FRENCH_3_DATASET,
                 frequency: str = 'Monthly', to_date: datetime = None, from_date=None):
        super().__init__(factor_dataset, ['MKT-RF'], frequency, to_date, from_date)
        self.excess_market_returns = self.factors_timedf.df_returns['MKT-RF']

    def beta_covariance_method(self, benchmark_returns):
        pass

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

    '''
    The Security Market Line (SML) graphically represents the relationship between the asset's return (on y-axis) and systematic risk (or beta, on x-axis).
    With E(R_i) = R_f + B_i * (E(R_m) - R_f), the y-intercept of the SML is equal to the risk-free interest rate, while the slope is equal to the market risk premium
    Plotting the SML for a market index (i.e. DJIA), individual assets that are correctly priced are plotted on the SML (in the ideal 'Efficient Market Hypothesis' world). 
    In real market scenarios, we are able to use the SML graph to determine if an asset being considered for a portfolio offers a reasonable expected return for the risk. 
    - If an asset is priced at a point above the SML, it is undervalued, since for a given amount of risk, it yields a higher return. 
    - Conversely, an asset priced below the SML is overvalued, since for a given amount of risk, it yields a lower return.
    '''

    def security_market_line(self, portfolio: Portfolio, date: datetime = None, regression_window: int = 36,
                             benchmark: pd.Series = None):

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


class FamaFrench_ThreeFactorModel(AssetPricingModel):

    def __init__(self, frequency: str = 'Monthly', to_date: datetime = None, from_date=None):
        super().__init__(FactorModelDataset.FAMA_FRENCH_3_DATASET, frequency, to_date, from_date)


class Carhart_FourFactorModel(AssetPricingModel):
    def __init__(self, frequency: str = 'Monthly', to_date: datetime = None, from_date=None):
        super().__init__(FactorModelDataset.CARHART, frequency, to_date, from_date)


class FamaFrench_FiveFactorModel(AssetPricingModel):

    def __init__(self, frequency: str = 'Monthly', to_date: datetime = None, from_date=None):
        super().__init__(FactorModelDataset.FAMA_FRENCH_5_DATASET, frequency, to_date, from_date)


class AQR_FactorModel(AssetPricingModel):
    def __init__(self, frequency: str = 'Monthly', to_date: datetime = None, from_date=None):
        super().__init__(FactorModelDataset.AQR_DATASET, frequency, to_date, from_date)


class Q_FactorModel(AssetPricingModel):
    pass


def factor_dataframe(portfolio_returns, regression_window: int = 36, benchmark_returns='MKT',
                     frequency='Monthly', date: datetime = None):
    capm_stats = capital_asset_pricing_model(portfolio_returns=portfolio_returns,
                                             regression_window=regression_window,
                                             benchmark_returns=benchmark_returns, frequency=frequency, date=date)
    carhart_stats = carhart_4_factor_model(portfolio_returns=portfolio_returns, regression_window=regression_window,
                                           benchmark_returns=benchmark_returns, frequency=frequency, date=date)
    ff3_stats = fama_french_3_factor_model(portfolio_returns=portfolio_returns, regression_window=regression_window,
                                           benchmark_returns=benchmark_returns, frequency=frequency, date=date)
    ff5_stats = fama_french_5_factor_model(portfolio_returns=portfolio_returns, regression_window=regression_window,
                                           benchmark_returns=benchmark_returns, frequency=frequency, date=date)

    # DataFrame with coefficients and t-stats
    results_df = pd.DataFrame({'CAPMcoeff': capm_stats.params, 'CAPMtstat': capm_stats.tvalues,
                               'FF3coeff': ff3_stats.params, 'FF3tstat': ff3_stats.tvalues,
                               'CARHARTcoeff': carhart_stats.params, 'CARHARTstat': carhart_stats.tvalues,
                               'FF5coeff': ff5_stats.params, 'FF5tstat': ff5_stats.tvalues},
                              index=['Intercept', 'MKT', 'SMB', 'HML', 'UMD', 'RMW', 'CMA'])

    dfoutput = summary_col([capm_stats, ff3_stats, carhart_stats, ff5_stats], stars=True, float_format='%0.4f',
                           model_names=['CAPM', 'FF3', 'CARHART', 'FF5'],
                           info_dict={'N': lambda x: "{0:d}".format(int(x.nobs)),
                                      'Adjusted R2': lambda x: "{:.4f}".format(x.rsquared_adj)},
                           regressor_order=['Intercept', 'MKT', 'SMB', 'HML', 'UMD', 'RMW', 'CMA'])
    print(dfoutput)
    return results_df


if __name__ == '__main__':
    portfolio = Portfolio(assets=['AAPL'])


    # capm = CapitalAssetPricingModel(frequency='Monthly').regress_factor_loadings(portfolio=portfolio,
    #                                                                              rolling=False,
    #                                                                              regression_window=36)
    # fama_french_3 = FamaFrench_ThreeFactorModel(frequency='Monthly').regress_factor_loadings(portfolio=portfolio,
    #                                                                                          rolling=False,
    #                                                                                          regression_window=36)
    # fama_french_5 = FamaFrench_FiveFactorModel(frequency='Monthly').regress_factor_loadings(portfolio=portfolio,
    #                                                                                         rolling=False,
    #                                                                                         regression_window=36)

    # capm.markowitz_efficient_frontier(portfolio=Portfolio(assets=MarketIndices.DOW_JONES))
    # capm.security_market_line(portfolio=Portfolio(assets=MarketIndices.DOW_JONES), date=datetime.now(),
    #                           regression_window=5 * 12)

    # # Setting for yahoo finance: monthly returns for past 5 years, using S&P 500 as benchmark
    # capital_asset_pricing_model(portfolio_returns='AAPL', regression_window=12 * 5, frequency='Monthly',
    #                             benchmark_returns='^GSPC')

    class SMB(Factor):
        def __init__(self):
            super().__init__(factors_names=['Market Cap'])

        def factor_formula(self, stock, date):
            return [metrics.market_capitalization(stock=stock, date=date)]


    class Quality(Factor):
        def __init__(self, weights=None, factors_names=None):

            if factors_names is None:
                factors_names = ['ROA', 'ROE']
            if weights is None:
                weights = [0.5, 0.5]
            super().__init__(weights=weights, factors_names=factors_names)

        def factor_formula(self, stock, date):
            return [ratios.return_on_assets(stock=stock, date=date, period='FY'),
                    ratios.return_on_equity(stock=stock, date=date, period='FY')]


    class MultiValue(Factor):
        def __init__(self, weights=None, factors_names=None):

            if factors_names is None:
                factors_names = ['P/E', 'P/B']
            if weights is None:
                weights = [0.5, 0.5]
            super().__init__(weights=weights, factors_names=factors_names)

        def factor_formula(self, stock, date):
            return [ratios.price_to_earnings(stock=stock, date=date, period='FY'),
                    ratios.price_to_book_value(stock=stock, date=date, period='FY')]


    tickers = macro.companies_in_index(config.MarketIndices.DOW_JONES)[:10]
    asset_pricing = CustomAssetPricingModel(factors=[SMB(), Quality(), MultiValue()], securities_universe=tickers,
                                            start_date=datetime(2019, 9, 1), end_date=datetime(2020, 3, 5),
                                            rebalancing_frequency=RebalancingFrequency.QUARTERLY
                                            )
    pipeline_df = asset_pricing.compute_raw_factors()
    print('Raw computed factors are\n', pipeline_df)

    # pipeline_df = asset_pricing.normalize_factors(pipeline_df=pipeline_df, winsorize_bounds=(0.20, 0.80),
    #                                               method='min-max')
    # print('Normalized factors are\n', pipeline_df)

    pipeline_df = asset_pricing.factor_weighted_sum(pipeline_df)
    print('Weighted summed factors are\n', pipeline_df)

    asset_pricing.portfolio_cross_section(pipeline_df)
