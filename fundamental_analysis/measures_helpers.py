from datetime import timedelta
from functools import partial
from typing import Callable
import numpy as np
from fundamental_analysis import accounting_ratios


def average(stock: str, metric: partial, how_many_periods: int = 5, intervals: timedelta = timedelta(days=90),
            weighted=False):
    lookback_period = metric.keywords['lookback_period']
    metrics = [metric(stock=stock, lookback_period=timedelta(days=lookback_period.days + intervals.days * i)) for i in
               range(how_many_periods + 1)]
    return np.mean(metrics)


average(stock='AAPL',
        metric=partial(accounting_ratios.price_to_earnings_ratio, annual=True, ttm=False,
                       lookback_period=timedelta(days=90)),
        how_many_periods=5, intervals=timedelta(days=365))


def growth_rate(stock: str, metric: Callable, how_many_years: int = 5, compound=True):
    pass


# against: 'industry', 'sector', 'market'
def comparison(stock: str, metric: partial, against: str = 'industry'):
    pass
