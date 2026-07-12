import numpy as np
from statsmodels.regression.linear_model import OLS
import statsmodels.api as sm
import matplotlib.pyplot as plt
import historical_data_collection.data_preparation_helpers as excel
import config
import pandas as pd
from datetime import timedelta

from matilda.portfolio_management.portfolio_simulator import Strategy


class MeanReversionStrategy(Strategy):
    def generate_assets_to_trade(self, current_date):
        pass


def get_rolling_mean(self, time_series, lookback=timedelta(days=365), describe=False):
    """

    :param self:
    :param time_series:
    :param lookback:
    :param describe:
    :return:
    """
    rolling_mean = time_series.rolling(window=lookback).mean()
    if describe:
        plt.plot(time_series)
        plt.plot(rolling_mean, 'r', alpha=0.9)
        plt.ylabel('Price')
        plt.legend(['Time Series', 'Moving Average'])
        plt.show()
    return rolling_mean


def get_best_fit_line(self, time_series, lookback=timedelta(days=365), describe=False):
    """

    :param self:
    :param time_series:
    :param lookback:
    :param describe:
    :return:
    """
    # Crop series according to lookback
    idx = excel.get_date_index(date=time_series.index[-1] - lookback, dates_values=time_series.index)
    time_series = time_series[idx:]
    X = np.arange(len(time_series.index))
    x = sm.add_constant(X)  # Add a column of ones so that line can have a y-intercept
    model = OLS(time_series, x).fit()
    a, b = model.params[0], model.params[1]
    line = pd.Series(X * b + a)
    line.index = time_series.index
    if describe:
        plt.plot(time_series)
        plt.plot(line, 'r', alpha=0.9)
        plt.ylabel('Price')
        plt.legend(['Time Series', 'Trendline'])
        plt.show()
    return line


def normalize(time_series, against=None):
    """

    :param time_series:
    :param against: Its mean, its regression...
    :return:
    """
    return (time_series - against) / time_series.std()


class MeanReversion:
    pass


class SingleStockMeanReversion(MeanReversion):
    pass


class PairsTrading(MeanReversion):
    pass


if __name__ == '__main__':
    ticker = 'AAPL'
    time_series = excel.read_df_from_csv('{}/{}.xlsx'.format(config.STOCK_PRICES_DIR_PATH, ticker))['Adj Close']
    find_rolling_mean(time_series, describe=True)
