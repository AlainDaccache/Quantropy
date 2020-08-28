from datetime import datetime, timedelta
import numpy as np
import config
import os
import historical_data_collection.excel_helpers as excel
import math


def read_financial_statement_entry(stock: str, financial_statement: str, entry_name: list,
                                   date: datetime = datetime.now(),
                                   lookback_period: timedelta = timedelta(days=0), period: str = '') -> float:
    '''
    Read an entry from a financial statement. By default, we read the most recent position for the balance sheet,
    and the trailing twelve months for the income statement and cash flow statement.
    
    :param financial_statement: 'Balance Sheet', 'Income Statement', 'Cash Flow Statement'
    :param stock:
    :param entry_name:
    :param date:
    :param lookback_period:
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months
    :return:
    '''
    path = os.path.join(config.FINANCIAL_STATEMENTS_DIR_PATH, stock + '.xlsx')
    if period == 'FY':
        sheet_name = config.balance_sheet_yearly if financial_statement == 'Balance Sheet' \
            else config.income_statement_yearly if financial_statement == 'Income Statement' \
            else config.cash_flow_statement_yearly if financial_statement == 'Cash Flow Statement' \
            else Exception
    elif period in ['Q', 'TTM', 'YTD']:
        sheet_name = config.balance_sheet_quarterly if financial_statement == 'Balance Sheet' \
            else config.income_statement_quarterly if financial_statement == 'Income Statement' \
            else config.cash_flow_statement_quarterly if financial_statement == 'Cash Flow Statement' \
            else Exception
    else:
        raise Exception

    if period == 'TTM':

        entries_for_ttm = [excel.read_entry_from_csv(path=path, sheet_name=sheet_name, y=entry_name, x=date,
                                                     lookback_index=math.floor(i + (lookback_period.days / 90)))
                           for i in range(4)]

        return float(np.mean(entries_for_ttm)) if financial_statement == 'Balance Sheet' \
            else float(np.sum(entries_for_ttm))  # income statement or cash flow statement, cumulative

    elif period == 'YTD':
        entries_post_year_beginning, i = [], 0
        while datetime((date - lookback_period).year, 1, 1) + timedelta(days=i * 90) < date:
            entry = excel.read_entry_from_csv(path=path, sheet_name=sheet_name,
                                              y=entry_name,
                                              x=datetime((date - lookback_period).year, 1, 1) + timedelta(days=i * 90),
                                              lookback_index=math.floor(lookback_period.days / 90))
            i = i + 1
            entries_post_year_beginning.append(entry)
        return float(np.mean(entries_post_year_beginning))

    return excel.read_entry_from_csv(path=path, sheet_name=sheet_name, y=entry_name, x=date,
                                     lookback_index=math.floor(lookback_period.days / 90) if period == 'Q'
                                     else math.floor(lookback_period.days / 365))


'''Balance Sheet Entries'''


def cash_and_cash_equivalents(stock: str, date: datetime = datetime.now(),
                              lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Assets', 'Current Assets', 'Cash and Cash Equivalents'],
                                          date=date, lookback_period=lookback_period, period=period)


def current_marketable_securities(stock: str, date: datetime = datetime.now(),
                                  lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Assets', 'Current Assets', 'Marketable Securities Current'],
                                          date=date, lookback_period=lookback_period, period=period)


def gross_accounts_receivable(stock: str, date: datetime = datetime.now(),
                              lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Assets', 'Current Assets', 'Gross Accounts Receivable'],
                                          date=date, lookback_period=lookback_period, period=period)


def allowances_for_doubtful_accounts(stock: str, date: datetime = datetime.now(),
                                     lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Assets', 'Current Assets', 'Allowances for Doubtful Accounts'],
                                          date=date, lookback_period=lookback_period, period=period)


def net_accounts_receivable(stock: str, date: datetime = datetime.now(),
                            lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Assets', 'Current Assets', 'Net Accounts Receivable'],
                                          date=date, lookback_period=lookback_period, period=period)


# TODO
def credit_sales(stock: str, date: datetime = datetime.now(),
                 lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    pass


# TODO
def credit_purchases(stock: str, date: datetime = datetime.now(),
                     lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    pass


def current_prepaid_expenses(stock: str, date: datetime = datetime.now(),
                             lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Assets', 'Current Assets', 'Prepaid Expense, Current'],
                                          date=date, lookback_period=lookback_period, period=period)


def net_inventory(stock: str, date: datetime = datetime.now(),
                  lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Assets', 'Current Assets', 'Inventory, Net'],
                                          date=date, lookback_period=lookback_period, period=period)


def current_income_taxes_receivable(stock: str, date: datetime = datetime.now(),
                                    lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Assets', 'Current Assets',
                                                      'Income Taxes Receivable, Current'],
                                          date=date, lookback_period=lookback_period, period=period)


def assets_held_for_sale(stock: str, date: datetime = datetime.now(), lookback_period: timedelta = timedelta(days=0),
                         period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Assets', 'Current Assets', 'Assets Held-for-sale'],
                                          date=date, lookback_period=lookback_period, period=period)


def current_deferred_tax_assets(stock: str, date: datetime = datetime.now(),
                                lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Assets', 'Current Assets', 'Deferred Tax Assets, Current'],
                                          date=date, lookback_period=lookback_period, period=period)


def other_current_assets(stock: str, date: datetime = datetime.now(), lookback_period: timedelta = timedelta(days=0),
                         period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Assets', 'Current Assets', 'Other Assets, Current'],
                                          date=date, lookback_period=lookback_period, period=period)


def current_total_assets(stock: str, date: datetime = datetime.now(),
                         lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Assets', 'Current Assets', 'Total Current Assets'],
                                          date=date, lookback_period=lookback_period, period=period)


def non_current_marketable_securities(stock: str, date: datetime = datetime.now(),
                                      lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Assets', 'Non Current Assets',
                                                      'Marketable Securities Non Current'],
                                          date=date, lookback_period=lookback_period, period=period)


def accumulated_depreciation_amortization(stock: str, date: datetime = datetime.now(),
                                          lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Assets', 'Non Current Assets',
                                                      'Accumulated Depreciation and Amortization'],
                                          date=date, lookback_period=lookback_period, period=period)


def net_property_plant_equipment(stock: str, date: datetime = datetime.now(),
                                 lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Assets', 'Non Current Assets',
                                                      'Property, Plant and Equipment, Net'],
                                          date=date, lookback_period=lookback_period, period=period)


def operating_lease_right_of_use_assets(stock: str, date: datetime = datetime.now(),
                                        lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Assets', 'Non Current Assets',
                                                      'Operating Lease Right-of-use Assets'],
                                          date=date, lookback_period=lookback_period, period=period)


def non_current_deferred_tax_assets(stock: str, date: datetime = datetime.now(),
                                    lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Assets', 'Non Current Assets',
                                                      'Deferred Tax Assets Non Current'],
                                          date=date, lookback_period=lookback_period, period=period)


def goodwill(stock: str, date: datetime = datetime.now(),
             lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Assets', 'Non Current Assets', 'Goodwill'],
                                          date=date, lookback_period=lookback_period, period=period)


def net_intangible_assets(stock: str, date: datetime = datetime.now(), lookback_period: timedelta = timedelta(days=0),
                          period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Assets', 'Non Current Assets',
                                                      'Intangible Assets, Net (Excluding Goodwill)'],
                                          date=date, lookback_period=lookback_period, period=period)


def total_intangible_assets(stock: str, date: datetime = datetime.now(), lookback_period: timedelta = timedelta(days=0),
                            period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Assets', 'Non Current Assets', 'Total Intangible Assets'],
                                          date=date, lookback_period=lookback_period, period=period)


def other_non_current_assets(stock: str, date: datetime = datetime.now(),
                             lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Assets', 'Non Current Assets', 'Other Non Current Assets'],
                                          date=date, lookback_period=lookback_period, period=period)


def total_non_current_assets(stock: str, date: datetime = datetime.now(),
                             lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Assets', 'Non Current Assets', 'Total Non Current Assets'],
                                          date=date, lookback_period=lookback_period, period=period)


def total_assets(stock: str, date: datetime = datetime.now(),
                 lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Assets', 'Total Assets', 'Total Assets'],
                                          date=date, lookback_period=lookback_period, period=period)


def long_term_debt_current_maturities(stock: str, date: datetime = datetime.now(),
                                      lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Liabilities and Shareholders\' Equity', 'Liabilities',
                                                      'Long-term Debt, Current Maturities'],
                                          date=date, lookback_period=lookback_period, period=period)


def accounts_payable(stock: str, date: datetime = datetime.now(), lookback_period: timedelta = timedelta(days=0),
                     period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Liabilities and Shareholders\' Equity', 'Liabilities',
                                                      'Accounts Payable'],
                                          date=date, lookback_period=lookback_period, period=period)


def current_deferred_revenues(stock: str, date: datetime = datetime.now(),
                              lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Liabilities and Shareholders\' Equity', 'Liabilities',
                                                      'Current Deferred Revenues'],
                                          date=date, lookback_period=lookback_period, period=period)


def current_accrued_liabilities(stock: str, date: datetime = datetime.now(),
                                lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Liabilities and Shareholders\' Equity', 'Liabilities',
                                                      'Accrued Liabilities, Current'],
                                          date=date, lookback_period=lookback_period, period=period)


def current_total_liabilities(stock: str, date: datetime = datetime.now(),
                              lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Liabilities and Shareholders\' Equity', 'Liabilities',
                                                      'Total Current Liabilities'],
                                          date=date, lookback_period=lookback_period, period=period)


def long_term_debt_excluding_current_portion(stock: str, date: datetime = datetime.now(),
                                             lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Liabilities and Shareholders\' Equity', 'Liabilities',
                                                      'Long-term Debt, Noncurrent Maturities'],
                                          date=date, lookback_period=lookback_period, period=period)


def total_long_term_debt(stock: str, date: datetime = datetime.now(), lookback_period: timedelta = timedelta(days=0),
                         period: str = 'Q'):
    return long_term_debt_current_maturities(stock=stock, date=date, lookback_period=lookback_period,
                                             period=period) + \
           long_term_debt_excluding_current_portion(stock=stock, date=date, lookback_period=lookback_period,
                                                    period=period)


def total_non_current_liabilities(stock: str, date: datetime = datetime.now(),
                                  lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Liabilities and Shareholders\' Equity', 'Liabilities',
                                                      'Total Non Current Liabilities'],
                                          date=date, lookback_period=lookback_period, period=period)


def total_liabilities(stock: str, date: datetime = datetime.now(), lookback_period: timedelta = timedelta(days=0),
                      period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Liabilities and Shareholders\' Equity', 'Liabilities',
                                                      'Total Liabilities'],
                                          date=date, lookback_period=lookback_period, period=period)


def preferred_stock_value(stock: str, date: datetime = datetime.now(), lookback_period: timedelta = timedelta(days=0),
                          period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Liabilities and Shareholders\' Equity',
                                                      'Shareholders\' Equity',
                                                      'Preferred Stock, Value, Issued'],
                                          date=date, lookback_period=lookback_period, period=period)


def additional_paid_in_capital(stock: str, date: datetime = datetime.now(),
                               lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Liabilities and Shareholders\' Equity',
                                                      'Shareholders\' Equity',
                                                      'Additional Paid in Capital'],
                                          date=date, lookback_period=lookback_period, period=period)


def retained_earnings(stock: str, date: datetime = datetime.now(), lookback_period: timedelta = timedelta(days=0),
                      period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Liabilities and Shareholders\' Equity',
                                                      'Shareholders\' Equity',
                                                      'Retained Earnings (Accumulated Deficit)'],
                                          date=date, lookback_period=lookback_period, period=period)


def accumulated_other_comprehensive_income(stock: str, date: datetime = datetime.now(),
                                           lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Liabilities and Shareholders\' Equity',
                                                      'Shareholders\' Equity',
                                                      'Accumulated Other Comprehensive Income (Loss)'],
                                          date=date, lookback_period=lookback_period, period=period)


def minority_interest(stock: str, date: datetime = datetime.now(), lookback_period: timedelta = timedelta(days=0),
                      period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                          entry_name=['Liabilities and Shareholders\' Equity',
                                                      'Shareholders\' Equity',
                                                      'Minority Interest'],
                                          date=date, lookback_period=lookback_period, period=period)


def total_shares_outstanding(stock: str, diluted_shares: bool = False, date: datetime = datetime.now(),
                             lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    entry = ['Liabilities and Shareholders\' Equity', 'Shareholders\' Equity',
             'Weighted Average Number of Shares Outstanding, Diluted'] if diluted_shares \
        else ['Liabilities and Shareholders\' Equity', 'Shareholders\' Equity',
              'Weighted Average Number of Shares Outstanding, Basic']
    return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock, entry_name=entry, date=date,
                                          lookback_period=lookback_period, period=period)


def total_shareholders_equity(stock: str, date: datetime = datetime.now(),
                              lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    including_noncontrolling = read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                                              entry_name=['Liabilities and Shareholders\' Equity',
                                                                          'Shareholders\' Equity',
                                                                          'Stockholders\' Equity, Including Portion Attributable to Noncontrolling Interest'],
                                                              date=date, lookback_period=lookback_period, period=period)
    if np.isnan(including_noncontrolling):
        return read_financial_statement_entry(financial_statement='Balance Sheet', stock=stock,
                                              entry_name=['Liabilities and Shareholders\' Equity',
                                                          'Shareholders\' Equity',
                                                          'Stockholders\' Equity Attributable to Parent'],
                                              date=date, lookback_period=lookback_period, period=period)
    else:
        return including_noncontrolling


'''Income Statement Entries'''


def net_sales(stock: str, date: datetime = datetime.now(),
              lookback_period: timedelta = timedelta(days=0), period: str = 'TTM'):
    return read_financial_statement_entry(financial_statement='Income Statement', stock=stock,
                                          entry_name=['Revenues', 'Net Sales'],
                                          date=date, lookback_period=lookback_period, period=period)


def cost_of_goods_services(stock: str, date: datetime = datetime.now(),
                           lookback_period: timedelta = timedelta(days=0), period: str = 'TTM'):
    return read_financial_statement_entry(financial_statement='Income Statement', stock=stock,
                                          entry_name=['Costs and Expenses', 'Cost of Goods and Services Sold'],
                                          date=date, lookback_period=lookback_period, period=period)


def research_development_expense(stock: str, date: datetime = datetime.now(),
                                 lookback_period: timedelta = timedelta(days=0), period: str = 'TTM'):
    return read_financial_statement_entry(financial_statement='Income Statement', stock=stock,
                                          entry_name=['Costs and Expenses',
                                                      'Research and Development Expense'],
                                          date=date, lookback_period=lookback_period, period=period)


def selling_general_administrative(stock: str, date: datetime = datetime.now(),
                                   lookback_period: timedelta = timedelta(days=0), period: str = 'TTM'):
    return read_financial_statement_entry(financial_statement='Income Statement', stock=stock,
                                          entry_name=['Costs and Expenses',
                                                      'Selling, General and Administrative'],
                                          date=date, lookback_period=lookback_period, period=period)


def total_operating_expenses(stock: str, date: datetime = datetime.now(),
                             lookback_period: timedelta = timedelta(days=0), period: str = 'TTM'):
    return read_financial_statement_entry(financial_statement='Income Statement', stock=stock,
                                          entry_name=['Costs and Expenses', 'Total Operating Expenses'],
                                          date=date, lookback_period=lookback_period, period=period)


def operating_income(stock: str, date: datetime = datetime.now(),
                     lookback_period: timedelta = timedelta(days=0), period: str = 'TTM'):
    return read_financial_statement_entry(financial_statement='Income Statement', stock=stock,
                                          entry_name=['Operating Income (Loss) / EBIT',
                                                      'Operating Income (Loss) / EBIT'],
                                          date=date,
                                          lookback_period=lookback_period, period=period)


def interest_income(stock: str, date: datetime = datetime.now(),
                    lookback_period: timedelta = timedelta(days=0), period: str = 'TTM'):
    for el in ['Interest and Dividend Income', 'Interest Income']:
        ans = read_financial_statement_entry(financial_statement='Income Statement', stock=stock,
                                             entry_name=['Non-Operating Income (Expense)', el],
                                             date=date, lookback_period=lookback_period, period=period)
        if not np.isnan(ans):
            return ans
    return np.nan


def interest_expense(stock: str, date: datetime = datetime.now(),
                     lookback_period: timedelta = timedelta(days=0), period: str = 'TTM'):
    return read_financial_statement_entry(financial_statement='Income Statement', stock=stock,
                                          entry_name=['Non-Operating Income (Expense)', 'Interest Expense'],
                                          date=date, lookback_period=lookback_period, period=period)


def interest_income_expense_net(stock: str, date: datetime = datetime.now(),
                                lookback_period: timedelta = timedelta(days=0), period: str = 'TTM'):
    return read_financial_statement_entry(financial_statement='Income Statement', stock=stock,
                                          entry_name=['Non-Operating Income (Expense)',
                                                      'Interest Income (Expense), Net'],
                                          date=date, lookback_period=lookback_period, period=period)


def non_operating_income(stock: str, date: datetime = datetime.now(),
                         lookback_period: timedelta = timedelta(days=0), period: str = 'TTM'):
    return read_financial_statement_entry(financial_statement='Income Statement', stock=stock,
                                          entry_name=['Non-Operating Income (Expense)',
                                                      'Non-Operating Income (Expense)'],
                                          date=date, lookback_period=lookback_period, period=period)


def income_tax_expense(stock: str, date: datetime = datetime.now(),
                       lookback_period: timedelta = timedelta(days=0), period: str = 'TTM'):
    return read_financial_statement_entry(financial_statement='Income Statement', stock=stock,
                                          entry_name=['Income Tax Expense (Benefit)', 'Income Tax Expense (Benefit)'],
                                          date=date, lookback_period=lookback_period, period=period)


def net_income(stock: str, date: datetime = datetime.now(),
               lookback_period: timedelta = timedelta(days=0), period: str = 'TTM'):
    for el in ['Net Income (Loss) Attributable to Parent',
               'Net Income (Loss) Available to Common Stockholders, Basic',
               'Net Income Loss Attributable to Noncontrolling (Minority) Interest']:
        ans = read_financial_statement_entry(financial_statement='Income Statement', stock=stock, entry_name=[el, el],
                                             date=date, lookback_period=lookback_period, period=period)
        if not np.isnan(ans):
            return ans
    return np.nan


def preferred_dividends(stock: str, date: datetime = datetime.now(),
                        lookback_period: timedelta = timedelta(days=0), period: str = 'TTM'):
    return np.nan_to_num(read_financial_statement_entry(financial_statement='Income Statement', stock=stock,
                                                        entry_name=['Preferred Stock Dividends', ' '],
                                                        date=date, lookback_period=lookback_period, period=period))


'''Cash Flow Statement Entries'''


def cash_flow_operating_activities(stock: str, date: datetime = datetime.now(),
                                   lookback_period: timedelta = timedelta(days=0), period: str = 'TTM'):
    '''
    Operating cash flow is a measure of cash generated/consumed by a business from its operating activities

    Computed as Net Income + Depreciation & Amortization + Non-Cash Items (i.e. stock-based compensation, unrealized gains/losses...) - Changes in Net Working Capital

    Unlike EBITDA, cash from operations is adjusted all non-cash items and changes in net working capital. However, it excludes capital expenditures.

    :param stock:
    :param date:
    :param lookback_period:
    :param period:
    :return:
    '''
    return read_financial_statement_entry(financial_statement='Cash Flow Statement', stock=stock,
                                          entry_name=['Operating Activities',
                                                      'Net Cash Provided by (Used in) Operating Activities'],
                                          date=date, lookback_period=lookback_period, period=period)


def depreciation_and_amortization(stock: str, date: datetime = datetime.now(),
                                  lookback_period: timedelta = timedelta(days=0), period: str = 'TTM'):
    from_income_statement = read_financial_statement_entry(financial_statement='Income Statement', stock=stock,
                                                           entry_name=['Costs and Expenses',
                                                                       'Depreciation and Amortization'],
                                                           date=date, lookback_period=lookback_period, period=period)
    if not np.isnan(from_income_statement):
        return from_income_statement
    else:
        return read_financial_statement_entry(financial_statement='Cash Flow Statement', stock=stock,
                                              entry_name=['Operating Activities',
                                                          'Depreciation, Depletion and Amortization'],
                                              date=date, lookback_period=lookback_period, period=period)


def acquisition_property_plant_equipment(stock: str, date: datetime = datetime.now(),
                                         lookback_period: timedelta = timedelta(days=0), period: str = 'TTM'):
    return read_financial_statement_entry(financial_statement='Cash Flow Statement', stock=stock,
                                          entry_name=['Investing Activities',
                                                      'Payments to Acquire Property, Plant, and Equipment'],
                                          date=date, lookback_period=lookback_period, period=period)


def cash_flow_investing_activities(stock: str, date: datetime = datetime.now(),
                                   lookback_period: timedelta = timedelta(days=0), period: str = 'TTM'):
    return read_financial_statement_entry(financial_statement='Cash Flow Statement', stock=stock,
                                          entry_name=['Investing Activities',
                                                      'Net Cash Provided by (Used in) Investing Activities'],
                                          date=date, lookback_period=lookback_period, period=period)


def cash_flow_financing_activities(stock: str, date: datetime = datetime.now(),
                                   lookback_period: timedelta = timedelta(days=0), period: str = 'TTM'):
    return read_financial_statement_entry(financial_statement='Cash Flow Statement', stock=stock,
                                          entry_name=['Financing Activities',
                                                      'Net Cash Provided by (Used in) Financing Activities'],
                                          date=date, lookback_period=lookback_period, period=period)


def payments_for_dividends(stock: str, date: datetime = datetime.now(),
                           lookback_period: timedelta = timedelta(days=0), period: str = 'TTM'):
    return read_financial_statement_entry(financial_statement='Cash Flow Statement', stock=stock,
                                          entry_name=['Financing Activities', 'Payments of Dividends'],
                                          date=date, lookback_period=lookback_period, period=period)


def net_debt_issued(stock: str, date: datetime = datetime.now(),
                    lookback_period: timedelta = timedelta(days=0), period: str = 'TTM'):
    proceeds_from_issuance_of_debt = read_financial_statement_entry(financial_statement='Cash Flow Statement',
                                                                    stock=stock,
                                                                    entry_name=['Financing Activities',
                                                                                'Proceeds from Issuance of Long-term Debt'],
                                                                    date=date, lookback_period=lookback_period,
                                                                    period=period)
    repayment_of_debt = abs(read_financial_statement_entry(financial_statement='Cash Flow Statement', stock=stock,
                                                           entry_name=['Financing Activities',
                                                                       'Repayments of Long-term Debt'],
                                                           date=date, lookback_period=lookback_period, period=period))
    return proceeds_from_issuance_of_debt - repayment_of_debt
