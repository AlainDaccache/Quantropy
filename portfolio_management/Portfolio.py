import os
import re

import pandas as pd
import typing
import historical_data_collection.data_preparation_helpers as excel
import config
import macroeconomic_analysis.macroeconomic_analysis as macro
import numpy as np
from datetime import timedelta, datetime
from datetime import datetime
from config import MarketIndices


class TimeDataFrame:
    def __init__(self, returns):
        returns_copy = []
        cur_max_freq = 'D'
        frequencies = ['D', 'W', 'M', 'Q', 'Y']
        if not isinstance(returns, list):
            returns = [returns]
        for retrn in returns:
            if isinstance(retrn, str):
                path = os.path.join(config.STOCK_PRICES_DIR_PATH, '{}.pkl'.format(retrn))
                series = pd.read_pickle(path)['Adj Close'].pct_change().rename(retrn)
                returns_copy.append(series)
                l_ = 1
            elif isinstance(retrn, pd.Series):
                returns_copy.append(retrn)
                l_ = 1
            elif isinstance(retrn, pd.DataFrame):
                for col in retrn.columns:
                    returns_copy.append(retrn[col])
                l_ = len(retrn.columns)
            else:
                raise Exception

            returns_freq = returns_copy[-1].index.inferred_freq
            if returns_freq is None:  # usually happens when weekend days are not in dataframe
                test_0, test_1 = returns_copy[-1].index[:2]  # take two consecutive elements
                delta = (test_1 - test_0).days  # timedelta object, get days
                if 1 <= delta <= 7:
                    returns_freq = 'D'
                elif 7 <= delta <= 30.5:
                    returns_freq = 'W'
                elif 30.5 <= delta <= 30.5 * 4:
                    returns_freq = 'M'
                elif 30.5 * 4 <= delta <= 365.25:
                    returns_freq = 'Q'
                else:
                    returns_freq = 'Y'
                for l in range(1, l_ + 1):
                    returns_copy[-l] = returns_copy[-l].asfreq(freq=returns_freq, fill_value=0.0)
            if frequencies.index(returns_freq) > frequencies.index(cur_max_freq):
                cur_max_freq = returns_freq

        self.frequency = cur_max_freq
        merged_returns = pd.DataFrame()
        for retrn in returns_copy:
            f = retrn.index.freq
            if hasattr(f, 'name'):
                f = retrn.index.freq.name
            if frequencies.index(f) < frequencies.index(cur_max_freq):
                resampled_returns = retrn.resample(self.frequency[0]).apply(
                    lambda x: ((x + 1).cumprod() - 1).last("D"))
                resampled_returns.index = resampled_returns.index + timedelta(days=1) - timedelta(seconds=1)
                merged_returns = merged_returns.join(resampled_returns.to_frame(), how='outer')
            else:
                merged_returns = merged_returns.join(retrn.to_frame(), how='outer')
        # usually happens when we resample to a frequency and certain date isn't there, it's replaced with []
        for col in merged_returns.columns:
            merged_returns[col] = merged_returns[col].apply(lambda y: 0 if isinstance(y, np.ndarray) else y)

        self.df_returns = merged_returns

    freq_to_yearly = {'D': 252, 'W': 52, 'M': 12, 'Y': 1}

    def set_frequency(self, frequency: str, inplace: bool = False):
        resampled = self.df_returns.resample(frequency[0]).apply(lambda x: ((x + 1).cumprod() - 1).last("D"))
        resampled.index = resampled.index + timedelta(days=1) - timedelta(seconds=1)
        if not inplace:
            class_ = self.__class__.__name__
            return self.__class__(resampled)
        else:
            self.df_returns = resampled
            self.frequency = frequency[0]

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
            lookback = timedelta(days=int(period_to_int[self.frequency[0]] * from_date))
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
            resampled_returns = retrn.df_returns.resample(self.frequency[0]).apply(
                lambda x: ((x + 1).cumprod() - 1).last("D"))
            resampled_returns.index = resampled_returns.index + timedelta(days=1) - timedelta(seconds=1)
            merged_returns = merged_returns.join(resampled_returns, how='inner')  # TODO inner or outer?
        if inplace:
            self.df_returns = merged_returns
        else:
            class_ = self.__class__.__name__
            return self.__class__(merged_returns)


class Portfolio(TimeDataFrame):
    def __init__(self, assets):
        if isinstance(assets, MarketIndices):
            assets = macro.companies_in_index(market_index=assets)[:5]
        super().__init__(assets)
        self.portfolio_tickers = self.df_returns.columns

    def get_volatility_returns(self):
        return self.df_returns.std(axis=0) * np.sqrt(self.freq_to_yearly[self.frequency[0]])

    def get_weighted_volatility_returns(self, weights):
        return np.sqrt(np.dot(weights, np.dot(weights, self.get_covariance_matrix())))

    def get_covariance_matrix(self):
        return self.df_returns.cov() * self.freq_to_yearly[self.frequency[0]]

    def get_mean_returns(self):
        return self.df_returns.mean(axis=0) * self.freq_to_yearly[self.frequency[0]]

    def get_weighted_sum_returns(self, weights):
        return np.sum(weights * self.df_returns, axis=1)

    def get_weighted_mean_returns(self, weights):
        return np.dot(weights, self.get_mean_returns())

# if __name__ == '__main__':
#     path = "C:\\Users\\15148\\Desktop\\Movies"
#     files = os.listdir(path=path)
#     files.sort(key=lambda x: re.split(r'(\d+)', x))
#     print(files)
