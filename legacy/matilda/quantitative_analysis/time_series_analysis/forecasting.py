import pickle
import re
import pandas as pd
import numpy as np
import math
from statsmodels.tsa.stattools import adfuller, kpss
from arch.unitroot import PhillipsPerron

"""
Refs: 
- https://www.machinelearningplus.com/time-series/time-series-analysis-python/
- https://machinelearningmastery.com/time-series-data-stationary-python/
- https://www.machinelearningplus.com/time-series/arima-model-time-series-forecasting-python/
"""


class TimeSeriesAnalysis:
    def __init__(self, series: pd.Series):
        self.original_series = series
        self.series = series

    def interpolate_ts(self, method: str):
        pass

    def test_stationarity(self, test: str, threshold=0.05, **kwargs):
        """
        Test for the stationarity of a given series around a deterministic trend.
        Interesting ref: https://stats.stackexchange.com/questions/88407/adf-test-pp-test-kpss-test-which-test-to-prefer

        :param test:    unit root test. The first three all start with the null of a unit root and have an
                        alternative of a stationary process. The last one, KPSS, has a null of a stationary process
                        with an alternative of a unit root.
                        - 'adf' for Augmented Dickey Fuller test,
                        - 'dfgls' for Elliott, Rothenberg and Stock’s GLS version of the Dickey-Fuller test
                        - 'pp' for Phillips–Perron test
                        - 'kpss' for Kwiatkowski–Phillips–Schmidt–Shin test,

        :param threshold:   confidence level for p_value. The p-value is the probability score based on which you can
                            decide whether to reject the null hypothesis or not.
                            If the p-value is less than a predefined alpha level (typically 0.05), we reject the null hypothesis.
        :param **kwargs:    Any additional arguments for the test in question i.e.
        :return: True if p-value below threshold (for DF and ADF) or above threshold (for KPSS), otherwise False.
        """
        if re.search('adf', test, re.IGNORECASE):
            test_statistic, p_value, n_lags_used, _, critical_values, _ = adfuller(self.series, **kwargs)
            return p_value < threshold
        elif re.search('kpss', test, re.IGNORECASE):
            test_statistic, p_value, n_lags_used, critical_values = kpss(self.series, **kwargs)
            return p_value > threshold  # for KPSS, series is NOT stationary if < threshold
        elif re.search('pp', test, re.IGNORECASE):
            result = PhillipsPerron(self.series)
            test_statistic, p_value, n_lags_used, critical_values = result.stat, result.pvalue, result.lags, result.critical_values
            return p_value < threshold
        else:
            raise Exception("Invalid `test`")

    def stationarize_ts(self, transform_fun, test_tup, n_thresh=10):
        """
        Making a time series stationary means to not make it a function of time, that is its mean and variance
        do not change over time.
        :param transform_fun: function to apply to time series.
            -   For **differentiation**, use `np.diff`. Preferably use `lambda x: np.diff(x, prepend=x[0])`
                to avoid losing data, since diff removes first element when differentiating,
                and need to prepend each time the first value.
            - For **log**, use `np.log`. To use different log bases, so use `lambda x: math.log(x, base)`
            -
        :param test_tup: tuple representing stationarity test and threshold
        :param n_thresh: max number of times to apply function before stopping
        :return:
        """

        def recursive_handler(n, *args):
            stationary = self.test_stationarity(test=test_tup[0], threshold=test_tup[1])
            if stationary or n == n_thresh:
                return args[0], n
            return recursive_handler(n + 1, transform_fun(*args))

        fun_applied_series, n = recursive_handler(0, self.series)
        print(f'function was applied {n} times.')
        self.series = pd.Series(index=self.series.index, data=fun_applied_series)
        return self.series, n

    def decompose_ts(self):
        pass

    def detrend_ts(self, method):
        """
        Remove the trend component from a time series.

        :param method:
            - Subtract the mean
            - Subtract the line of best fit from the time series, obtained from a linear regression model with
            the time steps as the predictor. For more complex trends, you may want to use quadratic terms (x^2) in the model.
            - Subtract the trend component obtained from time series decomposition we saw earlier.
            - Apply a filter like Baxter-King filter(statsmodels.tsa.filters.bkfilter) or the
            Hodrick-Prescott Filter (statsmodels.tsa.filters.hpfilter) to remove the moving average trend lines or the cyclical components.
        :return:
        """
        pass


if __name__ == '__main__':
    # with open('temp_prices.pkl', 'wb') as handle:
    #     data = YahooFinance(ticker='AAPL', period='YTD').convert_format('pandas')['Close']
    #     print(data)
    #     pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)

    with open('temp_prices.pkl', 'rb') as handle:
        data = pickle.load(handle)
        ts = TimeSeriesAnalysis(series=data)
        # print(ts.test_stationarity(test='adf'))
        print(ts.stationarize_ts(transform_fun=lambda x: np.diff(x, prepend=x[0]), test_tup=('pp', 0.05)))
