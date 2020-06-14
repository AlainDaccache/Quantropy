import re

date_regex = re.compile(r'^(0[1-9]|1[012])[- /.](0[1-9]|[12][0-9]|3[01])[- /.](19|20)\d\d$' # match mm/dd/yyyy
                        r'|'
                        r'^(0[1-9]|[12][0-9]|3[01])[- /.](0[1-9]|1[012])[- /.](19|20)\d\d$' # match dd-mm-yyyy
                        r'|'
                        r'^([^\s]+) (\d{2}),? ?(\d{4})$' # match Month D, Yr (i.e. February 17, 2009 or February 17,2009)
                        r'|'
                        r'^\d{4}$' # match year (i.e. 2011)
                            r'|'
                        'Fiscal\d{4}'
                        r'|'
                        r'^Change$'
                        r'|'
                        r'(\b\d{1,2}\D{0,3})?\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|(Nov|Dec)(?:ember)?)\D?(\d{1,2}\D?)?\D?((19[7-9]\d|20\d{2})|\d{2})')

balance_sheet_regex = r'Consolidated(.*?)(balance sheet|condition)'
cash_flow_statement_regex = r'Consolidated(.*?)cash flow'
income_statement_regex = r'Consolidated(.*?)statements of earnings'

cash_flow_investing_activities = {
    'Payments to Acquire Productive Assets': re.compile(r'Capital expenditures – excluding equipment leased to others', re.IGNORECASE),
    'Payments to Acquire Equipment on Lease': re.compile(r'Expenditures for equipment leased to others', re.IGNORECASE),
    'Proceeds from Sale of Property, Plant, and Equipment': re.compile(r'Proceeds from disposals of leased assets and property, plant and equipment', re.IGNORECASE),
    'Payments to acquire finance receivables': re.compile(r'Additions to finance receivables', re.IGNORECASE),
    'Proceeds from collection of finance receivables': re.compile(r'Collections of finance receivables', re.IGNORECASE),
    'Proceeds from sale of finance receivables': re.compile(r'Proceeds from sale of finance receivables', re.IGNORECASE),
    'Payments to acquire businesses net of cash acquired': re.compile(r'Investments and acquisitions \(net of cash acquired\)', re.IGNORECASE),
    'Proceeds from divestiture of businesses net of cash divested': re.compile(r'Proceeds from sale of businesses and investments \(net of cash sold\)', re.IGNORECASE),
    'Proceeds from sale and maturity of marketable securities': re.compile(r'Proceeds from sale of securities', re.IGNORECASE),
    'Payments to acquire marketable securities': re.compile(r'Investments in securities', re.IGNORECASE),
    'Payments for proceeds from other investing activities': re.compile(r'Other – net', re.IGNORECASE),
    'Net cash provided by/used in Investing Activities': re.compile(r'Net cash provided by \(used for\) investing activities', re.IGNORECASE)
}

cash_flow_operating_activities = {
    'Net Income (Loss)': re.compile(r'(Net Earnings)|(Profit \(loss\) of consolidated and affiliated companies)', re.IGNORECASE),
    'Adjustments for non-cash items': {
        'Depreciation, Depletion and Amortization, Nonproduction': re.compile(r'Depreciation and amortization', re.IGNORECASE),
        'DefinedBenefitPlanActuarialGainLoss': re.compile(r'Actuarial \(gain\) loss on pension and postretirement benefits', re.IGNORECASE),
        'Deferred Income Tax Expense (Benefit)': re.compile(r'(Provision \(benefit\) for )?deferred income taxes', re.IGNORECASE),
        'Share-based Compensation': re.compile(r'Share-based compensation', re.IGNORECASE),
        'Gain (Loss) on Extinguishment of Debt': re.compile(r'Gain related to extinguishment of unsecured borrowings', re.IGNORECASE),
        'Provision for Loan, Lease, and Other Losses': re.compile(r'Provision for credit losses', re.IGNORECASE),
        'OtherNoncashIncomeExpense': re.compile(r'Other', re.IGNORECASE)
    },
    'Changes in assets, net of acquisitions and diverstitures': {
        'Increase (Decrease) in Receivables': re.compile(r'Receivables', re.IGNORECASE),
        'Increase (Decrease) in Inventories': re.compile(r'Inventories', re.IGNORECASE),
        'Increase (Decrease) in Other Operating Assets': re.compile(r'Other assets – net', re.IGNORECASE),
    },
    'Changes in liabilities, net of acquisitions and diverstitures': {
        'Increase (Decrease) in Accounts Payable': re.compile(r'Accounts payable', re.IGNORECASE),
        'Increase (Decrease) in Accrued Liabilities': re.compile(r'Accrued expenses', re.IGNORECASE),
        'Increase (Decrease) in Employee Related Liabilities': re.compile(r'Accrued wages, salaries and employee benefits', re.IGNORECASE),
        'Increase (Decrease) in Customer Advances': re.compile(r'Customer advances', re.IGNORECASE),
        'Increase (Decrease) in Other Operating Liabilities': re.compile(r'Other liabilities – net', re.IGNORECASE)
    },
    'Net Cash Provided by (Used in) Operating Activities': re.compile(r'Net cash provided by \(used for\) operating activities', re.IGNORECASE),

}

cash_flow_financing_activities = {

}

financial_entries_regex_dict = {
    'Balance Sheet': {
        'Assets': {
            'Current Assets': {
                'Cash and Short Term Investments': {
                    'Cash and Cash Equivalents': re.compile(r'({}|Current Assets)(.*?)Cash and cash equivalents(.*?)(?!^Marketable Securities$)'.format(balance_sheet_regex), re.IGNORECASE),
                    'Marketable Securities Current': re.compile(r'({}|Current Assets)(.*?)Short-term marketable securities'.format(balance_sheet_regex), re.IGNORECASE),
                    'Cash and Short Term Investments': re.compile(r'{}|Current Assets(.*?)Cash and short-term investments', re.IGNORECASE)
                },
                'Accounts Receivable': {
                    'Gross Accounts Receivable': 0,
                    'Allowances for Doubtful Accounts': re.compile(r'{}(.*?)net of allowances of \$'.format(balance_sheet_regex), re.IGNORECASE), # TODO extract
                    'Net Accounts Receivable': re.compile(r'({}|Current Assets)(.*?)Receivables'.format(balance_sheet_regex), re.IGNORECASE),
                },
                'Inventories': re.compile(r'({}|Current Assets)(.*?)Inventories'.format(balance_sheet_regex), re.IGNORECASE),
                'Deferred Tax Assets Current': re.compile(r'({}|Current Assets)(.*?)Deferred tax assets'.format(balance_sheet_regex), re.IGNORECASE),
                'Vendor non-trade receivables': re.compile(r'({}|Current Assets)(.*?)Vendor non-trade receivables'.format(balance_sheet_regex), re.IGNORECASE),
                'Other Current Assets': 0,
                'Total Current Assets': 0
            },
            'Non Current Assets': {
                # TODO marketable securities wrong
                'Marketable Securities Non Current': re.compile(r'{}(.*?)((long-?term)|non-?current) (marketable securities)'.format(balance_sheet_regex), re.IGNORECASE),
                'Property, Plant and Equipment': {
                    'Gross Property, Plant and Equipment': re.compile(r'Property(.*?)Plant(.*?)Equipment(.*?)Gross', re.IGNORECASE),
                    'Accumulated Depreciation and Amortization': re.compile(r'Depreciation(.*?)Amortization', re.IGNORECASE),
                    'Property, Plant and Equipment, Net': re.compile(r'Property(.*?)Plant(.*?)Equipment(.*?)Net', re.IGNORECASE),
                },
                'Deferred Tax Assets Non Current': re.compile(r'Noncurrent deferred tax assets', re.IGNORECASE),
                'Intangible Assets': {
                    'Goodwill': re.compile(r'(({}|Intangible Assets)(.*?)Goodwill)'.format(balance_sheet_regex), re.IGNORECASE),
                    'Other Intangible Assets': 0,
                    'Total Intangible Assets': re.compile(r'{}(.*?)Intangible Assets(.*?)(?!^Goodwill$)'.format(balance_sheet_regex), re.IGNORECASE),
                },
                'Other Non Current Assets': 0,
                'Total Non Current Assets': 0,
            },
            'Total Assets': re.compile(r'Total ?(?!^Current$) ?Assets', re.IGNORECASE)
        },
        'Liabilities and Shareholders\' Equity': {
            'Liabilities': {
                'Current Liabilities': {
                    'Current Debt': {
                        'Commercial Paper': 0,
                        'Other Current Borrowings': 0,
                        'Total Current Debt': 0
                    },
                    'Accounts Payable': re.compile(r'({}|Current Liabilities)(.*?)(Accounts Payable)'.format(balance_sheet_regex), re.IGNORECASE),
                    'Accrued Liabilities': 0,
                    'Current Deferred Revenues': re.compile(r'({}|Current Liabilities)(.*?)(Deferred Revenues)'.format(balance_sheet_regex), re.IGNORECASE),
                    'Other Current Liabilities': 0,
                    'Total Current Liabilities': 0,
                },
                'Non Current Liabilities': {
                    'Deferred Tax Liabilities': 0,
                    'Non Current Debt': 0,
                    'Other Long-Term Liabilities': 0,
                    'Total Long-Term Liabilities': 0
                },
                'Total Liabilities': 0
            },
            'Shareholders\' Equity': {
                'Common Stock': 0,
                'Retained Earnings': 0,
                'Accumulated Other Comprehensive Income': 0,
                'Total Shareholders\' Equity': 0
            },
            'Total Liabilities and Shareholders\' Equity': 0
        },
    },
    'Income Statement': {
        'Revenues': {
            'Net Sales': re.compile(r'(Net|Product) sales', re.IGNORECASE),
            'Gross Margin': re.compile(r'Gross margin', re.IGNORECASE)
        },
        'Cost of Goods and Services Sold': re.compile(r'Cost of (goods sold|sales)', re.IGNORECASE),
        'Operating Expenses': {
            'Research and Development': re.compile(r'Research and development', re.IGNORECASE),
            'Selling, General and Administrative': re.compile(r'Selling, general and administrative', re.IGNORECASE),
            'Total Operating Expenses': re.compile(r'Total operating expenses', re.IGNORECASE)
        },
        'Operating Income (Loss) / EBIT': re.compile(r'Operating income'),
        'Non-Operating Income (Expenses)': 0,
        'Net Income (Loss)': 0,
        'Net Income Loss Attributable to Noncontrolling Interest': 0
    },
    'Cash Flow Statement': {
        'Operating Activities': re.compile(r'{}(.*?)Operating activities:(.*?)'.format(cash_flow_statement_regex), re.IGNORECASE),
        'Investing Activities': re.compile(r'{}(.*?)Investing activities:(.*?)'.format(cash_flow_statement_regex), re.IGNORECASE),
        'Financing Activities': re.compile(r'{}(.*?)Financing activities:(.*?)'.format(cash_flow_statement_regex), re.IGNORECASE),
    }
}
