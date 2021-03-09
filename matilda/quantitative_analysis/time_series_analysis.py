import numpy as np
from numpy.random import randn
import pandas as pd
import statsmodels.tsa.stattools as ts


class TimeSeriesBehavior:
    """
    This class provides functions to determine the behavior of a time series,
    specifically whether it is
        - A random walk. It has no memory. Examples: Brownian motion
        - A mean reverting series. Examples: Ornstein-Uhlenbeck process
        - A trending series
    """

    def __init__(self, time_series: pd.Series):
        self.time_series = time_series

    def augmented_dickey_fuller_test(self, max_lag: int = 1, pvalue_thresh: float = 0.05):
        """

        Null Hypothesis: The time series is not mean reverting

        :param max_lag:
        :param p_value_thresh:
        :return: True if time series is mean reverting, False if not
        """
        adfstat, pvalue, usedlag, nobs, critvalues = ts.adfuller(self.time_series, maxlag=max_lag)
        return pvalue < pvalue_thresh \
               and (adfstat < critvalues[0] and adfstat < critvalues[1] and adfstat < critvalues[2])

    def johansen_test(self, p_value_thresh: float = 0.95):
        pass

    def hurst_exponent(self, lag_range: tuple = (2, 100)):
        """
        Calculates the stationarity of the series. A time series (or stochastic process) is defined to be strongly
        stationary if its joint probability distribution is invariant under translations in time or space.
        In particular, and of key importance for traders, the mean and variance of the process do not change over time
        or space and they each do not follow a trend.

        A critical feature of stationary price series is that the prices within the series diffuse from their initial
        value at a rate slower than that of a Geometric Brownian Motion. By measuring the rate of this diffusive
        behaviour we can identify the nature of the time series.

        The Hurst Exponent tells you whether a series is
            * Geometric random walk (H=0.5)
            * Mean-reverting series (H<0.5)
            * Trending Series (H>0.5)

        Category: Measure of Autocorrelation

        :return:
        """

        lags = range(lag_range[0], lag_range[1])  # Create the range of lag values
        # Calculate the array of the variances of the lagged differences
        tau = [np.sqrt(np.std(np.subtract(self.time_series[lag:], self.time_series[:-lag]))) for lag in lags]
        poly = np.polyfit(np.log(lags), np.log(tau), 1)  # Use a linear fit to estimate the Hurst Exponent
        return poly[0] * 2.0  # Return the Hurst exponent from the polyfit output


if __name__ == '__main__':
    geometric_brownian_motion = np.log(np.cumsum(randn(100000)) + 1000)
    mean_reverting_series = np.log(randn(100000) + 1000)
    trending_series = np.log(np.cumsum(randn(100000) + 1) + 1000)
