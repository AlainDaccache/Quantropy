from datetime import datetime, timedelta
import financial_statement_analysis.financial_statements_entries as fi
import financial_statement_analysis.financial_metrics as me
import numpy as np

'''
Liquidity ratios are financial ratios that measure a company’s ability to repay both short- and long-term obligations.
'''


# The current ratio measures a company’s ability to pay off short-term liabilities with current assets
# Current Ratio = Current Assets / Current Liabilities
def current_ratio(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=True, ttm=True):
    return fi.current_total_assets(stock=stock, date=date, lookback_period=lookback_period, annual=annual,
                                   ttm=ttm) / fi.current_total_liabilities(stock=stock, date=date,
                                                                           lookback_period=lookback_period,
                                                                           annual=annual, ttm=ttm)


# The acid-test ratio measures a company’s ability to pay off short-term liabilities with quick assets
# Acid-test ratio = Current assets – Inventories / Current liabilities
def acid_test_ratio(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=True, ttm=True):
    return (fi.current_total_assets(stock=stock, date=date, lookback_period=lookback_period, annual=annual,
                                    ttm=ttm) - fi.net_inventory(stock=stock, date=date, lookback_period=lookback_period,
                                                                annual=annual, ttm=ttm)) \
           / (fi.current_total_liabilities(stock=stock, date=date, lookback_period=lookback_period, annual=annual,
                                           ttm=ttm))


# The cash ratio measures a company’s ability to pay off short-term liabilities with cash and cash equivalents
# Cash ratio = Cash and Cash equivalents / Current Liabilities
def cash_ratio(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=True, ttm=True):
    return fi.cash_and_cash_equivalents(stock=stock, date=date, lookback_period=lookback_period, annual=annual,
                                        ttm=ttm) / fi.current_total_liabilities(stock=stock, date=date,
                                                                                lookback_period=lookback_period,
                                                                                annual=annual, ttm=ttm)


# The operating cash flow ratio is a measure of the number of times a company can pay off current liabilities with the cash generated in a given period
# Operating cash flow ratio = Operating cash flow / Current liabilities
def operating_cash_flow_ratio(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=True, ttm=True):
    return fi.cash_flow_operating_activities(stock=stock, date=date, lookback_period=lookback_period, annual=annual,
                                             ttm=ttm) / fi.current_total_liabilities(stock=stock, date=date,
                                                                                     lookback_period=lookback_period,
                                                                                     annual=annual, ttm=ttm)


'''
Leverage ratios measure the amount of capital that comes from debt. In other words, leverage financial ratios are used to evaluate a company’s debt levels.
'''


def debt(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=True, ttm=True,
         interest_expense=False,  # any interest-bearing liability to qualify
         all_liabilities=False,  # including accounts payable and deferred income
         long_term_debt=True  # and its associated currently due portion (measures capital structure)
         ):
    if long_term_debt:
        using_long_term_debt = fi.total_long_term_debt(stock=stock, date=date, lookback_period=lookback_period,
                                                       annual=annual, ttm=ttm)
        if np.isnan(using_long_term_debt):
            return fi.total_liabilities(stock=stock, date=date, lookback_period=lookback_period, annual=annual,
                                        ttm=ttm)
        else:
            return using_long_term_debt

    if all_liabilities:
        return fi.total_liabilities(stock=stock, date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)

    if interest_expense:
        return fi.interest_expense(stock=stock, date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)


# The debt ratio measures the relative amount of a company’s assets that are provided from debt
# Debt ratio = Total liabilities / Total assets
def debt_to_assets(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=True, ttm=True,
                   interest_expense=False, all_liabilities=False, long_term_debt=True):
    denominator = (fi.total_assets(stock=stock, date=date, lookback_period=lookback_period, annual=annual, ttm=ttm) +
                   fi.total_assets(stock=stock, date=date, lookback_period=timedelta(days=365), annual=annual,
                                   ttm=ttm)) / 2

    return debt(stock=stock, date=date, lookback_period=lookback_period, annual=annual, ttm=ttm,
                interest_expense=interest_expense, all_liabilities=all_liabilities,
                long_term_debt=long_term_debt) / denominator


def asset_to_equity(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=True, ttm=True):
    total_assets = fi.total_assets(stock=stock, date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)
    total_equity = fi.total_shareholders_equity(stock=stock, date=date, lookback_period=lookback_period, annual=annual,
                                                ttm=ttm)
    return total_assets / total_equity


# The debt to equity ratio calculates the weight of total debt and financial liabilities against shareholders’ equity
# Debt to equity ratio = Total liabilities / Shareholder’s equity
def debt_to_equity(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=True, ttm=True,
                   interest_expense=False, all_liabilities=False, long_term_debt=True):
    denominator = (fi.total_shareholders_equity(stock=stock, date=date, lookback_period=lookback_period, annual=annual,
                                                ttm=ttm) +
                   fi.total_shareholders_equity(stock=stock, date=date, lookback_period=timedelta(days=365),
                                                annual=annual, ttm=ttm)) / 2

    return debt(stock=stock, date=date, lookback_period=lookback_period, annual=annual, ttm=ttm,
                interest_expense=interest_expense, all_liabilities=all_liabilities,
                long_term_debt=long_term_debt) / denominator


def debt_to_capital(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=True, ttm=True,
                    interest_expense=False, all_liabilities=False, long_term_debt=True):
    total_debt = debt(stock=stock, date=date, lookback_period=lookback_period, annual=annual, ttm=ttm,
                      interest_expense=interest_expense, all_liabilities=all_liabilities, long_term_debt=long_term_debt)

    return total_debt / (total_debt + fi.total_shareholders_equity(stock=stock, date=date,
                                                                   lookback_period=lookback_period, annual=annual,
                                                                   ttm=ttm))


# The interest coverage ratio shows how easily a company can pay its interest expenses
# Interest coverage ratio = Operating income / Interest expenses
def interest_coverage(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=True, ttm=True):
    return fi.operating_income(stock=stock, date=date, lookback_period=lookback_period, annual=annual,
                               ttm=ttm) / fi.interest_expense(stock=stock, date=date, lookback_period=lookback_period,
                                                              annual=annual, ttm=ttm)


# The debt service coverage ratio reveals how easily a company can pay its debt obligations
# Debt service coverage ratio = Operating income / Total debt service
# Some companies might prefer to subtract CAPEX because capital expenditure is not expensed on the income
# statement but rather considered as an “investment”. Excluding CAPEX from EBITDA will give the company the actual
# amount of operating income available for debt repayment.
def debt_service_coverage(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=True, ttm=True,
                          with_capex=False):
    numerator = me.earnings_before_interest_and_taxes_and_depreciation_and_amortization(stock=stock, date=date,
                                                                                        lookback_period=lookback_period,
                                                                                        annual=annual, ttm=ttm)
    numerator -= abs(me.capital_expenditures(stock=stock, date=date, lookback_period=lookback_period, annual=annual,
                                             ttm=ttm)) if with_capex else 0
    return numerator / me.debt_service(stock=stock, date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)


'''
Efficiency ratios, also known as activity financial ratios, are used to measure how well a company is utilizing its assets and resources.
'''


# The asset turnover ratio measures a company’s ability to generate sales from assets
# Asset turnover ratio = Net sales / Total assets
def asset_turnover_ratio(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=True, ttm=False,
                         average_assets=True):
    if average_assets:
        total_assets = (fi.total_assets(stock=stock, date=date, lookback_period=lookback_period, annual=annual,
                                        ttm=ttm)
                        + fi.total_assets(stock=stock, date=date - timedelta(days=365 if annual else 90),
                                          lookback_period=lookback_period, annual=annual, ttm=ttm)) / 2
    else:
        total_assets = fi.total_assets(stock=stock, date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)
    revenues = fi.net_sales(stock=stock, date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)
    return revenues / total_assets


# The inventory turnover ratio measures how many times a company’s inventory is sold and replaced over a given period
# Inventory turnover ratio = Cost of goods sold / Average inventory
def inventory_turnover(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=True, ttm=True,
                       average_inventory=True):
    if average_inventory:
        inventory = (fi.net_inventory(stock=stock, date=date, lookback_period=lookback_period, annual=annual,
                                      ttm=ttm)
                     + fi.net_inventory(stock=stock, date=date - timedelta(days=365 if annual else 90),
                                        lookback_period=lookback_period, annual=annual, ttm=ttm)) / 2
    else:
        inventory = fi.net_inventory(stock=stock, date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)
    return fi.cost_of_goods_services(stock=stock, date=date, lookback_period=lookback_period, annual=annual,
                                     ttm=ttm) / inventory


# The accounts receivable turnover ratio measures how many times a company can turn receivables into cash over a given period
# Receivables turnover ratio = Net credit sales / Average accounts receivable
def receivables_turnover(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=True, ttm=True,
                         average_receivables=True):
    if average_receivables:
        accounts_receivable = (fi.net_accounts_receivable(stock=stock, date=date, lookback_period=lookback_period,
                                                          annual=annual, ttm=ttm)
                               + fi.net_accounts_receivable(stock=stock,
                                                            date=date - timedelta(days=365 if annual else 90),
                                                            lookback_period=lookback_period, annual=annual,
                                                            ttm=ttm)) / 2
    else:
        accounts_receivable = fi.net_accounts_receivable(stock=stock, date=date, lookback_period=lookback_period,
                                                         annual=annual, ttm=ttm)
    return me.net_credit_sales(stock=stock, date=date, lookback_period=lookback_period, annual=annual,
                               ttm=ttm) / accounts_receivable


# The days sales in inventory ratio measures the average number of days that a company holds on to inventory before selling it to customers
# Days sales in inventory ratio = 365 days / Inventory turnover ratio
def days_sales_in_inventory(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=True, ttm=True,
                            average_inventory=True):
    return 365 / inventory_turnover(stock=stock, date=date, lookback_period=lookback_period, annual=annual, ttm=ttm,
                                    average_inventory=average_inventory)


def return_on_capital(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=True, ttm=True):
    net_fixed_assets = fi.total_non_current_assets(stock=stock, date=date, lookback_period=lookback_period,
                                                   annual=annual,
                                                   ttm=ttm) - fi.accumulated_depreciation_amortization(
        stock=stock, date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)
    return me.earnings_before_interest_and_taxes(stock=stock, date=date, lookback_period=lookback_period, annual=annual,
                                                 ttm=ttm) / (
                   net_fixed_assets + me.working_capital(stock=stock, date=date, lookback_period=lookback_period,
                                                         annual=annual, ttm=ttm))


def retention_ratio(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=True, ttm=True):
    net_income = fi.net_income(stock=stock, date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)
    dividends = fi.payments_for_dividends(stock=stock, date=date, lookback_period=lookback_period, annual=annual,
                                          ttm=ttm)
    return (net_income - abs(dividends)) / net_income


'''
Profitability ratios measure a company’s ability to generate income relative to revenue, balance sheet assets, operating costs, and equity. 
'''

def profit_margin(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=True, ttm=False):
    return fi.net_income(stock=stock, date=date, lookback_period=lookback_period, annual=annual,
                           ttm=ttm) / fi.net_sales(stock=stock, date=date, lookback_period=lookback_period,
                                                   annual=annual, ttm=ttm)


# The gross margin ratio compares the gross profit of a company to its net sales to show how much profit a company makes after paying its cost of goods sold
# Gross margin ratio = Gross profit / Net sales
def gross_margin(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=True, ttm=False):
    return me.gross_profit(stock=stock, date=date, lookback_period=lookback_period, annual=annual,
                           ttm=ttm) / fi.net_sales(stock=stock, date=date, lookback_period=lookback_period,
                                    annual=annual, ttm=ttm)


# The operating margin ratio compares the operating income of a company to its net sales to determine operating efficiency
# Operating margin ratio = Operating income / Net sales
def operating_margin(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=True, ttm=False):
    return fi.operating_income(stock=stock, date=date, lookback_period=lookback_period, annual=annual,
                               ttm=ttm) / fi.net_sales(stock=stock, date=date, lookback_period=lookback_period,
                                                       annual=annual, ttm=ttm)


# The return on assets ratio measures how efficiently a company is using its assets to generate profit
# Return on assets ratio = Net income / Total assets
def return_on_assets(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=True, ttm=False,
                     average_assets=True):
    total_assets = fi.total_assets(stock=stock, date=date, lookback_period=lookback_period, annual=annual,
                                   ttm=ttm)
    return fi.net_income(stock=stock, date=date, lookback_period=lookback_period, annual=annual,
                         ttm=ttm) / total_assets


# The return on equity ratio measures how efficiently a company is using its equity to generate profit
# Return on equity ratio = Net income Attributable to Common Stockholders / Shareholder’s equity
def return_on_equity(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=True, ttm=False,
                     average_equity=True):
    if average_equity:
        shareholders_equity = (fi.total_shareholders_equity(stock=stock, date=date, lookback_period=lookback_period,
                                                            annual=annual, ttm=ttm)
                               + fi.total_shareholders_equity(stock, date - timedelta(days=365), annual, ttm)) / 2
    else:
        shareholders_equity = fi.total_shareholders_equity(stock=stock, date=date, lookback_period=lookback_period,
                                                           annual=annual, ttm=ttm)

    return fi.net_income(stock=stock, date=date, lookback_period=lookback_period, annual=annual,
                         ttm=ttm) / shareholders_equity


'''
Market value ratios are used to evaluate the share price of a company’s stock.
'''


# The book value per share ratio calculates the per-share value of a company based on equity available to shareholders
# Book value per share ratio = Shareholder’s equity / Total shares outstanding
def book_value_per_share(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=True, ttm=False):
    return fi.total_shareholders_equity(stock=stock, date=date, lookback_period=lookback_period, annual=annual,
                                        ttm=ttm) / fi.total_shares_outstanding(stock, date, annual,
                                                                               ttm)


# The earnings per share ratio measures the amount of net income earned for each share outstanding:
# Earnings per share ratio = Net earnings / Total shares outstanding
# Compared with Earnings per share, a company's cash flow is better indicator of the company's earnings power.
# If a company's earnings per share is less than cash flow per share over long term, investors need to be cautious and find out why.
def earnings_per_share(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=True, ttm=True,
                       diluted=True, deduct_operating_income=False,
                       deduct_preferred_dividends=True):
    numerator = fi.net_income(stock=stock, date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)
    numerator -= fi.preferred_dividends(stock=stock, date=date, lookback_period=lookback_period, annual=annual,
                                        ttm=ttm) if deduct_preferred_dividends else 0
    numerator -= fi.non_operating_income(stock=stock, date=date, lookback_period=lookback_period, annual=annual,
                                         ttm=ttm) if deduct_operating_income else 0
    return numerator / fi.total_shares_outstanding(stock, date, diluted, annual, ttm)


# The price-earnings ratio compares a company’s share price to its earnings per share:
# Price-earnings ratio = Share price / Earnings per share
def price_to_earnings(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=True, ttm=True,
                      diluted=True, deduct_operating_income=False,
                      deduct_preferred_dividends=True):
    return me.market_price(stock, date) / earnings_per_share(stock=stock, date=date,
                                                             lookback_period=lookback_period, annual=annual,
                                                             ttm=ttm, diluted=diluted,
                                                             deduct_operating_income=deduct_operating_income,
                                                             deduct_preferred_dividends=deduct_preferred_dividends)


def price_to_earnings_to_growth(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=True,
                                ttm=True, diluted=True,
                                deduct_operating_income=False, deduct_preferred_dividends=True):
    eps_last_5_years = [
        earnings_per_share(stock, date - timedelta(days=365 * i if annual else 90 * i),
                           lookback_period=timedelta(days=365), annual=annual, ttm=ttm, diluted=diluted,
                           deduct_operating_income=deduct_operating_income,
                           deduct_preferred_dividends=deduct_preferred_dividends) for i in range(5)]
    return price_to_earnings(stock=stock, date=date, lookback_period=lookback_period, annual=annual, ttm=ttm,
                             diluted=diluted, deduct_operating_income=deduct_operating_income,
                             deduct_preferred_dividends=deduct_preferred_dividends) / average_growth(eps_last_5_years)

    # inverse of price to earnings


def earnings_yield(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=True, ttm=True,
                   diluted=True,
                   deduct_operating_income=False,
                   deduct_preferred_dividends=True):
    return earnings_per_share(stock=stock, date=date, lookback_period=lookback_period, annual=annual, ttm=ttm,
                              diluted=diluted, deduct_operating_income=deduct_operating_income,
                              deduct_preferred_dividends=deduct_preferred_dividends) / me.market_price(stock, date)


# there is an adjusted version of the formula that accounts for differences in the capital structure and tax rates
# between companies.
def adjusted_earnings_yield(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=True, ttm=False):
    return (me.earnings_before_interest_and_taxes(stock=stock, date=date, lookback_period=lookback_period,
                                                  annual=annual, ttm=ttm)
            + fi.accumulated_depreciation_amortization(stock=stock, date=date, lookback_period=lookback_period,
                                                       annual=annual, ttm=ttm)
            - abs(me.capital_expenditures(stock=stock, date=date, lookback_period=lookback_period, annual=annual,
                                          ttm=ttm))) / me.enterprise_value(stock=stock, date=date,
                                                                           lookback_period=lookback_period,
                                                                           annual=annual, ttm=ttm)


def greenblatt_earnings_yield(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=True,
                              ttm=False):
    return me.earnings_before_interest_and_taxes(stock=stock, date=date, lookback_period=lookback_period, annual=annual,
                                                 ttm=ttm) / me.enterprise_value(stock=stock, date=date,
                                                                                lookback_period=lookback_period,
                                                                                annual=annual, ttm=ttm)


'''
Helpers
'''


def average_growth(list):  # the list starts at most recent (so growth is backwards).
    # Make sure to include extra field in the end (because list effectively shortens by one)
    growths = []
    for i in range(len(list) - 1):
        growths.append((list[i] - list[i + 1]) / list[i + 1])
    return np.mean(growths)


if __name__ == '__main__':
    print(current_ratio('GOOG', ttm=False))
