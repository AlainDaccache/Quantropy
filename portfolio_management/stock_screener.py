from datetime import datetime
from enum import Enum
from pprint import pprint
from functools import partial
from config import MarketIndices, Exchanges, GICS_Sectors, SIC_Industries, GICS_Industries, Regions, SIC_Sectors
from portfolio_management.Portfolio import Portfolio, TimeDataFrame
from quantitative_analysis.risk_factor_modeling.asset_pricing_model import FactorModels

import pandas as pd
import macroeconomic_analysis.macroeconomic_analysis as macro
import fundamental_analysis.accounting_ratios as ratios
import inspect
import typing


def helper_condition(metric, comparator, otherside):
    def compare(x, comparator, y):
        if comparator == '>':
            return x > y
        elif comparator == '<':
            return x < y
        elif comparator == '=':
            return x == y
        elif comparator == '>=':
            return x >= y
        elif comparator == '<=':
            return x <= y

    if callable(otherside):  # we're comparing to another metric
        return lambda ticker, date: compare(metric(ticker, date), comparator, otherside(ticker, date))
    else:  # we're comparing to a value
        return lambda ticker, date: compare(metric(ticker, date), comparator, otherside)


class StockScreener:
    def __init__(self, securities_universe=None, date=datetime.now()):
        '''

        :param securities_universe:     by default, we start with the S&P 500, due to current functionality.
                                        It stays constant throughout the `StockScreener`, which is why we
                                        separate it from the `stocks` attribute.
        :param date: by default, now.
        '''

        self.securities_universe = securities_universe  # starting universe

        if securities_universe is None:
            self.stocks = macro.companies_in_index(MarketIndices.SP_500, date=date)
        else:
            self.stocks = securities_universe

        self.date = date
        self.conditions = []
        self.dataframe = pd.DataFrame()

    def run(self, conditions=None, date: datetime = datetime.now()):
        """
        Date setter. Reapply the conditions you applied so far, to any date

        :param conditions:  list of tuples, the first element of which is the `filter` function, and the rest
                            being the arguments. By default, the conditions already applied by the `StockScreener` object.
        :param date: datetime to which we need to apply the conditions. By default, now.
        :return:
        """
        new_screener = StockScreener(securities_universe=self.securities_universe, date=date)
        if conditions is None:
            conditions = self.conditions
        for condition in conditions:
            method_name = condition[0].__name__
            arg_names = inspect.getfullargspec(condition[0]).args
            arg_values = [new_screener] + list(condition)[1:]
            if 'date' in arg_names:
                arg_values.append(date)
            fn = partial(condition[0])
            for arg_name, arg_value in zip(arg_names, arg_values):
                fn.keywords[arg_name] = arg_value
                # fn = partial(fn, arg_name=arg_value)
            output = fn()
            print(f'{method_name} cur_stocks={output}')
        return new_screener.stocks

    def filter_by_market(self, filter):
        """
        If another market already exists, then we reapply the conditions of the `StockScreener` so far
        to the new market, and do a *union* (instead of an *intersection*) with the current filtered stocks.

        :param filter:  object of type `Regions`, `Exchanges`, `MarketIndices`, `SIC_Sectors`,
                        `GICS_Sectors`, `SIC_Industries`, or `GICS_Industries`
        :return: list of companies satisfying conditions so far in additional to market filter.

        """

        # TODO DO UNION BETWEEN, AND INTERSECTION WITHIN

        if isinstance(filter, Regions):
            companies_ = macro.companies_in_location(location=filter, date=self.date)

        elif isinstance(filter, Exchanges):
            companies_ = macro.companies_in_exchange(exchange=filter, date=self.date)

        elif isinstance(filter, MarketIndices):
            companies_ = macro.companies_in_index(market_index=filter, date=self.date)

        elif isinstance(filter, SIC_Sectors) or isinstance(filter, GICS_Sectors):
            companies_ = macro.companies_in_sector(sector=filter, date=self.date)

        elif isinstance(filter, SIC_Industries) or isinstance(filter, GICS_Industries):
            companies_ = macro.companies_in_industry(industry=filter, date=self.date)

        else:
            raise Exception("'filter' doesn't match any Region, Exchange, Market Index, Sector, or Industry")

        self.stocks = list(set(self.stocks).intersection(companies_))
        self.conditions.append((StockScreener.filter_by_market, filter))
        return self.stocks

    def filter_by_comparison_to_number(self, metric: partial, comparator: str, number: float):
        self.stocks = [stock for stock in self.stocks if
                       helper_condition(metric, comparator, number)(stock, self.date)]
        self.conditions.append((StockScreener.filter_by_comparison_to_number, metric, comparator, number))
        return self.stocks

    def filter_by_comparison_to_other_metric(self, metric: partial, comparator: str, other_metric: typing.Callable):
        self.stocks = [stock for stock in self.stocks if
                       helper_condition(metric, comparator, other_metric)(stock, self.date)]
        self.conditions.append(
            partial(StockScreener.filter_by_comparison_to_other_metric, metric, comparator, other_metric))
        return self.stocks

    def filter_by_exposure_from_factor_model(self, factor_model, lower_bounds: pd.Series, upper_bounds: pd.Series,
                                             benchmark_returns=None, regression_period: int = 36):
        """

        :param factor_model:
        :param lower_bounds: pd.Series of floats between 0 and 100, each representing a factor exposure.
            Example: lower_bounds = pd.Series(data=[80], index=['Alpha'])
        :param upper_bounds: pd.Series of floats between 0 and 100, each representing a factor exposure.
            Example: upper_bounds = pd.Series(data=[60, 90], index=['MKT', 'Alpha'])
        :param benchmark_returns:
        :param regression_period:
        :param frequency:
        :return:
        """

        if not isinstance(factor_model, FactorModels):
            raise Exception('Factor model should be of type `FactorModels`')

        self.conditions.append((StockScreener.filter_by_exposure_from_factor_model, factor_model,
                                lower_bounds, upper_bounds, benchmark_returns, regression_period))

        regression_dict = {}
        factor_model = factor_model.value(to_date=self.date)

        for stock in self.stocks:
            regression = factor_model.regress_factor_loadings(portfolio=TimeDataFrame(stock),
                                                              benchmark_returns=benchmark_returns,
                                                              regression_window=regression_period, rolling=False,
                                                              show=False)

            regression_dict[stock] = regression.params
        regression_df = pd.DataFrame(data=regression_dict)
        regression_df.rename(index={'Intercept': 'Alpha'}, inplace=True)
        # min-max normalize and scale
        normalized_df = regression_df.apply(func=lambda x: 100 * (x - min(x)) / (max(x) - min(x)), axis=1)
        for idx, factor in lower_bounds.iteritems():
            normalized_df = normalized_df.loc[:, normalized_df.loc[idx] >= factor]
        for idx, factor in upper_bounds.iteritems():
            normalized_df = normalized_df.loc[:, normalized_df.loc[idx] <= factor]
        return list(regression_df.columns)

    def filter_by_institutional_ownership_percentage(self, cutoff):
        pass

    def filter_by_institutional_holdings(self, institutions):
        pass

    def undo_condition(self, condition: typing.Callable, args):
        self.conditions.remove((condition, args))
        # re-add them
        stocks_that_meet_condition = condition(args)
        self.stocks.append(stocks_that_meet_condition)
        for condition, args in self.conditions:
            condition(args)

    def render_dataframe(self, columns=None, date=datetime.now()):
        """
        :param columns: Can enter one value for template:
            * 'Technical': ['Open', 'High', 'Low', 'Close', 'Volume', 'Change']
            * 'Valuation': ['Last', 'Market Cap', 'P/E', 'Price/Rev', 'EPS', 'EV/EBITDA']
        :param date:
        :return:
        """
        if columns is None:
            columns = [[partial(ratios.price_to_earnings, period='FY'),
                        partial(ratios.earnings_per_share, period='FY')]]

        stock_screener_dict = {stock: {metric.func.__name__: metric(stock, date)}
                               for stock in self.stocks
                               for metric in columns}
        stock_screener_df = pd.DataFrame.from_dict(stock_screener_dict, orient='index')

        return stock_screener_df


if __name__ == '__main__':
    stock_screener = StockScreener(securities_universe=['AAPL', 'AMGN', 'AXP', 'BA', 'CAT'])
    stock_screener.filter_by_comparison_to_number(partial(ratios.price_to_earnings, period='FY'), '>', 5)
    print(stock_screener.stocks)
    stock_screener.filter_by_market(filter=GICS_Sectors.INFORMATION_TECHNOLOGY)
    print(stock_screener.stocks)
    stock_screener.run(date=datetime(2018, 1, 1))
    lower_bounds = pd.Series(data=[40], index=['Alpha'])
    upper_bounds = pd.Series(data=[80], index=['MKT'])
    stock_screener.filter_by_exposure_from_factor_model(factor_model=FactorModels.CAPM,
                                                        lower_bounds=lower_bounds, upper_bounds=upper_bounds)
    print(stock_screener.stocks)
