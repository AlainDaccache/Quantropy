from datetime import timedelta

from matilda.fundamental_analysis.accounting_ratios import *

'''
Profitability ratios measure a company’s ability to generate income relative to revenue, balance sheet assets, operating costs, and equity. 
'''


def net_profit_margin(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'FY'):
    """

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetinow().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.

    :return: .. math:: \\text{Net Profit Margin} = \\frac{\\text{Net Income}}{\\text{Net Sales}}
    """

    return net_income(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / net_sales(stock=stock, date=date, lookback_period=lookback_period, period=period)


def gross_profit_margin(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'FY'):
    """
    The gross margin ratio compares the gross profit of a company to its net sales to show how much profit a company makes after paying its cost of goods sold

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetinow().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.

    :return: .. math:: \\text{Gross Margin Ratio} = \\frac{\\text{Gross Profit}}{\\text{Net Sales}}
    """

    return gross_profit(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / net_sales(stock=stock, date=date, lookback_period=lookback_period, period=period)


def operating_profit_margin(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'FY'):
    """
    The operating margin ratio compares the operating income of a company to its net sales to determine operating efficiency

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetinow().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.

    :return: .. math:: \\text{Operating Margin Ratio} = \\frac{\\text{Operating Income}}{\\text{Net Sales}}
    """
    return operating_income(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / net_sales(stock=stock, date=date, lookback_period=lookback_period, period=period)


def return_on_assets(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'FY'):
    """
    The return on assets ratio measures how efficiently a company is using its assets to generate profit

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetinow().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.

    :return: .. math:: \\text{Return on Assets} = \\frac{\\text{Net Income}}{\\text{Total Assets}}
    """
    return net_income(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / total_assets(stock=stock, date=date, lookback_period=lookback_period, period=period)


def return_on_equity(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'FY'):
    """
    The return on equity ratio measures how efficiently a company is using its equity to generate profit

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetinow().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.

    :return: .. math:: \\text{Return on Equity} = \\frac{\\text{Net Income}}{\\text{Shareholder’s equity}}
    """
    return net_income(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / total_shareholders_equity(stock=stock, date=date, lookback_period=lookback_period, period=period)


def return_on_net_assets(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'FY'):
    """

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetinow().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.

    :return: .. math:: \\text{Return on Net Assets} = \\frac{\\text{Net Income}}{\\text{Fixed Assets + Working Capital}}
    """
    return net_income(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / (net_property_plant_equipment(stock=stock, date=date, lookback_period=lookback_period, period=period)
              + net_working_capital(stock=stock, date=date, lookback_period=lookback_period, period=period))


def return_on_invested_capital(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'FY',
                               invested_capital_operating_approach=True):
    """

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetinow().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.

    :param invested_capital_operating_approach:
    :return: .. math:: \\text{Return on Invested Capital} = \\frac{\\text{NOPAT}}{\\text{Invested Capital}}
    """
    return net_operating_profit_after_tax(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / invested_capital(stock=stock, date=date, lookback_period=lookback_period, period=period,
                              operating_approach=invested_capital_operating_approach)


def return_on_capital_employed(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'FY'):
    """

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetinow().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :return: .. math:: \\text{Return on Capital Employed} = \\frac{\\text{EBIT}}{\\text{Capital Employed}}
    """
    return earnings_before_interest_and_taxes(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / capital_employed(stock=stock, date=date, lookback_period=lookback_period, period=period)


def cash_flow_return_on_investment(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                                   period: str = 'FY'):
    """

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetinow().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :return:  .. math:: \\text{Cash Flow Return on Investment} = \\frac{\\text{Cash Flow}}{\\text{Market Recapitalisation}}
    """
    pass


def efficiency_ratio(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'FY'):
    """

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetinow().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :return: .. math:: \\text{Efficiency Ratio} = \\frac{\\text{Non-Interest Expense}}{\\text{Revenue}}
    """
    pass


def net_gearing(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'FY'):
    """

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetinow().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :return: .. math:: \\text{Net Gearing} = \\frac{\\text{Net Debt}}{\\text{Equity}}
    """
    pass


def basic_earnings_power(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'FY'):
    """

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetinow().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :return: .. math:: \\text{} = \\frac{\\text{}}{\\text{}}
    """
    pass
