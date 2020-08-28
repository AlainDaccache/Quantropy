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
