import abc
import os
from enum import Enum
from datetime import timedelta, datetime
from pprint import pprint

import pandas as pd
import statsmodels.formula.api as sm
import typing

from pandas._libs.tslibs.timestamps import Timestamp
from sklearn import preprocessing
from scipy.stats import mstats, stats
from statsmodels.iolib.summary2 import summary_col
import matplotlib.pyplot as plt
import numpy as np
import historical_data_collection.data_preparation_helpers as excel
import config
import macroeconomic_analysis.macroeconomic_analysis as macro
from config import MarketIndices, RebalancingFrequency

'''
https://alphaarchitect.com/2011/08/01/how-to-use-the-fama-french-model/
https://www.sciencedirect.com/topics/economics-econometrics-and-finance/capm
https://hackernoon.com/using-capital-asset-pricing-model-capm-versus-black-scholes-model-to-value-stocks-a-how-to-guide-r53032tc
http://content.moneyinstructor.com/948/capm.html

BlackRock: https://www.blackrock.com/us/partner/tools/factor-box-360-evaluator-methodology
https://www.ishares.com/us/resources/tools/factor-box-resources#methodology
MorningStar: https://www.morningstar.com/InvGlossary/morningstar_style_box.aspx
http://news.morningstar.com/pdfs/FactSheet_StyleBox_Final.pdf

'''


# TODO Big concern as to how to consider edge cases for company universe, like
#  Bankruptcy,
#  Mergers, and Acquisition,
#  and stock split -> maybe in simulator consider only pct returns of adj close, but perform transactions with actual close

class FactorModelDataset(Enum):
    AQR_DATASET = 'AQR Factors Data.xlsx'
    FAMA_FRENCH_3_DATASET = 'Fama-French 3 Factors Data.xlsx'
    FAMA_FRENCH_5_DATASET = 'Fama-French 5 Factors Data.xlsx'
    Q_FACTOR_DATASET = 'Q Factors Data.xlsx'


# Shouldn't calculate every date in iterations, instead should do once and for all. So input can't be (stock, date) to factor
# TODO First abstraction: https://www.quantopian.com/posts/how-to-define-a-custom-factor-using-fundamental-data-of-morningstar-dataset
# TODO Second abstraction: http://alphacompiler.com/

class Factor(metaclass=abc.ABCMeta):
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


class TimeDataFrame:
    def __init__(self, returns):
        returns_copy = []
        cur_max_freq = 'D'
        frequencies = ['D', 'W', 'M', 'Q', 'Y']
        if not isinstance(returns, list):
            returns = [returns]
        for retrn in returns:
            if isinstance(retrn, str):
                path = '{}/{}.xlsx'.format(config.STOCK_PRICES_DIR_PATH, retrn)
                series = excel.read_df_from_csv(path)['Adj Close'].pct_change().rename(retrn)
                returns_copy.append(series)
            elif isinstance(retrn, pd.Series):
                returns_copy.append(retrn)
            elif isinstance(retrn, pd.DataFrame):
                for col in retrn.columns:
                    returns_copy.append(retrn[col])
            else:
                raise Exception

            returns_freq = returns_copy[-1].index.inferred_freq
            if returns_freq is None:
                returns_freq = 'D'  # from YahooFinance, check bug!
            if frequencies.index(returns_freq) > frequencies.index(cur_max_freq):
                cur_max_freq = returns_freq

        self.df_frequency = cur_max_freq
        merged_returns = pd.DataFrame()
        for retrn in returns_copy:
            resampled_returns = retrn.resample(self.df_frequency[0]).apply(lambda x: ((x + 1).cumprod() - 1).last("D"))
            resampled_returns.index = resampled_returns.index + timedelta(days=1) - timedelta(seconds=1)
            merged_returns = merged_returns.join(resampled_returns.to_frame(), how='outer')

        for col in merged_returns.columns:  # TODO, first off why do we need to do this? what triggers the [] to appear
            merged_returns[col] = merged_returns[col].apply(lambda y: 0 if isinstance(y, np.ndarray) else y)

        self.df_returns = merged_returns

    freq_to_yearly = {'D': 252, 'W': 52, 'M': 12, 'Y': 1}

    def set_frequency(self, frequency: str, inplace: bool = False):
        resampled = self.df_returns.resample(frequency[0]).apply(lambda x: ((x + 1).cumprod() - 1).last("D"))
        resampled.index = resampled.index + timedelta(days=1) - timedelta(seconds=1)
        if not inplace:
            return TimeDataFrame(resampled)
        else:
            self.df_returns = resampled
            self.df_frequency = frequency[0]

    def slice_dataframe(self, to_date: datetime = None, from_date=None, inplace: bool = False):
        if to_date is not None:
            to_date_idx = excel.get_date_index(date=to_date, dates_values=self.df_returns.index)
        else:
            to_date = self.df_returns.index[-1]
            to_date_idx = len(self.df_returns)

        if isinstance(from_date, datetime):
            from_date_idx = excel.get_date_index(date=from_date, dates_values=self.df_returns.index)
        elif isinstance(from_date, int):
            period_to_int = {'D': 1, 'W': 7, 'M': 30.5, 'Y': 365.25}
            lookback = timedelta(days=int(period_to_int[self.df_frequency[0]] * from_date))
            from_date_idx = excel.get_date_index(date=to_date - lookback, dates_values=self.df_returns.index)
        elif isinstance(from_date, timedelta):
            from_date_idx = excel.get_date_index(date=to_date - from_date, dates_values=self.df_returns.index)
        else:
            from_date_idx = 0

        if inplace:
            self.df_returns = self.df_returns.iloc[from_date_idx:to_date_idx]
        else:
            class_ = self.__class__.__name__
            return self.__class__(self.df_returns.iloc[from_date_idx:to_date_idx])

    def merge(self, time_dfs: typing.List, inplace: bool = False):
        merged_returns = self.df_returns
        for retrn in time_dfs:
            if not isinstance(retrn, TimeDataFrame):
                retrn = TimeDataFrame(retrn)
            resampled_returns = retrn.df_returns.resample(self.df_frequency[0]).apply(
                lambda x: ((x + 1).cumprod() - 1).last("D"))
            resampled_returns.index = resampled_returns.index + timedelta(days=1) - timedelta(seconds=1)
            merged_returns = merged_returns.join(resampled_returns, how='inner')  # TODO inner or outer?
        if inplace:
            self.df_returns = merged_returns
        else:
            return TimeDataFrame(merged_returns)


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


class AssetPricingModel:

    def __init__(self, *args):
        '''

        :param args:
        Import a dataframe
            * factor_df: pd.DataFrame   for your own dataframe
        Or for an already computed factors historical returns, like CAPM, Fama-French, AQR...
            * factor_model_type: FactorModelDataset
            * factors: list[str]        the factors in that model you want to use
            * frequency: str optional, Daily default
            * to_date: datetime optional
            * lookback_period or from_date: timedelta, datetime, or int.
        Or for even more customization
            * factor_model_dict: { factor_model: factors }
            * frequency: str optional, Daily default
            * to_date: datetime optional
            * lookback_period or from_date: timedelta, datetime, or int.

        '''
        # argspec = inspect.signature(self.__init__)
        frequency, from_date, to_date, lookback = 'Daily', None, None, None

        if isinstance(args[0], pd.DataFrame) and len(args) == 1:
            self.factor_timedf = TimeDataFrame([args])

        elif isinstance(args[0], FactorModelDataset) and len(args) >= 2:
            self.factor_model_type = args[0]
            path = os.path.join(config.FACTORS_DIR_PATH, args[0].value)
            factors = args[1] + ['RF']
            if len(args) >= 3 and isinstance(args[2], str):
                frequency = args[2]

            df = excel.read_df_from_csv(path=path, sheet_name=frequency)[factors]
            self.factors_timedf = TimeDataFrame(df).set_frequency(frequency=frequency, inplace=False)
            self.factors_timedf.df_returns = self.factors_timedf.df_returns.dropna(how='all')

            if len(args) >= 4 and isinstance(args[3], datetime):
                to_date = args[3]
            if len(args) >= 5 and (isinstance(args[4], datetime)
                                   or isinstance(args[4], timedelta) or isinstance(args[4], int)):
                from_date = args[4]

            self.factors_timedf.slice_dataframe(to_date=to_date, from_date=from_date, inplace=True)

    def regress_factor_loadings(self, portfolio, benchmark_returns: pd.Series = None,
                                date: datetime = None, regression_period: int = 36, plot=True):
        '''

        :param portfolio: str, pd.Series
        :param benchmark_returns:
        :param date:
        :param regression_period:
        :param plot:
        :return:
        '''

        if isinstance(portfolio, pd.DataFrame):
            raise TypeError('Inappropriate argument type for portfolio')

        portfolio = TimeDataFrame(portfolio)
        portfolio_copy = portfolio.set_frequency(self.factors_timedf.df_frequency, inplace=False) \
            .slice_dataframe(to_date=date, from_date=regression_period, inplace=False)

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

        # need to merge again to run regression on dataframe (with y being XsRet)
        df_stock_factor = pd.merge(portfolio_returns, factors_df, left_index=True, right_index=True)

        # rename because will give syntax error with '-' when running regression
        df_stock_factor.rename(columns={'MKT-RF': 'MKT'}, inplace=True)

        reg = sm.ols(formula='XsRet ~ {}'.format(' + '.join(factors_df.columns)),
                     data=df_stock_factor).fit(cov_type='HAC', cov_kwds={'maxlags': 1})
        print(reg.summary())
        return reg

    def plot(self, df_stock_factor, regression_model):
        plt.plot(df_stock_factor['XsRet'], df_stock_factor['MKT'], 'r.')
        # params[0] is const coef (y-axis intersection), and params[1] is AAPL coeff (correlation coefficient)
        plt.scatter(df_stock_factor['MKT'], df_stock_factor['XsRet'])
        plt.plot(df_stock_factor['MKT'],
                 regression_model.params[0] + regression_model.params[1] * df_stock_factor['MKT'], 'b', lw=2)
        plt.grid(True)
        plt.axis('tight')
        plt.xlabel('Portfolio Returns')
        plt.ylabel('Market Returns')
        plt.show()
        return plt


class CustomAssetPricingModel(AssetPricingModel):
    """

    How to identify the factor profile of a company or fund?

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

    def __init__(self, factors: typing.Dict, securities_universe):
        # super().__init__()
        self.factors = factors
        self.asset_returns = Portfolio(assets=securities_universe).df_returns
        self.securities_universe = self.asset_returns.columns

    def pre_filter_universe(self) -> bool:
        pass

    def construct_raw_df(self, start_date: datetime, end_date: datetime,
                         rebalancing_frequency: RebalancingFrequency) -> pd.DataFrame:
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

        # Generate range of dates between start and end date, at interval rebalancing frequency
        range_dates, i = [], 0
        while start_date + timedelta(days=round(i * rebalancing_frequency.value)) < end_date:
            range_dates.append(start_date + timedelta(days=round(i * rebalancing_frequency.value)))
            i = i + 1

        # Compute Raw Scores
        factors_dict = {
            (date, factor_type, factor, stock): cmp[0](stock, date)
            for date in range_dates
            for factor_type, factors in self.factors.items()
            for factor, cmp in factors.items()
            for stock in self.securities_universe
        }
        pipeline_df = pd.Series(factors_dict).unstack(level=[1, 2])

        # TODO do returns

        return pipeline_df

    def normalization_procedure(self, pipeline_df: pd.DataFrame, winsorize_bounds=(0.05, 0.95),
                                normalization_method='min-max'):
        '''

        :param pipeline_df:

        :param winsorize_bounds: to take care of outliers, specify bounds, or lambda function

        :param normalization_method: 'min-max', 'z-score', or lambda function
        Normalization makes training less sensitive to the scale of features, so we can better solve for coefficients.

        :return:
        '''

        # First, we winsorize. For each date, apply winsorization to each column
        # So first, split by date along rows (level=0, axis=0), then split by factor category along columns
        if winsorize_bounds is not None:
            winsorized_df = pipeline_df.groupby(level=0, axis=0).apply(
                lambda level_0_cols: level_0_cols.groupby(level=1, axis=1).apply(
                    lambda series: mstats.winsorize(a=series, limits=winsorize_bounds))
            )
            print(winsorized_df)

            # pipeline_df = pd.DataFrame(winsorized_df.values, index=pipeline_df.index, columns=pipeline_df.columns)

        # Then, normalize each factor according to some scheme

        def normalize(series):
            if normalization_method == 'z-score':
                return stats.zscore(series)
            elif normalization_method == 'min-max':
                return preprocessing.normalize(X=series)
            elif isinstance(normalization_method, typing.Callable):
                return normalization_method
            else:
                raise AttributeError

        normalized_df = pipeline_df.groupby(level=0, axis=0).apply(
            lambda level_0_cols: level_0_cols.groupby(level=1, axis=1).apply(lambda series: normalize(series)))
        # pipeline_df = pd.DataFrame(normalized_df.values, index=pipeline_df.index, columns=pipeline_df.columns)
        return pipeline_df

    def factors_ranking(self, pipeline_df):
        # Then, do a weighted sum of the factors for each category
        weighted_df = pipeline_df.groupby(level=0, axis=1).sum()
        pprint(weighted_df.to_dict())
        # lambda col_group: np.dot([], [])

        return weighted_df


def factor_dataframe(portfolio_returns, regression_period: int = 36, benchmark_returns='MKT',
                     frequency='Monthly', date: datetime = None):
    capm_stats = capital_asset_pricing_model(portfolio_returns=portfolio_returns,
                                             regression_period=regression_period,
                                             benchmark_returns=benchmark_returns, frequency=frequency, date=date)
    carhart_stats = carhart_4_factor_model(portfolio_returns=portfolio_returns, regression_period=regression_period,
                                           benchmark_returns=benchmark_returns, frequency=frequency, date=date)
    ff3_stats = fama_french_3_factor_model(portfolio_returns=portfolio_returns, regression_period=regression_period,
                                           benchmark_returns=benchmark_returns, frequency=frequency, date=date)
    ff5_stats = fama_french_5_factor_model(portfolio_returns=portfolio_returns, regression_period=regression_period,
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
    # security_market_line(assets_tickers=MarketIndices.DOW_JONES)
    # # Setting for yahoo finance: monthly returns for past 5 years, using S&P 500 as benchmark
    # capital_asset_pricing_model(portfolio_returns='AAPL', regression_period=12 * 5, frequency='Monthly',
    #                             benchmark_returns='^GSPC')
    # portfolio_returns = excel.slice_resample_merge_returns(['CAT', 'PG', 'CSCO'],
    #                                                        lookback=timedelta(days=int(365.25 * 5)))
    # efficient_frontier(portfolio_returns)

    # factors_dict = {'Value': {'Price-to-Earnings': (ratios.price_to_earnings_ratio, 0.75),
    #                           'Price-to-Book': (ratios.price_to_book_value_ratio, 0.25)},
    #                 'Size': {'Market Cap': (market_capitalization, 1)}}
    # asset_pricing = CustomAssetPricingModel(factors_dict)
    # pipeline_df = asset_pricing.construct_raw_df(securities_universe=['AAPL', 'AMGN'],
    #                                              start_date=datetime(2019, 9, 1), end_date=datetime(2020, 1, 1),
    #                                              rebalancing_frequency=RebalancingFrequency.QUARTERLY)
    # pipeline_df = asset_pricing.normalization_procedure(pipeline_df)
    dictio = {'Size': {(Timestamp('2019-09-01 00:00:00'), 'AAPL'): 2116356.037955703,
                       (Timestamp('2019-09-01 00:00:00'), 'AMGN'): 139551.76568603513,
                       (Timestamp('2019-12-02 00:00:00'), 'AAPL'): 2116356.037955703,
                       (Timestamp('2019-12-02 00:00:00'), 'AMGN'): 139551.76568603513},
              'Value': {(Timestamp('2019-09-01 00:00:00'), 'AAPL'): 101.33198101023262,
                        (Timestamp('2019-09-01 00:00:00'), 'AMGN'): 66.51600479006274,
                        (Timestamp('2019-12-02 00:00:00'), 'AAPL'): 100.90704728764197,
                        (Timestamp('2019-12-02 00:00:00'), 'AMGN'): 81.60759865965389}}
    quantiles_or_buckets = (0.3, 0.4, 0.7)
    pipeline_df = pd.DataFrame.from_dict(dictio)
    pipeline_grp_lvl0 = pipeline_df.groupby(level=0)
    for idx, (date, _) in enumerate(pipeline_grp_lvl0):
        next_date = list(pipeline_grp_lvl0.indices.keys())[idx + 1]
        for factor in pipeline_df.columns:
            stock_factors: pd.Series = pipeline_df[factor].loc[date]
            if isinstance(quantiles_or_buckets, int):
                quantiles_or_buckets = np.ones(quantiles_or_buckets) / quantiles_or_buckets

            long_stocks = stock_factors >= stock_factors.quantile(quantiles_or_buckets[0])
            long_stocks = [l for l, b in long_stocks.items() if b]
            long_portfolio = Portfolio(assets=long_stocks)
            weights = np.ones(len(long_stocks)) / len(long_stocks)
            long_portfolio_returns = long_portfolio.slice_dataframe(to_date=next_date, from_date=date) \
                .get_weighted_mean_returns(weights=weights)
            print(long_portfolio_returns)
            short_stocks = stock_factors <= stock_factors.quantile(quantiles_or_buckets[-1])
            short_stocks = [l for l, b in short_stocks.items() if b]

            print(next_date)
