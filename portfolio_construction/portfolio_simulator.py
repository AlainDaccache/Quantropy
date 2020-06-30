import math
from datetime import datetime, timedelta
import company_analysis.fundamental_analysis.financial_statements_entries as fi
import pandas as pd
from abc import ABC, abstractmethod
import data_scraping.excel_helpers as excel
import config
from functools import partial


class Stock:
    current_price = 0
    current_dividend = 0

    def __init__(self, ticker: str):
        self.ticker = ticker
        self.price_data = excel.read_df_from_csv(self.ticker, config.stock_prices_sheet_name)['Adj Close']
        self.dividend_data = pd.Series()  # how to enforce datetime type?
        for date in [datetime.today() - timedelta(days=x) for x in range(1000)]:
            self.dividend_data[date] = fi.preferred_dividends(self.ticker, date, annual=True)


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

    def __init__(self, window: int, ma_type: str, time_series: pd.Series() = pd.Series(), shift: int = 0):
        self.window = window
        self.ma_type = ma_type
        self.shift = shift
        self.time_series = time_series
        self.moving_average = pd.Series()


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
        self.short_term_moving_average = short_term_moving_average.moving_average
        self.long_term_moving_average = long_term_moving_average.moving_average

    def long_entry_condition(self):
        return self.short_term_moving_average[-1] > self.long_term_moving_average[-1]

    def long_exit_condition(self):
        return self.short_term_moving_average[-1] < self.long_term_moving_average[-1]

    def short_entry_condition(self):
        return self.short_term_moving_average[-1] < self.long_term_moving_average[-1]

    def short_exit_condition(self):
        return self.short_term_moving_average > self.long_term_moving_average

    def weight_of_portfolio_for_trade(self):
        return 0.1


def round_shares_from_portfolio_weight(stock, weight, balance):
    return math.floor(weight * balance / stock.current_price)


def make_position(portfolio: Portfolio, trade: Trade):
    if trade.direction:  # if True, then going long
        portfolio.balance -= (trade.stock.current_price * trade.shares + trade.commission)
        portfolio.float -= (trade.stock.current_price * trade.shares + trade.commission)
    else:  # else, going short
        portfolio.balance += (trade.stock.current_price * trade.shares + trade.commission)
        portfolio.float += (trade.stock.current_price * trade.shares + trade.commission)


def open_position(portfolio: Portfolio, trade: Trade):
    portfolio.trades.append(trade)
    make_position(portfolio, trade)


def close_position(portfolio: Portfolio, trade: Trade):
    portfolio.trades.pop(portfolio.trades.index(trade))
    make_position(portfolio, trade)


def get_stock_universe():
    stock_universe = []
    import os
    directory = config.financial_statements_folder_path
    for root, dirs, files in os.walk(directory):
        for file in files:
            ticker = os.path.splitext(file)[0]
            stock_universe.append(Stock(ticker))
    return stock_universe  # this is our stock universe


class Simulation:
    def __init__(self, initial_balance, trading_strategy: Strategy,
                 start_date: datetime = datetime(2000, 1, 1),
                 end_date: datetime = datetime.now(), commission: float = 5):
        self.trading_strategy = trading_strategy
        self.start_date = start_date
        self.end_date = end_date
        self.commission = commission
        self.portfolio = Portfolio(initial_balance, [])
        self.stock_universe = get_stock_universe()

    def update_from_last_day(self, date):

        for stock in self.stock_universe:  # update stock prices from yesterday to today
            all_dates = stock.price_data.index
            date_index = next((index for (index, item) in enumerate(all_dates) if item >= date), -1)
            stock.current_price = stock.price_data[date_index]

        for trade in self.portfolio.trades:  # update portfolio float
            all_dates = trade.stock.price_data.index
            date_index = next((index for (index, item) in enumerate(all_dates) if item >= date), -1)
            price_delta = trade.stock.current_price - trade.stock.price_data[date_index - 1]
            self.portfolio.float += price_delta * trade.shares

    def get_stocks_from_portfolio(self):
        ls = [x.stock for x in self.portfolio.trades]
        return list(set(ls))  # for unique stocks

    def portfolio_periodic_return(self):
        pass

    def portfolio_cumulative_return(self):
        pass

    def simulate(self):
        strategy = None
        coll = pd.Series()
        for stock in self.stock_universe:

            if isinstance(self.trading_strategy, MovingAverageCrossover):
                self.trading_strategy.short_term_moving_average.append()
                moving_average_1 = MovingAverage(window=self.trading_strategy.short_term_moving_average.window,
                                                 ma_type=self.trading_strategy.short_term_moving_average.ma_type,
                                                 time_series=stock.price_data)
                moving_average_2 = MovingAverage(window=self.trading_strategy.long_term_moving_average.window,
                                                 ma_type=self.trading_strategy.long_term_moving_average.ma_type,
                                                 time_series=stock.price_data)

                coll[stock.ticker] = (moving_average_1, moving_average_2)

        for date in pd.date_range(start=self.start_date, end=self.end_date):
            self.update_from_last_day(date)
            stocks_in_portfolio = self.get_stocks_from_portfolio()

            for stock in self.stock_universe:

                if isinstance(self.trading_strategy, MovingAverageCrossover):
                    date_index = next((index for (index, item) in enumerate(all_dates) if item >= date), -1)
                    moving_average_1 = coll[stock][0].moving_average[moving_average_1.moving_average.index]
                    moving_average_2 = coll[stock][1].moving_average[moving_average_2.moving_average.index]
                    strategy = MovingAverageCrossover(moving_average_1, moving_average_2)
                    portfolio_weight = round_shares_from_portfolio_weight(stock=stock,
                                                                          weight=self.trading_strategy.weight_of_portfolio_for_trade(),
                                                                          balance=self.portfolio.balance)

                if strategy.long_entry_condition() and stock not in stocks_in_portfolio:
                    open_position(self.portfolio, Trade(stock=stock, direction=True,
                                                        shares=portfolio_weight, date=date))
                elif strategy.short_entry_condition() and stock not in stocks_in_portfolio:
                    open_position(self.portfolio, Trade(stock=stock, direction=False,
                                                        shares=portfolio_weight, date=date))
            for trade in self.portfolio.trades:
                if self.trading_strategy.long_exit_condition():
                    close_position(self.portfolio, trade)
                elif self.trading_strategy.short_exit_condition():
                    close_position(self.portfolio, trade)


# apple = Stock('AAPL')
# trade = Trade(apple, True, 100, datetime.now())
# portfolio = Portfolio(10000, [trade])
# moving_average_1 = MovingAverage(window=50, ma_type='sma', shift=0)
# moving_average_2 = MovingAverage(window=100, ma_type='sma', shift=0)
# moving_average_crossover = MovingAverageCrossover(moving_average_1, moving_average_2)
# Simulation(0, moving_average_crossover).simulate()
