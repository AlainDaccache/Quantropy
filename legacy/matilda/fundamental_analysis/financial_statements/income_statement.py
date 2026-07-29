"""
Income Statement Entries
"""

from datetime import timedelta
from matilda.data_pipeline.db_crud import read_financial_statement_entry
import numpy as np


def net_sales(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'TTM'):
    return read_financial_statement_entry(financial_statement='IncomeStatement', stock=stock,
                                          entry_name=['Revenues', 'NetSales'],
                                          date=date, lookback_period=lookback_period, period=period)


def cost_of_goods_services(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'TTM'):
    return read_financial_statement_entry(financial_statement='IncomeStatement', stock=stock,
                                          entry_name=['CostOfGoodsAndServicesSold', 'CostOfGoodsAndServicesSold'],
                                          date=date, lookback_period=lookback_period, period=period)


def research_development_expense(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'TTM'):
    return read_financial_statement_entry(financial_statement='IncomeStatement', stock=stock,
                                          entry_name=['OperatingExpenses', 'ResearchAndDevelopmentExpense'],
                                          date=date, lookback_period=lookback_period, period=period)


def selling_general_administrative(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                                   period: str = 'TTM'):
    return read_financial_statement_entry(financial_statement='IncomeStatement', stock=stock,
                                          entry_name=['OperatingExpenses', 'SellingGeneralAndAdministrative'],
                                          date=date, lookback_period=lookback_period, period=period)


def total_operating_expenses(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'TTM'):
    return read_financial_statement_entry(financial_statement='IncomeStatement', stock=stock,
                                          entry_name=['OperatingExpenses', 'TotalOperatingExpenses'],
                                          date=date, lookback_period=lookback_period, period=period)


def operating_income(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'TTM'):
    """
    The **operating income** is the profit realized from a business's operations, after deducting operating expenses
    such as wages, depreciation, and cost of goods sold (COGS).

    :param stock:
    :param date:
    :param lookback_period:
    :param period:
    :return:
    """
    return read_financial_statement_entry(financial_statement='IncomeStatement', stock=stock,
                                          entry_name=['OperatingIncomeLoss'], date=date,
                                          lookback_period=lookback_period, period=period)


def interest_income(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'TTM'):
    # TODO try InterestAndDividendIncome also
    return read_financial_statement_entry(financial_statement='IncomeStatement', stock=stock,
                                          entry_name=['NonOperatingIncomeExpense', 'InterestIncome'], date=date,
                                          lookback_period=lookback_period, period=period)


def interest_expense(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'TTM'):
    return read_financial_statement_entry(financial_statement='IncomeStatement', stock=stock,
                                          entry_name=['NonOperatingIncomeExpense', 'InterestExpense'],
                                          date=date, lookback_period=lookback_period, period=period)


def interest_income_expense_net(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'TTM'):
    return read_financial_statement_entry(financial_statement='IncomeStatement', stock=stock,
                                          entry_name=['NonOperatingIncomeExpense', 'InterestIncomeExpenseNet'],
                                          date=date, lookback_period=lookback_period, period=period)


def non_operating_income(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'TTM'):
    return read_financial_statement_entry(financial_statement='IncomeStatement', stock=stock,
                                          entry_name=['NonOperatingIncomeExpense', 'NonOperatingIncomeExpense'],
                                          date=date, lookback_period=lookback_period, period=period)


def income_tax_expense(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'TTM'):
    return read_financial_statement_entry(financial_statement='IncomeStatement', stock=stock,
                                          entry_name=['IncomeTaxExpenseBenefit'],
                                          date=date, lookback_period=lookback_period, period=period)


def net_income(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'TTM'):
    return read_financial_statement_entry(financial_statement='IncomeStatement', stock=stock,
                                          entry_name=['NetIncomeLossAttributableToParent'],
                                          date=date, lookback_period=lookback_period, period=period)
    # return try_multiple_entries(stock=stock, statement='IncomeStatement', date=date, lookback_period=lookback_period,
    #                             period=period,
    #                             entries=[['NetIncomeLossAttributableToParent'],
    #                                      ['NetIncomeLossAvailableToCommonStockholdersBasic'],
    #                                      ['NetIncomeLossAttributableToMinorityInterest']])


def preferred_dividends(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'TTM'):
    return np.nan_to_num(read_financial_statement_entry(financial_statement='IncomeStatement', stock=stock,
                                                        entry_name=['PreferredStockDividends'],
                                                        date=date, lookback_period=lookback_period, period=period))
