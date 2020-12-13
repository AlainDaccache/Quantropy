import typing
from datetime import datetime
from enum import Enum
from functools import partial
import pandas as pd
import macroeconomic_analysis.macroeconomic_analysis as macro
import fundamental_analysis.accounting_ratios as ratios
from config import MarketIndices, Exchanges, GICS_Sectors, Industries, Regions, SIC_Sectors
from portfolio_management.Portfolio import Portfolio
from quantitative_analysis.risk_factor_modeling import AssetPricingModel


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
    def __init__(self):
        '''

        :param stocks: either a list, or a MarketIndices, or Exchanges, or Regions object (to avoid survivorship
            bias when selecting a date to filter)
        :param columns: Can enter one value for template:
            * 'Technical': ['Open', 'High', 'Low', 'Close', 'Volume', 'Change']
            * 'Valuation': ['Last', 'Market Cap', 'P/E', 'Price/Rev', 'EPS', 'EV/EBITDA']
        :param date:
        '''
        self.stocks = macro.companies_in_index(MarketIndices.SP_500)  # starting universe
        self.conditions = []
        self.dataframe = pd.DataFrame()

    def run(self, conditions=None, date: datetime = datetime.now()):
        if conditions is None:
            conditions = self.conditions
        for condition in conditions:
            args = condition[1:]
            fn = condition[0](args)

    def filter_by_market(self, region):

        if not isinstance(region, Regions):
            raise Exception

        companies_ = macro.companies_in_location(location=region.value)
        self.stocks = list(set(self.stocks).intersection(companies_))
        self.conditions.append((self.filter_by_market, region.value))
        return self.stocks

    def filter_by_exchange(self, exchange):
        if not isinstance(exchange, Exchanges):
            raise Exception

        companies_ = macro.companies_in_exchange(exchange=exchange.value)
        self.stocks = list(set(self.stocks).intersection(companies_))
        self.conditions.append((self.filter_by_exchange, exchange.value))
        return self.stocks

    def filter_by_market_index(self, market_index):
        if not isinstance(market_index, MarketIndices):
            raise Exception

        companies_ = macro.companies_in_index(market_index=market_index.value)
        self.stocks = list(set(self.stocks).intersection(companies_))
        self.conditions.append((self.filter_by_market_index, market_index.value))
        return self.stocks

    def filter_by_sector(self, sector):

        if not (isinstance(sector, SIC_Sectors) or isinstance(sector, GICS_Sectors)):
            raise Exception

        companies_ = macro.companies_in_sector(sector=sector)
        self.stocks = list(set(self.stocks).intersection(companies_))
        self.conditions.append((self.filter_by_sector, sector.value))
        return self.stocks

    def filter_by_industry(self, industry: Industries):

        if not isinstance(industry, Industries):
            raise Exception

        companies_ = macro.companies_in_industry(industry=industry.value)
        self.stocks = list(set(self.stocks).intersection(companies_))
        self.conditions.append((self.filter_by_industry, industry.value))
        return self.stocks

    def filter_by_comparison_to_number(self, metric: partial, comparator: str, number: float, date=None):
        if date is not None:
            self.stocks = [stock for stock in self.stocks if
                           helper_condition(metric, comparator, number)(stock, date)]
        self.conditions.append((self.filter_by_comparison_to_other_metric, metric, comparator, number))
        return self.stocks

    def filter_by_comparison_to_other_metric(self, metric: partial, comparator: str, other_metric: typing.Callable,
                                             date=None):
        if date is not None:
            self.stocks = [stock for stock in self.stocks if
                           helper_condition(metric, comparator, other_metric)(stock, date)]
        self.conditions.append((self.filter_by_comparison_to_other_metric, metric, comparator, other_metric))
        return self.stocks

    def filter_by_exposure_from_factor_model(self, factor_model: AssetPricingModel,
                                             lower_bounds: typing.List, upper_bounds: typing.List,
                                             benchmark_returns=None, regression_period: int = 36):
        """

        :param factor_model:
        :param lower_bounds: List of ints between 0 and 100, each representing a factor exposure.
        Make sure they are in the order of the factor dataframe. If don't want to filter by a  certain factor, just put 0
        :param upper_bounds: List of ints between 0 and 100, each representing a factor exposure.
        Make sure they are in the order of the factor dataframe. If don't want to filter by a certain factor, just put 100
        :param benchmark_returns:
        :param regression_period:
        :param frequency:
        :return:
        """
        regression_dict = {}
        portfolio = Portfolio(assets=self.stocks)
        for stock in self.stocks:
            regression = factor_model.regress_factor_loadings(portfolio=portfolio, benchmark_returns=benchmark_returns,
                                                              regression_window=regression_period, rolling=False)

            regression_dict[stock] = {factor[0]: factor[1] for factor in regression.params}
        regression_df = pd.DataFrame.from_dict(data=regression_dict, orient='index')
        # min-max normalize and scale
        regression_df = regression_df.apply(func=lambda x: 100 * (x - min(x) / (max(x) - min(x))), axis=0)
        for idx, factor in enumerate(regression_df.columns):
            regression_df = regression_df[regression_df[factor] > lower_bounds[idx]
                                          & regression_df[factor] < upper_bounds[idx]]
        self.conditions.append((self.filter_by_exposure_from_factor_model, factor_model, lower_bounds, upper_bounds,
                                benchmark_returns, regression_period))
        return list(regression_df.index)

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
        if columns is None:
            columns = [[partial(ratios.price_to_earnings, period='FY'),
                        partial(ratios.earnings_per_share, period='FY')]]

        stock_screener_dict = {stock: {metric.func.__name__: metric(stock, date)}
                               for stock in self.stocks
                               for metric in columns}
        stock_screener_df = pd.DataFrame.from_dict(stock_screener_dict, orient='index')

        return stock_screener_df


if __name__ == '__main__':
    stock_screener = StockScreener()
    # stock_screener.filter_by_exposure_from_factor_model(factor_model=FactorModels.FAMA_FRENCH_3,
    #                                                     factors=[''],
    #                                                     lower_bound=20, upper_bound=40, regression_period=36)
    # print(stock_screener.render_dataframe())
    stock_screener.filter_by_comparison_to_number(partial(ratios.price_to_earnings, period='FY'), '>', 20)
    print(stock_screener.stocks)
    stock_screener.filter_by_sector(sector=GICS_Sectors.INFORMATION_TECHNOLOGY)
    print(stock_screener.stocks)
