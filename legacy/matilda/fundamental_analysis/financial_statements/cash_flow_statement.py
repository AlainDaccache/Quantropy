"""
Cash Flow Statement
"""

from datetime import timedelta
from matilda.data_pipeline.db_crud import read_financial_statement_entry


def cash_flow_operating_activities(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                                   period: str = 'TTM'):
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
    return read_financial_statement_entry(financial_statement='CashFlowStatement', stock=stock,
                                          entry_name=['OperatingActivities',
                                                      'NetCashProvidedByUsedInOperatingActivities'],
                                          date=date, lookback_period=lookback_period, period=period)


def depreciation_and_amortization(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                                  period: str = 'TTM'):
    """
    This income statement expense reduces net income but has no effect on cash flow, so it must be added back
    when reconciling net income and cash flow from operations.

    :param stock:
    :param date:
    :param lookback_period:
    :param period:
    :return:
    """
    return read_financial_statement_entry(financial_statement='CashFlowStatement', stock=stock,
                                          entry_name=['AdjustmentsToReconcileNetIncome',
                                                      'DepreciationDepletionAndAmortization'],
                                          date=date, lookback_period=lookback_period, period=period)


def acquisition_property_plant_equipment(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                                         period: str = 'TTM'):
    return read_financial_statement_entry(financial_statement='CashFlowStatement', stock=stock,
                                          entry_name=['InvestingActivities',
                                                      'PaymentsToAcquirePropertyPlantAndEquipment'],
                                          date=date, lookback_period=lookback_period, period=period)


def cash_flow_investing_activities(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                                   period: str = 'TTM'):
    return read_financial_statement_entry(financial_statement='CashFlowStatement', stock=stock,
                                          entry_name=['InvestingActivities',
                                                      'NetCashProvidedByUsedInInvestingActivities'],
                                          date=date, lookback_period=lookback_period, period=period)


def cash_flow_financing_activities(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                                   period: str = 'TTM'):
    return read_financial_statement_entry(financial_statement='CashFlowStatement', stock=stock,
                                          entry_name=['FinancingActivities',
                                                      'NetCashProvidedByUsedInFinancingActivities'],
                                          date=date, lookback_period=lookback_period, period=period)


def payments_of_dividends(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'TTM'):
    return read_financial_statement_entry(financial_statement='CashFlowStatement', stock=stock,
                                          entry_name=['FinancingActivities', 'PaymentsOfDividends'],
                                          date=date, lookback_period=lookback_period, period=period)


def net_debt_issued(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'TTM'):
    proceeds_from_issuance_of_debt = read_financial_statement_entry(financial_statement='CashFlowStatement',
                                                                    stock=stock, entry_name=['Financing Activities',
                                                                                             'ProceedsFromIssuanceOfLongTermDebt'],
                                                                    date=date, lookback_period=lookback_period,
                                                                    period=period)
    repayment_of_debt = abs(read_financial_statement_entry(financial_statement='CashFlowStatement', stock=stock,
                                                           entry_name=['Financing Activities',
                                                                       'RepaymentsOfLongTermDebt'],
                                                           date=date, lookback_period=lookback_period, period=period))
    return proceeds_from_issuance_of_debt - repayment_of_debt
