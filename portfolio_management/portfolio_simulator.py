import abc
import math
from datetime import datetime, timedelta
import typing
from functools import partial
import pandas as pd
import numpy as np
from abc import abstractmethod
from scipy import stats
import historical_data_collection.excel_helpers as excel
import config
import fundamental_analysis.accounting_ratios as ratios
import matplotlib.pyplot as plt
import portfolio_management.risk_quantification as risk_measures
from portfolio_management.portfolio_optimization import optimal_portfolio_allocation
import seaborn
import statsmodels
import statsmodels.api as sm
from statsmodels.tsa.stattools import coint

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

    def rebalance_portfolio(self, stocks_to_trade, weights, commission, fractional_shares):
        '''
        Place Positions (Rebalance Portfolio)
        First sweep over the stocks already for which we need to sell some of its shares (entry short or exit long)
        (gives us capital to invest for the others). Second sweep is for buying
        :return:
        '''
        long_stocks, short_stocks = stocks_to_trade
        for i in range(2):

            for stock in stocks_to_trade:
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


class Strategy(metaclass=abc.ABCMeta):

    def __init__(self, starting_date: datetime, ending_date: datetime,
                 starting_capital: float, securities_universe: typing.List[str], max_stocks_count_in_portfolio: int,
                 portfolio_exposure: typing.Callable,
                 portfolio_allocation: typing.Callable, maximum_leverage: float = 1.0,
                 reinvest_dividends: bool = False, fractional_shares: bool = False,
                 include_slippage: bool = False, include_capital_gains_tax: bool = False, commission: int = 2):

        self.starting_date = starting_date
        self.ending_date = ending_date
        self.starting_capital = starting_capital
        self.securities_universe = populate_stock_universe(securities_universe)
        self.max_stocks_count_in_portfolio = max_stocks_count_in_portfolio
        self.portfolio_exposure = portfolio_exposure
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

                for trade in portfolio.trades:  # update portfolio float
                    date_index = excel.get_date_index(date, trade.stock.price_data['Adj Close'].index)
                    daily_pct_return = trade.stock.price_data['Pct Change'].iloc[date_index]
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
                for stock_ticker in stocks_to_trade:
                    stock = self.securities_universe[stock_ticker]
                    to_date = excel.get_date_index(date, stock.price_data.index)
                    portfolio_returns[stock.ticker] = stock.price_data['Adj Close'].iloc[:to_date].pct_change()

                weights = self.portfolio_allocation(portfolio_returns=portfolio_returns, longs=long_stocks,
                                                    shorts=short_stocks)


                portfolio.rebalance_portfolio(stocks_to_trade, weights, self.commission, self.fractional_shares)

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


class RebalancingFrequency:
    def rebalance_at_interval(self, rebalancing_freq):
        return lambda current_date, last_rebalancing_day: \
            (current_date - last_rebalancing_day).days < timedelta(days=rebalancing_freq)


class AssetSelectionStrategies:
    def __init__(self, stocks: pd.Series(), date):
        self.stocks = stocks
        self.date = date

    def split_based_on_conditions(self, filter_conditions: typing.List[partial]):
        stock_screener_dict = {}
        for stock in self.stocks:
            meets_all_conditions = True
            for (metric, comparator, otherside) in filter_conditions:
                if not helper_condition(metric, comparator, otherside)(stock.ticker, self.date):
                    meets_all_conditions = False
            if meets_all_conditions:
                for (metric, comparator, otherside) in filter_conditions:
                    stock_screener_dict[stock.ticker] = {} if stock.ticker not in stock_screener_dict.keys() else \
                        stock_screener_dict[stock.ticker]
                    stock_screener_dict[stock.ticker][metric.func.__name__] = metric(stock.ticker, self.date)

        stock_screener_df = pd.DataFrame.from_dict(stock_screener_dict, orient='index')
        print('For {}'.format(self.date))
        print(stock_screener_df.to_string())
        stocks_to_trade = stock_screener_df.index
        return stocks_to_trade, self.stocks.drop(stocks_to_trade)

    def split_based_on_pairs(self, compute_z_score_thresh: typing.Callable,
                             stat=partial(coint), p_value_thresh=0.05, z_score_ma=None):
        '''

        :param stat: coint, pearsonr...
        :return:
        '''
        longs, shorts = [], []
        data = pd.Series()
        for stock in self.stocks:
            data[stock.ticker] = stock.price_data['Adj Close'][-1000:]  # fix

        n, keys, pairs = len(data), data.keys(), []
        score_matrix, pvalue_matrix = np.zeros((n, n)), np.ones((n, n))

        for i in range(n):
            for j in range(i + 1, n):
                '''
                TODO: further tests for co-integration . It would be useful to form a linear combination of both the stocks 
                and estimating the ordinary least squares and testing the residuals for stationarity in the second step
                 using an Augmented Dickey-Fuller Test, Phillips-Perron Test, e.t.c.
                '''
                t_stat, p_value, crit_value = stat(data[keys[i]], data[keys[j]])
                score_matrix[i, j], pvalue_matrix[i, j] = t_stat, p_value
                if p_value < p_value_thresh:
                    pairs.append((keys[i], keys[j]))

        seaborn.heatmap(pvalue_matrix, xticklabels=data.index, yticklabels=data.index,
                        cmap='plasma', mask=(pvalue_matrix >= p_value_thresh))
        plt.show()
        for pair in pairs:
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
                longs.append(pair[1])
                shorts.append(pair[0])
            elif z_score[-1] < z_score_thresh:
                longs.append(pair[0])
                shorts.append(pair[1])

        return longs, shorts


class TrendFollowingStrategy(Strategy):
    def generate_assets_to_trade(self, current_date):
        pass


class MomentumStrategy(TrendFollowingStrategy):
    def generate_assets_to_trade(self, current_date):
        pass


class BreakoutStrategy(MomentumStrategy):
    def generate_assets_to_trade(self, current_date):
        pass


class MeanReversionStrategy(Strategy):
    def generate_assets_to_trade(self, current_date):
        pass


class PairsTrading(MeanReversionStrategy):

    def generate_assets_to_trade(self, current_date):
        return AssetSelectionStrategies(stocks=self.securities_universe, date=current_date) \
            .split_based_on_pairs(compute_z_score_thresh=lambda zscore: 3)


class MultiFactorStrategy(Strategy):
    def __init__(self, pre_filter_conditions: typing.List, factors: dict, starting_date: datetime,
                 ending_date: datetime, starting_capital: float, securities_universe: typing.List[str],
                 rebalancing_frequency: typing.Callable, max_stocks_count_in_portfolio: int,
                 portfolio_exposure: typing.Callable, portfolio_allocation: typing.Callable):
        super().__init__(starting_date, ending_date, starting_capital, securities_universe, rebalancing_frequency,
                         max_stocks_count_in_portfolio, portfolio_exposure, portfolio_allocation)
        self.pre_filter_conditions = pre_filter_conditions
        self.factors = factors

    def assets_to_trade(self, current_date):

        # we won't be using the short stocks, because they didn't pass condition
        long_stocks, short_stocks = AssetSelectionStrategies(stocks=self.securities_universe, date=current_date) \
            .split_based_on_conditions(self.pre_filter_conditions)

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
        if self.portfolio_exposure.__name__ == 'long_only':
            long_stocks, short_stocks = long_stocks[:self.max_stocks_count_in_portfolio], []
        elif self.portfolio_exposure.__name__ == 'short_only':
            long_stocks, short_stocks = [], long_stocks[-self.max_stocks_count_in_portfolio:]
        else:  # long and short
            long_stocks, short_stocks = long_stocks[:math.floor(self.max_stocks_count_in_portfolio / 2)], \
                                        long_stocks[-math.floor(self.max_stocks_count_in_portfolio / 2):]

        return list(long_stocks), list(short_stocks)


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


class PortfolioExposure:

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


class PortfolioAllocation:
    def __init__(self, portfolio_returns):
        self.portfolio_returns = portfolio_returns

    def Equally_Weighted_Allocation(self, portfolio_returns):
        output = pd.Series()
        for ticker, stock_return in portfolio_returns.iteritems():
            output[ticker] = 1 / len(portfolio_returns)
        return output

    def Market_Cap_Weighted_Allocation(self):
        return 0


class MomentsBasedOptimization(PortfolioAllocation):
    def maximize_returns(self):
        pass

    def minimize_volatility(self):
        pass

    def maximize_kurtosis(self):
        pass

    def minimize_skewness(self):
        pass


class RiskAdjustedReturnsOptimization(PortfolioAllocation):

    def maximize_treynor_ratio(self, portfolio_returns, benchmark_returns='^GSPC', longs: [] = None, shorts: [] = None):
        return optimal_portfolio_allocation(risk_measure=partial(risk_measures.treynor_ratio,
                                                                 benchmark_returns=benchmark_returns),
                                            portfolio_returns=portfolio_returns, longs=longs, shorts=shorts)

    def maximize_sharpe_ratio(self, portfolio_returns, longs: [] = None, shorts: [] = None):
        return optimal_portfolio_allocation(risk_measure=partial(risk_measures.sharpe_ratio),
                                            portfolio_returns=portfolio_returns, longs=longs, shorts=shorts)

    def maximize_information_ratio(self, portfolio_returns, benchmark_returns='^GPSC', longs: [] = None,
                                   shorts: [] = None):
        return optimal_portfolio_allocation(risk_measure=partial(risk_measures.information_ratio,
                                                                 benchmark_returns=benchmark_returns),
                                            portfolio_returns=portfolio_returns, longs=longs, shorts=shorts)

    def maximize_modigliani_ratio(self, portfolio_returns, benchmark_returns='^GPSC', longs: [] = None,
                                  shorts: [] = None):
        return optimal_portfolio_allocation(risk_measure=partial(risk_measures.modigliani_ratio,
                                                                 benchmark_returns=benchmark_returns),
                                            portfolio_returns=portfolio_returns, longs=longs, shorts=shorts)

    def maximize_roys_safety_first_criterion(self, portfolio_returns, minimum_threshold=0.02, longs: [] = None,
                                             shorts: [] = None):
        return optimal_portfolio_allocation(
            risk_measure=partial(risk_measures.roys_safety_first_criterion, minimum_threshold=minimum_threshold),
            portfolio_returns=portfolio_returns, longs=longs, shorts=shorts)

    def maximize_excess_return_value_at_risk(self, portfolio_returns, benchmark_returns='^GSPC', confidence_level=0.05,
                                             longs: [] = None, shorts: [] = None):
        return optimal_portfolio_allocation(
            risk_measure=partial(risk_measures.excess_return_value_at_risk, benchmark_returns=benchmark_returns,
                                 confidence_level=confidence_level),
            portfolio_returns=portfolio_returns, longs=longs, shorts=shorts)

    def maximize_conditional_sharpe_ratio(self, portfolio_returns, confidence_level=0.05, longs: [] = None,
                                          shorts: [] = None):
        return optimal_portfolio_allocation(
            risk_measure=partial(risk_measures.conditional_value_at_risk, confidence_level=confidence_level),
            portfolio_returns=portfolio_returns, longs=longs, shorts=shorts)

    def maximize_jensens_alpha(self, portfolio_returns, benchmark_returns='^GSPC', longs: [] = None, shorts: [] = None):
        return optimal_portfolio_allocation(
            risk_measure=partial(risk_measures.jensens_alpha, benchmark_returns=benchmark_returns),
            portfolio_returns=portfolio_returns, longs=longs, shorts=shorts)

    def maximize_omega_ratio(self, portfolio_returns, target=0, longs: [] = None, shorts: [] = None):
        return optimal_portfolio_allocation(
            risk_measure=partial(risk_measures.omega_ratio, target=target),
            portfolio_returns=portfolio_returns, longs=longs, shorts=shorts)

    def maximize_sortino_ratio(self, portfolio_returns, target=0, longs: [] = None, shorts: [] = None):
        return optimal_portfolio_allocation(
            risk_measure=partial(risk_measures.sortino_ratio, target=target),
            portfolio_returns=portfolio_returns, longs=longs, shorts=shorts)

    def kappa_three_ratio(self, portfolio_returns, target=0, longs: [] = None, shorts: [] = None):
        return optimal_portfolio_allocation(
            risk_measure=partial(risk_measures.kappa_three_ratio, target=target),
            portfolio_returns=portfolio_returns, longs=longs, shorts=shorts)

    def gain_loss_ratio(self, portfolio_returns, target=0, longs: [] = None, shorts: [] = None):
        return optimal_portfolio_allocation(
            risk_measure=partial(risk_measures.gain_loss_ratio, target=target),
            portfolio_returns=portfolio_returns, longs=longs, shorts=shorts)

    def maximize_upside_potential_ratio(self, portfolio_returns, target=0, longs: [] = None, shorts: [] = None):
        return optimal_portfolio_allocation(
            risk_measure=partial(risk_measures.upside_potential_ratio, target=target),
            portfolio_returns=portfolio_returns, longs=longs, shorts=shorts)


if __name__ == '__main__':
    # portfolio_simulator(starting_date=datetime(2019, 1, 1),
    #                     ending_date=datetime.now(),
    #                     starting_capital=10000,
    #                     maximum_leverage=1.0,
    #                     securities_universe=excel.get_stock_universe(),
    #                     pre_filter=[(partial(ratios.current_ratio, annual=True, ttm=False), '>', 1)],
    #                     factors={'Value': pd.Series([partial(ratios.price_to_earnings_ratio, ttm=False, annual=True),
    #                                                  partial(ratios.price_to_book_value_ratio, ttm=False,
    #                                                          annual=True)]),
    #                              'Quality': pd.Series([partial(ratios.return_on_equity, ttm=False, annual=True)]),
    #                              'Growth': pd.Series(),
    #                              'Momentum': pd.Series(),
    #                              'Volatility': pd.Series(),
    #                              'Dividend': pd.Series()},
    #                     max_stocks_count_in_portfolio=2,
    #                     portfolio_exposure=PortfolioExposure().long_only,
    #                     portfolio_allocation=RiskAdjustedReturnsOptimization().maximize_jensens_alpha,
    #                     portfolio_rebalancing_frequency=RebalancingFrequency().monthly
    #                     )
    stocks = pd.Series()
    for ticker in ['AAPL', 'FB', 'GOOG', 'MSFT']:
        stocks[ticker] = Stock(ticker)
    pairs_trading = AssetSelectionStrategies(date=datetime.today(), stocks=stocks).split_based_on_pairs()
