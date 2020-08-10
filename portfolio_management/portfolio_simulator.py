import math
from datetime import datetime, timedelta
import typing
from functools import partial
import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
import data_scraping.excel_helpers as excel
import config
import financial_statement_analysis.accounting_ratios as ratios
import matplotlib.pyplot as plt

plt.style.use('fivethirtyeight')


# TODO: Add statistics i.e. average drawdown, alpha, beta/sharpe/sortino...
# TODO: Functionality for reinvesting dividends
# TODO: Functionality for stock screening
# TODO: implement technical indicators in corresponding files


class Stock:

    def __init__(self, ticker: str):
        self.ticker = ticker
        self.price_data = excel.read_df_from_csv('{}/{}.xlsx'.format(config.STOCK_PRICES_DIR_PATH, self.ticker))
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


# making a position should only affect the balance, not the float
def make_position(portfolio: Portfolio, trade: Trade, entry: bool):
    # if entering a long position or exiting a short position
    if (trade.direction and entry) or (not trade.direction and not entry):
        portfolio.balance -= (trade.stock.current_price * trade.shares + trade.commission)
    # if exiting a long position or entering a short position
    elif (trade.direction and not entry) or (not trade.direction and entry):
        portfolio.balance += (trade.stock.current_price * trade.shares + trade.commission)
    else:
        return


# example use: helper_condition(rsi, '>', 70)
def helper_condition(indicator: partial, comparator: str, otherside):
    def compare(x, comparator, y):
        if comparator == '>':
            return x > y
        elif comparator == '<':
            return x < y
        elif comparator == '=':
            return x == y

    if callable(otherside):
        return lambda ticker, date: compare(indicator(ticker, date), comparator, otherside(ticker, date))
    else:
        return lambda ticker, date: compare(indicator(ticker, date), comparator, otherside)


class PortfolioAllocation:

    def long_only(self):
        pass

    def short_only(self):
        pass

    def long_short_market_neutral(self):  # weighted sum of betas is 0
        pass

    # Requires that the sum of the weights (positive or negative) of all assets in the portfolio fall between min and max
    # For example, net_exposure(-0.1, 0.1) constrains the difference in value between the portfolio's longs and shorts to be between -10% and 10% of the current portfolio value.
    # Special case: min=0, max=0 means no difference in weight, so dollar neutral (i.e. 50% long, 50% short)
    # TODO: Special case: min=50, max=70 means 1X0/X0?
    def long_short_net_exposure(self, minimum_exposure: int, maximum_exposure: int, percent_tolerance: int):
        pass


class RebalancingFrequency:
    def daily(self):
        return timedelta(days=1)

    def monthly(self):
        return timedelta(days=30)

    def yearly(self):
        return timedelta(days=365)


class Optimization:
    def maximize_treynor(self):
        pass

    def maximize_sharpe(self):
        pass

    def maximize_sortino(self):
        pass

    def maximize_modigliani(self):
        pass

    def maximize_information(self):
        pass

    def maximize_kelly_criterion(self):
        pass

    def maximize_roys_safety_first_criterion(self):
        pass

    def maximize_upside_potential(self):
        pass

    def maximize_jensens_alpha(self):
        pass


def systematic_investing_simulator(starting_date: datetime,
                                   ending_date: datetime,
                                   starting_capital: float,
                                   securities_universe: typing.List[str],
                                   portfolio_rebalancing_frequency: typing.Callable,
                                   metrics,
                                   max_stocks_count_in_portfolio: int,
                                   portfolio_allocation: typing.Callable,
                                   portfolio_optimization: typing.Callable,
                                   maximum_leverage: float = 1.0):
    pass

if __name__ == '__main__':
    systematic_investing_simulator(metrics=pd.Series([partial(ratios.price_to_earnings), partial(ratios.return_on_capital)]))


def stock_screening_simulator(starting_date: datetime,
                              ending_date: datetime,
                              starting_capital: float,
                              securities_universe: typing.List[str],
                              portfolio_rebalancing_frequency: typing.Callable,
                              pre_filter: typing.List,
                              max_stocks_count_in_portfolio: int,
                              portfolio_allocation: typing.Callable,
                              portfolio_optimization: typing.Callable,
                              maximum_leverage: float = 1.0):
    results = []
    portfolio = Portfolio(balance=starting_capital, trades=[], date=starting_date)
    securities_universe_objects = pd.Series()
    for ticker in securities_universe:  # populate stock universe
        securities_universe_objects[ticker] = Stock(ticker)

    for date in pd.date_range(start=starting_date, end=ending_date):
        try:
            portfolio.date = date
            stocks_in_portfolio = list(set([x.stock for x in portfolio.trades]))  # get stocks currently in portfolio

            for stock in securities_universe_objects:  # update current prices according to date
                date_index = excel.get_date_index(date, stock.price_data['Adj Close'].index)
                stock.current_price = stock.price_data['Adj Close'].iloc[date_index]

            for trade in portfolio.trades:  # update portfolio float
                date_index = excel.get_date_index(date, trade.stock.price_data['Adj Close'].index)
                daily_pct_return = trade.stock.price_data['Pct Change'].iloc[date_index]
                daily_doll_return = daily_pct_return * trade.stock.current_price * trade.shares
                portfolio.float = portfolio.float + daily_doll_return if trade.direction else portfolio.float - daily_doll_return

            if date != starting_date and (
                    date - portfolio.last_rebalancing_day).days < portfolio_rebalancing_frequency().days:
                continue
            portfolio.last_rebalancing_day = date  # rebalancing day, now can go on:

            stock_screener_dict = {}
            for stock in securities_universe_objects:  # first step, pre filter stocks
                meets_all_conditions = True
                for (metric, comparator, otherside) in pre_filter:
                    if not helper_condition(metric, comparator, otherside)(stock.ticker, date):
                        meets_all_conditions = False
                if meets_all_conditions:
                    for (metric, comparator, otherside) in pre_filter:
                        stock_screener_dict[stock.ticker] = {} if stock.ticker not in stock_screener_dict.keys() else \
                            stock_screener_dict[stock.ticker]
                        stock_screener_dict[stock.ticker][metric.func.__name__] = metric(stock.ticker, date)

            stock_screener_df = pd.DataFrame.from_dict(stock_screener_dict, orient='index')
            print('For {}'.format(date))
            print(stock_screener_df.to_string())

            for trade in portfolio.trades:  # close portfolio trades that no longer meet condition
                if trade.stock.ticker not in stock_screener_df.index:
                    portfolio.trades.pop(portfolio.trades.index(trade))
                    make_position(portfolio, trade, entry=False)
            for stock in securities_universe_objects:
                if stock.ticker in stock_screener_df.index:  # place trades for stocks that meet condition
                    shares_to_buy = math.floor(0.1 * portfolio.balance / stock.current_price)  # TODO
                    commission = 2  # TODO
                    if shares_to_buy > 0 and portfolio.balance > commission + (shares_to_buy * stock.current_price):
                        trade = Trade(stock=stock, direction=True, shares=shares_to_buy, date=date)
                        portfolio.trades.append(trade)
                        make_position(portfolio, trade, entry=True)
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
    evolution_df['Cumulative (%) Return'] = evolution_df.filter(['Float']).pct_change().apply(lambda x: x + 1).cumprod()
    evolution_df['Cumulative (%) Return'].plot(grid=True, figsize=(10, 6))
    plt.show()
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(evolution_df.to_string())
    return evolution_df


stock_screening_simulator(starting_date=datetime(2019, 1, 1),
         ending_date=datetime.now(),
         starting_capital=10000,
         maximum_leverage=1.0,
         securities_universe=excel.get_stock_universe(),
         pre_filter=[(partial(ratios.current_ratio, annual=True, ttm=False), '>', 1)],
         max_stocks_count_in_portfolio=12,
         portfolio_allocation=PortfolioAllocation().long_only,
         portfolio_optimization=Optimization().maximize_jensens_alpha,
         portfolio_rebalancing_frequency=RebalancingFrequency().monthly
         )

# TODO add functionaliy for
# - reinvesting dividends (optional)
# - fractional shares (optional)
# - commision (as percent of trade or fix cost)
# - slippage (as function of daily volume?)
