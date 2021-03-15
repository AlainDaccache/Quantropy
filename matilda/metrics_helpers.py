import re
from datetime import timedelta, datetime
from functools import partial
from typing import Callable

import numpy as np
from scipy import stats

from matilda import total_assets, earnings_per_share
from matilda.data_pipeline.db_crud import *


def mean_over_time(metric, how_many_periods=5, geometric=False, interval=timedelta(days=90)):
    """
    Mean over time intervals
    :param metric: partially applied function, accepting stock, date, lookback period, and period.
    :param interval:
    :param how_many_periods:
    :param geometric:
    :return:
    """
    lookback_period = metric.keywords['lookback_period'].days if 'lookback_period' in metric.keywords else 0
    metrics = [metric(
        lookback_period=timedelta(days=(lookback_period + interval.days * i)))
        for i in range(how_many_periods + 1)]
    return np.mean(metrics) if not geometric else stats.gmean(metrics)


def mean_metric_growth_rate(metric, stock, date, periods: int = 5, lookback_period=timedelta(days=0),
                            interval: str = 'Y-Y', weighted_average=False):
    """
    The average growth rate from period to period.

    If the metric computes to [1, 2, 3, 4, 5] at different points in time, the mean growth rate is
    the mean of [1, (2-1)/1, (3-2)/2, (4-3)/3, (5-4)/4]

    :param metric:
    :param periods:
    :param lookback_period:
    :param interval: 'Y-Y' for Year-to-Year, 'Q-Q' for Quarter-to-Quarter
    :param weighted_average:
    :return:
    """

    def average_growth_over_time(lst):  # assumes order from left to right chronological
        growths = [(lst[i] - lst[i - 1]) / lst[i - 1] for i in range(1, len(lst))]
        return np.mean(growths)

    multiplier = 365 if interval == 'Y-Y' else 90 if interval == 'Q-Q' else Exception('Invalid interval')
    ls = [metric(
        stock=stock, date=date,
        lookback_period=timedelta(days=lookback_period.days + multiplier * i))
        for i in range(0, periods + 1)]
    return average_growth_over_time(ls[::-1])  # reverse since the most recent is first, but should be last


def compare_against_macro(metric, stock, against, date=None,
                          fn=lambda metric_stock, metric_in_macro: stats.percentileofscore(
                              metric_in_macro, metric_stock)):
    '''
    Compare across competitors. By default returns percentile.
    Can also just return average of macro by changine fn.

    :param against: config.GICS_Sectors, config.SIC_Sectors, config.GICS_Industries, config.SIC_Industries,
                    config.MarketIndices, config.Exchanges, config.Regions
    :return:
    '''

    enum_str_pairs = {config.GICS_Sectors: 'gics_sector', config.SIC_Sectors: 'sic_sector',
                      config.GICS_Industries: 'gics_indsutry', config.SIC_Industries: 'sic_industry',
                      config.Regions: 'location', config.Exchanges: 'exchange', config.MarketIndices: ''}
    classification = get_company_classification(stock=stock)[enum_str_pairs[against]]
    stocks_in_macro = companies_in_classification(class_=against(classification), date=date)
    metric_applied_in_macro = list(map(lambda ticker: metric(ticker, date), stocks_in_macro))
    metric_applied_to_stock = metric(stock, date)
    # np.percentile(metric_applied_in_industry, metric_applied_to_stock)
    return fn(metric_applied_to_stock, metric_applied_in_macro)


if __name__ == '__main__':
    # metric = partial(total_assets, stock='AAPL')
    # print(mean_over_time(metric=metric))
    # print(percentile_against_macro(metric=metric, against='industry'))
    # print(mean_metric_growth_rate(metric=earnings_per_share,
    #                               stock='AAPL', date=datetime.now(), interval='Y-Y', periods=1))
    print(compare_against_macro(metric=total_assets, stock='AAPL', against=config.SIC_Industries,
                                fn=lambda metric_stock, metric_in_macro: mean(metric_in_macro))
          )
