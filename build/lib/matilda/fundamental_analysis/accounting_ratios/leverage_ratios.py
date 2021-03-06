from datetime import timedelta
from matilda.fundamental_analysis.supporting_metrics import *
from matilda.fundamental_analysis.financial_statements import *
'''
Leverage ratios measure the amount of capital that comes from debt. In other words, leverage financial ratios are used to evaluate a company’s debt levels.
'''


def debt_ratio(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    """
    The debt ratio measures the relative amount of a company’s assets that are provided from debt

    * *Category:* Leverage Ratio
    * *Healthy Range:*

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetinow().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :return: .. math:: \\text{Debt Ratio} = \\frac{\\text{Total Liabilities}}{\\text{Total Assets}}
    """
    return total_liabilities(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / total_assets(stock=stock, date=date, lookback_period=lookback_period, period=period)


def asset_to_equity(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    '''
    The asset/equity ratio indicates the relationship of the total assets of the firm to the part owned by shareholders (aka, owner's equity)

    * *Category:* Leverage Ratio
    * *Healthy Range:*

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetinow().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :return: .. math:: \\text{Asset to Equity Ratio} = \\frac{\\text{Total Assets}}{\\text{Shareholder’s equity}}
    '''
    total_assets_ = total_assets(stock=stock, date=date, lookback_period=lookback_period, period=period)
    total_equity_ = total_shareholders_equity(stock=stock, date=date, lookback_period=lookback_period, period=period)
    return total_assets_ / total_equity_


def debt_to_equity(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q',
                   only_interest_expense=False, all_liabilities=False, only_long_term_debt=True,
                   exclude_current_portion_long_term_debt=False):
    '''
    The debt to equity ratio calculates the weight of total debt and financial liabilities against shareholders’ equity

    * *Category:* Leverage Ratio
    * *Healthy Range:*

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetinow().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :param only_interest_expense:
    :param all_liabilities:
    :param only_long_term_debt:
    :param exclude_current_portion_long_term_debt:
    :return: .. math:: \\text{Debt to Equity Ratio} = \\frac{\\text{Total Liabilities}}{\\text{Shareholder’s equity}}
    '''
    return debt(stock=stock, date=date, lookback_period=lookback_period, period=period,
                   only_interest_expense=only_interest_expense, all_liabilities=all_liabilities,
                   long_term_debt=only_long_term_debt,
                   exclude_current_portion_long_term_debt=exclude_current_portion_long_term_debt) \
           / total_shareholders_equity(stock=stock, date=date, lookback_period=lookback_period, period=period)


def debt_to_capital(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q',
                    interest_expense=False, all_liabilities=False, long_term_debt=True):
    '''
    A company's debt-to-capital ratio or D/C ratio is the ratio of its total debt to its total capital, its debt and equity combined. The ratio measures a company's capital structure, financial solvency, and degree of leverage, at a particular point in ti

    * *Category:* Leverage Ratio
    * *Healthy Range:*

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetinow().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :param interest_expense:
    :param all_liabilities:
    :param long_term_debt:
    :return: .. math:: \\text{Debt to Capital Ratio} = \\frac{\\text{Debt}}{\\text{Debt + Shareholder’s equity}}
    '''
    total_debt = debt(stock=stock, date=date, lookback_period=lookback_period, period=period,
                         only_interest_expense=interest_expense, all_liabilities=all_liabilities,
                         long_term_debt=long_term_debt)

    return total_debt / (total_debt + total_shareholders_equity(stock=stock, date=date,
                                                                   lookback_period=lookback_period, period=period))


def interest_coverage(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                      period: str = ''):
    '''
    The interest coverage ratio shows how easily a company can pay its interest expenses

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetinow().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :return: .. math:: \\text{Interest Coverage Ratio} = \\frac{\\text{Operating Income}}{\\text{Interest Expenses}}
    '''
    return earnings_before_interest_and_taxes(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / interest_expense(stock=stock, date=date, lookback_period=lookback_period, period=period)


def debt_service_coverage(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = '',
                          with_capex=False):
    """
    The debt service coverage ratio reveals how easily a company can pay its debt obligations

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetinow().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :param with_capex: Some companies might prefer to subtract CAPEX because capital expenditure is not expensed on the income
    statement but rather considered as an “investment”. Excluding CAPEX from EBITDA will give the company the actual
    amount of operating income available for debt repayment.
    :return: .. math:: \\text{Debt Service Coverage Ratio} = \\frac{\\text{Operating Income}}{\\text{Total Debt Service}}
    """
    numerator = operating_income(stock=stock, date=date, lookback_period=lookback_period, period=period)
    numerator -= abs(capital_expenditures(stock=stock, date=date, lookback_period=lookback_period,
                                             period=period)) if with_capex else 0
    return numerator / debt_service(stock=stock, date=date, lookback_period=lookback_period, period=period)
