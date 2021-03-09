from datetime import datetime

from matilda.data_infrastructure.db_crud import read_market_price
from matilda.fundamental_analysis.financial_statements import *

'''
Intermediary data from financial statements used in accounting ratios and financial modeling
'''


def dividend_per_share(stock: str, date: datetime = datetime.now(), lookback_period: timedelta = timedelta(days=0),
                       period: str = '', diluted_shares: bool = True, deduct_preferred_dividends: bool = False):
    dividends_paid = payments_of_dividends(stock=stock, date=date, lookback_period=lookback_period, period=period)
    dividends_paid -= abs(preferred_dividends(stock=stock, date=date, lookback_period=lookback_period,
                                              period=period)) if deduct_preferred_dividends else 0
    shares_outstanding = total_shares_outstanding(stock=stock, diluted_shares=diluted_shares, date=date,
                                                  lookback_period=lookback_period, period=period)
    return abs(dividends_paid) / shares_outstanding


def cash_flow_per_share(cash_flow_metric, stock, date=datetime.today(), lookback_period=timedelta(days=0),
                        period: str = '', diluted_shares=True):
    cash_flow = cash_flow_metric(stock=stock, date=date, lookback_period=lookback_period, period=period)
    shares_outstanding = total_shares_outstanding(stock=stock, date=date, lookback_period=lookback_period,
                                                  period=period, diluted_shares=diluted_shares)
    return cash_flow / shares_outstanding


def market_capitalization(stock: str, diluted_shares: bool = False, date: datetime = datetime.now(),
                          lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    shares_outstanding = total_shares_outstanding(stock=stock, date=date, lookback_period=lookback_period,
                                                  period=period, diluted_shares=diluted_shares)
    output = read_market_price(stock, date, lookback_period) * shares_outstanding * 1000000  # TODO hotfix!
    print('Market Capitalization for {} on the {} is: {}'.format(stock, date, output))
    return output


def enterprise_value(stock: str, date: datetime = datetime.now(), lookback_period: timedelta = timedelta(days=0),
                     period: str = ''):
    """


    :param stock:
    :param date:
    :param lookback_period:
    :param period:
    :return:
    """
    # TODO check for unfunded pension liabilities and other debt-deemed provisions, and value of associate companies
    output = market_capitalization(stock=stock, date=date, lookback_period=lookback_period, period=period) \
             + total_long_term_debt(stock=stock, date=date, lookback_period=lookback_period, period=period) \
             + np.nan_to_num(
        minority_interest(stock=stock, date=date, lookback_period=lookback_period, period=period)) \
             + np.nan_to_num(
        preferred_stock_value(stock=stock, date=date, lookback_period=lookback_period, period=period)) \
             - cash_and_cash_equivalents(stock=stock, date=date, lookback_period=lookback_period, period=period)
    print('Enterprise Value for {} on the {} is: {}'.format(stock, date, output))
    return output


def gross_profit(stock: str, date: datetime = datetime.now(), lookback_period: timedelta = timedelta(days=0),
                 period: str = ''):
    return net_sales(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           - cost_of_goods_services(stock=stock, date=date, lookback_period=lookback_period, period=period)


def debt(stock: str, date: datetime = datetime.now(), lookback_period: timedelta = timedelta(days=0),
         period: str = '',
         only_interest_expense=False,  # any interest-bearing liability to qualify
         all_liabilities=False,  # including accounts payable and deferred income
         long_term_debt=True,  # and its associated currently due portion (measures capital structure)
         exclude_current_portion_long_term_debt=False  # if true then also above should be true
         ):
    if long_term_debt:
        if not exclude_current_portion_long_term_debt:
            return total_long_term_debt(stock=stock, date=date, lookback_period=lookback_period, period=period)
        else:
            return long_term_debt_excluding_current_portion(stock=stock, date=date, lookback_period=lookback_period,
                                                            period=period)

    if all_liabilities:
        return total_liabilities(stock=stock, date=date, lookback_period=lookback_period, period=period)

    if only_interest_expense:
        return interest_expense(stock=stock, date=date, lookback_period=lookback_period, period=period)


# TODO Review
def debt_service(stock: str, date: datetime = datetime.now(), lookback_period: timedelta = timedelta(days=0),
                 period: str = ''):
    return interest_expense(stock=stock, date=date, lookback_period=lookback_period, period=period)


# TODO Review
def net_credit_sales(stock: str, date: datetime = datetime.now(), lookback_period: timedelta = timedelta(days=0),
                     period: str = ''):
    return net_sales(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           - net_accounts_receivable(stock=stock, date=date, lookback_period=lookback_period, period=period)


def earnings_before_interest_and_taxes_and_depreciation_and_amortization(stock: str, date: datetime = datetime.now(),
                                                                         lookback_period: timedelta = timedelta(days=0),
                                                                         period: str = ''):
    return earnings_before_interest_and_taxes(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           + depreciation_and_amortization(stock=stock, date=date, lookback_period=lookback_period, period=period)


def earnings_before_interest_and_taxes(stock: str, date: datetime = datetime.now(),
                                       lookback_period: timedelta = timedelta(days=0),
                                       period: str = ''):
    return earnings_before_taxes(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           + income_tax_expense(stock=stock, date=date, lookback_period=lookback_period, period=period)


def earnings_before_taxes(stock: str, date: datetime = datetime.now(), lookback_period: timedelta = timedelta(days=0),
                          period: str = ''):
    directly_from_statement = read_financial_statement_entry(financial_statement='Income Statement', stock=stock,
                                                             entry_name=[
                                                                 'Income (Loss) from Continuing Operations before Income Taxes, Noncontrolling Interest',
                                                                 ' '],
                                                             date=date, lookback_period=lookback_period,
                                                             period=period)
    if not np.isnan(directly_from_statement):
        return directly_from_statement
    else:
        return net_income(stock=stock, date=date, lookback_period=lookback_period, period=period) \
               + income_tax_expense(stock=stock, date=date, lookback_period=lookback_period, period=period)


def effective_tax_rate(stock: str, date: datetime = datetime.now(), lookback_period: timedelta = timedelta(days=0),
                       period: str = ''):
    return income_tax_expense(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / earnings_before_taxes(stock=stock, date=date, lookback_period=lookback_period, period=period)


def capital_expenditures(stock: str, date: datetime = datetime.now(), lookback_period: timedelta = timedelta(days=0),
                         period: str = ''):
    from_cash_flow_statement = acquisition_property_plant_equipment(stock=stock, date=date,
                                                                    lookback_period=lookback_period, period=period)
    if not np.isnan(from_cash_flow_statement):
        return from_cash_flow_statement
    else:
        return net_property_plant_equipment(stock=stock, date=date, lookback_period=lookback_period, period=period) \
               - net_property_plant_equipment(stock=stock, date=date - timedelta(days=365 if period != 'Q' else 90),
                                              lookback_period=lookback_period, period=period) \
               + depreciation_and_amortization(stock=stock, date=date, lookback_period=lookback_period,
                                               period=period)


def funds_from_operations():
    pass


def adjusted_funds_from_operations():
    pass


# NOPAT
def net_operating_profit_after_tax(stock: str, date: datetime = datetime.now(),
                                   lookback_period: timedelta = timedelta(days=0),
                                   period: str = ''):
    return earnings_before_interest_and_taxes(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           * (1 - effective_tax_rate(stock=stock, date=date, lookback_period=lookback_period, period=period))


def net_current_asset_value(stock: str, date: datetime = datetime.now(), lookback_period: timedelta = timedelta(days=0),
                            period: str = ''):
    return total_current_assets(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           - total_liabilities(stock=stock, date=date, lookback_period=lookback_period, period=period)


def net_working_capital(stock: str, date: datetime = datetime.now(), lookback_period: timedelta = timedelta(days=0),
                        period: str = '',
                        exclude_current_portion_cash_and_debt=False,
                        only_include_payables_receivables_inventory=False):
    # broadest (as it includes all accounts)
    if not (exclude_current_portion_cash_and_debt or only_include_payables_receivables_inventory):
        return total_current_assets(stock=stock, date=date, lookback_period=lookback_period, period=period) \
               - total_current_liabilities(stock=stock, date=date, lookback_period=lookback_period, period=period)

    if exclude_current_portion_cash_and_debt:  # more narrow
        return (total_current_assets(stock=stock, date=date, lookback_period=lookback_period, period=period) -
                cash_and_cash_equivalents(stock=stock, date=date, lookback_period=lookback_period, period=period)) \
               - (total_current_liabilities(stock=stock, date=date, lookback_period=lookback_period, period=period)
                  - long_term_debt_current_maturities(stock=stock, date=date, lookback_period=lookback_period,
                                                      period=period))

    if only_include_payables_receivables_inventory:  # most narrow
        return net_accounts_receivable(stock=stock, date=date, lookback_period=lookback_period, period=period) \
               + net_inventory(stock=stock, date=date, lookback_period=lookback_period, period=period) \
               - accounts_payable(stock=stock, date=date, lookback_period=lookback_period, period=period)


def invested_capital(stock: str, date: datetime = datetime.now(), lookback_period: timedelta = timedelta(days=0),
                     period: str = '', operating_approach=True):
    if operating_approach:
        return net_working_capital(stock=stock, date=date, lookback_period=lookback_period, period=period,
                                   exclude_current_portion_cash_and_debt=True) \
               + net_property_plant_equipment(stock=stock, date=date, lookback_period=lookback_period, period=period) \
               + total_intangible_assets(stock=stock, date=date, lookback_period=lookback_period, period=period)
    else:  # investing approach
        return total_current_liabilities(stock=stock, date=date, lookback_period=lookback_period, period=period) \
               + long_term_debt_excluding_current_portion(stock, date, lookback_period=timedelta(days=0),
                                                          period=period) \
               + total_shareholders_equity(stock=stock, date=date, lookback_period=lookback_period, period=period) \
               + cash_flow_financing_activities(stock=stock, date=date, lookback_period=lookback_period,
                                                period=period) \
               + cash_flow_investing_activities(stock=stock, date=date, lookback_period=lookback_period,
                                                period=period)


def capital_employed(stock: str, date: datetime = datetime.now(), lookback_period: timedelta = timedelta(days=0),
                     period: str = ''):
    return total_assets(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           - total_current_liabilities(stock=stock, date=date, lookback_period=lookback_period, period=period)


def liquid_assets(stock: str, date: datetime = datetime.now(), lookback_period: timedelta = timedelta(days=0),
                  period: str = ''):
    return cash_and_cash_equivalents(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           + current_marketable_securities(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           + net_accounts_receivable(stock=stock, date=date, lookback_period=lookback_period, period=period)


def free_cash_flow(stock: str, date: datetime = datetime.now(), lookback_period: timedelta = timedelta(days=0),
                   period: str = ''):
    """
    Free Cash Flow is the amount of cash flow available for discretionary spending by the company after the necessary capital invesment.
    It builds on CFO but takes into account (deducts) Capital Expenditures. Unlike FCFE and FCFF, it is a generic measure of cash flow.

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetime.now().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.

    :return:
    """
    return cash_flow_operating_activities(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           - abs(capital_expenditures(stock=stock, date=date, lookback_period=lookback_period, period=period))


# FCFE is the amount of cash flow available to equity investors after paying interest to debt holders, considering net debt issued (or repaid) and reinvesting capital in the business.
# It is the Operating Cash Flow - Capital Expenditures + Net Debt Issued
def free_cash_flow_to_equity(stock: str, date: datetime = datetime.now(),
                             lookback_period: timedelta = timedelta(days=0), period: str = ''):
    return free_cash_flow(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           + net_debt_issued(stock=stock, date=date, lookback_period=lookback_period, period=period)


# FCFF equires multi-step calculation and is used in DCF analysis to arrive at the enterprise value.
# It is a hypothetical figure to estimate the firm value if it has no debt (i.e. if it was completely equity financed).
# It is the EBIT * (1 - Tax Rate) + Depreciation & Amortization - Increase in Non-Cash Working Capital - Capital Expenditures
def free_cash_flow_to_firm(stock: str, date: datetime = datetime.now(), lookback_period: timedelta = timedelta(days=0),
                           period: str = ''):
    return earnings_before_interest_and_taxes(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           * (1 - effective_tax_rate(stock=stock, date=date, lookback_period=lookback_period, period=period)) \
           + depreciation_and_amortization(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           - (net_working_capital(stock=stock, date=date, lookback_period=lookback_period, period=period)
              - net_working_capital(stock=stock, date=date - timedelta(days=365 if period != 'Q' else 90),
                                    lookback_period=lookback_period, period=period)) \
           - capital_expenditures(stock=stock, date=date, lookback_period=lookback_period, period=period)
