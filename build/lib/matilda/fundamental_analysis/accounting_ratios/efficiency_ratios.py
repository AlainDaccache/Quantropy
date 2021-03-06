from datetime import timedelta
from matilda.fundamental_analysis.supporting_metrics import *
from matilda.fundamental_analysis.financial_statements import *

'''
Efficiency ratios, also known as activity financial ratios, are used to measure how well a company is utilizing its assets and resources.
'''


def degree_of_operating_leverage(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'FY'):
    """

    .. warning::
        Currently nonfunctional. Refrain from using for now. Need to collect more data.

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetime.now().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :return: .. math:: \\text{Degree of Operating Leverage} = \\frac{\\text{}}{\\text{}}
    """
    pass


def asset_turnover_ratio(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'FY'):
    """
    The asset turnover ratio measures a company’s ability to generate sales from assets.

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetime.now().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :return: .. math:: \\text{Asset Turnover Ratio} = \\frac{\\text{Net Sales}}{\\text{Total Assets}}
    """
    return net_sales(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / total_assets(stock=stock, date=date, lookback_period=lookback_period, period=period)


def accounts_payables_turnover_ratio(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                                     period: str = 'FY'):
    """
    The accounts payables turnover ratio measures the number of times the company pays off all its creditors in one year.

    * *Category*: Efficiency (Activity) Ratio
    * *Subcategory*: Accounts Payable

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetime.now().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :return:  .. math:: \\text{Accounts Payables Turnover Ratio} = \\frac{\\text{Cost of Goods Sold}}{\\text{Average Accounts Payable}}
    """
    return cost_of_goods_services(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / accounts_payable(stock=stock, date=date, lookback_period=lookback_period, period=period)


def payables_conversion_period(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'FY',
                               number_of_days=365):
    """
    The payables conversion period, or Days Payable Outstanding (DPO), is the average number of days of payables.
    For instance, a conversion period of 30 means that on average, the company takes 30 days to pay its creditors.
    It is an element of the cash conversion cycle.

    * *Category*: Efficiency (Activity) Ratio
    * *Subcategory*: Accounts Payable

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetime.now().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :param number_of_days: Number of days in period. By default the period is 365 days, but some analysts use 360.
    :return: .. math:: \\text{Payables Conversion Period} = \\frac{\\text{365}}{\\text{Payables Turnover}}
    """
    return number_of_days / accounts_payables_turnover_ratio(stock=stock, date=date, lookback_period=lookback_period,
                                                             period=period)


def inventory_turnover_ratio(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'FY'):
    """
    The inventory (or stock) turnover ratio measures how many times a company’s inventory is sold and replaced over a given period

    * *Category*: Efficiency (Activity) Ratio
    * *Subcategory*: Inventory

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetime.now().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :return: .. math:: \\text{Inventory Turnover Ratio} = \\frac{\\text{Cost of Goods Sold}}{\\text{Average Inventory}}
    """
    return cost_of_goods_services(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / net_inventory(stock=stock, date=date, lookback_period=lookback_period, period=period)


def inventory_conversion_period(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'FY',
                                number_of_days=365):
    """
    The inventory conversion period, or days inventory outstanding (DIO), measures the average number of days that a
    company holds on to inventory before selling it to customers. It is an element of the cash conversion cycle.

    * *Category*: Efficiency (Activity) Ratio
    * *Subcategory*: Inventory

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetime.now().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :param number_of_days: Number of days in period. By default the period is 365 days, but some analysts use 360.
    :return: .. math:: \\text{Inventory Conversion Period} = \\frac{\\text{365}}{\\text{Inventory Turnover}}
    """
    return number_of_days / inventory_turnover_ratio(stock=stock, date=date, lookback_period=lookback_period,
                                                     period=period)


def accounts_receivables_turnover_ratio(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                                        period: str = 'FY'):
    """
    The accounts receivable turnover ratio measures how many times a company can turn receivables into cash over a given period

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetime.now().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :return: .. math:: \\text{Accounts Receivables Turnover Ratio} = \\frac{\\text{Net Credit Sales}}{\\text{Accounts Receivables}}
    """
    return net_credit_sales(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / net_accounts_receivable(stock=stock, date=date, lookback_period=lookback_period, period=period)


def average_collection_period(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'FY',
                              number_of_days=365):
    """

    The average collection period, or Days Sales Outstanding (DSO), represents the average number of days between the date a credit sale is made and the date the purchaser pays for that sale.
    It is an element of the cash conversion cycle.

    * *Category*: Efficiency (Activity) Ratio
    * *Subcategory*: Accounts Receivables

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetime.now().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :param number_of_days: Number of days in period. By default the period is 365 days, but some analysts use 360.

    :return: .. math:: \\text{Average Collection Period} = \\frac{\\text{365}}{\\text{Accounts Receivables Turnover Ratio}}
    """
    return number_of_days / accounts_receivables_turnover_ratio(stock=stock, date=date, lookback_period=lookback_period,
                                                                period=period)


def cash_conversion_cycle(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'FY'):
    """
    The cash conversion cycle (CCC) is a metric that expresses the time (measured in days) it takes for a company to
    convert its investments in inventory and other resources into cash flows from sales

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetime.now().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :return: .. math:: \\text{Cash Conversion Cycle} = \\text{Days Inventory Outstanding} + \\text{Days Sales Outstanding} + \\text{Days Payable Outstanding}
    """
    return inventory_conversion_period(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           + average_collection_period(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           - payables_conversion_period(stock=stock, date=date, lookback_period=lookback_period, period=period)
