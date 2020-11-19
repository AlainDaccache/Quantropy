import math
from abc import abstractmethod
from datetime import datetime, timedelta
from functools import partial

from scipy import stats
import typing
import portfolio_management.portfolio_simulator as simulator
import pandas as pd
import numpy as np

import fundamental_analysis.accounting_ratios as ratios
from historical_data_collection import data_preparation_helpers
from portfolio_management.portfolio_optimization import EquallyWeightedPortfolio


class MultiFactorStrategy(simulator.Strategy):
    def __init__(self, starting_date: datetime, ending_date: datetime, starting_capital: float,
                 securities_universe: typing.List[str], max_stocks_count_in_portfolio: int, net_exposure: tuple,
                 portfolio_allocation: typing.Callable, pre_filter_conditions, factors,
                 rebalancing_frequency):

        super().__init__(starting_date, ending_date, starting_capital, securities_universe,
                         max_stocks_count_in_portfolio, net_exposure, portfolio_allocation)
        self.pre_filter_conditions = pre_filter_conditions
        self.factors = factors
        self.rebalancing_frequency = rebalancing_frequency

    def is_time_to_reschedule(self, current_date, last_rebalancing_day):
        '''
        Returns
        :param current_date:
        :param last_rebalancing_day:
        :return:
        '''
        return (current_date - last_rebalancing_day).days >= self.rebalancing_frequency.value

    def generate_assets_to_trade(self, current_date):

        # we won't be using the short stocks, because they didn't pass condition
        long_stocks, _ = simulator.AssetSelectionStrategies(stocks=self.securities_universe,
                                                            date=current_date).stock_screening_filter(
            self.pre_filter_conditions)

        # Next step, compute factors for each factor category for each stock
        factors_dict = {
            (factor_type, factor.func.__name__): long_stocks.map(lambda stock: factor(stock, current_date))
            for factor_type, factor_list in self.factors.items()
            for factor in factor_list
        }

        factors_df = pd.DataFrame(data=list(factors_dict.values()),
                                  index=pd.MultiIndex.from_tuples(factors_dict.keys()),
                                  columns=long_stocks)
        print(factors_df.to_string())

        # Then, normalize each factor (compute Z-score i.e. (x - mu) / sigma)
        factors_df = factors_df.apply(stats.zscore, axis=1)
        factors_df = pd.DataFrame(factors_df.values.tolist(), index=factors_df.index, columns=long_stocks)

        # Then, add factors for each factor category for each company to make score for that company
        factors_df = factors_df.groupby(level=0, axis=0).agg(np.sum)
        print(factors_df.to_string())

        # Then, normalize again and sum across factor categories, and rank
        factors_df = factors_df.apply(stats.zscore, axis=1)
        factors_df = pd.DataFrame(factors_df.values.tolist(), index=factors_df.index, columns=long_stocks)
        factors_df = factors_df.apply(np.sum, axis=0)
        factors_df.sort_values(axis=0, ascending=False, inplace=True)
        print(factors_df.to_string())

        # Stocks to go long and/or short on
        if self.net_exposure[1] == 0:
            long_stocks, short_stocks = factors_df.index[:self.max_stocks_count_in_portfolio], []
        elif self.net_exposure[0] == 0:
            long_stocks, short_stocks = [], factors_df.index[-self.max_stocks_count_in_portfolio:]
        else:  # long and short
            long_stocks, short_stocks = factors_df.index[:math.floor(self.max_stocks_count_in_portfolio / 2)], \
                                        factors_df.index[-math.floor(self.max_stocks_count_in_portfolio / 2):]

        return list(long_stocks), list(short_stocks)


def FFCM_Smart_Beta_Strategy():
    '''

    https://www.ishares.com/us/strategies/smart-beta-investing
    :return:
    '''
    pass


if __name__ == '__main__':
    multi_factor = MultiFactorStrategy(starting_date=datetime.now() - timedelta(days=2 * 365),
                                       ending_date=datetime.now(),
                                       starting_capital=10000,
                                       securities_universe=data_preparation_helpers.get_stock_universe()[:4],
                                       max_stocks_count_in_portfolio=12,
                                       net_exposure=(100, 0),
                                       portfolio_allocation=EquallyWeightedPortfolio,
                                       pre_filter_conditions=[
                                           (partial(ratios.current_ratio, period='Q'), '>', 1)],
                                       factors={
                                           'Value': pd.Series(
                                               [partial(ratios.earnings_yield, period='Q'),
                                                partial(ratios.book_value_to_price_ratio, period='Q')]),
                                           'Quality': pd.Series(
                                               [partial(ratios.return_on_equity, period='Q')])},
                                       rebalancing_frequency=simulator.RebalancingFrequency.Quarterly
                                       )
    evolution_df = multi_factor.simulate_strategy()
