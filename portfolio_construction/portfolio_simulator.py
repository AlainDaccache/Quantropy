import math
from datetime import datetime
import pandas as pd
from abc import ABC, abstractmethod
import data_scraping.excel_helpers as excel
import config
import matplotlib.pyplot as plt
plt.style.use('fivethirtyeight')


# TODO: Add statistics i.e. average drawdown, alpha, beta/sharpe/sortino...
# TODO: Functionality for reinvesting dividends
# TODO: Functionality for stock screening
# TODO: implement technical indicators in corresponding files


def rsi(df, date):
    return df['momentum_rsi'].loc[date]


def cci(df, date):
    return df['trend_cci'].loc[date]


class Stock:

    def __init__(self, ticker: str):
        self.ticker = ticker
        self.price_data = excel.read_df_from_csv(self.ticker, config.stock_prices_sheet_name)
        self.technical_indicators = excel.read_df_from_csv(self.ticker, config.technical_indicators_name)


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
        self.float = float(balance)
        self.date = 0
        self.last_rebalancing_day = datetime


class Strategy(ABC):

    def __init__(self, rebalancing_period, portfolio_stock_count):
        self.rebalancing_period = rebalancing_period
        self.portfolio_stock_count = portfolio_stock_count
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


def make_position(portfolio: Portfolio, trade: Trade, entry: bool):
    current_price = trade.stock.price_data['Adj Close'].loc[portfolio.date]
    # if entering a long position or exiting a short position, then subtract from account
    if (trade.direction and entry) or (not trade.direction and not entry):
        portfolio.balance -= (current_price * trade.shares + trade.commission)
        portfolio.float -= (current_price * trade.shares + trade.commission)
    else:
        if trade.direction and not entry:  # if exiting a long position, add to account
            portfolio.balance += (current_price * trade.shares + trade.commission)
            portfolio.float += (current_price * trade.shares + trade.commission)
        else:  # if entering a short position, nothing to balance
            pass


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

    def simulate(self):
        results = []
        self.portfolio.last_rebalancing_day = self.start_date
        # populate stock universe
        for ticker in excel.get_stock_universe()[:2]:
            stock_obj = Stock(ticker)
            self.stock_universe[stock_obj.ticker] = stock_obj

        for date in pd.date_range(start=self.start_date, end=self.end_date):

            if (date - self.portfolio.last_rebalancing_day).days < self.trading_strategy.rebalancing_period:
                continue

            self.portfolio.date = date
            self.portfolio.last_rebalancing_day = date

            # get stocks from portfolio
            stocks_in_portfolio = list(set([x.stock for x in self.portfolio.trades]))

            for stock in self.stock_universe:
                if date not in stock.price_data['Adj Close'].index:
                    continue
                else:  # get current (date simulated) price from csv file which contains all prices
                    stock.current_price = stock.price_data['Adj Close'].loc[date]

            # update portfolio float
            for trade in self.portfolio.trades:
                if date not in trade.stock.price_data['Adj Close'].index:
                    continue
                else:
                    daily_pct_return = trade.stock.price_data['pct_change'].loc[date]
                    daily_doll_return = daily_pct_return * trade.stock.price_data['Adj Close'].loc[date] * trade.shares
                    if trade.direction:  # if going long
                        self.portfolio.float += daily_doll_return
                    else:
                        self.portfolio.float -= daily_doll_return

            # print('Portfolio float on {} is ${:.2f}'.format(date.strftime("%Y-%m-%d"),
            #                                                 self.portfolio.float))
            for stock in self.stock_universe:

                if date not in stock.price_data['Adj Close'].index:
                    continue

                if (self.trading_strategy.long_entry_condition()(stock.technical_indicators, date)
                    or self.trading_strategy.short_entry_condition()(stock.technical_indicators, date))  \
                        and stock not in stocks_in_portfolio:
                    trade = Trade(stock=stock,
                                  direction=True if self.trading_strategy.long_entry_condition()(stock.technical_indicators, date) else False,
                                  shares=math.floor(self.trading_strategy.weight_of_portfolio_for_trade() * self.portfolio.balance / stock.price_data['Adj Close'].loc[date]),
                                  date=date)
                    if self.portfolio.balance > trade.commission + (trade.shares * trade.stock.price_data['Adj Close'].loc[date]):
                        self.portfolio.trades.append(trade)
                        make_position(self.portfolio, trade, entry=True)
                        # print('Went {} for {} shares of {} at ${:.2f}. Balance is now ${:.2f}'.format('Long' if trade.direction else 'Short',
                        #                                                                               trade.shares,
                        #                                                                               trade.stock.ticker,
                        #                                                                               trade.stock.price_data['Adj Close'].loc[date],
                        #                                                                               self.portfolio.balance))

            for trade in self.portfolio.trades:
                if date not in trade.stock.price_data['Adj Close'].index:
                    continue
                if (self.trading_strategy.long_exit_condition()(trade.stock.technical_indicators, date) and trade.direction) \
                        or (self.trading_strategy.short_exit_condition()(trade.stock.technical_indicators, date) and not trade.direction):
                    self.portfolio.trades.pop(self.portfolio.trades.index(trade))
                    make_position(self.portfolio, trade, entry=False)
                    # print('Close {} Position of {} for {} shares at ${:.2f}. Balance is now ${:.2f}'.format('Long' if self.trading_strategy.long_exit_condition()(trade.stock.technical_indicators, date) else 'Short',
                    #                                                                                     trade.stock.ticker,
                    #                                                                                     trade.shares,
                    #                                                                                     trade.stock.price_data['Adj Close'].loc[date],
                    #                                                                                     self.portfolio.balance))

            results.append([date.strftime("%Y-%m-%d"),
                            [(x.stock.ticker, x.shares) for x in self.portfolio.trades],
                            round(self.portfolio.balance, 2),
                            round(self.portfolio.float, 2)])

        evolution_df = pd.DataFrame(results, columns=['Date', 'Holdings', 'Balance', 'Float'])
        evolution_df.set_index('Date', inplace=True)
        evolution_df['Daily ($) Return'] = evolution_df['Float'] - evolution_df['Float'].shift(-1)
        evolution_df['Cumulative (%) Return'] = evolution_df['Float'].pct_change().cumsum()

        evolution_df['Cumulative (%) Return'].plot(grid=True, figsize=(10, 6))
        plt.show()
        with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            print(evolution_df.to_string())
        return evolution_df


def compare(x, comparator, y):
    if comparator == '>':
        return x > y
    elif comparator == '<':
        return x < y
    elif comparator == '=':
        return x == y


def helper_condition(indicator, comparator, otherside):
    if callable(otherside):
        return lambda x, date: compare(indicator(x, date), comparator, otherside(x, date))
    else:
        return lambda x, date: compare(indicator(x, date), comparator, otherside)


class UserStrategy(Strategy):
    def __init__(self):
        super().__init__(rebalancing_period=1, portfolio_stock_count=12)

    def long_entry_condition(self):
        return helper_condition(rsi, '>', 70)

    def long_exit_condition(self):
        return helper_condition(rsi, '<', 30)

    def short_entry_condition(self):
        return helper_condition(rsi, '<', 30)

    def short_exit_condition(self):
        return helper_condition(rsi, '>', 70)

    def weight_of_portfolio_for_trade(self):
        return 0.1


if __name__ == '__main__':
    Simulation(10000, UserStrategy()).simulate()
