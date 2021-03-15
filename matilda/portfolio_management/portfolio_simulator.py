import abc
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from datetime import datetime, timedelta
from functools import partial
from abc import abstractmethod
from enum import Enum
from matilda import config
from matilda.broker_deployment.alpaca import AlpacaBroker
from matilda.portfolio_management.Portfolio import Portfolio
from matilda.broker_deployment.broker_interface import Broker
from matilda.portfolio_management.stock_screener import StockScreener

plt.style.use('fivethirtyeight')


# TODO: Add statistics i.e. average drawdown, alpha, beta/sharpe/sortino...
#       Functionality for reinvesting dividends
#       Functionality for stock screening
#       Functionality for technical indicators
#       Functionality for commission (as percent of trade or fix cost)
#       Functionality for slippage (do one day slippage)
#       Functionality for fractional shares (optional)


class RebalancingFrequency(Enum):
    Daily = 1
    Weekly = 5
    Monthly = 21
    Quarterly = 63
    Semiannually = 126
    Annually = 252


class Strategy(metaclass=abc.ABCMeta):

    def __init__(self, max_stocks_count_in_portfolio: int, net_exposure: tuple,
                 maximum_leverage: float = 1.0,
                 reinvest_dividends: bool = False, fractional_shares: bool = False,
                 ):

        """

        :param max_stocks_count_in_portfolio:
        :param net_exposure: tuple that represents (long_percent, short_percent)
            * (0.5, 0.5) is Dollar Neutral Strategy
            * (1.3, 0.3) is 130-30 Strategy
        :param maximum_leverage:
        :param reinvest_dividends:
        :param fractional_shares:

        """
        self.max_stocks_count_in_portfolio = max_stocks_count_in_portfolio
        self.net_exposure = net_exposure
        self.maximum_leverage = maximum_leverage
        self.reinvest_dividends = reinvest_dividends
        self.fractional_shares = fractional_shares

    @abstractmethod
    def screen_stocks(self, current_date):
        """
        Filter stocks. Can use a StockScreener object
        :param current_date:
        :return: a tuple of two lists: long stocks, and short stocks.
        """
        pass

    @abstractmethod
    def portfolio_allocation_regime(self, portfolio):
        """
        Can use our PortfolioOptimization library.
        Example: `return EquallyWeightedPortfolio(portfolio).solve_weights()`
        :param portfolio:
        :return: pd.Series with indices being stock tickers (string), and value being weight to allocate (not in percentage)

        """
        pass

    @abstractmethod
    def is_market_timing(self, portfolio: Portfolio):
        """
        Is it time to rebalance the portfolio.
        Example: `return (current_date - last_rebalancing_day).days > config.RebalancingFrequency.Quarterly.value`

        :param portfolio:
        :return: Boolean true if we need to rebalance our portfolio, False otherwise

        """
        pass

    def historical_simulation(self, starting_date: datetime, ending_date: datetime, starting_capital: float,
                              include_slippage: bool = False, include_capital_gains_tax: bool = False,
                              commission: int = 2):
        results = []
        portfolio = Portfolio(assets=[], balance=starting_capital, trades=[], date=starting_date)

        # First, populate stock returns universe
        securities_universe_prices_df = pd.DataFrame()
        for stock in os.listdir(path=config.STOCK_PRICES_DIR_PATH):
            ticker = stock.strip('.pkl')
            series = pd.read_pickle(os.path.join(config.STOCK_PRICES_DIR_PATH, stock))['Adj Close']

            dummy_dates = pd.date_range(start=series.index[0], end=series.index[-1])
            zeros_dummy = pd.Series(data=np.zeros(shape=len(dummy_dates)).fill(np.nan),
                                    index=dummy_dates, name='Dummy', dtype='float64')

            series = pd.concat([series, zeros_dummy], axis=1).iloc[:, 0]
            securities_universe_prices_df[ticker] = series.ffill()

        securities_universe_returns_df = securities_universe_prices_df.pct_change()

        for date in pd.date_range(start=starting_date, end=ending_date):
            portfolio.date = datetime(year=date.year, month=date.month, day=date.day)

            for trade in portfolio.trades:  # update portfolio float
                date_loc = trade.stock.index.get_loc(date - timedelta(seconds=1))

                daily_pct_return = (trade.stock.iloc[date_loc] - trade.stock.iloc[date_loc - 1]) \
                                   / trade.stock.iloc[date_loc - 1]

                daily_doll_return = daily_pct_return * trade.stock.loc[date - timedelta(seconds=1)] * trade.shares

                portfolio.float = portfolio.float + daily_doll_return if trade.direction \
                    else portfolio.float - daily_doll_return

            if not (self.is_market_timing(portfolio=portfolio) or date == starting_date):
                continue

            portfolio.last_rebalancing_day = date  # rebalancing day, now can go on:
            stocks_to_trade = self.screen_stocks(current_date=portfolio.date)
            long_stocks, short_stocks = stocks_to_trade

            for trade in portfolio.trades:  # close portfolio trades that no longer meet condition
                if trade.stock.name not in long_stocks + short_stocks:
                    portfolio.make_position(trade, entry=False)

            # Get portfolio returns of selected stocks up to current date, and optimize portfolio allocation
            portfolio.df_returns = securities_universe_returns_df[long_stocks]
            sliced_portfolio = portfolio.slice_dataframe(to_date=date, inplace=False)
            weights = self.portfolio_allocation_regime(portfolio=sliced_portfolio)

            portfolio.rebalance_portfolio(long_stocks=securities_universe_prices_df[long_stocks],
                                          short_stocks=securities_universe_prices_df[short_stocks],
                                          weights=weights, commission=commission,
                                          fractional_shares=self.fractional_shares)

            # Aggregate trades for better formatting in the dataframe
            dictionary = dict()
            for trade in portfolio.trades:
                dictionary[trade.stock.name] = dictionary.get(trade.stock.name, 0) + trade.shares

            aggregated_trades = [(key, val) for (key, val) in dictionary.items()]
            results.append([date.strftime("%Y-%m-%d"), aggregated_trades,
                            round(portfolio.balance, 2), round(portfolio.float, 2)])

        evolution_df = pd.DataFrame(results, columns=['Date', 'Holdings', 'Balance', 'Float'])
        evolution_df.set_index('Date', inplace=True)
        evolution_df['Cumulative (%) Return'] = evolution_df.filter(['Float']).pct_change().apply(
            lambda x: x + 1).cumprod()
        evolution_df['Float'].plot(grid=True, figsize=(10, 6))
        plt.show()
        with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            print(evolution_df.to_string())
        return evolution_df

    def broker_deployment(self, broker):
        """
        Of course, need to schedule that function depending on the `is_time_to_reschedule`. Potentially use AWS Lambda

        :param broker:
        :return:
        """
        if not issubclass(broker.__class__, Broker):
            raise Exception('Ensure that the broker object inherits from the `Broker` class.')

        assets_to_long, assets_to_short = self.screen_stocks(current_date=datetime.now())
        # TODO long for now, improve optimization to include diff constraints
        weights = self.portfolio_allocation_regime(portfolio=Portfolio(assets_to_long))
        broker.place_order(symbol='AAPL', side='buy')
        current_positions = broker.list_positions()
        for position in current_positions:
            print(position)
        broker.place_order()


# import pyformulas as pf
# import matplotlib.pyplot as plt
# import numpy as np
# import time
#
# fig = plt.figure()
#
# canvas = np.zeros((480,640))
# screen = pf.screen(canvas, 'Sinusoid')
#
# start = time.time()
# while True:
#     now = time.time() - start
#
#     x = np.linspace(now-2, now, 100)
#     y = np.sin(2*np.pi*x) + np.sin(3*np.pi*x)
#     plt.xlim(now-2,now+1)
#     plt.ylim(-3,3)
#     plt.plot(x, y, c='black')
#
#     # If we haven't already shown or saved the plot, then we need to draw the figure first...
#     fig.canvas.draw()
#
#     image = np.fromstring(fig.canvas.tostring_rgb(), dtype=np.uint8, sep='')
#     image = image.reshape(fig.canvas.get_width_height()[::-1] + (3,))
#
#     screen.update(image)
#
# #screen.close()

if __name__ == '__main__':
    # some imports for minimal example
    from matilda import piotroski_f_score, earnings_per_share, return_on_equity, FactorModels, \
        EquallyWeightedPortfolio, AlpacaBroker
    from matilda.metrics_helpers import mean_metric_growth_rate, compare_against_macro

    # initialize stock screener with an initial universe of Dow Jones stocks
    stock_screener = StockScreener(securities_universe=config.MarketIndices.DOW_JONES)

    # filter by industry, sector, location, exchange...
    stock_screener.filter_by_market(filter=[config.GICS_Sectors.INFORMATION_TECHNOLOGY,
                                            config.GICS_Sectors.CONSUMER_DISCRETIONARY])

    # filter by fundamental metric against absolute number.
    # The Piotroski score, a criteria-based metric used to evaluate value stocks, should be above 8.
    stock_screener.filter_by_comparison_to_number(partial(piotroski_f_score, period='FY'), '>=', 8)

    stock_screener.run()  # can run the stock screener, by default based on today's values

    # can also filter based on growth, mean, etc. over time.
    fn = partial(mean_metric_growth_rate, metric=earnings_per_share, interval='Y-Y', periods=1)
    # EPS growth rates of at least 25% compared with year-ago levels suggest a company has products/services in strong demand
    stock_screener.filter_by_comparison_to_number(fn, '>=', 0.25)

    # can also filter these based on percentile against competitors (industry, sector...)
    # Ideally, ROE is equal to or just above the median for the peer group
    fn = partial(compare_against_macro, metric=return_on_equity, against=config.SIC_Industries)
    stock_screener.filter_by_comparison_to_number(fn, '>=', 50)

    # regress against exposure to a certain risk factor model
    lower_bounds = pd.Series(data=[40], index=['Alpha'])
    upper_bounds = pd.Series(data=[80], index=['MKT'])
    stock_screener.filter_by_exposure_from_factor_model(factor_model=FactorModels.FamaFrench3,
                                                        lower_bounds=lower_bounds, upper_bounds=upper_bounds)

    # can also specify another date when running the stock screener
    stock_screener.run(date=datetime(2018, 1, 1))
    print(stock_screener.stocks)

    # specify your strategy's rules for stock selection, portfolio allocation, and market timing
    class CustomStrategy(Strategy):
        def is_market_timing(self, portfolio):
            # rebalance every quarter (3 months)
            current_date = portfolio.df_returns.index[-1]
            last_rebalancing_day = portfolio.last_rebalancing_day
            return (current_date - last_rebalancing_day).days > config.RebalancingFrequency.Quarterly.value

        def screen_stocks(self, current_date):
            # use the stock screener we previous specified
            stock_screener.run(date=current_date)
            return stock_screener.stocks, []

        def portfolio_allocation_regime(self, portfolio):
            return EquallyWeightedPortfolio(portfolio).solve_weights()

    # instantiate the custom strategy
    strategy = CustomStrategy(max_stocks_count_in_portfolio=12, net_exposure=(100, 0),
                              maximum_leverage=1.0, reinvest_dividends=True, fractional_shares=True)

    # historically simulate (i.e. backtest) your strategy
    strategy.historical_simulation(starting_date=datetime(2019, 1, 1), ending_date=datetime(2020, 12, 1),
                                   starting_capital=50000, include_capital_gains_tax=False,
                                   include_slippage=False)

    # deploy your strategy. fill your broker's API key ID and secret in config.py
    strategy.broker_deployment(broker=AlpacaBroker())
