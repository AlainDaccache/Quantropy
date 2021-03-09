"""
Balance Sheet Entries
"""

from datetime import timedelta

from matilda import config
from matilda.data_infrastructure.db_crud import read_financial_statement_entry, companies_in_classification


def cash_and_cash_equivalents(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    """
    **Cash and Cash Equivalents** is the amount of money on deposit in the bank. It is composed of

        *   Short-term investments:sfsf

        *   Cash: fh;ohif

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetime.now().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.

    :return:
    """
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['Assets', 'CurrentAssets', 'Cash and Cash Equivalents'],
                                          date=date, lookback_period=lookback_period, period=period)

def current_marketable_securities(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    """
    Hello Paola!
    
    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=datetime.now().
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.

    :return: 
    """
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['Assets', 'CurrentAssets', 'CashAndShortTermInvestments',
                                                      'MarketableSecurities'],
                                          date=date, lookback_period=lookback_period, period=period)


def net_accounts_receivable(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    """
    Invoices

    :param stock:
    :param date:
    :param lookback_period:
    :param period:
    :return:
    """
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['Assets', 'CurrentAssets', 'AccountsReceivable',
                                                      'NetAccountsReceivable'],
                                          date=date, lookback_period=lookback_period, period=period)


def allowances_for_doubtful_accounts(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                                     period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['Assets', 'CurrentAssets', 'AccountsReceivable',
                                                      'AllowanceForDoubtfulAccounts'],
                                          date=date, lookback_period=lookback_period, period=period)


def credit_sales(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    pass


def credit_purchases(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    pass


def current_prepaid_expenses(stock, date=None,
                             lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['Assets', 'CurrentAssets', 'PrepaidExpense'],
                                          date=date, lookback_period=lookback_period, period=period)


def net_inventory(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['Assets', 'CurrentAssets', 'InventoryNet'],
                                          date=date, lookback_period=lookback_period, period=period)


def current_income_taxes_receivable(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                                    period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['Assets', 'CurrentAssets', 'IncomeTaxesReceivable'],
                                          date=date, lookback_period=lookback_period, period=period)


def assets_held_for_sale(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['Assets', 'CurrentAssets', 'Assets Held-for-sale'],
                                          date=date, lookback_period=lookback_period, period=period)


def current_deferred_tax_assets(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['Assets', 'CurrentAssets', 'DeferredTaxAssets'],
                                          date=date, lookback_period=lookback_period, period=period)


def other_current_assets(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['Assets', 'CurrentAssets', 'Other Assets, Current'],
                                          date=date, lookback_period=lookback_period, period=period)


def total_current_assets(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['Assets', 'CurrentAssets', 'TotalCurrentAssets'],
                                          date=date, lookback_period=lookback_period, period=period)


def non_current_marketable_securities(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                                      period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['Assets', 'NonCurrentAssets', 'MarketableSecurities'],
                                          date=date, lookback_period=lookback_period, period=period)


def gross_property_plant_and_equipment(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                                       period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['Assets', 'NonCurrentAssets', 'PropertyPlantAndEquipment',
                                                      'GrossPropertyPlantAndEquipment'],
                                          date=date, lookback_period=lookback_period, period=period)


def accumulated_depreciation_amortization(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                                          period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['Assets', 'NonCurrentAssets', 'PropertyPlantAndEquipment',
                                                      'AccumulatedDepreciationAndAmortization'],
                                          date=date, lookback_period=lookback_period, period=period)


def net_property_plant_equipment(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['Assets', 'NonCurrentAssets', 'PropertyPlantAndEquipment',
                                                      'NetPropertyPlantAndEquipment'],
                                          date=date, lookback_period=lookback_period, period=period)


def operating_lease_right_of_use_assets(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                                        period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['Assets', 'NonCurrentAssets', 'OperatingLeaseRightOfUseAssets'],
                                          date=date, lookback_period=lookback_period, period=period)


def non_current_deferred_tax_assets(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                                    period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['Assets', 'NonCurrentAssets', 'DeferredTaxAssets'],
                                          date=date, lookback_period=lookback_period, period=period)


def goodwill(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['Assets', 'NonCurrentAssets', 'IntangibleAssets', 'Goodwill'],
                                          date=date, lookback_period=lookback_period, period=period)


def net_intangible_assets(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['Assets', 'NonCurrentAssets', 'IntangibleAssets',
                                                      'NetIntangibleAssetsExcludingGoodwill'],
                                          date=date, lookback_period=lookback_period, period=period)


def total_intangible_assets(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['Assets', 'NonCurrentAssets', 'IntangibleAssets',
                                                      'TotalIntangibleAssets'],
                                          date=date, lookback_period=lookback_period, period=period)


def other_non_current_assets(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['Assets', 'NonCurrentAssets', 'OtherNonCurrentAssets'],
                                          date=date, lookback_period=lookback_period, period=period)


def total_non_current_assets(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['Assets', 'NonCurrentAssets', 'TotalNonCurrentAssets'],
                                          date=date, lookback_period=lookback_period, period=period)


def total_assets(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['Assets', 'TotalAssets'],
                                          date=date, lookback_period=lookback_period, period=period)


def long_term_debt_current_maturities(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                                      period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['LiabilitiesAndShareholdersEquity', 'Liabilities',
                                                      'CurrentLiabilities', 'LongTermDebtCurrentMaturities'],
                                          date=date, lookback_period=lookback_period, period=period)


def accounts_payable(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['LiabilitiesAndShareholdersEquity', 'Liabilities',
                                                      'CurrentLiabilities', 'AccountsPayable'],
                                          date=date, lookback_period=lookback_period, period=period)


def current_deferred_revenues(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['LiabilitiesAndShareholdersEquity', 'Liabilities',
                                                      'CurrentLiabilities', 'DeferredRevenue'],
                                          date=date, lookback_period=lookback_period, period=period)


def current_operating_lease_liabilities(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                                        period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['LiabilitiesAndShareholdersEquity', 'Liabilities',
                                                      'CurrentLiabilities', 'OperatingLeaseLiability'],
                                          date=date, lookback_period=lookback_period, period=period)


def current_employee_related_liabilities(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                                         period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['LiabilitiesAndShareholdersEquity', 'Liabilities',
                                                      'CurrentLiabilities', 'EmployeeRelatedLiabilities'],
                                          date=date, lookback_period=lookback_period, period=period)


def current_accrued_income_taxes_liabilities(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                                             period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['LiabilitiesAndShareholdersEquity', 'Liabilities',
                                                      'CurrentLiabilities', 'AccruedIncomeTaxes'],
                                          date=date, lookback_period=lookback_period, period=period)


def current_income_taxes_payable(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                                 period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['LiabilitiesAndShareholdersEquity', 'Liabilities',
                                                      'CurrentLiabilities', 'IncomeTaxesPayable'],
                                          date=date, lookback_period=lookback_period, period=period)


def current_accrued_liabilities(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['LiabilitiesAndShareholdersEquity', 'Liabilities',
                                                      'CurrentLiabilities', 'AccruedLiabilities'],
                                          date=date, lookback_period=lookback_period, period=period)


def other_current_liabilities(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                              period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['LiabilitiesAndShareholdersEquity', 'Liabilities',
                                                      'CurrentLiabilities', 'OtherCurrentLiabilities'],
                                          date=date, lookback_period=lookback_period, period=period)


def total_current_liabilities(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['LiabilitiesAndShareholdersEquity', 'Liabilities',
                                                      'CurrentLiabilities', 'TotalCurrentLiabilities'],
                                          date=date, lookback_period=lookback_period, period=period)


def long_term_debt_excluding_current_portion(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                                             period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['LiabilitiesAndShareholdersEquity', 'Liabilities',
                                                      'NonCurrentLiabilities', 'LongTermDebtNonCurrentMaturities'],
                                          date=date, lookback_period=lookback_period, period=period)


def total_long_term_debt(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return long_term_debt_current_maturities(stock=stock, date=date, lookback_period=lookback_period, period=period) + \
           long_term_debt_excluding_current_portion(stock=stock, date=date, lookback_period=lookback_period,
                                                    period=period)


def defined_benefit_plan_non_current_liabilities(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                                                 period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['LiabilitiesAndShareholdersEquity', 'Liabilities',
                                                      'NonCurrentLiabilities', 'DefinedBenefitPlan'],
                                          date=date, lookback_period=lookback_period, period=period)


def accrued_income_taxes_non_current_liabilities(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                                                 period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['LiabilitiesAndShareholdersEquity', 'Liabilities',
                                                      'NonCurrentLiabilities', 'AccruedIncomeTaxes'],
                                          date=date, lookback_period=lookback_period, period=period)


def deferred_revenue_non_current_liabilities(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                                             period: str = 'Q'):
    """
    Also known as *long-term unearned revenue*

    :param stock:
    :param date:
    :param lookback_period:
    :param period:
    :return:
    """
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['LiabilitiesAndShareholdersEquity', 'Liabilities',
                                                      'NonCurrentLiabilities', 'DeferredRevenue'],
                                          date=date, lookback_period=lookback_period, period=period)


def other_non_current_liabilities(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['LiabilitiesAndShareholdersEquity', 'Liabilities',
                                                      'NonCurrentLiabilities', 'OtherLiabilitiesNonCurrent'],
                                          date=date, lookback_period=lookback_period, period=period)


def total_non_current_liabilities(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['LiabilitiesAndShareholdersEquity', 'Liabilities',
                                                      'NonCurrentLiabilities', 'TotalNonCurrentLiabilities'],
                                          date=date, lookback_period=lookback_period, period=period)


def total_liabilities(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['LiabilitiesAndShareholdersEquity', 'Liabilities',
                                                      'TotalLiabilities'],
                                          date=date, lookback_period=lookback_period, period=period)


def preferred_stock_value(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['LiabilitiesAndShareholdersEquity',
                                                      'ShareholdersEquity', 'PreferredStockValueIssued'],
                                          date=date, lookback_period=lookback_period, period=period)


def common_stock_value_issued(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['LiabilitiesAndShareholdersEquity', 'ShareholdersEquity',
                                                      'CommonStockAndAdditionalPaidInCapital',
                                                      'CommonStockValueIssued'],
                                          date=date, lookback_period=lookback_period, period=period)


def additional_paid_in_capital(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['LiabilitiesAndShareholdersEquity', 'ShareholdersEquity',
                                                      'CommonStockAndAdditionalPaidInCapital',
                                                      'AdditionalPaidInCapital'],
                                          date=date, lookback_period=lookback_period, period=period)


def common_stocks_including_additional_paid_in_capital(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                                                       period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['LiabilitiesAndShareholdersEquity', 'ShareholdersEquity',
                                                      'CommonStockAndAdditionalPaidInCapital',
                                                      'CommonStocksIncludingAdditionalPaidInCapital'],
                                          date=date, lookback_period=lookback_period, period=period)


def retained_earnings(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['LiabilitiesAndShareholdersEquity',
                                                      'ShareholdersEquity', 'RetainedEarningsAccumulatedDeficit'],
                                          date=date, lookback_period=lookback_period, period=period)


def accumulated_other_comprehensive_income(stock, date=None, lookback_period: timedelta = timedelta(days=0),
                                           period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['LiabilitiesAndShareholdersEquity', 'ShareholdersEquity',
                                                      'AccumulatedOtherComprehensiveIncomeLoss'],
                                          date=date, lookback_period=lookback_period, period=period)


def minority_interest(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['LiabilitiesAndShareholdersEquity', 'ShareholdersEquity',
                                                      'MinorityInterest'],
                                          date=date, lookback_period=lookback_period, period=period)


def total_shares_outstanding(stock, diluted_shares: bool = False, date=None,
                             lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    """

    :param stock:
    :param diluted_shares: Share dilution is when a company issues additional stock, reducing the ownership proportion
    of a current shareholder. Shares can be diluted through a conversion by holders of optionable securities, secondary
    offerings to raise additional capital, or offering new shares in exchange for acquisitions or services.
    :param date:
    :param lookback_period:
    :param period:
    :return:
    """
    entry = ['LiabilitiesAndShareholdersEquity', 'ShareholdersEquity', 'CommonStockAndAdditionalPaidInCapital',
             'WeightedAverageNumberOfSharesOutstandingDiluted'] if diluted_shares \
        else ['LiabilitiesAndShareholdersEquity', 'ShareholdersEquity', 'CommonStockAndAdditionalPaidInCapital',
              'WeightedAverageNumberOfSharesOutstandingBasic']
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock, entry_name=entry, date=date,
                                          lookback_period=lookback_period, period=period)


def total_shareholders_equity(stock, date=None, lookback_period: timedelta = timedelta(days=0), period: str = 'Q'):
    # return try_multiple_entries(stock=stock, date=date, lookback_period=lookback_period, period=period,
    #                             statement='BalanceSheet',
    #                             entries=[['LiabilitiesAndShareholdersEquity',
    #                                       'ShareholdersEquity',
    #                                       'Stockholders\' Equity, Including Portion Attributable to Noncontrolling Interest'],
    #                                      ['LiabilitiesAndShareholdersEquity',
    #                                       'ShareholdersEquity',
    #                                       'Stockholders\' Equity Attributable to Parent']
    #                                      ])
    return read_financial_statement_entry(financial_statement='BalanceSheet', stock=stock,
                                          entry_name=['LiabilitiesAndShareholdersEquity', 'ShareholdersEquity',
                                                      'StockholdersEquityAttributableToParent'],
                                          date=date, lookback_period=lookback_period, period=period)
