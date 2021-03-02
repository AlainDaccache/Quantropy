from datetime import timedelta, datetime
from functools import partial
from typing import Callable

import numpy as np
from scipy import stats

from matilda import total_assets


def mean_over_time_intervals(metric, how_many_periods=5, geometric=False, interval=timedelta(days=90)):
    """

    :param metric: partially applied function, accepting stock, date, lookback period, and period.
    :param interval:
    :param how_many_periods:
    :param geometric:
    :return:
    """
    metrics = [metric(lookback_period=timedelta(days=metric.keywords['lookback_period'].days +
                                                     interval.days * i)) for i in range(how_many_periods + 1)]
    return np.mean(metrics) if not geometric else stats.gmean(metrics)


def mean_metric_growth_rate(metric, periods: int = 5, lookback_period=timedelta(days=0), period: str = 'FY',
                            weighted_average=False):
    """
    If the metric computes to [1, 2, 3, 4, 5] at different points in time, the mean growth rate is
    the mean of [1, (2-1)/1, (3-2)/2, (4-3)/3, (5-4)/4]

    :param metric:
    :param periods:
    :param lookback_period:
    :param period:
    :param weighted_average:
    :return:
    """
    def average_growth_over_time(lst):  # assumes order from left to right chronological
        growths = [(lst[i] - lst[i - 1]) / lst[i - 1] for i in range(1, len(lst))]
        return np.mean(growths)

    ls = [metric(lookback_period=lookback_period - timedelta(days=365 * i if period == 'FY' else 90 * i))
          for i in range(0, periods)]
    return average_growth_over_time(ls[::-1])  # reverse since the most recent is first, but should be last


def percentile_against_macro(metric, against: str):
    '''
    Compare across competitors

    :param against: industry, sector, market, exchange, index...
    :return:
    '''
    if against == 'industry':
        stock_macro = macroeconomic_analysis.company_industry(ticker=metric.keywords['stock'],
                                                              date=metric.keywords['date'])
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


class VisualizationMetricsHelpers:
    def __init__(self):
        pass

    def balance_sheet_evolution(self, stock: str, from_date: datetime, to_date=datetime.today()):
        dates = [to_date - timedelta(days=x) for x in range()]
        assets = total_assets(stock=stock, date=dates, )


if __name__ == '__main__':
    helpers = NumericalMetricsHelpers(stock='AAPL', date=datetime.now(), metric=total_assets)
    print(helpers.percentile_against_macro('sector'))
