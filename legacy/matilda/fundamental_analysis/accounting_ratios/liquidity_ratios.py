'''
Liquidity ratios are financial ratios that measure a company’s ability to repay both short- and long-term obligations.
'''
from datetime import timedelta
from matilda.fundamental_analysis.supporting_metrics import *
from matilda.fundamental_analysis.financial_statements import *

def current_ratio(stock, date=None, lookback_period=timedelta(days=0), period: str = 'Q') -> float:
    """
    The **current ratio** measures a company’s ability to pay off short-term liabilities with current assets.
    It is thus a *liquidity ratio*.

    .. note::
        A **healthy range** for the `current_ratio` is between 1.2 and 2. However, this varies between industries,
        so a good practice would be to use it as a relative metric, comparing a company against its industry
        (in terms of percentile, how far from the average...).

    :param stock:
        Ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be
        * a *datetime* (i.e. datetime(2019, 1, 1)),
        * a *list of datetimes* (for certain points in time i.e. [datetime(2018, 6, 1), datetime(2019, 8, 3), datetime(2020, 1, 1)]),
        * a *tuple of two datetimes* (for a range between them i.e. (datetime(2018, 6, 1), datetime(2020, 1, 1)).

        It doesn't need to be the exact date of reporting, as it will look for the closest from that date.
        The most recent date of reporting from that date will be used. By default, date=datetime.now().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :return: .. math:: \\text{Current Ratio} = \\frac{\\text{Current Assets}}{\\text{Current Liabilities}}


    """
    return total_current_assets(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / total_current_liabilities(stock=stock, date=date, lookback_period=lookback_period, period=period)


def acid_test_ratio(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    """
    The acid-test ratio (or quick ratio) measures a company’s ability to pay off short-term liabilities with quick assets

    * *Category:* Liquidity Ratio
    * *Healthy Range:*

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetime.now().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :return: .. math:: \\text{Acid-Test Ratio} = \\frac{\\text{Liquid Assets}}{\\text{Current Liabilities}}
    """
    return liquid_assets(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / total_current_liabilities(stock=stock, date=date, lookback_period=lookback_period, period=period)


def cash_ratio(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    """
    The cash ratio measures a company’s ability to pay off short-term liabilities with cash and cash equivalents

    * *Category:* Liquidity Ratio
    * *Healthy Range:*

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetime.now().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :return: .. math:: \\text{Cash Ratio} = \\frac{\\text{Cash and Cash equivalents + Current Marketable Securities}}{\\text{Current Liabilities}}
    """
    return (cash_and_cash_equivalents(stock=stock, date=date, lookback_period=lookback_period, period=period)
            + current_marketable_securities(stock=stock, date=date, lookback_period=lookback_period, period=period)) \
           / total_current_liabilities(stock=stock, date=date, lookback_period=lookback_period, period=period)


def operating_cash_flow_ratio(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    """
    The operating cash flow ratio is a measure of the number of times a company can pay off current liabilities with the cash generated in a given period

    * *Category:* Liquidity Ratio
    * *Healthy Range:*

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetime.now().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :return: .. math:: \\text{Operating Cash Flow Ratio} = \\frac{\\text{Operating Cash Flow}}{\\text{Current Liabilities}}
    """
    return cash_flow_operating_activities(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / total_current_liabilities(stock=stock, date=date, lookback_period=lookback_period, period=period)
