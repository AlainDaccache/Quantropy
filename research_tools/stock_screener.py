import typing
from datetime import datetime
from enum import Enum
from functools import partial
import pandas as pd
import fundamental_analysis.macroeconomic_analysis as macro
import fundamental_analysis.accounting_ratios as ratios
from config import MarketIndices, Exchanges, GICS_Sectors, Industries, Regions, SIC_Sectors
import FactorBox.asset_pricing_models as pricing_model

'''
I. Market:
    * Region: USA...
    * Stock Exchange: NYSE, AMEX, NASDAQ...
    * Index: Dow Jones, S&P, Russell...
    * Industry: 
    * Sector: 
    * Market Capitalization
    
II. Technicals:
    Select timeframe for each: 1m, 5m, 15m, 1h, 4h, 1d, 1w, 1m, 1y
    * Performance: Change %, New High, New Low
    * Volatility: Beta, Standard Deviation
    * Indicators: Below, Below or Equal, Above, Above or Equal, Crosses, Crosses up, Crosses down, Between, Outside, Equal, Not Equal
        * 
    * Chart Patterns:
    * Candlestick Patterns: 

III. Fundamentals:
    Select timeframe for each: Fiscal Year (FY), Most Recent Quarter (MRQ), Trailing Twelve Months (TTM)
    * Financial Statements: 
        * Balance Sheet: 
        * Income Statement: 
        * Cash Flow Statement:
    * Accounting Ratios
        * 
    * Scores:
    
    * Valuation: 
    
Once Filtered, user selects template for columns (inspired from TradingView)
'''


class FactorModels(Enum):
    pass
    # CAPM = partial(pricing_model.capital_asset_pricing_model)
    # FAMA_FRENCH_3 = partial(pricing_model.fama_french_3_factor_model)
    # CARHART_4 = partial(pricing_model.carhart_4_factor_model)
    # FAMA_FRENCH_5 = partial(pricing_model.fama_french_5_factor_model)


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
    def __init__(self, stocks=None, columns=None, date=datetime.now()):
        '''

        :param stocks:
        :param columns: Can enter one value for template:
            * 'Technical': ['Open', 'High', 'Low', 'Close', 'Volume', 'Change']
            * 'Valuation': ['Last', 'Market Cap', 'P/E', 'Price/Rev', 'EPS', 'EV/EBITDA']
        :param date:
        '''
        self.stocks = stocks if stocks is not None else macro.companies_in_index(market_index='S&P-500')
        self.date = date
        self.conditions = []
        self.columns = columns if columns is not None else [[partial(ratios.price_to_earnings_ratio, period='Q'),
                                                             partial(ratios.earnings_per_share, period='Q')]]
        self.dataframe = pd.DataFrame()

    def filter_by_region(self, region):

        if not isinstance(region, Regions):
            raise Exception

        companies_ = macro.companies_in_location(location=region.value)
        self.stocks = list(set(self.stocks).intersection(companies_))
        self.conditions.append((self.filter_by_region, region.value))
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

        companies_ = macro.companies_in_sector(sector=sector.value)
        self.stocks = list(set(self.stocks).intersection(companies_))
        self.conditions.append((self.filter_by_sector, sector.value))
        return self.stocks

    def filter_by_industry(self, industry):

        if not isinstance(industry, Industries):
            raise Exception

        companies_ = macro.companies_in_industry(industry=industry.value)
        self.stocks = list(set(self.stocks).intersection(companies_))
        self.conditions.append((self.filter_by_industry, industry.value))
        return self.stocks

    def filter_by_metric_comparison(self, metric: partial, comparator: str, otherside):
        '''

        Example use: helper_condition(rsi, '>', 70)

        :param metric:
        :param comparator:
        :param otherside: might be a value or another metric
        :return:
        '''
        self.stocks = [stock for stock in self.stocks if
                       helper_condition(metric, comparator, otherside)(stock, self.date)]
        self.conditions.append((self.filter_by_metric_comparison, metric, comparator, otherside))
        return self.stocks

    def filter_by_exposure_from_factor_model(self, factor_model: FactorModels,
                                             lower_bound: int, upper_bound: int, regression_period: int = 36,
                                             frequency: str = 'Monthly', factors: typing.List = None):

        for stock in self.stocks:
            regression = factor_model.value(portfolio_returns=stock, regression_period=regression_period,
                                            frequency=frequency)
            print(regression)

    def filter_by_institutional_ownership_percentage(self, cutoff):
        pass

    def filter_by_institutional_holdings(self, institutions):
        pass

    def undo_condition(self, condition: typing.Callable, args):
        self.conditions.remove((condition, args))
        stocks_that_meet_condition = condition(args)
        self.stocks.append(stocks_that_meet_condition)
        for condition, args in self.conditions:
            condition(args)

    def render_dataframe(self):
        stock_screener_dict = {stock: {metric.func.__name__: metric(stock, self.date)}
                               for stock in self.stocks
                               for metric in self.columns}
        stock_screener_df = pd.DataFrame.from_dict(stock_screener_dict, orient='index')

        return stock_screener_df


if __name__ == '__main__':
    stock_screener = StockScreener(stocks=['AAPL', 'AMGN'])
    stock_screener.filter_by_exposure_from_factor_model(factor_model=FactorModels.FAMA_FRENCH_3,
                                                        factors=[''],
                                                        lower_bound=20, upper_bound=40, regression_period=36)
    print(stock_screener.render_dataframe())
    # stock_screener.filter_by_metric_comparison(partial(ratios.price_to_earnings_ratio, period='Q'), '>', 2)
    # print(stock_screener.stocks)
