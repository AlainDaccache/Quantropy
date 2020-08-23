import math
from datetime import datetime, timedelta
import typing
from functools import partial
import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from scipy import stats
import data_scraping.excel_helpers as excel
import config
import financial_statement_analysis.accounting_ratios as ratios
import matplotlib.pyplot as plt
import portfolio_management.risk_quantification as risk_measures
from portfolio_management.portfolio_optimization import optimal_portfolio

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


class PortfolioDirection:

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
    def maximize_treynor_ratio(self, portfolio_returns, benchmark_returns='^GSPC'):
        return risk_measures.risk_measures_wrapper(risk_measure=partial(risk_measures.treynor_ratio,
                                                                        benchmark_returns=benchmark_returns),
                                                   portfolio_returns=portfolio_returns)

    def maximize_sharpe_ratio(self, portfolio_returns):
        return risk_measures.risk_measures_wrapper(risk_measure=partial(risk_measures.sharpe_ratio),
                                                   portfolio_returns=portfolio_returns)

    def maximize_information_ratio(self, portfolio_returns, benchmark_returns='^GPSC'):
        return risk_measures.risk_measures_wrapper(
            risk_measure=partial(risk_measures.information_ratio,
                                 benchmark_returns=benchmark_returns),
            portfolio_returns=portfolio_returns)

    def maximize_modigliani_ratio(self, portfolio_returns, benchmark_returns='^GPSC'):
        return risk_measures.risk_measures_wrapper(
            risk_measure=partial(risk_measures.modigliani_ratio, benchmark_returns=benchmark_returns),
            portfolio_returns=portfolio_returns)

    def maximize_roys_safety_first_criterion(self, portfolio_returns, minimum_threshold=0.02):
        return risk_measures.risk_measures_wrapper(
            risk_measure=partial(risk_measures.roys_safety_first_criterion, minimum_threshold=minimum_threshold),
            portfolio_returns=portfolio_returns)

    def maximize_excess_return_value_at_risk(self, portfolio_returns, benchmark_returns='^GSPC', confidence_level=0.05):
        return risk_measures.risk_measures_wrapper(risk_measure=partial(risk_measures.excess_return_value_at_risk,
                                                                        benchmark_returns=benchmark_returns,
                                                                        confidence_level=confidence_level),
                                                   portfolio_returns=portfolio_returns)

    def maximize_conditional_sharpe_ratio(self, portfolio_returns, confidence_level=0.05):
        return risk_measures.risk_measures_wrapper(risk_measure=partial(risk_measures.conditional_sharpe_ratio,
                                                                        confidence_level=confidence_level),
                                                   portfolio_returns=portfolio_returns)

    def maximize_jensens_alpha(self, benchmark_returns='^GSPC'):
        return partial(risk_measures.jensens_alpha,
                       benchmark_returns=benchmark_returns)

    def maximize_omega_ratio(self, portfolio_returns, target=0):
        return risk_measures.risk_measures_wrapper(risk_measure=partial(risk_measures.omega_ratio, target=target),
                                                   portfolio_returns=portfolio_returns)

    def maximize_sortino_ratio(self, portfolio_returns, target=0):
        return risk_measures.risk_measures_wrapper(risk_measure=partial(risk_measures.sortino_ratio, target=target),
                                                   portfolio_returns=portfolio_returns)

    def kappa_three_ratio(self, portfolio_returns, target=0):
        return risk_measures.risk_measures_wrapper(risk_measure=partial(risk_measures.kappa_three_ratio, target=target),
                                                   portfolio_returns=portfolio_returns)

    def gain_loss_ratio(self, portfolio_returns, target=0):
        return risk_measures.risk_measures_wrapper(risk_measure=partial(risk_measures.gain_loss_ratio, target=target),
                                                   portfolio_returns=portfolio_returns)

    def maximize_upside_potential_ratio(self, portfolio_returns, target=0):
        return risk_measures.risk_measures_wrapper(risk_measure=partial(risk_measures.kappa_three_ratio, target=target),
                                                   portfolio_returns=portfolio_returns)


def portfolio_simulator(starting_date: datetime, ending_date: datetime,
                        starting_capital: float, securities_universe: typing.List[str],
                        portfolio_rebalancing_frequency: typing.Callable, pre_filter: typing.List, factors: dict,
                        max_stocks_count_in_portfolio: int, portfolio_direction: typing.Callable,
                        portfolio_optimization: typing.Callable, maximum_leverage: float = 1.0,
                        reinvest_dividends: bool = False, fractional_shares: bool = False,
                        include_slippage: bool = False, include_capital_gains_tax: bool = False, commission: int = 2):
    results = []
    portfolio = Portfolio(balance=starting_capital, trades=[], date=starting_date)
    securities_universe_objects = pd.Series()
    for ticker in securities_universe:  # populate stock universe
        securities_universe_objects[ticker] = Stock(ticker)

    for date in pd.date_range(start=starting_date, end=ending_date):
        try:
            portfolio.date = date
            # stocks in portfolio: list(set([x.stock for x in portfolio.trades]))
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
                    portfolio.make_position(trade, entry=False)

            # Next step, compute factors for each factor category for each stock
            factors_dict = {
                (factor_type, factor.func.__name__): stock_screener_df.index.map(lambda stock: factor(stock, date))
                for factor_type, factor_list in factors.items()
                for factor in factor_list
            }

            factors_df = pd.DataFrame(data=list(factors_dict.values()),
                                      index=pd.MultiIndex.from_tuples(factors_dict.keys()),
                                      columns=stock_screener_df.index)
            print(factors_df.to_string())

            # Then, normalize each factor (compute Z-score i.e. (x - mu) / sigma)
            factors_df = factors_df.apply(stats.zscore, axis=1)
            factors_df = pd.DataFrame(factors_df.values.tolist(), index=factors_df.index,
                                      columns=stock_screener_df.index)

            # Then, add factors for each factor category for each company to make score for that company
            factors_df = factors_df.groupby(level=0, axis=0).agg(np.sum)
            print(factors_df.to_string())

            # Then, normalize again and sum across factor categories, and rank
            factors_df = factors_df.apply(stats.zscore, axis=1)
            factors_df = pd.DataFrame(factors_df.values.tolist(), index=factors_df.index,
                                      columns=stock_screener_df.index)
            factors_df = factors_df.apply(np.sum, axis=0)
            factors_df.sort_values(axis=0, ascending=False, inplace=True)
            print(factors_df.to_string())

            # Stocks to go long and/or short on
            if portfolio_direction.__name__ == 'long_only':
                long_stocks, short_stocks = stock_screener_df.index[:max_stocks_count_in_portfolio], []
            elif portfolio_direction.__name__ == 'short_only':
                long_stocks, short_stocks = [], stock_screener_df.index[-max_stocks_count_in_portfolio:]
            else:  # long and short
                long_stocks, short_stocks = stock_screener_df.index[:math.floor(max_stocks_count_in_portfolio / 2)], \
                                            stock_screener_df.index[-math.floor(max_stocks_count_in_portfolio / 2):]

            stocks_to_trade = list(long_stocks) + list(short_stocks)

            # Close positions for stocks that are in neither long and short:
            for trade in portfolio.trades:
                if trade.stock.ticker not in stocks_to_trade:
                    portfolio.make_position(trade, entry=False)

            # Get portfolio returns of selected stocks up to current date, and optimize portfolio allocation
            portfolio_returns = pd.Series()
            for stock_ticker in stocks_to_trade:
                stock = securities_universe_objects[stock_ticker]
                to_date = excel.get_date_index(date, stock.price_data.index)
                portfolio_returns[stock.ticker] = stock.price_data['Adj Close'].iloc[:to_date].pct_change()

            weights = optimal_portfolio(returns=portfolio_returns, longs=long_stocks, shorts=short_stocks,
                                        risk_measure=portfolio_optimization)

            # Place Positions (Rebalance Portfolio)
            # First sweep over the stocks already for which we need to sell some of its shares (entry short or exit long)
            # (gives us capital to invest for the others). Second sweep is for buying

            for i in range(2):

                for stock_ticker in stocks_to_trade:
                    stock_is_in_portfolio = False
                    stock = securities_universe_objects[stock_ticker]
                    for trade in portfolio.trades:

                        # If the stock computed is already part of our portfolio, then:
                        if stock.ticker == trade.stock.ticker \
                                and ((stock.ticker in long_stocks and trade.stock.ticker in long_stocks)
                                     or (stock.ticker in short_stocks and trade.stock.ticker in short_stocks)):

                            stock_is_in_portfolio = True

                            # Aggregate total weight of asset in portfolio
                            current_weight_in_portfolio = 0
                            for trade in portfolio.trades:
                                if stock.ticker == trade.stock.ticker:
                                    current_weight_in_portfolio += trade.shares * trade.stock.current_price \
                                                                  / portfolio.float

                            # The weight we need to rebalance for
                            delta_weights = weights[stock.ticker] - current_weight_in_portfolio
                            delta_shares = (abs(delta_weights) * portfolio.float - commission) \
                                           / stock.current_price

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
                                                  stock=stock, shares=delta_shares, date=date)
                                    # we're exiting longs and entering shorts
                                    portfolio.make_position(trade, entry=False if stock.ticker in long_stocks else True)
                                    break

                    # If the stock computed is not already part of our portfolio
                    if not stock_is_in_portfolio:
                        shares_to_trade = (weights[stock.ticker] * portfolio.float - commission) \
                                          / stock.current_price
                        if not fractional_shares:
                            shares_to_trade = math.floor(shares_to_trade)
                        if shares_to_trade > 0:
                            if i == 0 and stock_ticker in short_stocks:  # entering shorts
                                trade = Trade(direction=False, stock=stock, shares=shares_to_trade, date=date)
                                portfolio.make_position(trade, entry=True)
                            if i == 1 and stock_ticker in long_stocks: # entering longs
                                trade = Trade(direction=True, stock=stock, shares=shares_to_trade, date=date)
                                portfolio.make_position(trade, entry=True)

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


if __name__ == '__main__':
    portfolio_simulator(starting_date=datetime(2019, 1, 1),
                        ending_date=datetime.now(),
                        starting_capital=10000,
                        maximum_leverage=1.0,
                        securities_universe=excel.get_stock_universe(),
                        pre_filter=[(partial(ratios.current_ratio, annual=True, ttm=False), '>', 1)],
                        factors={'Value': pd.Series([partial(ratios.price_to_earnings_ratio, ttm=False, annual=True),
                                                     partial(ratios.price_to_book_value_ratio, ttm=False,
                                                             annual=True)]),
                                 'Quality': pd.Series([partial(ratios.return_on_equity, ttm=False, annual=True)]),
                                 'Growth': pd.Series(),
                                 'Momentum': pd.Series(),
                                 'Volatility': pd.Series(),
                                 'Dividend': pd.Series()},
                        max_stocks_count_in_portfolio=2,
                        portfolio_direction=PortfolioDirection().long_only,
                        portfolio_optimization=Optimization().maximize_jensens_alpha(),
                        portfolio_rebalancing_frequency=RebalancingFrequency().monthly
                        )
