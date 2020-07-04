import math
from datetime import datetime, timedelta
import company_analysis.fundamental_analysis.financial_statements_entries as fi
import pandas as pd
from abc import ABC, abstractmethod
import data_scraping.excel_helpers as excel
import config
from functools import partial
from pandas.util.testing import assert_frame_equal

# TODO: Build dataframe tracking everyday portfolio holdings
# TODO: Add statistics i.e. average drawdown, alpha, beta/sharpe/sortino...
# TODO: Functionality for reinvesting dividends

def rsi(x, date):
    df = excel.read_df_from_csv(x, config.technical_indicators_name)
    return df['momentum_rsi'].loc[date]


def cci(x, date):
    df = excel.read_df_from_csv(x, config.technical_indicators_name)
    return df['trend_cci'].loc[date]


class Stock:

    def __init__(self, ticker: str):
        self.ticker = ticker
        self.price_data = excel.read_df_from_csv(self.ticker, config.stock_prices_sheet_name)


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
    def __init__(self, balance: float, trades: list):
        self.balance = balance
        self.trades = trades
        self.float = balance
        self.date = 0


class MovingAverage:
    def sma_current(self, data):
        if len(data) < self.window:
            return None
        return sum(data[-self.window:]) / float(self.window)

    def ema_current(self, data):
        if len(data) < 2 * self.window:
            return None
        c = 2.0 / (self.window + 1)
        current_ema = self.sma_current(data[-self.window*2:-self.window])
        for value in data[-self.window:]:
            current_ema = (c * value) + ((1 - c) * current_ema)
        return current_ema

    def all_series_ma(self):
        output = pd.Series()
        for index, date in enumerate(self.time_series.index):
            if self.ma_type == 'sma':
                output[date] = self.sma_current(self.time_series[:index])
            elif self.ma_type == 'ema':
                output[date] = self.ema_current(self.time_series[:index])
        return output

    def __init__(self, window: int, ma_type: str, time_series: pd.Series(dtype='float64') = pd.Series(dtype='float64'), shift: int = 0):
        self.window = window
        self.ma_type = ma_type
        self.shift = shift
        self.time_series = time_series
        self.moving_average = pd.Series(dtype='float64')

    def update_time_series(self, latest: float):
        self.time_series.append(latest)
        latest_ma = self.sma_current(self.time_series) if self.ma_type == 'sma' else self.ema_current(self.time_series)
        self.moving_average.append(latest_ma)


class Strategy(ABC):

    def __init__(self):
        super().__init__()

    @abstractmethod
    def long_entry_condition(self):
        pass

    @abstractmethod
    def long_exit_condition(self):
        pass

    @abstractmethod
    def short_entry_condition(self):
        pass

    @abstractmethod
    def short_exit_condition(self):
        pass

    @abstractmethod
    def weight_of_portfolio_for_trade(self):
        pass


class MovingAverageCrossover(Strategy):
    def __init__(self, short_term_moving_average: MovingAverage, long_term_moving_average: MovingAverage):
        super().__init__()
        self.short_term_moving_average = short_term_moving_average
        self.long_term_moving_average = long_term_moving_average

    def long_entry_condition(self):
        return self.short_term_moving_average.moving_average[-1] > self.long_term_moving_average.moving_average[-1]

    def long_exit_condition(self):
        return self.short_term_moving_average.moving_average[-1] < self.long_term_moving_average.moving_average[-1]

    def short_entry_condition(self):
        return self.short_term_moving_average.moving_average[-1] < self.long_term_moving_average.moving_average[-1]

    def short_exit_condition(self):
        return self.short_term_moving_average.moving_average[-1] > self.long_term_moving_average.moving_average[-1]

    def weight_of_portfolio_for_trade(self):
        return 0.1


def round_shares_from_portfolio_weight(stock_price, weight, balance):
    return math.floor(weight * balance / stock_price)


def make_position(portfolio: Portfolio, trade: Trade, entry: bool):
    # if entering a long position or exiting a short position, then subtract from account
    if (trade.direction and entry) or (not trade.direction and not entry):
        portfolio.balance -= (trade.stock.price_data['Adj Close'].loc[portfolio.date] * trade.shares + trade.commission)
    else:
        portfolio.balance += (trade.stock.price_data['Adj Close'].loc[portfolio.date] * trade.shares + trade.commission)


class Simulation:
    def __init__(self, balance, trading_strategy: Strategy,
                 start_date: datetime = datetime(2000, 1, 1),
                 end_date: datetime = datetime.now(), commission: float = 5):
        self.trading_strategy = trading_strategy
        self.start_date = start_date
        self.end_date = end_date
        self.commission = commission
        self.portfolio = Portfolio(balance, [])
        self.stock_universe = pd.Series(dtype='float64')


    def portfolio_periodic_return(self):
        pass

    def portfolio_cumulative_return(self):
        pass

    def simulate(self):

        # populate stock universe
        for ticker in excel.get_stock_universe()[:1]:
            stock_obj = Stock(ticker)
            self.stock_universe[stock_obj.ticker] = stock_obj

        for date in pd.date_range(start=self.start_date, end=self.end_date):
            self.portfolio.date = date

            # get stocks from portfolio
            stocks_in_portfolio = list(set([x.stock for x in self.portfolio.trades]))

            for stock in self.stock_universe:
                if date not in stock.price_data['Adj Close'].index:
                    continue
                # get current (date simulated) price from csv file which contains all prices
                else:
                    stock.current_price = stock.price_data['Adj Close'].loc[date]

            # update portfolio float
            for trade in self.portfolio.trades:
                if date not in trade.stock.price_data['Adj Close'].index:
                    continue
                else:
                    daily_return = trade.stock.price_data['pct_change'].loc[date]
                    if trade.direction: # if going long
                        self.portfolio.float += daily_return * trade.shares
                    else:
                        self.portfolio.float -= daily_return * trade.shares

            for stock in self.stock_universe:

                if date not in stock.price_data['Adj Close'].index:
                    continue

                if self.trading_strategy.long_entry_condition()(stock.ticker, date) and stock not in stocks_in_portfolio:
                    trade = Trade(stock=stock,
                                  direction=True,
                                  shares=round_shares_from_portfolio_weight(stock.price_data['Adj Close'].loc[date],
                                                                            self.trading_strategy.weight_of_portfolio_for_trade(),
                                                                            self.portfolio.balance),
                                  date=date)
                    if self.portfolio.balance > trade.commission + (trade.shares * trade.stock.price_data['Adj Close'].loc[date]):
                        self.portfolio.trades.append(trade)
                        make_position(self.portfolio, trade, entry=True)

                elif self.trading_strategy.short_entry_condition()(stock.ticker, date) and stock not in stocks_in_portfolio:
                    trade = Trade(stock=stock,
                                  direction=False,
                                  shares=round_shares_from_portfolio_weight(stock.price_data['Adj Close'].loc[date],
                                                                            self.trading_strategy.weight_of_portfolio_for_trade(),
                                                                            self.portfolio.balance),
                                  date=date)
                    if self.portfolio.balance > trade.commission + (trade.shares * trade.stock.price_data['Adj Close'].loc[date]):
                        self.portfolio.trades.append(trade)
                        make_position(self.portfolio, trade, entry=True)

            for trade in self.portfolio.trades:
                if self.trading_strategy.long_exit_condition()(trade.stock.ticker, date):
                    self.portfolio.trades.pop(self.portfolio.trades.index(trade))
                    make_position(self.portfolio, trade, entry=False)
                elif self.trading_strategy.short_exit_condition()(trade.stock.ticker, date):
                    self.portfolio.trades.pop(self.portfolio.trades.index(trade))
                    make_position(self.portfolio, trade, entry=False)


def helper_condition(indicator, comparator, otherside):
    if callable(otherside):
        return lambda x, date: compare(indicator(x, date), comparator, otherside(x, date))
    else:
        return lambda x, date: compare(indicator(x, date), comparator, otherside)


class UserStrategy(Strategy):
    def __init__(self):
        super().__init__()

    def long_entry_condition(self):
        return helper_condition(rsi, '>', 40) and helper_condition(cci, '>', 50)

    def long_exit_condition(self):
        return helper_condition(rsi, '<', 40) and helper_condition(cci, '<', 50)

    def short_entry_condition(self):
        return helper_condition(rsi, '<', 40) and helper_condition(cci, '<', 50)

    def short_exit_condition(self):
        return helper_condition(rsi, '>', 40) and helper_condition(cci, '>', 50)

    def weight_of_portfolio_for_trade(self):
        return 0.1


'''Helpers'''
def compare(x, comparator, y):
    if comparator == '>':
        return x > y
    elif comparator == '<':
        return x < y
    elif comparator == '=':
        return x == y

if __name__ == '__main__':
    Simulation(10000, UserStrategy()).simulate()
# apple = Stock('AAPL')
# trade = Trade(apple, True, 100, datetime.now())
# portfolio = Portfolio(10000, [trade])
# moving_average_1 = MovingAverage(window=50, ma_type='sma', shift=0)
# moving_average_2 = MovingAverage(window=100, ma_type='sma', shift=0)
# moving_average_crossover = MovingAverageCrossover(moving_average_1, moving_average_2)
# Simulation(0, moving_average_crossover).simulate()