from datetime import datetime, timedelta
import fundamental_analysis.financial_statements_entries as fi
import fundamental_analysis.supporting_metrics as me
import historical_data_collection.data_preparation_helpers as excel
import fundamental_analysis.equity_valuation_models.equity_valuation_models as valuation

'''
Liquidity ratios are financial ratios that measure a company’s ability to repay both short- and long-term obligations.
'''


def current_ratio(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q') -> float:
    """
    The **current ratio** measures a company’s ability to pay off short-term liabilities with current assets.

    * *Category:* Liquidity Ratio
    * *Healthy Range:* between 1.2 and 2

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetime.now().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :return: .. math:: \\text{Current Ratio} = \\frac{\\text{Current Assets}}{\\text{Current Liabilities}}
    """
    return fi.current_total_assets(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / fi.current_total_liabilities(stock=stock, date=date, lookback_period=lookback_period, period=period)


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
    return me.liquid_assets(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / fi.current_total_liabilities(stock=stock, date=date, lookback_period=lookback_period, period=period)


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
    return (fi.cash_and_cash_equivalents(stock=stock, date=date, lookback_period=lookback_period, period=period)
            + fi.current_marketable_securities(stock=stock, date=date, lookback_period=lookback_period, period=period)) \
           / fi.current_total_liabilities(stock=stock, date=date, lookback_period=lookback_period, period=period)


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
    return fi.cash_flow_operating_activities(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / fi.current_total_liabilities(stock=stock, date=date, lookback_period=lookback_period, period=period)


'''
Leverage ratios measure the amount of capital that comes from debt. In other words, leverage financial ratios are used to evaluate a company’s debt levels.
'''


def debt_ratio(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    """
    The debt ratio measures the relative amount of a company’s assets that are provided from debt

    * *Category:* Leverage Ratio
    * *Healthy Range:*

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetime.now().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :return: .. math:: \\text{Debt Ratio} = \\frac{\\text{Total Liabilities}}{\\text{Total Assets}}
    """
    return fi.total_liabilities(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / fi.total_assets(stock=stock, date=date, lookback_period=lookback_period, period=period)


def asset_to_equity(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    '''
    The asset/equity ratio indicates the relationship of the total assets of the firm to the part owned by shareholders (aka, owner's equity)

    * *Category:* Leverage Ratio
    * *Healthy Range:*

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetime.now().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :return: .. math:: \\text{Asset to Equity Ratio} = \\frac{\\text{Total Assets}}{\\text{Shareholder’s equity}}
    '''
    total_assets = fi.total_assets(stock=stock, date=date, lookback_period=lookback_period, period=period)
    total_equity = fi.total_shareholders_equity(stock=stock, date=date, lookback_period=lookback_period, period=period)
    return total_assets / total_equity


def debt_to_equity(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q',
                   only_interest_expense=False, all_liabilities=False, only_long_term_debt=True,
                   exclude_current_portion_long_term_debt=False):
    '''
    The debt to equity ratio calculates the weight of total debt and financial liabilities against shareholders’ equity

    * *Category:* Leverage Ratio
    * *Healthy Range:*

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetime.now().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :param only_interest_expense:
    :param all_liabilities:
    :param only_long_term_debt:
    :param exclude_current_portion_long_term_debt:
    :return: .. math:: \\text{Debt to Equity Ratio} = \\frac{\\text{Total Liabilities}}{\\text{Shareholder’s equity}}
    '''
    return me.debt(stock=stock, date=date, lookback_period=lookback_period, period=period,
                   only_interest_expense=only_interest_expense, all_liabilities=all_liabilities,
                   long_term_debt=only_long_term_debt,
                   exclude_current_portion_long_term_debt=exclude_current_portion_long_term_debt) \
           / fi.total_shareholders_equity(stock=stock, date=date, lookback_period=lookback_period, period=period)


def debt_to_capital(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q',
                    interest_expense=False, all_liabilities=False, long_term_debt=True):
    '''
    A company's debt-to-capital ratio or D/C ratio is the ratio of its total debt to its total capital, its debt and equity combined. The ratio measures a company's capital structure, financial solvency, and degree of leverage, at a particular point in time.

    * *Category:* Leverage Ratio
    * *Healthy Range:*

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetime.now().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :param interest_expense:
    :param all_liabilities:
    :param long_term_debt:
    :return: .. math:: \\text{Debt to Capital Ratio} = \\frac{\\text{Debt}}{\\text{Debt + Shareholder’s equity}}
    '''
    total_debt = me.debt(stock=stock, date=date, lookback_period=lookback_period, period=period,
                         only_interest_expense=interest_expense, all_liabilities=all_liabilities,
                         long_term_debt=long_term_debt)

    return total_debt / (total_debt + fi.total_shareholders_equity(stock=stock, date=date,
                                                                   lookback_period=lookback_period, period=period))


def interest_coverage(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                      period: str = ''):
    '''
    The interest coverage ratio shows how easily a company can pay its interest expenses

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetime.now().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :return: .. math:: \\text{Interest Coverage Ratio} = \\frac{\\text{Operating Income}}{\\text{Interest Expenses}}
    '''
    return me.earnings_before_interest_and_taxes(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / fi.interest_expense(stock=stock, date=date, lookback_period=lookback_period, period=period)


def debt_service_coverage(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = '',
                          with_capex=False):
    """
    The debt service coverage ratio reveals how easily a company can pay its debt obligations

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetime.now().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :param with_capex: Some companies might prefer to subtract CAPEX because capital expenditure is not expensed on the income
    statement but rather considered as an “investment”. Excluding CAPEX from EBITDA will give the company the actual
    amount of operating income available for debt repayment.
    :return: .. math:: \\text{Debt Service Coverage Ratio} = \\frac{\\text{Operating Income}}{\\text{Total Debt Service}}
    """
    numerator = fi.operating_income(stock=stock, date=date, lookback_period=lookback_period, period=period)
    numerator -= abs(me.capital_expenditures(stock=stock, date=date, lookback_period=lookback_period,
                                             period=period)) if with_capex else 0
    return numerator / me.debt_service(stock=stock, date=date, lookback_period=lookback_period, period=period)


'''
Efficiency ratios, also known as activity financial ratios, are used to measure how well a company is utilizing its assets and resources.
'''


def degree_of_operating_leverage(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'FY'):
    """

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
    return fi.net_sales(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / fi.total_assets(stock=stock, date=date, lookback_period=lookback_period, period=period)


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
    return fi.cost_of_goods_services(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / fi.accounts_payable(stock=stock, date=date, lookback_period=lookback_period, period=period)


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
    return fi.cost_of_goods_services(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / fi.net_inventory(stock=stock, date=date, lookback_period=lookback_period, period=period)


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
    return me.net_credit_sales(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / fi.net_accounts_receivable(stock=stock, date=date, lookback_period=lookback_period, period=period)


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


'''
Profitability ratios measure a company’s ability to generate income relative to revenue, balance sheet assets, operating costs, and equity. 
'''


def net_profit_margin(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'FY'):
    """

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetime.now().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.

    :return: .. math:: \\text{Net Profit Margin} = \\frac{\\text{Net Income}}{\\text{Net Sales}}
    """

    return fi.net_income(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / fi.net_sales(stock=stock, date=date, lookback_period=lookback_period, period=period)


def gross_profit_margin(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'FY'):
    """
    The gross margin ratio compares the gross profit of a company to its net sales to show how much profit a company makes after paying its cost of goods sold

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetime.now().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.

    :return: .. math:: \\text{Gross Margin Ratio} = \\frac{\\text{Gross Profit}}{\\text{Net Sales}}
    """

    return me.gross_profit(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / fi.net_sales(stock=stock, date=date, lookback_period=lookback_period, period=period)


def operating_profit_margin(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'FY'):
    """
    The operating margin ratio compares the operating income of a company to its net sales to determine operating efficiency

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetime.now().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.

    :return: .. math:: \\text{Operating Margin Ratio} = \\frac{\\text{Operating Income}}{\\text{Net Sales}}
    """
    return fi.operating_income(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / fi.net_sales(stock=stock, date=date, lookback_period=lookback_period, period=period)


def return_on_assets(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'FY'):
    """
    The return on assets ratio measures how efficiently a company is using its assets to generate profit

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetime.now().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.

    :return: .. math:: \\text{Return on Assets} = \\frac{\\text{Net Income}}{\\text{Total Assets}}
    """
    return fi.net_income(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / fi.total_assets(stock=stock, date=date, lookback_period=lookback_period, period=period)


def return_on_equity(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'FY'):
    """
    The return on equity ratio measures how efficiently a company is using its equity to generate profit

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetime.now().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.

    :return: .. math:: \\text{Return on Equity} = \\frac{\\text{Net Income}}{\\text{Shareholder’s equity}}
    """
    return fi.net_income(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / fi.total_shareholders_equity(stock=stock, date=date, lookback_period=lookback_period, period=period)


def return_on_net_assets(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'FY'):
    """

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetime.now().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.

    :return: .. math:: \\text{Return on Net Assets} = \\frac{\\text{Net Income}}{\\text{Fixed Assets + Working Capital}}
    """
    return fi.net_income(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / (fi.net_property_plant_equipment(stock=stock, date=date, lookback_period=lookback_period, period=period)
              + me.net_working_capital(stock=stock, date=date, lookback_period=lookback_period, period=period))


def return_on_invested_capital(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'FY',
                               invested_capital_operating_approach=True):
    """

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetime.now().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.

    :param invested_capital_operating_approach:
    :return: .. math:: \\text{Return on Invested Capital} = \\frac{\\text{NOPAT}}{\\text{Invested Capital}}
    """
    return me.net_operating_profit_after_tax(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / me.invested_capital(stock=stock, date=date, lookback_period=lookback_period, period=period,
                                 operating_approach=invested_capital_operating_approach)


def return_on_capital_employed(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'FY'):
    """

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetime.now().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :return: .. math:: \\text{Return on Capital Employed} = \\frac{\\text{EBIT}}{\\text{Capital Employed}}
    """
    return me.earnings_before_interest_and_taxes(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / me.capital_employed(stock=stock, date=date, lookback_period=lookback_period, period=period)


def cash_flow_return_on_investment(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                                   period: str = 'FY'):
    """

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetime.now().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :return:  .. math:: \\text{Cash Flow Return on Investment} = \\frac{\\text{Cash Flow}}{\\text{Market Recapitalisation}}
    """
    pass


def efficiency_ratio(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'FY'):
    """

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetime.now().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :return: .. math:: \\text{Efficiency Ratio} = \\frac{\\text{Non-Interest Expense}}{\\text{Revenue}}
    """
    pass


def net_gearing(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'FY'):
    """

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetime.now().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :return: .. math:: \\text{Net Gearing} = \\frac{\\text{Net Debt}}{\\text{Equity}}
    """
    pass


def basic_earnings_power(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'FY'):
    """

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetime.now().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :return: .. math:: \\text{} = \\frac{\\text{}}{\\text{}}
    """
    pass


'''
Market value ratios are used to evaluate the share price of a company’s stock.
'''


def dividend_payout_ratio(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                          period: str = '', deduct_preferred_dividends: bool = True, use_augmented_ratio: bool = False):
    """
    The dividend payout ratio is the fraction of net income a firm pays to its stockholders in dividends.
    The part of earnings not paid to investors is *retained* i.e. left for investment to provide for future earnings growth.
    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetime.now().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :param deduct_preferred_dividends:
    :param use_augmented_ratio: Some companies choose stock buybacks as an alternative to dividends; in such cases this ratio becomes less meaningful.
    The augmented ratio adds *Buybacks* to the Dividends in the numerator.
    :return: .. math:: \\text{Dividend Payout Ratio} = \\frac{\\text{Dividends}}{\\text{Net Income}}
    """
    dividends = fi.payments_for_dividends(stock=stock, date=date, lookback_period=lookback_period, period=period)
    dividends -= abs(fi.preferred_dividends(stock=stock, date=date, lookback_period=lookback_period,
                                            period=period)) if deduct_preferred_dividends else 0
    net_income = fi.net_income(stock=stock, date=date, lookback_period=lookback_period, period=period)
    return dividends / net_income


def retention_ratio(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'FY',
                    deduct_preferred_dividends: bool = True, use_augmented_ratio: bool = False):
    """
    The **retention ratio** indicates the percentage of a company's earnings that are not paid out in dividends but
    credited to retained earnings. It is the opposite of the dividend payout ratio

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetime.now().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :param deduct_preferred_dividends:
    :param use_augmented_ratio: Some companies choose stock buybacks as an alternative to dividends; in such cases this ratio becomes less meaningful.
        The augmented ratio adds *Buybacks* to the Dividends in the numerator.
    :return: .. math:: \\text{Retention Ratio} = 1 - \\text{Dividend Payout Ratio} = \\frac{\\text{Retained Earnings}}{\\text{Net Income}}
    """
    return 1 - dividend_payout_ratio(stock=stock, date=date, lookback_period=lookback_period, period=period,
                                     deduct_preferred_dividends=deduct_preferred_dividends,
                                     use_augmented_ratio=use_augmented_ratio)


def dividend_coverage_ratio(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                            period: str = '', deduct_preferred_dividends: bool = True,
                            use_augmented_ratio: bool = False):
    """
    The **dividend coverage ratio** is the ratio of company's earnings (net income) over the dividend paid to shareholders, calculated as net profit or loss attributable to ordinary shareholders by total ordinary dividend.

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetime.now().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :param use_augmented_ratio:
    :param deduct_preferred_dividends:
    :return: .. math:: \\text{Dividend Coverage Ratio} = \\frac{\\text{Net Income}}{\\text{Dividends}}
    """
    return 1 / dividend_payout_ratio(stock=stock, date=date, lookback_period=lookback_period, period=period,
                                     deduct_preferred_dividends=deduct_preferred_dividends,
                                     use_augmented_ratio=use_augmented_ratio)


def dividend_yield(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'TTM',
                   diluted_shares: bool = False):
    """

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetime.now().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :param diluted_shares: use diluted shares instead of basic in calculations. use diluted shares in the computations.
    :return: .. math:: \\text{Dividend Yield} = \\frac{\\text{Dividend-per-share}}{\\text{Share Price}}
    """
    return me.dividend_per_share(stock=stock, date=date, lookback_period=lookback_period, period=period,
                                 diluted_shares=diluted_shares) \
           / me.market_price(stock=stock, date=date, lookback_period=lookback_period)


def earnings_per_share(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                       period: str = 'TTM', diluted_shares: bool = False, use_income_from_operations: bool = False,
                       deduct_preferred_dividends: bool = True, weighted_average_shares: bool = True,
                       as_reported: bool = True):
    '''
    The earnings per share ratio measures the amount of net income earned for each share outstanding

    *Category:* Market Value Ratios
    *Subcategory:* Equity Value Ratios

    *Notes:* Compared with Earnings per share, a company's cash flow is better indicator of the company's earnings power.
    If a company's earnings per share is less than cash flow per share over long term, investors need to be cautious and find out why.

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetime.now().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :param as_reported: outputs the EPS as reported by the company in the 10-K or 10-Q filing.
    :param diluted_shares: use diluted shares instead of basic in calculations.
    :param use_income_from_operations: Use income from continuing operations instead of Net Income in the numerator.
    :param deduct_preferred_dividends:
    :param weighted_average_shares:  It is more accurate to use a weighted average number of common shares over the reporting term because the number of shares can change over time.
    :return: .. math:: \\text{Earnings Per Share} = \\frac{\\text{Net Income}}{\\text{Total Shares Outstanding}}
    '''
    numerator = fi.net_income(stock=stock, date=date, lookback_period=lookback_period, period=period)
    numerator -= abs(fi.preferred_dividends(stock=stock, date=date, lookback_period=lookback_period,
                                            period=period)) if deduct_preferred_dividends else 0
    numerator += fi.non_operating_income(stock=stock, date=date, lookback_period=lookback_period,
                                         period=period) if use_income_from_operations else 0

    shares_outstanding_ = fi.total_shares_outstanding(stock=stock, date=date, lookback_period=lookback_period,
                                                      period=period, diluted_shares=diluted_shares)
    return numerator / shares_outstanding_


def book_value_per_share(stock, date=datetime.now(), lookback_period=timedelta(days=0), period: str = 'Q',
                         diluted_shares: bool = False, tangible=False):
    '''
    The book value per share ratio calculates the per-share value of a company based on equity available to shareholders

    *Category:* Market Value Ratios

    *Subcategory:* Equity Value Ratios

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetime.now().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :param diluted_shares: use diluted shares instead of basic in calculations.
    :param tangible:
    :return: .. math:: \\text{Book Value Per Share} = \\frac{\\text{Shareholder's Equity}}{\\text{Total Shares Outstanding}}
    '''
    numerator = fi.total_shareholders_equity(stock=stock, date=date, lookback_period=lookback_period, period=period)
    if tangible:
        numerator = - fi.total_intangible_assets(stock=stock, date=date, lookback_period=lookback_period, period=period)

    return numerator / fi.total_shares_outstanding(stock=stock, date=date, lookback_period=lookback_period,
                                                   period=period, diluted_shares=diluted_shares)


def price_to_cash_flow_ratio(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                             period: str = 'TTM', diluted_shares: bool = False):
    """
    The **price/cash flow ratio** (or P/CF) is used to compare a company's market value to its cash flow; or, equivalently,
    divide the per-share stock price by the per-share operating cash flow.

    *Category:* Market Value Ratios

    *Subcategory:* Equity Value Ratios

    *Notes:* A high P/CF ratio indicated that the specific firm is trading at a high price but is not generating enough
    cash flows to support the multiple—sometimes this is OK, depending on the firm, industry, and its specific operations.
    Smaller price ratios are generally preferred, as they may reveal a firm generating ample cash flows that are not yet
    properly considered in the current share price. Holding all factors constant, from an investment perspective, a smaller P/CF is preferred over a larger multiple

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetime.now().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :param diluted_shares: use diluted shares instead of basic in calculations.
    :return: .. math:: \\text{Price-to-Cash Flow Ratio} = \\frac{\\text{Market Capitalization}}{\\text{Operating Cash Flow}} =
    \\frac{\\text{Share Price}}{\\text{Operating Cash Flow per Share}}
    """
    return me.market_capitalization(stock=stock, date=date, lookback_period=lookback_period, period=period,
                                    diluted_shares=diluted_shares) \
           / fi.cash_flow_operating_activities(stock=stock, date=date, lookback_period=lookback_period, period=period)


def price_to_book_ratio(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q',
                        diluted_shares: bool = False, tangible_book_value: bool = False):
    """
    The price-to-book ratio (or P/B ratio) is used to compare a company's current market capitalization to its book value;
    or, equivalently, divide the per-share stock price by the per-share book value.

    *Category:* Market Value Ratios

    *Subcategory:* Equity Value Ratios

    *Notes:*
        *   A higher P/B ratio implies that investors expect management to create more value from a given set of
            assets, all else equal (and/or that the market value of the firm's assets is significantly higher than their accounting
            value). P/B ratios do not, however, directly provide any information on the ability of the firm to generate profits
            or cash for shareholders.

        *   As with most ratios, it varies a fair amount by industry. Industries that require more infrastructure capital
            (for each dollar of profit) will usually trade at P/B ratios much lower than, for example, consulting firms. P/B
            ratios are commonly used to compare banks, because most assets and liabilities of banks are constantly valued at
            market values.

        *   This ratio also gives some idea of whether an investor is paying too much for what would be left if the company
            went bankrupt immediately. For companies in distress, the book value is usually calculated without the intangible
            assets that would have no resale value. In such cases, P/B should also be calculated on a "diluted" basis, because
            stock options may well vest on sale of the company or change of control or firing of management.

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetime.now().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :param diluted_shares: use diluted shares instead of basic in calculations.
    :param tangible_book_value: P/B can be calculated either including or excluding intangible assets and goodwill. When intangible assets and goodwill are excluded,
        the ratio is often specified to be "price to tangible book value"
    :return: .. math:: \\text{Price-to-Book Ratio} = \\frac{\\text{Market Capitalization}}{\\text{Book Value}} = \\frac{\\text{Share Price}}{\\text{Book Value per Share}}
    """
    denominator = fi.total_shareholders_equity(stock=stock, date=date, lookback_period=lookback_period, period=period)
    if tangible_book_value:
        denominator -= fi.total_intangible_assets(stock=stock, date=date, lookback_period=lookback_period,
                                                  period=period)
    return me.market_capitalization(stock=stock, date=date, lookback_period=lookback_period, period=period,
                                    diluted_shares=diluted_shares) / denominator


def price_to_sales(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'TTM',
                   diluted_shares: bool = False):
    """
    Price–sales ratio (or P/S ratio, or PSR) is used to compare a company's current market capitalization and the revenue in
    the most recent year; or, equivalently, divide the per-share stock price by the per-share revenue.

    *Category:* Market Value Ratios

    *Subcategory:* Equity Value Ratios

    *Notes:*

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetime.now().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :param diluted_shares: use diluted shares instead of basic in calculations. use diluted shares instead of basic in calculations.
    :return: .. math:: \\text{Price-to-Sales Ratio} = \\frac{\\text{Market Capitalization}}{\\text{Revenue}} = \\frac{\\text{Share Price}}{\\text{Per-Share Revenue}}
    """
    return me.market_capitalization(stock=stock, date=date, lookback_period=lookback_period, period=period,
                                    diluted_shares=diluted_shares) \
           / fi.net_sales(stock=stock, date=date, lookback_period=lookback_period, period=period)


def justified_price_to_sales(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'TTM',
                             diluted_shares: bool = False):
    """
    The justified P/S ratio is calculated as the price-to-sales ratio based on the Gordon Growth Model.
    Thus, it is the price-to-sales ratio based on the company's fundamentals rather than .
    Here, *g* is the sustainable growth rate as defined below and *r* is the required rate of return.

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetime.now().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :param diluted_shares: use diluted shares instead of basic in calculations.
    :return: .. math:: \\text{Justified P/S} = \\text{Profit Margin} * \\text{Payout} * \\frac{1+g}{r-g} where .. math:: g = \\text{Retention Ratio} * \\text{Net Profit Margin} * \\frac{\\text{Sales}}{\\text{Assets}} * \\frac{\\text{Assets}}{\\text{Shareholders' Equity}}
    """
    from fundamental_analysis.equity_valuation_models.cost_of_capital import weighted_average_cost_of_capital
    g = valuation.growth_rate_PRAT_model(stock=stock, date=date, lookback_period=lookback_period, period=period)
    r = weighted_average_cost_of_capital(stock=stock, date=date, lookback_period=lookback_period, period=period)
    return net_profit_margin(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           * dividend_payout_ratio(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           * (1 + g) / (r - g)


def price_to_earnings(stock, date=datetime.now(), lookback_period: timedelta = timedelta(days=0),
                      period: str = 'TTM', diluted_shares: bool = False,
                      use_income_from_operations=False, deduct_preferred_dividends=True):
    """
    The price-earnings ratio compares a company’s share price to its earnings per share

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetime.now().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :param diluted_shares: use diluted shares instead of basic in calculations.
    :param use_income_from_operations:
    :param deduct_preferred_dividends:
    :return: .. math:: \\text{Price-earnings ratio} = \\frac{\\text{Share Price}}{\\text{Earnings Per Share}}
    """
    market_price_ = me.market_price(stock=stock, date=date, lookback_period=lookback_period)
    earnings_per_share_ = earnings_per_share(stock=stock, date=date, lookback_period=lookback_period, period=period,
                                             diluted_shares=diluted_shares,
                                             use_income_from_operations=use_income_from_operations,
                                             deduct_preferred_dividends=deduct_preferred_dividends)
    return market_price_ / earnings_per_share_


def earnings_yield(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                   period: str = '', diluted_shares: bool = False,
                   use_income_from_operations=False, deduct_preferred_dividends=True):
    """
    The **earnings yield** is the inverse of price to earnings.

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetime.now().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :param diluted_shares: use diluted shares instead of basic in calculations.
    :param use_income_from_operations:
    :param deduct_preferred_dividends:
    :return: .. math:: \\text{Earnings Yield} = \\frac{\\text{Earnings Per Share}}{\\text{Share Price}}
    """
    return 1 / price_to_earnings(stock=stock, date=date, lookback_period=lookback_period, period=period,
                                 diluted_shares=diluted_shares, use_income_from_operations=use_income_from_operations,
                                 deduct_preferred_dividends=deduct_preferred_dividends)


def greenblatt_earnings_yield(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'FY'):
    """

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetime.now().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :return: .. math:: \\text{Greenblatt Earnings Yield} = \\frac{\\text{EBIT}}{\\text{EV}}
    """

    return me.earnings_before_interest_and_taxes(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / me.enterprise_value(stock=stock, date=date, lookback_period=lookback_period, period=period)


def price_to_earnings_to_growth(stock, date=datetime.now(), lookback_period=timedelta(days=0),
                                period: str = 'TTM', growth_periods: int = 5, diluted_shares: bool = False,
                                use_income_from_operations: bool = False, deduct_preferred_dividends: bool = True):
    """
    The price/earnings to growth ratio (or PEG ratio) is a valuation metric for determining the relative trade-off
    between the price of a stock, the earnings generated per share (EPS), and the company's expected growth.

    *Category:* Market Value Ratios

    *Subcategory:* Equity Value Ratios

    *Notes:*
        *   In general, the P/E ratio is higher for a company with a higher growth rate. Thus, using just the P/E ratio
            would make high-growth companies appear overvalued relative to others. It is assumed that by dividing the P/E
            ratio by the earnings growth rate, the resulting ratio is better for comparing companies with different growth
            rates. Therefore, a lower ratio is "better" (cheaper) and a higher ratio is "worse" (expensive).

        *   According to Peter Lynch in his book *One Up on Wall Street*, the P/E ratio of any company that's fairly
            priced will equal its growth rate", i.e., a fairly valued company will have its PEG equal to 1.

        *   The P/E ratio used in the calculation may be projected or trailing. The (annual) growth rate is expressed as
            a percent value, and should use real growth only, to correct for inflation. It may be the
            expected growth rate for the next year or the next five years.

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetime.now().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :param growth_periods:
    :param diluted_shares: use diluted shares instead of basic in calculations.
    :param use_income_from_operations:
    :param deduct_preferred_dividends:
    :return: .. math:: \\text{} = \\frac{\\text{}}{\\text{}}
    """
    lookbacks = [timedelta(days=365 * i if period != 'Q' else 90 * i) for i in range(growth_periods)]
    eps_series = [earnings_per_share(stock=stock, date=date, lookback_period=lookback, period=period,
                                     diluted_shares=diluted_shares,
                                     use_income_from_operations=use_income_from_operations,
                                     deduct_preferred_dividends=deduct_preferred_dividends) for lookback in lookbacks]
    eps_growth = average_growth(eps_series[::-1])
    output = price_to_earnings(stock=stock, date=date, lookback_period=lookback_period, period=period,
                               diluted_shares=diluted_shares,
                               use_income_from_operations=use_income_from_operations,
                               deduct_preferred_dividends=deduct_preferred_dividends) / eps_growth
    return output


'''Enterprise Value Ratios'''


def enterprise_value_to_revenue(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'TTM'):
    """
    The enterprise value-to-revenue multiple is a measure of the value of a stock that compares a company's enterprise value to its revenue.
    It is often used to determine a company's valuation in the case of a potential acquisition, and can be used for
    companies that do not generate income or profits.

    *Category:* Enterprise Value Ratios

    *Subcategory:* Equity Value Ratios

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetime.now().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :return:
    """
    return me.enterprise_value(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / fi.net_sales(stock=stock, date=date, lookback_period=lookback_period, period=period)


def enterprise_value_to_ebitda(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'TTM'):
    """

    *Category:* Enterprise Value Ratios

    *Subcategory:* Equity Value Ratios

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetime.now().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :return:
    """
    return me.enterprise_value(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / me.earnings_before_interest_and_taxes_and_depreciation_and_amortization(stock=stock, date=date,
                                                                                     lookback_period=lookback_period,
                                                                                     period=period)


def enterprise_value_to_ebit(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'TTM'):
    """

    *Category:* Enterprise Value Ratios

    *Subcategory:* Equity Value Ratios

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetime.now().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :return:
    """
    return me.enterprise_value(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / me.earnings_before_interest_and_taxes(stock=stock, date=date, lookback_period=lookback_period,
                                                   period=period)


def enterprise_value_to_invested_capital(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                                         period: str = 'TTM'):
    """

    *Category:* Enterprise Value Ratios

    *Subcategory:* Equity Value Ratios

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetime.now().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :return:
    """
    return me.enterprise_value(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / me.invested_capital(stock=stock, date=date, lookback_period=lookback_period, period=period)


def enterprise_value_to_free_cash_flow(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                                       period: str = 'TTM'):
    """
    *Category:* Enterprise Value Ratios

    *Subcategory:* Equity Value Ratios

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetime.now().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :return:
    """
    return me.enterprise_value(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / me.free_cash_flow(stock=stock, date=date, lookback_period=lookback_period, period=period)


if __name__ == '__main__':
    print(price_to_book_ratio(stock=['BA', 'AXP'], date=[datetime.now(), datetime(2019, 9, 1)], period='FY'))
    print(me.market_price(stock=['BA', 'AXP'],
                          date=[datetime.now(), datetime(2019, 1, 1)]))
