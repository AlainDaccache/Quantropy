import abc
import math
import os
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

import macroeconomic_analysis.macroeconomic_analysis as macro
from fundamental_analysis.accounting_ratios import price_to_earnings
from portfolio_management.Portfolio import Portfolio, TimeDataFrame
from portfolio_management.broker_deployment.alpaca import AlpacaBroker
from portfolio_management.broker_deployment.broker_interface import Broker
from portfolio_management.portfolio_optimization import EquallyWeightedPortfolio, ModernPortfolioTheory, \
    PortfolioAllocationModel, PostModernPortfolioTheory
from portfolio_management.risk_quantification import sharpe_ratio
from portfolio_management.stock_screener import StockScreener

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

    def __init__(self, starting_date: datetime, ending_date: datetime, starting_capital: float,
                 stock_screener: StockScreener, max_stocks_count_in_portfolio: int,
                 net_exposure: tuple, maximum_leverage: float = 1.0,
                 reinvest_dividends: bool = False, fractional_shares: bool = False,
                 include_slippage: bool = False, include_capital_gains_tax: bool = False, commission: int = 2):

        """

        :param starting_date:
        :param ending_date:
        :param starting_capital:
        :param stock_screener:
        :param max_stocks_count_in_portfolio:
        :param net_exposure: tuple that represents (long_percent, short_percent)
            * (0.5, 0.5) is Dollar Neutral Strategy
            * (1.3, 0.3) is 130-30 Strategy
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
        self.stock_screener = stock_screener
        self.max_stocks_count_in_portfolio = max_stocks_count_in_portfolio
        self.net_exposure = net_exposure
        self.maximum_leverage = maximum_leverage
        self.reinvest_dividends = reinvest_dividends
        self.fractional_shares = fractional_shares
        self.include_slippage = include_slippage
        self.include_capital_gains_tax = include_capital_gains_tax
        self.commission = commission

    def generate_assets_to_trade(self, current_date):
        """
        This is basic implementation. You can implement for other strategies like smart-beta.
        :param current_date:
        :return: a tuple of two lists: long stocks, and short stocks.
        """
        self.stock_screener.run(date=current_date)
        return self.stock_screener.stocks, []

    @abstractmethod
    def allocation_regime(self, portfolio):
        return EquallyWeightedPortfolio(portfolio).solve_weights()

    @abstractmethod
    def is_time_to_reschedule(self, current_date, last_rebalancing_day):
        pass

    def historical_simulation(self):
        results = []
        portfolio = Portfolio(assets=[], balance=self.starting_capital, trades=[], date=self.starting_date)

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

        for date in pd.date_range(start=self.starting_date, end=self.ending_date):
            portfolio.date = datetime(year=date.year, month=date.month, day=date.day)

            for trade in portfolio.trades:  # update portfolio float
                date_loc = trade.stock.index.get_loc(date - timedelta(seconds=1))

                daily_pct_return = (trade.stock.iloc[date_loc] - trade.stock.iloc[date_loc - 1]) \
                                   / trade.stock.iloc[date_loc - 1]

                daily_doll_return = daily_pct_return * trade.stock.loc[date - timedelta(seconds=1)] * trade.shares

                portfolio.float = portfolio.float + daily_doll_return if trade.direction \
                    else portfolio.float - daily_doll_return

            if not (self.is_time_to_reschedule(current_date=date,
                                               last_rebalancing_day=portfolio.last_rebalancing_day)
                    or date == self.starting_date):
                continue

            portfolio.last_rebalancing_day = date  # rebalancing day, now can go on:
            stocks_to_trade = self.generate_assets_to_trade(portfolio.date)
            long_stocks, short_stocks = stocks_to_trade

            for trade in portfolio.trades:  # close portfolio trades that no longer meet condition
                if trade.stock.name not in long_stocks + short_stocks:
                    portfolio.make_position(trade, entry=False)

            # Get portfolio returns of selected stocks up to current date, and optimize portfolio allocation
            portfolio.df_returns = securities_universe_returns_df[long_stocks]
            sliced_portfolio = portfolio.slice_dataframe(to_date=date, inplace=False)
            weights = self.allocation_regime(portfolio=sliced_portfolio)

            portfolio.rebalance_portfolio(long_stocks=securities_universe_prices_df[long_stocks],
                                          short_stocks=securities_universe_prices_df[short_stocks],
                                          weights=weights, commission=self.commission,
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

        assets_to_long, assets_to_short = self.generate_assets_to_trade(datetime.now())
        # TODO long for now, improve optimization to include diff constraints
        weights = self.portfolio_allocation(portfolio=Portfolio(assets_to_long)).solve_weights()
        broker.place_order(symbol='AAPL', side='buy')
        current_positions = broker.list_positions()
        for position in current_positions:
            print(position)
        broker.place_order()


def sort_df(df, column_idx, key):
    '''Takes dataframe, column index and custom function for sorting,
    returns dataframe sorted by this column using this function'''

    col = df.iloc[:, column_idx]
    temp = np.array(col.values.tolist())
    order = sorted(range(len(temp)), key=lambda j: key(temp[j]))
    return df.iloc[order]


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
    stock_screener = StockScreener(securities_universe=config.MarketIndices.DOW_JONES)
    stock_screener.filter_by_comparison_to_number(partial(price_to_earnings, period='FY'), '>', 5)
    stock_screener.filter_by_market(filter=config.GICS_Sectors.INFORMATION_TECHNOLOGY)
    stock_screener.run()


    # # TODO percentile_against_macro
    #
    # lower_bounds = pd.Series(data=[40], index=['Alpha'])
    # upper_bounds = pd.Series(data=[80], index=['MKT'])
    # stock_screener.filter_by_exposure_from_factor_model(factor_model=FactorModels.CAPM,
    #                                                     lower_bounds=lower_bounds, upper_bounds=upper_bounds)
    # stock_screener.run(date=datetime(2018, 1, 1))
    # print(stock_screener.stocks)

    class Alainps(Strategy):
        def is_time_to_reschedule(self, current_date, last_rebalancing_day):
            return (current_date - last_rebalancing_day).days > config.RebalancingFrequency.QUARTERLY.value

        def allocation_regime(self, portfolio: Portfolio):
            return PostModernPortfolioTheory(portfolio).solve_weights(risk_metric=sharpe_ratio, objective='maximize')


    strategy = Alainps(starting_date=datetime(2019, 1, 1), ending_date=datetime(2020, 12, 1),
                       starting_capital=50000, stock_screener=stock_screener,
                       max_stocks_count_in_portfolio=12, net_exposure=(100, 0))

    strategy.historical_simulation()

    # API_KEY_ID = 'PKOG800MQG7J30EZ1PJ0'
    # API_SECRET_KEY = 'MED9IwqKOfZ1HYNa4Iy5BeJoR3yEPaP5d34TwnxY'
    # API_ENDPOINT = 'https://paper-api.alpaca.markets'
    # alpaca = AlpacaBroker(key_id=API_KEY_ID, secret_key=API_SECRET_KEY, endpoint=API_ENDPOINT)
    # strategy.broker_deployment(broker=alpaca)
