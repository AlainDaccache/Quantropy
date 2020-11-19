import abc
import math
from datetime import datetime, timedelta
import typing
from functools import partial
import pandas as pd
import numpy as np
from abc import abstractmethod
import historical_data_collection.data_preparation_helpers as excel
import config
import matplotlib.pyplot as plt
import seaborn
from statsmodels.tsa.stattools import coint
from enum import Enum

plt.style.use('fivethirtyeight')


# TODO: Add statistics i.e. average drawdown, alpha, beta/sharpe/sortino...
# TODO: Functionality for reinvesting dividends
# TODO: Functionality for stock screening
# TODO: Functionality for technical indicators
# TODO: Functionality for commission (as percent of trade or fix cost)
# TODO: Functionality for slippage (do one day slippage)
# TODO: Functionality for fractional shares (optional)

class Stock:

    def __init__(self, ticker: str):
        self.ticker = ticker
        self.price_data = excel.read_df_from_csv('{}/{}.xlsx'.format(config.STOCK_PRICES_DIR_PATH, self.ticker))
        self.price_date_idx = 0
        self.current_price = 0


class Trade:
    def __init__(self, stock: Stock, direction: bool, shares: int, date: datetime,
                 stop_loss: float = None, take_profit: float = None, commission: float = 5):
        self.stock = stock
        self.direction = direction
        self.shares = shares
        self.date = date
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.commission = commission


class Portfolio:
    def __init__(self, balance: float, trades: list, date: datetime):
        self.balance = balance
        self.trades = trades
        self.float = float(balance)
        self.date = date
        self.last_rebalancing_day = date

    def rebalance_portfolio(self, stocks_to_trade, weights, commission, fractional_shares):
        '''
        Place Positions (Rebalance Portfolio)
        First sweep over the stocks already for which we need to sell some of its shares (entry short or exit long)
        (gives us capital to invest for the others). Second sweep is for buying
        :return:
        '''
        long_stocks, short_stocks = stocks_to_trade
        for i in range(2):

            for stock in long_stocks + short_stocks:
                stock_is_in_portfolio = False

                for trade in self.trades:

                    # If the stock computed is already part of our portfolio, then:
                    if stock.ticker == trade.stock.ticker \
                            and ((stock.ticker in long_stocks and trade.stock.ticker in long_stocks)
                                 or (stock.ticker in short_stocks and trade.stock.ticker in short_stocks)):

                        stock_is_in_portfolio = True

                        # Aggregate total weight of asset in portfolio
                        current_weight_in_portfolio = 0
                        for trade in self.trades:
                            if stock.ticker == trade.stock.ticker:
                                current_weight_in_portfolio += trade.shares * trade.stock.current_price \
                                                               / self.float

                        # The weight we need to rebalance for
                        delta_weights = weights[stock.ticker] - current_weight_in_portfolio
                        delta_shares = (abs(delta_weights) * self.float - commission) / stock.current_price

                        # for first sweep, target weight should less than current weight and original position is long
                        #  or vice versa for short (means we're selling)
                        # for second sweep, target weight should be more than current weight and original position is long
                        # or vice versa for short (means we're buying)

                        if delta_shares > 0 and \
                                (i == 0 and ((delta_weights < 0 and trade.direction)
                                             or (delta_weights > 0 and not trade.direction))
                                 or (i == 1 and ((delta_weights > 0 and trade.direction)
                                                 or (delta_weights < 0 and not trade.direction)))):
                            if not fractional_shares:
                                delta_shares = math.floor(delta_shares)
                            if delta_shares > 0:
                                trade = Trade(direction=True if stock.ticker in long_stocks else False,
                                              stock=stock, shares=delta_shares, date=self.date)
                                # we're exiting longs and entering shorts
                                self.make_position(trade, entry=False if stock.ticker in long_stocks else True)
                                break

                # If the stock computed is not already part of our portfolio
                if not stock_is_in_portfolio:
                    shares_to_trade = (weights[stock.ticker] * self.float - commission) \
                                      / stock.current_price
                    if not fractional_shares:
                        shares_to_trade = math.floor(shares_to_trade)
                    if shares_to_trade > 0:
                        if i == 0 and stock.ticker in short_stocks:  # entering shorts
                            trade = Trade(direction=False, stock=stock, shares=shares_to_trade, date=self.date)
                            self.make_position(trade, entry=True)
                        if i == 1 and stock.ticker in long_stocks:  # entering longs
                            trade = Trade(direction=True, stock=stock, shares=shares_to_trade, date=self.date)
                            self.make_position(trade, entry=True)

    def make_position(self, trade: Trade, entry: bool):

        if not entry:  # if I am exiting a position

            shares_left = trade.shares
            for portfolio_trade in self.trades:
                if portfolio_trade.stock.ticker == trade.stock.ticker and trade.direction == portfolio_trade.direction:
                    # If the number of shares to exit is greater than the trade in the portfolio
                    # (total exit or simply partial exit with more shares than trade placed at such date)
                    if shares_left > portfolio_trade.shares:
                        self.trades.pop(self.trades.index(portfolio_trade))
                        shares_left -= portfolio_trade.shares
                    else:  # partial exit
                        portfolio_trade.shares -= shares_left
                        break
        else:
            if self.balance > trade.stock.current_price * trade.shares + trade.commission:
                self.trades.append(trade)
        # Now Adjust Balance: making a position should only affect the balance, not the float

        # if entering a long position or exiting a short position
        if (trade.direction and entry) or (not trade.direction and not entry):
            if self.balance > trade.stock.current_price * trade.shares + trade.commission:
                self.balance = self.balance - (trade.stock.current_price * trade.shares + trade.commission)
        # if exiting a long position or entering a short position
        elif (trade.direction and not entry) or (not trade.direction and entry):
            self.balance = self.balance + (trade.stock.current_price * trade.shares - trade.commission)
        else:
            return


def populate_stock_universe(securities_universe: typing.List[str]):
    securities_universe_objects = pd.Series()
    for ticker in securities_universe:
        securities_universe_objects[ticker] = Stock(ticker)
    return securities_universe_objects


class RebalancingFrequency(Enum):
    Daily = 1
    Weekly = 5
    Monthly = 21
    Quarterly = 63
    Semiannually = 126
    Annually = 252


class Strategy(metaclass=abc.ABCMeta):

    def __init__(self, starting_date: datetime, ending_date: datetime,
                 starting_capital: float, securities_universe: typing.List[str], max_stocks_count_in_portfolio: int,
                 net_exposure: tuple,
                 portfolio_allocation, maximum_leverage: float = 1.0,
                 reinvest_dividends: bool = False, fractional_shares: bool = False,
                 include_slippage: bool = False, include_capital_gains_tax: bool = False, commission: int = 2):

        """

        :param starting_date:
        :param ending_date:
        :param starting_capital:
        :param securities_universe:
        :param max_stocks_count_in_portfolio:
        :param net_exposure: tuple that represents (long_percent, short_percent)
            * (0.5, 0.5) is Dollar Neutral Strategy
            * (1.3, 0.3) is 130-30 Strategy
        :param portfolio_allocation:
        :param maximum_leverage:
        :param reinvest_dividends:
        :param fractional_shares:
        :param include_slippage:
        :param include_capital_gains_tax:
        :param commission:
        """
        self.starting_date = starting_date
        self.ending_date = ending_date
        self.starting_capital = starting_capital
        self.securities_universe = populate_stock_universe(securities_universe)
        self.max_stocks_count_in_portfolio = max_stocks_count_in_portfolio
        self.net_exposure = net_exposure
        self.portfolio_allocation = portfolio_allocation
        self.maximum_leverage = maximum_leverage
        self.reinvest_dividends = reinvest_dividends
        self.fractional_shares = fractional_shares
        self.include_slippage = include_slippage
        self.include_capital_gains_tax = include_capital_gains_tax
        self.commission = commission

    @abstractmethod
    def generate_assets_to_trade(self, current_date):
        pass

    @abstractmethod
    def is_time_to_reschedule(self, current_date, last_rebalancing_day):
        pass

    def simulate_strategy(self):
        results = []
        portfolio = Portfolio(balance=self.starting_capital, trades=[], date=self.starting_date)

        for date in pd.date_range(start=self.starting_date, end=self.ending_date):
            try:
                portfolio.date = date
                # stocks in portfolio: list(set([x.stock for x in portfolio.trades]))
                for stock in self.securities_universe:  # update current prices according to date
                    date_index = excel.get_date_index(date, stock.price_data['Adj Close'].index)
                    stock.current_price = stock.price_data['Adj Close'].iloc[date_index]
                    stock.price_date_idx = date_index

                for trade in portfolio.trades:  # update portfolio float
                    daily_pct_return = trade.stock.price_data['Pct Change'].iloc[trade.stock.price_date_idx]
                    daily_doll_return = daily_pct_return * trade.stock.current_price * trade.shares
                    portfolio.float = portfolio.float + daily_doll_return if trade.direction else portfolio.float - daily_doll_return

                if not self.is_time_to_reschedule(current_date=date,
                                                  last_rebalancing_day=portfolio.last_rebalancing_day):
                    continue

                portfolio.last_rebalancing_day = date  # rebalancing day, now can go on:

                stocks_to_trade = self.generate_assets_to_trade(portfolio.date)

                long_stocks, short_stocks = stocks_to_trade
                for trade in portfolio.trades:  # close portfolio trades that no longer meet condition
                    if trade.stock.ticker not in stocks_to_trade:
                        portfolio.make_position(trade, entry=False)

                # Close positions for stocks that are in neither long and short:
                for trade in portfolio.trades:
                    if trade.stock.ticker not in stocks_to_trade:
                        portfolio.make_position(trade, entry=False)

                # Get portfolio returns of selected stocks up to current date, and optimize portfolio allocation
                portfolio_returns = pd.Series()
                stock_objects = ([], [])
                for stock_ticker in stocks_to_trade[0]:
                    stock = self.securities_universe[stock_ticker]
                    stock_objects[0].append(stock)
                    portfolio_returns[stock.ticker] = stock.price_data['Pct Change'].iloc[:stock.price_date_idx]

                for stock_ticker in stocks_to_trade[1]:
                    stock = self.securities_universe[stock_ticker]
                    stock_objects[1].append(stock)
                    portfolio_returns[stock.ticker] = stock.price_data['Pct Change'].iloc[:stock.price_date_idx]

                weights = self.portfolio_allocation(portfolio_returns=portfolio_returns).solve_weights()

                portfolio.rebalance_portfolio(stock_objects, weights, self.commission, self.fractional_shares)

            finally:
                # that's to aggregate trades for better formatting in the dataframe
                dictionary = dict()
                for trade in portfolio.trades:
                    dictionary[trade.stock.ticker] = dictionary.get(trade.stock.ticker, 0) + trade.shares

                aggregated_trades = [(key, val) for (key, val) in dictionary.items()]
                results.append([date.strftime("%Y-%m-%d"),
                                aggregated_trades,
                                round(portfolio.balance, 2),
                                round(portfolio.float, 2)])

        evolution_df = pd.DataFrame(results, columns=['Date', 'Holdings', 'Balance', 'Float'])
        evolution_df.set_index('Date', inplace=True)
        evolution_df['Cumulative (%) Return'] = evolution_df.filter(['Float']).pct_change().apply(
            lambda x: x + 1).cumprod()
        evolution_df['Cumulative (%) Return'].plot(grid=True, figsize=(10, 6))
        plt.show()
        with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            print(evolution_df.to_string())
        return evolution_df


class StockMarketIndices:

    def sp500_index(self, date, top=500):
        '''

        :param top: Top by default 500, but other indices exist such as S&P 100 (so top=100)
        :param date:
        :return:
        '''
        pass

    def russell3000_index(self, date, top=3000):
        pass

    def djia30_index(self, date, top=30):
        pass


"""
def sort_df(df, column_idx, key):
    '''Takes dataframe, column index and custom function for sorting,
    returns dataframe sorted by this column using this function'''
    
    col = df.iloc[:,column_idx]
    temp = np.array(col.values.tolist())
    order = sorted(range(len(temp)), key=lambda j: key(temp[j]))
    return df.iloc[order]
"""

if __name__ == '__main__':
    stocks = pd.Series()
    for ticker in ['AAPL', 'FB', 'GOOG', 'MSFT']:
        stocks[ticker] = Stock(ticker)
    pairs_trading = AssetSelectionStrategies(date=datetime.today(), stocks=stocks).split_based_on_pairs()
