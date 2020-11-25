from datetime import datetime, timedelta
import fundamental_analysis.financial_statements_entries as fi
import fundamental_analysis.supporting_metrics as me
import historical_data_collection.data_preparation_helpers as excel
import fundamental_analysis.equity_valuation_models.equity_valuation_models as valuation

'''
Liquidity ratios are financial ratios that measure a company’s ability to repay both short- and long-term obligations.
'''


def current(stock, date=None, lookback_period: timedelta = timedelta(days=0),
            period: str = 'Q') -> float:
    """
    The current ratio measures a company’s ability to pay off short-term liabilities with current assets.

    Category: Liquidity Ratio

    :param stock: ticker in question i.e. 'AAPL'
    :param date: date (the most recent date of reporting from that date will be used) i.e. datetime(2019, 1, 1)
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90)
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months
    :return: Current Assets / Current Liabilities
    """
    return fi.current_total_assets(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / fi.current_total_liabilities(stock=stock, date=date, lookback_period=lookback_period, period=period)


def acid_test(stock, date=None, lookback_period: timedelta = timedelta(days=0),
              period: str = 'Q'):
    """
    The acid-test ratio (or quick ratio) measures a company’s ability to pay off short-term liabilities with quick assets

    Category: Liquidity Ratio

    :param stock: ticker in question i.e. 'AAPL'
    :param date: date (the most recent date of reporting from that date will be used) i.e. datetime(2019, 1, 1)
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90)
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months
    :return: Liquid Assets / Current liabilities
    """
    return me.liquid_assets(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / fi.current_total_liabilities(stock=stock, date=date, lookback_period=lookback_period, period=period)


def cash(stock, date=None, lookback_period: timedelta = timedelta(days=0),
         period: str = 'Q'):
    """
    The cash ratio measures a company’s ability to pay off short-term liabilities with cash and cash equivalents

    Category: Liquidity Ratio

    :param stock: ticker in question i.e. 'AAPL'
    :param date: date (the most recent date of reporting from that date will be used) i.e. datetime(2019, 1, 1)
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90)
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months
    :return: (Cash and Cash equivalents + Current Marketable Securities) / Current Liabilities
    """
    return (fi.cash_and_cash_equivalents(stock=stock, date=date, lookback_period=lookback_period, period=period)
            + fi.current_marketable_securities(stock=stock, date=date, lookback_period=lookback_period, period=period)) \
           / fi.current_total_liabilities(stock=stock, date=date, lookback_period=lookback_period, period=period)


def operating_cash_flow(stock, date=None,
                        lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    """
    The operating cash flow ratio is a measure of the number of times a company can pay off current liabilities with the cash generated in a given period

    Category: Liquidity Ratio

    :param stock: ticker in question i.e. 'AAPL'
    :param date: date (the most recent date of reporting from that date will be used) i.e. datetime(2019, 1, 1)
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90)
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months
    :return: Operating Cash Flow / Current liabilities
    """
    return fi.cash_flow_operating_activities(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / fi.current_total_liabilities(stock=stock, date=date, lookback_period=lookback_period, period=period)


'''
Leverage ratios measure the amount of capital that comes from debt. In other words, leverage financial ratios are used to evaluate a company’s debt levels.
'''


def debt(stock, date=None,
         lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    """
    The debt ratio measures the relative amount of a company’s assets that are provided from debt

    Category: Leverage Ratios

    :param stock: ticker in question i.e. 'AAPL'
    :param date: date (the most recent date of reporting from that date will be used) i.e. datetime(2019, 1, 1)
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90)
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months
    :return: Total liabilities / Total assets
    """
    return fi.total_liabilities(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / fi.total_assets(stock=stock, date=date, lookback_period=lookback_period, period=period)


def asset_to_equity(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                    period: str = 'Q'):
    '''
    The asset/equity ratio indicates the relationship of the total assets of the firm to the part owned by shareholders (aka, owner's equity)

    Category: Leverage Ratios

    :param stock: ticker in question i.e. 'AAPL'
    :param date: date (the most recent date of reporting from that date will be used) i.e. datetime(2019, 1, 1)
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90)
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months
    :return:
    '''
    total_assets = fi.total_assets(stock=stock, date=date, lookback_period=lookback_period, period=period)
    total_equity = fi.total_shareholders_equity(stock=stock, date=date, lookback_period=lookback_period, period=period)
    return total_assets / total_equity


def debt_to_equity(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                   period: str = 'Q',
                   only_interest_expense=False, all_liabilities=False, only_long_term_debt=True,
                   exclude_current_portion_long_term_debt=False):
    '''
    The debt to equity ratio calculates the weight of total debt and financial liabilities against shareholders’ equity

    Category: Leverage Ratios

    :param stock: ticker in question i.e. 'AAPL'
    :param date: date (the most recent date of reporting from that date will be used) i.e. datetime(2019, 1, 1)
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90)
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months
    :param only_interest_expense:
    :param all_liabilities:
    :param only_long_term_debt:
    :param exclude_current_portion_long_term_debt:
    :return: Debt to equity ratio = Total liabilities / Shareholder’s equity
    '''
    return me.debt(stock=stock, date=date, lookback_period=lookback_period, period=period,
                   only_interest_expense=only_interest_expense, all_liabilities=all_liabilities,
                   long_term_debt=only_long_term_debt,
                   exclude_current_portion_long_term_debt=exclude_current_portion_long_term_debt) \
           / fi.total_shareholders_equity(stock=stock, date=date, lookback_period=lookback_period, period=period)


def debt_to_capital(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                    period: str = 'Q', interest_expense=False, all_liabilities=False, long_term_debt=True):
    '''
    A company's debt-to-capital ratio or D/C ratio is the ratio of its total debt to its total capital, its debt and equity combined. The ratio measures a company's capital structure, financial solvency, and degree of leverage, at a particular point in time.

    Category: Leverage Ratios

    :param stock: ticker in question i.e. 'AAPL'
    :param date: date (the most recent date of reporting from that date will be used) i.e. datetime(2019, 1, 1)
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90)
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months
    :param interest_expense:
    :param all_liabilities:
    :param long_term_debt:
    :return:
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

    :param stock: ticker in question i.e. 'AAPL'
    :param date: date (the most recent date of reporting from that date will be used) i.e. datetime(2019, 1, 1)
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90)
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months
    :return: Operating income / Interest expenses
    '''
    return me.earnings_before_interest_and_taxes(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / fi.interest_expense(stock=stock, date=date, lookback_period=lookback_period, period=period)


# The debt service coverage ratio reveals how easily a company can pay its debt obligations
# Debt service coverage ratio = Operating income / Total debt service
# Some companies might prefer to subtract CAPEX because capital expenditure is not expensed on the income
# statement but rather considered as an “investment”. Excluding CAPEX from EBITDA will give the company the actual
# amount of operating income available for debt repayment.
# TODO Review
def debt_service_coverage(stock, date=None,
                          lookback_period: timedelta = timedelta(days=0), period: str = '', with_capex=False):
    numerator = fi.operating_income(stock=stock, date=date, lookback_period=lookback_period, period=period)
    numerator -= abs(me.capital_expenditures(stock=stock, date=date, lookback_period=lookback_period,
                                             period=period)) if with_capex else 0
    return numerator / me.debt_service(stock=stock, date=date, lookback_period=lookback_period, period=period)


'''
Efficiency ratios, also known as activity financial ratios, are used to measure how well a company is utilizing its assets and resources.
'''


def degree_of_operating_leverage(stock, date=datetime.now(), lookback_period=timedelta(days=0), period: str = ''):
    pass


'''Accounts Payable'''


def payables_turnover(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                      period: str = ''):
    return fi.credit_purchases(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / fi.accounts_payable(stock=stock, date=date, lookback_period=lookback_period, period=period)


def payables_conversion_period(stock, date=datetime.now(), lookback_period=timedelta(days=0), period: str = ''):
    return 365 \
           / payables_turnover(stock=stock, date=date, lookback_period=lookback_period, period=period)


# The asset turnover ratio measures a company’s ability to generate sales from assets
# Asset turnover ratio = Net sales / Total assets
def asset_turnover(stock, date=datetime.now(), lookback_period=timedelta(days=0), period: str = ''):
    return fi.net_sales(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / fi.total_assets(stock=stock, date=date, lookback_period=lookback_period, period=period)


'''Inventory'''


# The inventory (or stock) turnover ratio measures how many times a company’s inventory is sold and replaced over a given period
# Inventory turnover ratio = Cost of goods sold / Average inventory
def inventory_turnover(stock, date=None,
                       lookback_period: timedelta = timedelta(days=0),
                       period: str = ''):
    return fi.cost_of_goods_services(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / fi.net_inventory(stock=stock, date=date, lookback_period=lookback_period, period=period)


def inventory_conversion_period(stock, date=None,
                                lookback_period: timedelta = timedelta(days=0),
                                period: str = ''):
    return 365 / inventory_turnover(stock=stock, date=date, lookback_period=lookback_period, period=period)


# The days sales in inventory ratio measures the average number of days that a company holds on to inventory before selling it to customers
# Days sales in inventory ratio = 365 days / Inventory turnover ratio
def days_sales_in_inventory(stock, date=None,
                            lookback_period: timedelta = timedelta(days=0),
                            period: str = ''):
    return 365 / inventory_turnover(stock=stock, date=date, lookback_period=lookback_period, period=period)


'''Accounts Receivables'''


def average_collection_period(stock, date=datetime.now(), lookback_period=timedelta(days=0), period: str = ''):
    return fi.net_accounts_receivable(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / (fi.credit_sales(stock=stock, date=date, lookback_period=lookback_period, period=period) / 365)


# The accounts receivable turnover ratio measures how many times a company can turn receivables into cash over a given period
# Receivables turnover ratio = Net credit sales / Average accounts receivable
def receivables_turnover(stock, date=None,
                         lookback_period: timedelta = timedelta(days=0),
                         period: str = ''):
    return me.net_credit_sales(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / fi.net_accounts_receivable(stock=stock, date=date, lookback_period=lookback_period, period=period)


def days_sales_outstanding(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                           period: str = ''):
    """
    Days sales outstanding is a calculation used by a company to estimate the size of their outstanding
    accounts receivable. It measures this size not in units of currency, but in average sales days.
    Typically, days sales outstanding is calculated monthly

    :param stock:
    :param date:
    :param lookback_period:
    :param period:
    :return: Net Accounts Receivables / Net Sales
    """
    return fi.net_accounts_receivable(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / (fi.net_sales(stock=stock, date=date, lookback_period=lookback_period, period=period) / 365)


def receivables_conversion_period(stock, date=None,
                                  lookback_period: timedelta = timedelta(days=0),
                                  period: str = ''):
    return 365 \
           / receivables_turnover(stock=stock, date=date, lookback_period=lookback_period, period=period)


def cash_conversion_cycle(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                          period: str = ''):
    return inventory_conversion_period(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           + receivables_conversion_period(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           - payables_conversion_period(stock=stock, date=date, lookback_period=lookback_period, period=period)


def retention(stock, date=None, lookback_period: timedelta = timedelta(days=0),
              period: str = ''):
    net_income = fi.net_income(stock=stock, date=date, lookback_period=lookback_period, period=period)
    dividends = fi.payments_for_dividends(stock=stock, date=date, lookback_period=lookback_period, period=period)
    return (net_income - abs(dividends)) / net_income


'''
Profitability ratios measure a company’s ability to generate income relative to revenue, balance sheet assets, operating costs, and equity. 
'''


def net_profit_margin(stock, date=datetime.now(), lookback_period=timedelta(days=0), period: str = ''):
    return fi.net_income(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / fi.net_sales(stock=stock, date=date, lookback_period=lookback_period, period=period)


# The gross margin ratio compares the gross profit of a company to its net sales to show how much profit a company makes after paying its cost of goods sold
# Gross margin ratio = Gross profit / Net sales
def gross_profit_margin(stock, date=datetime.now(), lookback_period=timedelta(days=0), period: str = ''):
    return me.gross_profit(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / fi.net_sales(stock=stock, date=date, lookback_period=lookback_period, period=period)


# The operating margin ratio compares the operating income of a company to its net sales to determine operating efficiency
# Operating margin ratio = Operating income / Net sales
def operating_profit_margin(stock, date=datetime.now(), lookback_period=timedelta(days=0), period: str = ''):
    return fi.operating_income(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / fi.net_sales(stock=stock, date=date, lookback_period=lookback_period, period=period)


def return_on_assets(stock, date=datetime.now(), lookback_period=timedelta(days=0), period: str = ''):
    """
    The return on assets ratio measures how efficiently a company is using its assets to generate profit

    :param stock:
    :param date:
    :param lookback_period:
    :param period:
    :return: Net income / Total assets
    """
    return fi.net_income(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / fi.total_assets(stock=stock, date=date, lookback_period=lookback_period, period=period)


# The return on equity ratio measures how efficiently a company is using its equity to generate profit
# Return on equity ratio = Net income Attributable to Common Stockholders / Shareholder’s equity
def return_on_equity(stock, date=datetime.now(), lookback_period=timedelta(days=0), period: str = ''):
    return fi.net_income(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / fi.total_shareholders_equity(stock=stock, date=date, lookback_period=lookback_period, period=period)


def return_on_net_assets(stock, date=datetime.now(), lookback_period=timedelta(days=0), period: str = ''):
    return fi.net_income(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / (fi.net_property_plant_equipment(stock=stock, date=date, lookback_period=lookback_period, period=period)
              + me.net_working_capital(stock=stock, date=date, lookback_period=lookback_period, period=period))


def return_on_invested_capital(stock, date=datetime.now(), lookback_period=timedelta(days=0), period: str = '',
                               invested_capital_operating_approach=True):
    return me.net_operating_profit_after_tax(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / me.invested_capital(stock=stock, date=date, lookback_period=lookback_period, period=period,
                                 operating_approach=invested_capital_operating_approach)


def return_on_capital_employed(stock, date=datetime.now(), lookback_period=timedelta(days=0), period: str = ''):
    return me.earnings_before_interest_and_taxes(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / me.capital_employed(stock=stock, date=date, lookback_period=lookback_period, period=period)


def cash_flow_return_on_investment(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=True,
                                   ttm=False):
    pass


def efficiency(stock, date=datetime.now(), lookback_period=timedelta(days=0), period: str = ''):
    pass


def net_gearing(stock, date=datetime.now(), lookback_period=timedelta(days=0), period: str = ''):
    pass


def basic_earnings_power(stock, date=datetime.now(), lookback_period=timedelta(days=0), period: str = ''):
    pass


'''
Market value ratios are used to evaluate the share price of a company’s stock.
'''


def book_value_per_share(stock, date=datetime.now(), lookback_period=timedelta(days=0), period: str = 'Q',
                         diluted_shares: bool = False):
    '''
    The book value per share ratio calculates the per-share value of a company based on equity available to shareholders

    Subcategory: Equity Value Ratios

    Category: Market Value Ratios

    :param stock: ticker in question i.e. 'AAPL'
    :param date: date (the most recent date of reporting from that date will be used) i.e. datetime(2019, 1, 1)
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90)
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months
    :param diluted_shares:
    :return: Shareholder’s equity / Total shares outstanding
    '''
    return fi.total_shareholders_equity(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / fi.total_shares_outstanding(stock=stock, date=date, lookback_period=lookback_period, period=period,
                                         diluted_shares=diluted_shares)


def tangible_book_value_per_share(stock, date=datetime.now(), lookback_period=timedelta(days=0), period: str = '',
                                  diluted_shares: bool = False):
    return (fi.total_shareholders_equity(stock=stock, date=date, lookback_period=lookback_period, period=period) \
            - fi.total_intangible_assets(stock=stock, date=date, lookback_period=lookback_period, period=period)) \
           / fi.total_shares_outstanding(stock=stock, date=date, lookback_period=lookback_period, period=period,
                                         diluted_shares=diluted_shares)


def earnings_per_share(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                       period: str = 'TTM', diluted_shares: bool = False,
                       deduct_operating_income: bool = False, deduct_preferred_dividends: bool = True):
    '''
    The earnings per share ratio measures the amount of net income earned for each share outstanding

    research_tools: Compared with Earnings per share, a company's cash flow is better indicator of the company's earnings power.
    If a company's earnings per share is less than cash flow per share over long term, investors need to be cautious and find out why.

    :param stock: ticker in question i.e. 'AAPL'
    :param date: date (the most recent date of reporting from that date will be used) i.e. datetime(2019, 1, 1)
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90)
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months
    :param diluted_shares:
    :param deduct_operating_income:
    :param deduct_preferred_dividends:
    :return: Net Income / Total shares outstanding
    '''
    numerator = fi.net_income(stock=stock, date=date, lookback_period=lookback_period, period=period)
    numerator -= abs(fi.preferred_dividends(stock=stock, date=date, lookback_period=lookback_period,
                                            period=period)) if deduct_preferred_dividends else 0
    numerator += fi.non_operating_income(stock=stock, date=date, lookback_period=lookback_period,
                                         period=period) if deduct_operating_income else 0

    shares_outstanding_ = fi.total_shares_outstanding(stock=stock, date=date, lookback_period=lookback_period,
                                                      period=period, diluted_shares=diluted_shares)
    return numerator / shares_outstanding_


def dividend_payout(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                    period: str = '', diluted_shares: bool = False,
                    deduct_operating_income=False, deduct_preferred_dividends=True):
    return me.dividend_per_share(stock=stock, date=date, lookback_period=lookback_period, period=period,
                                 diluted_shares=diluted_shares) \
           / earnings_per_share(stock=stock, date=date, lookback_period=lookback_period, period=period,
                                diluted_shares=diluted_shares, deduct_operating_income=deduct_operating_income,
                                deduct_preferred_dividends=deduct_preferred_dividends)


def dividend_coverage(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                      period: str = '', diluted_shares: bool = False,
                      deduct_operating_income=False, deduct_preferred_dividends=True):
    return 1 / dividend_payout(stock=stock, date=date, lookback_period=lookback_period, period=period,
                               diluted_shares=diluted_shares, deduct_operating_income=deduct_operating_income,
                               deduct_preferred_dividends=deduct_preferred_dividends)


def dividend_yield(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                   period: str = '', diluted_shares: bool = False):
    return me.dividend_per_share(stock=stock, date=date, lookback_period=lookback_period, period=period,
                                 diluted_shares=diluted_shares) \
           / me.market_price(stock=stock, date=date, lookback_period=lookback_period)


def price_to_cash_flow(stock, date=None,
                       lookback_period: timedelta = timedelta(days=0),
                       period: str = '', diluted_shares: bool = False):
    return me.market_price(stock=stock, date=date, lookback_period=lookback_period) \
           / (fi.cash_flow_operating_activities(stock=stock, date=date, lookback_period=lookback_period, period=period)
              / fi.total_shares_outstanding(stock=stock, date=date, lookback_period=lookback_period, period=period,
                                            diluted_shares=diluted_shares))


def price_to_book_value(stock, date=None,
                        lookback_period: timedelta = timedelta(days=0),
                        period: str = 'Q', diluted_shares: bool = False):
    return me.market_price(stock=stock, date=date, lookback_period=lookback_period) \
           / book_value_per_share(stock=stock, date=date, lookback_period=lookback_period, period=period,
                                  diluted_shares=diluted_shares)


def book_value_to_price(stock, date=None,
                        lookback_period: timedelta = timedelta(days=0),
                        period: str = '', diluted_shares: bool = False):
    return 1 / price_to_book_value(stock=stock, date=date, lookback_period=lookback_period,
                                   period=period, diluted_shares=diluted_shares)


def price_to_tangible_book_value(stock, date=None,
                                 lookback_period: timedelta = timedelta(days=0),
                                 period: str = '', diluted_shares: bool = False):
    return me.market_price(stock=stock, date=date, lookback_period=lookback_period) \
           / tangible_book_value_per_share(stock=stock, date=date, lookback_period=lookback_period, period=period,
                                           diluted_shares=diluted_shares)


def justified_price_to_book_value(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=True,
                                  ttm=True,
                                  diluted=True):
    pass


def price_to_sales(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                   period: str = '', diluted_shares: bool = False):
    return me.market_capitalization(stock=stock, date=date, lookback_period=lookback_period, period=period,
                                    diluted_shares=diluted_shares) \
           / fi.net_sales(stock=stock, date=date, lookback_period=lookback_period, period=period)


def justified_price_to_sales(stock, date=None,
                             lookback_period: timedelta = timedelta(days=0),
                             period: str = '', diluted_shares: bool = False):
    from fundamental_analysis.equity_valuation_models.cost_of_capital import weighted_average_cost_of_capital
    g = valuation.growth_rate_PRAT_model(stock=stock, date=date, lookback_period=lookback_period, period=period)
    r = weighted_average_cost_of_capital(stock=stock, date=date, lookback_period=lookback_period, period=period)
    return net_profit_margin(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           * dividend_payout(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           * (1 + g) / (r - g)


# The price-earnings ratio compares a company’s share price to its earnings per share:
# Price-earnings ratio = Share price / Earnings per share
def price_to_earnings(stock, date=datetime.now(), lookback_period: timedelta = timedelta(days=0),
                      period: str = 'TTM', diluted_shares: bool = False,
                      deduct_operating_income=False, deduct_preferred_dividends=True):
    market_price_ = me.market_price(stock=stock, date=date, lookback_period=lookback_period, spec='Close')
    earnings_per_share_ = earnings_per_share(stock=stock, date=date, lookback_period=lookback_period, period=period,
                                             diluted_shares=diluted_shares,
                                             deduct_operating_income=deduct_operating_income,
                                             deduct_preferred_dividends=deduct_preferred_dividends)
    return market_price_ / earnings_per_share_


# inverse of price to earnings
def earnings_yield(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                   period: str = '', diluted_shares: bool = False,
                   deduct_operating_income=False, deduct_preferred_dividends=True):
    return 1 / price_to_earnings(stock=stock, date=date, lookback_period=lookback_period, period=period,
                                 diluted_shares=diluted_shares, deduct_operating_income=deduct_operating_income,
                                 deduct_preferred_dividends=deduct_preferred_dividends)


# there is an adjusted version of the formula that accounts for differences in the capital structure and tax rates
# between companies.
def adjusted_earnings_yield(stock, date=datetime.now(), lookback_period=timedelta(days=0), period: str = ''):
    return (me.earnings_before_interest_and_taxes(stock=stock, date=date, lookback_period=lookback_period,
                                                  period=period)
            + fi.accumulated_depreciation_amortization(stock=stock, date=date, lookback_period=lookback_period,
                                                       period=period)
            - abs(me.capital_expenditures(stock=stock, date=date, lookback_period=lookback_period,
                                          period=period))) / me.enterprise_value(stock=stock, date=date,
                                                                                 lookback_period=lookback_period,
                                                                                 period=period)


def greenblatt_earnings_yield(stock, date=datetime.now(), lookback_period=timedelta(days=0), period: str = ''):
    return me.earnings_before_interest_and_taxes(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / me.enterprise_value(stock=stock, date=date, lookback_period=lookback_period, period=period)


def price_to_earnings_to_growth(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=True,
                                period: str = '', diluted_shares: bool = False,
                                deduct_operating_income: bool = False, deduct_preferred_dividends: bool = True):
    eps_last_5_periods = [
        earnings_per_share(stock, date - timedelta(days=365 * i if annual else 90 * i),
                           lookback_period=timedelta(days=365), period=period, diluted_shares=diluted_shares,
                           deduct_operating_income=deduct_operating_income,
                           deduct_preferred_dividends=deduct_preferred_dividends) for i in range(5)]
    return price_to_earnings(stock=stock, date=date, lookback_period=lookback_period, period=period,
                             diluted_shares=diluted_shares, deduct_operating_income=deduct_operating_income,
                             deduct_preferred_dividends=deduct_preferred_dividends) \
           / excel.average_growth(eps_last_5_periods[::-1])


def price_to_cash_flow(stock, date=None,
                       lookback_period: timedelta = timedelta(days=0),
                       period: str = '', diluted_shares: bool = False):
    return


'''Enterprise Value Ratios'''


def enterprise_value_to_revenue(stock, date=None,
                                lookback_period: timedelta = timedelta(days=0),
                                period: str = ''):
    return me.enterprise_value(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / fi.net_sales(stock=stock, date=date, lookback_period=lookback_period, period=period)


def enterprise_value_to_ebitda(stock, date=None,
                               lookback_period: timedelta = timedelta(days=0),
                               period: str = ''):
    return me.enterprise_value(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / me.earnings_before_interest_and_taxes_and_depreciation_and_amortization(stock=stock, date=date,
                                                                                     lookback_period=lookback_period,
                                                                                     period=period)


def enterprise_value_to_ebit(stock, date=None,
                             lookback_period: timedelta = timedelta(days=0),
                             period: str = ''):
    return me.enterprise_value(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / me.earnings_before_interest_and_taxes(stock=stock, date=date, lookback_period=lookback_period,
                                                   period=period)


def enterprise_value_to_invested_capital(stock, date=None,
                                         lookback_period: timedelta = timedelta(days=0),
                                         period: str = ''):
    return me.enterprise_value(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / me.invested_capital(stock=stock, date=date, lookback_period=lookback_period, period=period)


def enterprise_value_to_free_cash_flow(stock, date=None,
                                       lookback_period: timedelta = timedelta(days=0),
                                       period: str = ''):
    return me.enterprise_value(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / me.free_cash_flow(stock=stock, date=date, lookback_period=lookback_period, period=period)


if __name__ == '__main__':
    # print(earnings_per_share(stock='AAPL', date=[datetime.now(), datetime(2019, 1, 1)], period='FY'))
    print(price_to_earnings(stock='AAPL', date=[datetime.now(), datetime(2019, 1, 1)], period='FY'))
