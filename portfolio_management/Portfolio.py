import math
import os
import re

import pandas as pd
import typing
import historical_data_collection.data_preparation_helpers as excel
import config
import numpy as np
from datetime import timedelta, datetime
from datetime import datetime
import config


class Trade:
    def __init__(self, stock: pd.Series, direction: bool, shares: int, date: datetime,
                 stop_loss: float = None, take_profit: float = None, commission: float = 5):
        self.stock = stock
        self.direction = direction
        self.shares = shares
        self.date = date
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.commission = commission


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
            if returns_freq is not None:
                returns_copy[-1].index = pd.DatetimeIndex(returns_copy[-1].index.values, freq=returns_freq)
            else:  # usually happens when weekend days are not in dataframe
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
            # case where it's a dataframe that was split in the previous loop, need
            # to go through all, l_ representing the length of that dataframe
            for l in range(1, l_ + 1):
                returns_copy[-l] = returns_copy[-l].asfreq(freq=returns_freq)
            if frequencies.index(returns_freq) > frequencies.index(cur_max_freq):
                cur_max_freq = returns_freq

        self.frequency = cur_max_freq
        merged_returns = pd.DataFrame()
        for retrn in returns_copy:
            f = retrn.index.freq
            if hasattr(f, 'name'):
                f = f.name
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

        merged_returns.dropna(how='all', inplace=True)
        self.df_returns = merged_returns

    freq_multipliers = {'D': {'Y': 252, 'M': 21, 'W': 5},
                        'W': {'Y': 52, 'M': 4},
                        'M': {'Y': 12},
                        'Y': 1}

    def set_frequency(self, frequency: str, inplace: bool = False):

        if self.frequency == frequency:
            return

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
    def __init__(self, assets, balance: float = 0, trades=None, date: datetime = datetime.now()):
        """

        :param assets:
        :param balance:
        :param trades:
        :param date:
        """
        if trades is None:
            trades = []

        super().__init__(assets)
        self.stocks = self.df_returns.columns
        self.balance = balance
        self.trades = trades
        self.float = float(balance)
        self.date = date
        self.last_rebalancing_day = date

    def rebalance_portfolio(self, long_stocks: pd.DataFrame, short_stocks: pd.DataFrame, weights, commission,
                            fractional_shares):
        '''
        Place Positions (Rebalance Portfolio)
        First sweep over the stocks already for which we need to sell some of its shares (entry short or exit long)
        (gives us capital to invest for the others). Second sweep is for buying
        :return:
        '''
        long_short = pd.concat([long_stocks, short_stocks], axis=1)
        float_before_trades = self.float
        for i in range(2):
            for stock, prices in long_short.iteritems():
                closing_price = prices.loc[self.date - timedelta(seconds=1)]  # TODO end of day or start?
                stock_is_in_portfolio = False

                for trade in self.trades:

                    # If the stock computed is already part of our portfolio, then:
                    if stock == trade.stock.name \
                            and ((stock in long_stocks.columns and trade.stock.name in long_stocks.columns)
                                 or (stock in short_stocks.columns and trade.stock.name in short_stocks.columns)):

                        stock_is_in_portfolio = True

                        # Aggregate total weight of asset in portfolio
                        current_weight_in_portfolio = 0
                        for trade in self.trades:
                            if stock == trade.stock.name:
                                current_weight_in_portfolio += trade.shares * closing_price / float_before_trades

                        # The weight we need to rebalance for
                        delta_weights = weights[stock] - current_weight_in_portfolio
                        delta_shares = (abs(delta_weights) * float_before_trades - commission) / closing_price

                        # for first sweep, target weight should less than current weight and original position is long
                        #  or vice versa for short (means we're selling)
                        # for second sweep, target weight should be more than current weight and original position is
                        # long or vice versa for short (means we're buying)

                        if delta_shares > 0:
                            if not fractional_shares:
                                delta_shares = math.floor(delta_shares)
                            if (i == 0 and ((delta_weights < 0 and trade.direction)
                                            or (delta_weights > 0 and not trade.direction))):
                                # we're exiting longs and entering shorts
                                trade = Trade(direction=True if stock in long_stocks.columns else False,
                                              stock=prices, shares=delta_shares, date=self.date)
                                self.make_position(trade, entry=False if stock in long_stocks.columns else True)
                                break
                            elif (i == 1 and ((delta_weights > 0 and trade.direction)
                                              or (delta_weights < 0 and not trade.direction))):
                                # we're entering longs and exiting shorts
                                trade = Trade(direction=True if stock in long_stocks.columns else False,
                                              stock=prices, shares=delta_shares, date=self.date)
                                self.make_position(trade, entry=True if stock in long_stocks.columns else False)
                                break

                # If the stock computed is not already part of our portfolio
                if not stock_is_in_portfolio:
                    shares_to_trade = (weights[stock] * float_before_trades - commission) / closing_price
                    if not fractional_shares:
                        shares_to_trade = math.floor(shares_to_trade)
                    if shares_to_trade > 0:
                        if i == 0 and stock in short_stocks.columns:  # entering shorts
                            trade = Trade(direction=False, stock=prices, shares=shares_to_trade, date=self.date)
                            self.make_position(trade, entry=True)
                        if i == 1 and stock in long_stocks.columns:  # entering longs
                            trade = Trade(direction=True, stock=prices, shares=shares_to_trade, date=self.date)
                            self.make_position(trade, entry=True)

    def make_position(self, trade: Trade, entry: bool):
        trade_closing_price = trade.stock[self.date - timedelta(seconds=1)]
        if not entry:  # if I am exiting a position

            shares_left = trade.shares
            for portfolio_trade in self.trades:
                if portfolio_trade.stock.name == trade.stock.name and trade.direction == portfolio_trade.direction:
                    # If the number of shares to exit is greater than the trade in the portfolio
                    # (total exit or simply partial exit with more shares than trade placed at such date)
                    if shares_left > portfolio_trade.shares:
                        self.trades.pop(self.trades.index(portfolio_trade))
                        shares_left -= portfolio_trade.shares
                    else:  # partial exit
                        portfolio_trade.shares -= shares_left
                        break
        else:
            if self.balance > trade_closing_price * trade.shares + trade.commission:
                self.trades.append(trade)
        # Now Adjust Balance: making a position should only affect the balance, not the float

        # if entering a long position or exiting a short position
        if (trade.direction and entry) or (not trade.direction and not entry):
            if self.balance > trade_closing_price * trade.shares + trade.commission:
                self.balance = self.balance - (trade_closing_price * trade.shares + trade.commission)
        # if exiting a long position or entering a short position
        elif (trade.direction and not entry) or (not trade.direction and entry):
            self.balance = self.balance + (trade_closing_price * trade.shares - trade.commission)
        else:
            return

    def get_volatility_returns(self, to_freq: str = 'Y'):
        return self.df_returns.std(axis=0) * np.sqrt(self.freq_multipliers[self.frequency[0]][to_freq])

    def get_weighted_volatility_returns(self, weights):
        return np.sqrt(np.dot(weights, np.dot(weights, self.get_covariance_matrix())))

    def get_covariance_matrix(self, to_freq: str = 'Y'):
        return self.df_returns.cov() * self.freq_multipliers[self.frequency[0]][to_freq]

    def get_mean_returns(self, to_freq: str = 'Y'):
        return self.df_returns.mean(axis=0) * self.freq_multipliers[self.frequency[0]][to_freq]

    def get_weighted_sum_returns(self, weights):
        return np.sum(weights * self.df_returns, axis=1)

    def get_weighted_mean_returns(self, weights):
        return np.dot(weights, self.get_mean_returns())

# if __name__ == '__main__':
#     path = "C:\\Users\\15148\\Desktop\\Movies"
#     files = os.listdir(path=path)
#     files.sort(key=lambda x: re.split(r'(\d+)', x))
#     print(files)
