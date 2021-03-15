"""

Tangible
Top down
When there is no

any industry that tries to keep lock people in to their way of doing things, eventually ends
up being disrupted. I want to become the industry standard for algorithmic trading.
A standardized layer that allows you to access data from multiple sources and

When you write code, you write to specified broker.

we have a black box api_routes, that talks to many brokers and providers,
while the coder only talks to us

advanced features
* screening
* optimization
* portfolio construction (asset pricing models)

they end up dependent on me, but on something that is (a) free

standardizing a fragmented market of the communication link for algorithmic trading
* no more reinventing the wheel or from-scratch
/
my available market is in terms of deployment fees (brokers alreayd have that). the total avialable
market is tools for stock screening, data etc.

easy way to talk to provider for free
premium service for advanced tools: educational

people already subscribe to diff data, diff analytics, different broker
-> it's fragmented. Time to integrate, reinvent wheel etc.

People pay subscriptions for services like that -> whats the amount for that kind of info
"""

import os
from functools import partial
import pandas as pd
import statsmodels.formula.api as sm
import matplotlib.pyplot as plt
import typing
import numpy as np
from math import ceil, floor
from statsmodels.regression.rolling import RollingOLS
from matilda.portfolio_management.Portfolio import TimeDataFrame
from datetime import timedelta
from sklearn import preprocessing
from scipy.stats import mstats, stats
from matilda import config
from datetime import datetime
from enum import Enum
from statsmodels.iolib.summary2 import summary_col
from matilda.portfolio_management.Portfolio import Portfolio
import abc


class AssetPricingModel:

    def __init__(self, *args):
        '''

        :param args:
        Import a dataframe
            * factor_df: pd.DataFrame   for your own dataframe

        Or for an already computed factors historical returns, like CAPM, Fama-French, AQR...
            * factor_model_type: FactorModelDataset.
            * factors: list[str]        the factors in that model you want to use. By default all.

        Or for even more customization
            * factor_model_dict: { factor_model: factors }

        Other parameters:
            * frequency: str optional, Monthly default.
            * to_date: datetime optional, otherwise keeps all dates available for no information loss.
            * lookback_period or from_date: timedelta, datetime, or int.
        '''
        # argspec = inspect.signature(self.__init__)
        # we keep an internal granular df to resample from (it's Daily)
        frequency, from_date, to_date, lookback = 'Monthly', None, None, None

        # Case one
        if (isinstance(args[0], pd.DataFrame) or isinstance(args[0], pd.Series)) and len(args) >= 1:
            self.factors_timedf = TimeDataFrame([args[0]])
            self.granular_df = self.factors_timedf

            if len(args) >= 2 and isinstance(args[1], str):
                frequency = args[1]

            if self.factors_timedf.frequency != frequency[0]:
                self.factors_timedf = self.factors_timedf.set_frequency(frequency=frequency, inplace=False)

            self.factors_timedf.df_returns = self.factors_timedf.df_returns.dropna(how='all')

            if len(args) >= 3 and isinstance(args[2], datetime):
                to_date = args[2]
            if len(args) >= 4 and (isinstance(args[3], datetime)
                                   or isinstance(args[3], timedelta) or isinstance(args[3], int)):
                from_date = args[3]

            self.factors_timedf.slice_dataframe(to_date=to_date, from_date=from_date, inplace=True)
        # Case two
        elif isinstance(args[0], FactorModelDataset) and len(args) >= 2:
            self.factor_model_type = args[0]
            path = os.path.join(config.FACTORS_DIR_PATH, 'pickle', '{}.pkl'.format(args[0].value))
            self.granular_df = pd.read_pickle(path)[frequency]

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
        self.factors = self.factors_timedf.df_returns.columns

    def regress_factor_loadings(self, portfolio, benchmark_returns: pd.Series = None,
                                date: datetime = None, regression_window: int = 36, rolling=False, show=True):
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
            if show:
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
            if show:
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
                    # plt.draw()
                    # plt.pause(0.001)

                    ax.scatter(df_stock_factor[factor], df_stock_factor.iloc[:, 0], alpha=0.3)
                    ax.grid(True)
                    ax.axis('tight')
                    ax.set_xlabel(factor if factor != 'MKT' else 'MKT-RF')
                    ax.set_ylabel('Portfolio Excess Returns')
                # plt.ion()
                plt.show()

            return reg

    def get_factor_scores_from_model(self, portfolio):
        pass

    def get_expected_returns(self, portfolio, benchmark_returns: pd.Series = None,
                             date: datetime = None, regression_window: int = 36):
        """

        :param portfolio:
        :param benchmark_returns:
        :param date:
        :param regression_window:
        :return:
        """
        betas = self.regress_factor_loadings(portfolio=portfolio, benchmark_returns=benchmark_returns,
                                             date=date, regression_window=regression_window)


class FactorModelDataset(Enum):
    AQR_DATASET = 'AQR Factors'
    FAMA_FRENCH_3_DATASET = 'Fama-French 3 Factors'
    CARHART_4_DATASET = 'Carhart 4 Factors'
    FAMA_FRENCH_5_DATASET = 'Fama-French 5 Factors'
    Q_FACTOR_DATASET = 'Q Factors'


class CapitalAssetPricingModel(AssetPricingModel):

    def __init__(self, factor_dataset=None, frequency: str = 'Monthly', to_date: datetime = None, from_date=None):
        """

        :param factor_dataset: Either a pandas DataFrame/Series
            or a FactorModelDataset object. By default, takes FAMA_FRENCH_3_DATASET, i.e. the market returns
            the returns AMEX, NYSE, NASDAQ overall.
        :param frequency: The desired resampling frequency of the returns.
            'Daily', 'Weekly', 'Monthly', 'Quarterly', 'Yearly'.
        :param to_date: By default, takes the last day in the factor_dataset
        :param from_date: Typically datetime object. If timedelta object, then deducts from to_date.
            If int, then deducts from to_date with given frequency parameter.
        """
        if factor_dataset is None:
            factor_dataset = FactorModelDataset.FAMA_FRENCH_3_DATASET
            super().__init__(factor_dataset, ['MKT-RF'], frequency, to_date, from_date)
            self.excess_market_returns = self.factors_timedf.df_returns['MKT-RF']
        else:
            # factor_dataset.rename('MKT')
            # rf = macro.risk_free_rates()
            super().__init__(factor_dataset, frequency, to_date, from_date)
            self.excess_market_returns = self.factors_timedf.df_returns.iloc[:, 0]

    def beta_covariance_method(self):
        """
        Divides the covariance of an asset (or portfolio) returns and those of the market, by the variance of the market's returns.

        :return: the beta of an asset (or portfolio)
        """
        pass


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


class FactorModels(Enum):
    CAPM = CapitalAssetPricingModel
    FamaFrench3 = FamaFrench_ThreeFactorModel
    Carhart4 = Carhart_FourFactorModel
    FamaFrench5 = FamaFrench_FiveFactorModel
    AQR = AQR_FactorModel
    Q = Q_FactorModel


def factor_dataframe(portfolio: Portfolio, regression_window: int = 36, frequency='Monthly'):
    capm_stats = CapitalAssetPricingModel(frequency=frequency).regress_factor_loadings(portfolio=portfolio,
                                                                                       rolling=False,
                                                                                       regression_window=regression_window)
    ff3_stats = FamaFrench_ThreeFactorModel(frequency=frequency).regress_factor_loadings(portfolio=portfolio,
                                                                                         rolling=False,
                                                                                         regression_window=regression_window)
    carhart_stats = Carhart_FourFactorModel(frequency=frequency).regress_factor_loadings(portfolio=portfolio,
                                                                                         rolling=False,
                                                                                         regression_window=regression_window)
    ff5_stats = FamaFrench_FiveFactorModel(frequency=frequency).regress_factor_loadings(portfolio=portfolio,
                                                                                        rolling=False,
                                                                                        regression_window=regression_window)

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

        self.holdings = pd.DataFrame(columns=['Long Stocks', 'Short Stocks'])  # will store (stock, weight) tuples
        self.returns = None

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

    def breakdown_by_buckets(self, buckets: int):
        '''
        When evaluating a factor, you need to see a clear linear relationship between the rankings and the returns

        :param factor:
        :param buckets:
        :return:
        '''

        pass

    def breakdown_by_sector(self):
        """
        For this factor, we observe at each point in time (so in a 'snapshot'):
            For our long portfolio, and for our short portfolio, do:
                Which stocks are we holding in this portfolio, along with weight?
                Add weights together for each sector
        :return:
        """

        pass


class CustomAssetPricingModel(AssetPricingModel):
    """
    Design your own asset pricing model

    * **Factors choice:**
        * We specify factors, such as Value, Growth, Quality etc.
        * Each of those factors will be an aggregate of some metrics
        * Each of those metrics is assigned a weight (so for each category, weights sum to 1).
        For example, Value is an aggregate of P/E (75%) and P/B (25%).

    * **Ranking scheme:**
        * For each stock, we compute and normalize those metrics (can winsorize first, apply different methods like min-max, z-score).
        * Then, we compute the weighted sum of the metrics for each stock, to make a score for each factor
        * Now, we sum those factors once again, so each stock will have one score, and we can rank based on that

    * **Portfolio construction:**


    As an extra step, we can find the Beta exposures by regressing to the factors in asset pricing models
    """

    def __init__(self, factors: typing.List, securities_universe, start_date: datetime,
                 end_date: datetime, rebalancing_frequency: config.RebalancingFrequency):
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

    def portfolio_cross_section(self, pipeline_df: pd.DataFrame, allocation_method): #=ValueWeightedAllocation
        """
        We cross-split the portfolio based on factors and percentiles, and pick the
        resulting portfolios to go long and short on. For example:
        +-----------------------------------------------------------+
        |                       |           Median ME               |
        +-----------------------+-----------------------------------|

                                                |
                                Small Value     |   Big Value
        70th BE/ME Percentile ------------------|-------------
                                Small Neutral   |   Big Neutral
        30th BE/ME Percentile ------------------|--------------
                                Small Growth    |   Big Growth
        :param allocation_method:
        :param pipeline_df
        :return:
        """

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

                        cross_section_returns = {name: {}
                                                 for name in ['Small Top', 'Big Top', 'Small Bottom', 'Big Bottom']}

                        for name, stocks in zip(['Small Top', 'Big Top', 'Small Bottom', 'Big Bottom'],
                                                [small_top_stocks, big_top_stocks, small_bottom_stocks,
                                                 big_bottom_stocks]):
                            if len(stocks) > 0:
                                portfolio = self.asset_returns[stocks]
                                # To allocate weight, need history of returns up to now
                                weights = allocation_method(Portfolio(portfolio.loc[:from_date])).solve_weights()
                                cross_section_returns[name]['Weight Allocation'] \
                                    = [(stock, weight) for stock, weight in zip(portfolio.columns, weights)]

                                returns = np.sum(weights * portfolio.loc[from_date:to_date], axis=1)
                                cross_section_returns[name]['Returns'] = returns
                            else:
                                dates = pd.date_range(start=from_date + timedelta(days=1) - timedelta(seconds=1),
                                                      end=to_date + timedelta(days=1) - timedelta(seconds=1)).to_list()
                                cross_section_returns[name]['Returns'] = pd.Series(
                                    np.zeros((to_date - from_date).days + 1), index=dates)
                                cross_section_returns[name]['Weight Allocation'] = [('', 0)]
                        # HML = 1/2 (Small Value + Big Value) - 1/2 (Small Growth + Big Growth).
                        long_stocks = small_top_stocks | big_top_stocks
                        short_stocks = small_bottom_stocks | big_bottom_stocks

                        for factor_ in self.factors:
                            if factor_.__class__.__name__ == factor:
                                # TODO
                                df = pd.DataFrame(columns=['Long Stocks', 'Short Stocks'], data=0)
                                factor_.holdings.append()

                        returns = 0.5 * (cross_section_returns['Small Top']['Returns'].add(
                            cross_section_returns['Big Top']['Returns'], fill_value=0)) \
                                  - 0.5 * (cross_section_returns['Small Bottom']['Returns'].add(
                            cross_section_returns['Big Bottom']['Returns'], fill_value=0))
                        returns.name = factor
                        returns_df = returns_df.join([returns],
                                                     how='inner') if not returns_df.empty else returns.to_frame()
            for factor, returns in returns_df.iteritems():
                factor_obj = None
                for f_ in self.factors:
                    if f_.__class__.__name__ == factor:
                        factor_obj = f_
                factor_obj.returns = returns
                # factor_obj.holdings =
            return returns_df

        factor_returns = pipeline_df.groupby(level=0, axis=0).apply(select_stocks)
        factor_returns.index = factor_returns.index.droplevel(0)
        return factor_returns

# if __name__ == '__main__':
#     # sp_500_market = Portfolio(assets=['AAPL'])
#     # capm = CapitalAssetPricingModel(frequency='Monthly', to_date=datetime.today(), from_date=80)
#     # reg = capm.regress_factor_loadings(portfolio=Portfolio(assets=['MSFT']))
#     # print(reg.params)
#
#     ff3 = FamaFrench_ThreeFactorModel(frequency='Monthly', to_date=datetime.today())
#     reg = ff3.regress_factor_loadings(portfolio=Portfolio(assets=['MSFT']))
#     print(reg.params)
