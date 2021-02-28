from datetime import timedelta, datetime
from functools import partial
from typing import Callable

import numpy as np
import matilda.accounting_ratios
from matilda.macroeconomic_analysis import macroeconomic_analysis
from scipy import stats
import pandas as pd
import matilda.fundamental_analysis.financial_statements_entries as fi


class VisualizationMetricsHelpers:
    def __init__(self):
        pass

    def balance_sheet_evolution(self, stock: str, from_date: datetime, to_date=datetime.today()):
        dates = [to_date - timedelta(days=x) for x in range()]
        assets = fi.total_assets(stock=stock, date=dates, )




class NumericalMetricsHelpers:
    def __init__(self, metric, stock, period, date=None):
        if not (isinstance(metric, Callable) or isinstance(metric, partial)):
            raise Exception
        self.metric = metric
        self.stock = stock
        self.date = date
        self.period = period

    # Helpers to compare across time
    def mean_over_time_intervals(self, how_many_periods: int = 5, geometric=False):
        lookback_period = self.metric.keywords['lookback_period']
        metrics = [self.metric(stock=self.stock, date=self.date,
                               lookback_period=timedelta(days=lookback_period.days + intervals.days * i)) for i
                   in range(how_many_periods + 1)]
        return np.mean(metrics) if not geometric else stats.gmean(metrics)

    def mean_metric_growth_rate(self, periods: int = 5, lookback_period=timedelta(days=0), period: str = 'FY',
                                weighted_average=False):
        def average_growth_over_time(lst):  # assumes order from left to right chronological
            growths = [(lst[i] - lst[i - 1]) / lst[i - 1] for i in range(1, len(lst))]
            return np.mean(growths)

        ls = [self.metric(stock=self.stock, date=self.date - timedelta(days=365 * i if period == 'FY' else 90 * i),
                          lookback_period=lookback_period, period=period)
              for i in range(0, periods)]
        return average_growth_over_time(ls[::-1])  # reverse

    # Helpers to compare across competition
    def percentile_against_macro(self, against: str):
        '''

        :param against: industry, sector, market, exchange, index...
        :return:
        '''
        if against == 'industry':
            stock_macro = macroeconomic_analysis.company_industry(ticker=self.stock, date=self.date)
            stocks_in_macro = macroeconomic_analysis.companies_in_industry(industry=stock_macro, date=self.date)
        elif against == 'sector':
            stock_macro = macroeconomic_analysis.company_sector(ticker=self.stock, date=self.date)
            stocks_in_macro = macroeconomic_analysis.companies_in_sector(sector=stock_macro, date=self.date)
        elif against == 'market':
            stock_macro = macroeconomic_analysis.company_location(ticker=self.stock, date=self.date)
            stocks_in_macro = macroeconomic_analysis.companies_in_location(location=stock_macro, date=self.date)
        else:
            return Exception
        metric_applied_in_macro = stocks_in_macro.map(lambda ticker: self.metric(ticker, self.date))
        metric_applied_to_stock = self.metric(self.stock, self.date)
        # np.percentile(metric_applied_in_industry, metric_applied_to_stock)
        return stats.percentileofscore(metric_applied_in_macro, metric_applied_to_stock)


if __name__ == '__main__':
    pass
    # helpers = FundamentalMetricsHelpers(stock='AAPL', date=datetime.now(), metric=price_to_earnings)
    # print(helpers.percentile_against_macro('sector'))
