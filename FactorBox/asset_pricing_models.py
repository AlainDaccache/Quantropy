import abc
import os
from enum import Enum
import pickle
from datetime import timedelta, datetime
import pandas as pd
import statsmodels.formula.api as sm
import typing
import inspect

from scipy.optimize import LinearConstraint, minimize, Bounds
from statsmodels.iolib.summary2 import summary_col
import matplotlib.pyplot as plt
import numpy as np
import historical_data_collection.data_preparation_helpers as excel
import config
import exceptions_library as exception
import fundamental_analysis.macroeconomic_analysis as macro
from config import MarketIndices, RebalancingFrequency
import fundamental_analysis.accounting_ratios as ratios
from fundamental_analysis.supporting_metrics import market_capitalization

'''
https://alphaarchitect.com/2011/08/01/how-to-use-the-fama-french-model/
https://www.sciencedirect.com/topics/economics-econometrics-and-finance/capm
https://hackernoon.com/using-capital-asset-pricing-model-capm-versus-black-scholes-model-to-value-stocks-a-how-to-guide-r53032tc
http://content.moneyinstructor.com/948/capm.html
'''


class FactorModelDataset(Enum):
    AQR_DATASET = 'AQR Factors Data.xlsx'
    FAMA_FRENCH_DATASET = 'Fama-French Factors Data.xlsx'
    Q_FACTOR_DATASET = 'Q Factors Data.xlsx'


# TODO follow methodology of
# - BlackRock: https://www.ishares.com/us/resources/tools/factor-box-resources#methodology
# -

# Shouldn't calculate every date in iterations, instead should do once and for all. So input can't be (stock, date) to factor
# TODO First abstraction: https://www.quantopian.com/posts/how-to-define-a-custom-factor-using-fundamental-data-of-morningstar-dataset
# TODO Second abstraction: http://alphacompiler.com/

class Factor(metaclass=abc.ABCMeta):
    def __init__(self, percentile_breakpoints):
        self.percentile_breakpoints = percentile_breakpoints

    @abc.abstractmethod
    def compute(self, stock, date):
        pass


class TimeDataFrame:
    # TODO i think there should be internal structure just for Daily, inaccessible to user, so that we can resample from.
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
            return TimeDataFrame(self.df_returns.iloc[from_date_idx:to_date_idx])

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
    def __init__(self, *args):
        super().__init__(*args)

    def pre_filter_universe(self) -> bool:
        pass

    def construct_raw_df(self, securities_universe, factors_dct,
                         start_date: datetime, end_date: datetime, rebalancing_frequency: RebalancingFrequency,
                         portfolio_allocation_policy=None, long_short_exposure=None) -> pd.DataFrame:
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
            for factor_type, factors in factors_dct.items()
            for factor, cmp in factors.items()
            for stock in securities_universe
        }
        pipeline_df = pd.Series(factors_dict).unstack(level=[1, 2])
        print(pipeline_df.head(20))

        return pipeline_df

    def normalization_process(self, pipeline_df):
        # Now, winsorize

        # # Then, normalize each factor (compute Z-score i.e. (x - mu) / sigma)
        # factors_df = factors_df.apply(stats.zscore, axis=1)
        # factors_df = pd.DataFrame(factors_df.values.tolist(), index=factors_df.index, columns=long_stocks)
        #
        # # Then, add factors for each factor category for each company to make score for that company
        # factors_df = factors_df.groupby(level=0, axis=0).agg(np.sum)
        # print(factors_df.to_string())
        #
        # # Then, normalize again and sum across factor categories, and rank
        # factors_df = factors_df.apply(stats.zscore, axis=1)
        # factors_df = pd.DataFrame(factors_df.values.tolist(), index=factors_df.index, columns=long_stocks)
        # factors_df = factors_df.apply(np.sum, axis=0)
        # factors_df.sort_values(axis=0, ascending=False, inplace=True)
        # print(factors_df.to_string())
        pass


def factor_dataframe(portfolio_returns, regression_period: int = 36, benchmark_returns='MKT',
                     frequency='Monthly', date: datetime = None):
    capm_stats = capital_asset_pricing_model(portfolio_returns=portfolio_returns, regression_period=regression_period,
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
    # Setting for yahoo finance: monthly returns for past 5 years, using S&P 500 as benchmark
    # capital_asset_pricing_model(portfolio_returns='AAPL', regression_period=12 * 5, frequency='Monthly',
    #                             benchmark_returns='^GSPC')
    # portfolio_returns = excel.slice_resample_merge_returns(['CAT', 'PG', 'CSCO'],
    #                                                        lookback=timedelta(days=int(365.25 * 5)))
    # efficient_frontier(portfolio_returns)
    asset_pricing = CustomAssetPricingModel()
    asset_pricing.construct_raw_df(securities_universe=['AAPL', 'AMGN'],
                                   factors_dct={
                                       'Value': {'Price-to-Earnings': (ratios.price_to_earnings_ratio, 0.25),
                                                 'Price-to-Book': (ratios.price_to_book_value_ratio, 0.25)},
                                       'Size': {'Market Cap': (market_capitalization, 1)}},
                                   start_date=datetime(2019, 1, 1), end_date=datetime(2020, 1, 1),
                                   rebalancing_frequency=RebalancingFrequency.QUARTERLY)

"""
How to identify the factor profile of a company or fund?
--------------------------------------------------------

We specify factors, such as Value, Growth, Quality etc.

Each of those factors will be an aggregate of some metrics. For example, Value is an aggregate of P/E and P/B

We give each of those factors and metrics within, a weighting. For instance P/E is worth 75%, and P/B 25%

For each stock, we compute those metrics.

Then, we normalize each metric (either across all universe, selected universe, each sector, each capitalization category...)

Finally, we compute the weighted sum of the metrics for each stock, to make a score. Now, each factor has a score for each stock.

--------------------------------------------------------------------------------------

Alternatively, we find the Beta exposures to the factors in asset pricing models such as Fama-French and AQR

https://www.blackrock.com/us/partner/tools/factor-box-360-evaluator-methodology

https://www.morningstar.com/InvGlossary/morningstar_style_box.aspx
http://news.morningstar.com/pdfs/FactSheet_StyleBox_Final.pdf


"""
