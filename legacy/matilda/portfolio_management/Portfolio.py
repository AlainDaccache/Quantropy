import math
import pandas as pd
import numpy as np
from datetime import timedelta
from datetime import datetime

from matilda.data_pipeline.TimeDataFrame import TimeDataFrame


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
