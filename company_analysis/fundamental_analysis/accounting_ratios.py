from datetime import datetime, timedelta
import company_analysis.fundamental_analysis.financial_statements_entries as fi
import company_analysis.fundamental_analysis.financial_metrics as me
import numpy as np

'''
Liquidity ratios are financial ratios that measure a company’s ability to repay both short- and long-term obligations.
'''


# The current ratio measures a company’s ability to pay off short-term liabilities with current assets
# Current Ratio = Current Assets / Current Liabilities
def current_ratio(stock, date=datetime.now(), annual=True, ttm=True):
    return fi.current_total_assets(stock, date, annual, ttm) / fi.current_total_liabilities(stock, date, annual, ttm)


# The acid-test ratio measures a company’s ability to pay off short-term liabilities with quick assets
# Acid-test ratio = Current assets – Inventories / Current liabilities
def acid_test_ratio(stock, date=datetime.now(), annual=True, ttm=True):
    return (fi.current_total_assets(stock, date, annual, ttm) - fi.net_inventory(stock, date, annual, ttm)) \
           / (fi.current_total_liabilities(stock, date, annual, ttm))


# The cash ratio measures a company’s ability to pay off short-term liabilities with cash and cash equivalents
# Cash ratio = Cash and Cash equivalents / Current Liabilities
def cash_ratio(stock, date=datetime.now(), annual=True, ttm=True):
    return fi.cash_and_cash_equivalents(stock, date, annual, ttm) / fi.current_total_liabilities(stock, date, annual, ttm)


# The operating cash flow ratio is a measure of the number of times a company can pay off current liabilities with the cash generated in a given period
# Operating cash flow ratio = Operating cash flow / Current liabilities
def operating_cash_flow_ratio(stock, date=datetime.now(), annual=True, ttm=True):
    return fi.cash_flow_operating_activities(stock, date, annual, ttm) / fi.current_total_liabilities(stock, date, annual, ttm)


'''
Leverage ratios measure the amount of capital that comes from debt. In other words, leverage financial ratios are used to evaluate a company’s debt levels.
'''


# The debt ratio measures the relative amount of a company’s assets that are provided from debt
# Debt ratio = Total liabilities / Total assets
def debt_to_assets(stock, date=datetime.now(), annual=True, ttm=True, long_term=False):
    numerator = fi.total_non_current_liabilities(stock, date, annual, ttm) if long_term else fi.total_liabilities(stock, date, annual, ttm)
    return numerator / fi.total_assets(stock, date, annual, ttm)


# The debt to equity ratio calculates the weight of total debt and financial liabilities against shareholders’ equity
# Debt to equity ratio = Total liabilities / Shareholder’s equity
def debt_to_equity(stock, date=datetime.now(), annual=True, ttm=True, long_term=False):
    numerator = fi.total_non_current_liabilities(stock, date, annual, ttm) if long_term else fi.total_liabilities(stock, date, annual, ttm)
    return numerator / fi.total_shareholders_equity(stock, date, annual, ttm)


def debt_to_capital(stock, date=datetime.now(), annual=True, ttm=True, long_term=False):
    numerator = fi.total_non_current_liabilities(stock, date, annual, ttm) if long_term else fi.total_liabilities(stock, date, annual, ttm)
    return numerator / (fi.total_shareholders_equity(stock, date, annual, ttm)
                                                             + fi.total_liabilities(stock, date, annual, ttm))


# The interest coverage ratio shows how easily a company can pay its interest expenses
# Interest coverage ratio = Operating income / Interest expenses
def interest_coverage(stock, date=datetime.now(), annual=True, ttm=True):
    return fi.operating_income(stock, date, annual, ttm) / fi.interest_expense(stock, date, annual, ttm)


# The debt service coverage ratio reveals how easily a company can pay its debt obligations
# Debt service coverage ratio = Operating income / Total debt service
# Some companies might prefer to subtract CAPEX because capital expenditure is not expensed on the income
# statement but rather considered as an “investment”. Excluding CAPEX from EBITDA will give the company the actual
# amount of operating income available for debt repayment.
def debt_service_coverage(stock, date=datetime.now(), annual=True, ttm=True, with_capex=False):
    numerator = me.ebitda(stock, date, annual, ttm)
    numerator -= me.capex(stock, date, annual, ttm) if with_capex else 0
    return numerator / me.debt_service(stock, date, annual, ttm)


'''
Efficiency ratios, also known as activity financial ratios, are used to measure how well a company is utilizing its assets and resources.
'''


# The asset turnover ratio measures a company’s ability to generate sales from assets
# Asset turnover ratio = Net sales / Total assets
def asset_turnover_ratio(stock, date=datetime.now(), annual=True, ttm=False):
    average_total_assets = (fi.total_assets(stock, date, annual, ttm) + fi.total_assets(stock, date-timedelta(days=365), annual, ttm)) / 2
    return fi.net_sales(stock, date, annual, ttm) / average_total_assets


# The inventory turnover ratio measures how many times a company’s inventory is sold and replaced over a given period
# Inventory turnover ratio = Cost of goods sold / Average inventory
def inventory_turnover(stock, date=datetime.now(), annual=True, ttm=True):
    average_inventory = (fi.net_inventory(stock, date, annual, ttm) + fi.net_inventory(stock, date - timedelta(days=365), annual, ttm)) / 2
    return fi.cost_of_goods_services(stock, date, annual, ttm) / average_inventory


# The accounts receivable turnover ratio measures how many times a company can turn receivables into cash over a given period
# Receivables turnover ratio = Net credit sales / Average accounts receivable
def receivables_turnover(stock, date=datetime.now(), annual=True, ttm=True):
    average_accounts_receivable = (fi.net_accounts_receivable(stock, date, annual, ttm) + fi.net_accounts_receivable(stock, date - timedelta(days=365), annual, ttm)) / 2
    return me.net_credit_sales(stock, date, annual, ttm) / average_accounts_receivable


# The days sales in inventory ratio measures the average number of days that a company holds on to inventory before selling it to customers
# Days sales in inventory ratio = 365 days / Inventory turnover ratio
def days_sales_in_inventory(stock, date=datetime.now(), annual=True, ttm=True):
    return 365 / inventory_turnover(stock, date, annual, ttm)


def return_on_capital(stock, date=datetime.now(), annual=True, ttm=True):
    net_fixed_assets = fi.total_non_current_assets(stock, date, annual, ttm) - fi.accumulated_depreciation_amortization(stock, date, annual, ttm)
    return me.ebit(stock, date, annual, ttm) / (net_fixed_assets + me.working_capital(stock, date, annual, ttm))


'''
Profitability ratios measure a company’s ability to generate income relative to revenue, balance sheet assets, operating costs, and equity. 
'''


# The gross margin ratio compares the gross profit of a company to its net sales to show how much profit a company makes after paying its cost of goods sold
# Gross margin ratio = Gross profit / Net sales
def gross_margin(stock, date, annual=True, ttm=False):
    return me.gross_profit(stock, date, annual, ttm) / fi.net_sales(stock, date, annual, ttm)


# The operating margin ratio compares the operating income of a company to its net sales to determine operating efficiency
# Operating margin ratio = Operating income / Net sales
def operating_margin(stock, date=datetime.now(), annual=True, ttm=False):
    return fi.operating_income(stock, date, annual, ttm) / fi.net_sales(stock, date, annual, ttm)


# The return on assets ratio measures how efficiently a company is using its assets to generate profit
# Return on assets ratio = Net income / Total assets
def return_on_assets(stock, date=datetime.now(), annual=True, ttm=False):
    average_total_assets = (fi.total_assets(stock, date, annual, ttm) + fi.total_assets(stock, date - timedelta(days=365), annual, ttm)) / 2
    return fi.net_income(stock, date, annual) / average_total_assets


# The return on equity ratio measures how efficiently a company is using its equity to generate profit
# Return on equity ratio = Net income Attributable to Common Stockholders / Shareholder’s equity
def return_on_equity(stock, date=datetime.now(), annual=True, ttm=False):
    average_shareholders_equity = (fi.total_shareholders_equity(stock, date, annual, ttm)
                                   + fi.total_shareholders_equity(stock, date-timedelta(days=365), annual, ttm)) / 2
    return fi.net_income(stock, date, annual, ttm) / average_shareholders_equity

'''
Market value ratios are used to evaluate the share price of a company’s stock.
'''


# The book value per share ratio calculates the per-share value of a company based on equity available to shareholders
# Book value per share ratio = Shareholder’s equity / Total shares outstanding
def book_value_per_share(stock, date=datetime.now(), annual=True, ttm=False):
    return fi.total_shareholders_equity(stock, date, annual, ttm) / fi.total_shares_outstanding(stock, date, annual, ttm)


# The earnings per share ratio measures the amount of net income earned for each share outstanding:
# Earnings per share ratio = Net earnings / Total shares outstanding
# Compared with Earnings per share, a company's cash flow is better indicator of the company's earnings power.
# If a company's earnings per share is less than cash flow per share over long term, investors need to be cautious and find out why.
def earnings_per_share(stock, date=datetime.now(), annual=True, ttm=True, diluted=True, deduct_operating_income=False, deduct_preferred_dividends=True):
    numerator = fi.net_income(stock, date, annual, ttm)
    numerator -= fi.preferred_dividends(stock, date, annual, ttm) if deduct_preferred_dividends else 0
    numerator -= fi.non_operating_income(stock, date, annual, ttm) if deduct_operating_income else 0
    return numerator / fi.total_shares_outstanding(stock, date, diluted, annual, ttm)


# The price-earnings ratio compares a company’s share price to its earnings per share:
# Price-earnings ratio = Share price / Earnings per share
def price_to_earnings(stock, date=datetime.now(), annual=True, ttm=True, diluted=True, deduct_operating_income=False, deduct_preferred_dividends=True):
    return me.market_price(stock, date) / earnings_per_share(stock, date, annual, ttm, diluted, deduct_operating_income, deduct_preferred_dividends)


def price_to_earnings_to_growth(stock, date=datetime.now(), annual=True, ttm=True, diluted=True, deduct_operating_income=False, deduct_preferred_dividends=True):
    eps_last_5_years = [earnings_per_share(stock, date-timedelta(365*i), annual, ttm, diluted, deduct_operating_income, deduct_preferred_dividends) for i in range(5)]
    return price_to_earnings(stock, date, annual, ttm, diluted, deduct_operating_income, deduct_preferred_dividends) / average_growth(eps_last_5_years)


# inverse of price to earnings
def earnings_yield(stock, date=datetime.now(), annual=True, ttm=True, diluted=True, deduct_operating_income=False, deduct_preferred_dividends=True):
    return earnings_per_share(stock, date, ttm, diluted, deduct_operating_income, deduct_preferred_dividends) / me.market_price(stock, date)


# there is an adjusted version of the formula that accounts for differences in the capital structure and tax rates
# between companies.
def adjusted_earnings_yield(stock, date=datetime.now(), annual=True, ttm=False):
    return (me.ebit(stock, date, annual, ttm)
            + fi.accumulated_depreciation_amortization(stock, date, annual, ttm)
            - me.capex(stock, date, annual, ttm)) / me.enterprise_value(stock, date, annual, ttm)


def greenblatt_earnings_yield(stock, date=datetime.now(), annual=True, ttm=False):
    return me.ebit(stock, date, annual, ttm) / me.enterprise_value(stock, date, annual, ttm)


'''
Helpers
'''


def average_growth(list): # the list starts at most recent (so growth is backwards).
    # Make sure to include extra field in the end (because list effectively shortens by one)
    growths = []
    for i in range(len(list)-1):
        growths.append((list[i]-list[i+1])/list[i+1])
    return np.mean(growths)

if __name__ == '__main__':
    print(current_ratio('GOOG', ttm=False))
