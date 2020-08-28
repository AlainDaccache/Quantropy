import numpy as np
import pandas as pd
import config
from historical_data_collection import excel_helpers


class MomentumFactors:
    def __init__(self, prices: pd.Series, frequency: str = 'Months', window_size: int = 12):
        '''
        :param prices:
        :param frequency: 'Daily', 'Weekly', 'Monthly', 'Yearly'
        :param window_size: the returns over how many periods (of frequency)
        '''
        self.prices = prices
        self.frequency_in_trading_days = 1 if frequency == 'Days' else 5 if frequency == 'Weeks' \
            else 21 if frequency == 'Months' else 252 if frequency == 'Years' else Exception
        self.lookback_idx = self.frequency_in_trading_days * window_size

    def traditional(self):
        '''
        The classical momentum would be one year percentage price change
        :return:
        '''
        return (prices[-1] - prices[-self.lookback_idx]) / prices[-self.lookback_idx]

    def less_last(self, less_last_window_size: int = 1):
        '''
        Improvement: the last month price change was removed from the computation
        less_last_window_size
        :return:
        '''
        less_last_indx = self.frequency_in_trading_days * less_last_window_size
        return (prices[-less_last_indx] - prices[-self.lookback_idx]) / prices[-self.lookback_idx]

    def mean_reverting(self, less_last_window_size: int = 1):
        '''
        Improvement: they subtracted the last month price change from the annual momentum, as they also discovered that the stocks are actually mean reverting in the last month
        less_last_window_size
        :return:
        '''
        less_last_indx = self.frequency_in_trading_days * less_last_window_size
        return (prices[-less_last_indx] - prices[-self.lookback_idx]) \
               / prices[-self.lookback_idx] - (prices[-1] - prices[-less_last_indx]) \
               / prices[-less_last_indx]

    def with_volatility(self, less_last_window_size: int = 1):
        '''
        Improvement: they also found out that stocks that have lower volatility perform better than stocks with high volatility
        :param less_last_window_size:
        :return:
        '''
        volatility = np.nanstd(prices.pct_change(), axis=0) * np.sqrt(self.frequency_in_trading_days)
        return self.mean_reverting(less_last_window_size=less_last_window_size) / volatility


if __name__ == '__main__':
    stock = 'AAPL'
    prices = excel_helpers.read_df_from_csv('{}/{}.xlsx'.format(config.STOCK_PRICES_DIR_PATH, stock))['Adj Close']
    # One year percentage price change
    momo_1_a = MomentumFactors(prices=prices, frequency='Years', window_size=1).traditional()
    # Six months percentage price change
    momo_1_b = MomentumFactors(prices=prices, frequency='Months', window_size=6).traditional()
    # One year minus Two month
    momo_2_a = MomentumFactors(prices=prices, frequency='Months', window_size=12).less_last(less_last_window_size=2)
    # Same but Mean Reverting
    momo_3 = MomentumFactors(prices=prices, frequency='Months', window_size=12).mean_reverting(less_last_window_size=2)
    # Same but with volatility
    momo_4 = MomentumFactors(prices=prices, frequency='Months', window_size=12).with_volatility(less_last_window_size=2)
