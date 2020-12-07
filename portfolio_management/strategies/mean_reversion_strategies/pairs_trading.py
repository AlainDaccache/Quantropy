import typing
from abc import abstractmethod

from portfolio_management.strategies.mean_reversion_strategies.single_stock_mean_reversion import MeanReversionStrategy
import matplotlib.pyplot as plt
import seaborn
import pandas as pd
import numpy as np


class PairsTrading(MeanReversionStrategy):
    @abstractmethod
    def test_pair(self, stock_1, stock_2, stationarity_stat, cointegration_stat, p_value_threshold: float = 0.05):
        '''

        :param stock_1:
        :param stock_2:
        :param stationarity_stat: 'DFT' for Dickey-Fuller Test, 'ADFT' for Augmented Dickey-Fuller Test, 'OLS' to test for residuals in regression, 'PPT' for Phillips-Perron Test
        :param cointegration_stat:
            * For cointegration: 'Johansen', 'Engle-Granger', and 'Phillips-Ouliaris'
            * For correlation: 'Pearson', 'Kendall', 'Spearman'
        :return: True or False
        '''

        # First, test for a unit root in each
        if stationarity_stat == 'OLS':
            pass
        elif stationarity_stat == 'DFT':
            pass
        elif stationarity_stat == 'ADFT':
            pass
        elif stationarity_stat == 'PPT':
            pass
        else:
            raise Exception

        if cointegration_stat == 'corr':
            pass
        elif cointegration_stat == 'coint':
            pass

    @abstractmethod
    def compute_threshold(self):
        pass

    @abstractmethod
    def compute_hedge_ratio(self):
        pass

    def generate_assets_to_trade(self, current_date):
        pass

    def is_time_to_reschedule(self, current_date, last_rebalancing_day):
        pass

    def split_based_on_pairs(self, compute_z_score_thresh: typing.Callable,
                             stat, z_score_ma=None):
        '''

        :param compute_z_score_thresh:
        :param p_value_thresh:
        :param z_score_ma:
        :return:
        '''
        pairs = []  # list of (long, short) tuples
        data = pd.Series()
        for stock in self.stocks:
            data[stock.ticker] = stock.price_data['Adj Close'][-1000:]  # fix

        n, keys, prelim_pairs = len(data), data.keys(), []
        score_matrix, pvalue_matrix = np.zeros((n, n)), np.ones((n, n))

        for i in range(n):
            for j in range(i + 1, n):
                t_stat, p_value, crit_value = stat(data[keys[i]], data[keys[j]])
                score_matrix[i, j], pvalue_matrix[i, j] = t_stat, p_value
                if p_value < p_value_thresh:
                    prelim_pairs.append((keys[i], keys[j]))

        seaborn.heatmap(pvalue_matrix, xticklabels=data.index, yticklabels=data.index,
                        cmap='plasma', mask=(pvalue_matrix >= p_value_thresh))
        plt.show()
        for pair in prelim_pairs:
            spread = data[pair[0]] - data[pair[1]]
            spread.plot(label='Spread')
            plt.axhline(spread.mean(), c='r')
            plt.show()
            if z_score_ma is not None:
                z_score = (spread - spread.rolling(z_score_ma).mean()) / spread.rolling(z_score_ma).std()
            else:
                z_score = (spread - spread.mean()) / spread.std()
            z_score.plot()

            z_score_thresh = compute_z_score_thresh(z_score)
            if z_score[-1] > z_score_thresh:
                pairs.append((pair[1], pair[0]))
            elif z_score[-1] < z_score_thresh:
                pairs.append((pair[0], pair[1]))

        return longs, shorts

    # def generate_assets_to_trade(self, current_date):
    #     return AssetSelectionStrategies(stocks=self.securities_universe, date=current_date) \
    #         .split_based_on_pairs(compute_z_score_thresh=lambda zscore: 3)


class LTCM_Delta_Hedging_Strategy(PairsTrading):
    '''

    https://www.bauer.uh.edu/rsusmel/7386/ltcm-2.htm#:~:text=LTCM's%20main%20strategy%20was%20to,positions%20in%20the%20rich%20ones.&text=Long%20positions%20in%20emerging%20markets%20sovereigns%2C%20hedged%20back%20to%20dollars.
    :return:
    '''
    pass
