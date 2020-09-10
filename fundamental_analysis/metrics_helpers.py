from datetime import timedelta, datetime
from functools import partial
from typing import Callable
import numpy as np
from fundamental_analysis import accounting_ratios, macroeconomic_analysis, supporting_metrics
from historical_data_collection import excel_helpers as excel
import pandas as pd
from scipy import stats
import fundamental_analysis.financial_statements_entries as fi


# def metric_per_share(metric: Callable, diluted_shares=False):
#     metric_args = 0
#     return metric() / fi.total_shares_outstanding(stock=stock, date=date, lookback_period=lookback_period,
#                                                   period=period,
#                                                   diluted_shares=diluted_shares)


def mean_over_time(stock: str, metric: partial, how_many_periods: int = 5, intervals: timedelta = timedelta(days=90),
                   geometric=False):
    '''
    Arithmetic mean by default

    :param stock:
    :param metric:
    :param how_many_periods:
    :param intervals:
    :param geometric:
    :return:
    '''
    lookback_period = metric.keywords['lookback_period']
    metrics = [metric(stock=stock, lookback_period=timedelta(days=lookback_period.days + intervals.days * i)) for i in
               range(how_many_periods + 1)]
    return np.mean(metrics) if not geometric else stats.gmean(metrics)


def average_growth_over_time(lst):  # assumes order from left to right chronological
    growths = [(lst[i] - lst[i - 1]) / lst[i - 1] for i in range(1, len(lst))]
    return np.mean(growths)


def metric_growth_rate(cash_flow_type: partial, stock, periods: int = 5, date=datetime.now(),
                       lookback_period=timedelta(days=0), period: str = 'FY', weighted_average=False):
    ls = [cash_flow_type(stock=stock, date=date - timedelta(days=365 * i if period == 'FY' else 90 * i),
                         lookback_period=lookback_period, period=period)
          for i in range(0, periods)]
    return average_growth_over_time(ls[::-1])  # reverse


def stock_macro_percentile(stock: str, metric: partial, against: str = 'industry'):
    '''

    :param stock:
    :param metric:
    :param against: 'industry', 'sector', 'market'
    :return:
    '''
    if against == 'industry':
        stock_macro = macroeconomic_analysis.company_industry(ticker=stock)
        stocks_in_macro = macroeconomic_analysis.companies_in_industry(industry=stock_macro)
    elif against == 'sector':
        stock_macro = macroeconomic_analysis.company_sector(ticker=stock)
        stocks_in_macro = macroeconomic_analysis.companies_in_sector(sector=stock_macro)
    else:
        return Exception
    metric_applied_in_macro = stocks_in_macro.map(lambda ticker: metric(ticker))
    metric_applied_to_stock = metric(stock)
    # np.percentile(metric_applied_in_industry, metric_applied_to_stock)
    return stats.percentileofscore(metric_applied_in_macro, metric_applied_to_stock)


if __name__ == '__main__':
    print(stock_macro_percentile('MSFT',
                                 metric=partial(accounting_ratios.price_to_earnings_ratio, period='FY'),
                                 against='sector'))
