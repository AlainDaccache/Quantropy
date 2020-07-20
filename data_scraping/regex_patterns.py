import re

# TODO REVIEW THIS https://stackoverflow.com/questions/6259443/how-to-match-a-line-not-containing-a-word

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

balance_sheet_regex = r'(balance ?sheet|condition)'
cash_flow_statement_regex = r'(Consolidated(.*?)cash flow)|(cash( ?)flow(s?) statement(s?))'
income_statement_regex = r'(Consolidated(.*?)statements of (income|earnings))|(income statement)|(CONSOLIDATED STATEMENTS OF OPERATIONS)'

non_current = '(?=.*non[- ]?current(?!.*[_]))'
current = '(?!.*non[- ]?current)(?=.*(current|short-term))'

financial_entries_regex_dict = {
    'Balance Sheet': {
        'Assets': {
            'Current Assets': {
                'Cash and Short Term Investments': {
                    'Cash and Cash Equivalents': r'(?!.*marketable securities)(?=.*cash and cash equivalents)(?!.*marketable securities)',
                    'Marketable Securities Current': r'(?!.*non[- ]?current)(?=.*(current|short-term))(?=.*(marketable securities|investments)|(Available-for-sale investment securities))', # (?!.*cash.*_)
                    'Cash and Short Term Investments': r'(?=.*cash)(?=.*(marketable securities|short-term investments))'
                },
                'Accounts Receivable': {
                    # 'Gross Accounts Receivable': r'$^', # TODO
                    # 'Allowances for Doubtful Accounts': r'(?=.*Receivable)(?=.*allowances.*\$(\d+))',
                    # bug in this one (?=.*Receivable.*allowances).*(\$(\d+))*,
                    'Other Receivables': r'(?=.*Receivable)(?!.*(allowances|net))',
                    'Net Accounts Receivable': r'(?=.*Receivable)(?=.*(allowances|net))',
                },
                'Prepaid Expense, Current': r'(?=.*Prepaid expenses)',
                'Inventory, Net': r'(?=.*Inventor(y|ies))',
                'Income Taxes Receivable, Current': r'(?=.*Income taxes receivable)',
                'Assets Held-for-sale': r'Assets Held[- ]for[- ]sale',
                # taxes that have been already paid despite not yet having been incurred
                'Deferred Tax Assets, Current': r'(?=.*(Deferred tax(es)? (assets)|(on income))|(Prepaid taxes)){}'.format(current),
                'Other Assets, Current': r'$^',
                'Total Assets, Current': r'(?=.*Total(?!.*[_]))(?=.*Assets(?!.*[_:])){}'.format(current)
            },
            'Non Current Assets': {

                'Marketable Securities Non Current': r'(?!.*short-term)(?=.*marketable securities|investments){}'.format(non_current),
                'Restricted Cash Non Current': r'(?=.*Restricted cash){}'.format(non_current),
                'Property, Plant and Equipment': {
                    'Gross Property, Plant and Equipment': r'(?=.*Property)(?=.*(Plant|Land))(?=.*Equipment)(?=.*Gross)',
                    'Accumulated Depreciation and Amortization': r'(?=.*(Property|Equipment).*_)(?=.*accumulated depreciation(?!.*[_]))',
                    'Property, Plant and Equipment, Net': r'(?=.*Property)(?=.*(Plant|Land))?(?=.*Equipment)(?=.*Net)',
                },
                'Operating Lease Right-of-use Assets': r'Operating lease right-of-use assets',
                'Deferred Tax Assets Non Current': r'(?=.*deferred tax assets){}'.format(non_current),
                'Intangible Assets': {
                    'Goodwill': r'(?!.*net)(?=.*Goodwill)(?!.*net)',
                    'Intangible Assets, Net (Excluding Goodwill)': r'(?=.*(other|net))(?=.*intangible assets)',
                    'Total Intangible Assets': r'(?!.*other)(?!.*goodwill)(?!.*net)(?=.*intangible assets)(?!.*goodwill)(?!.*other)(?!.*net)',
                },
                'Other Non Current Assets': r'(?=.*Other)(?=.*assets(?!.*[_])){}'.format(non_current),
                'Total Non Current Assets': r'(?=.*Total(?!.*[_]))(?=.*assets(?!.*[_])){}'.format(non_current),
            },
            'Total Assets': r'(?=.*Total Assets(?!.*[_:]))'
        },
        'Liabilities and Shareholders\' Equity': {
            'Liabilities': {
                'Current Liabilities': {
                    'Short-Term Debt': r'(?=.*(Commercial Paper|Current Debt))',
                    'Long-term Debt, Current Maturities': r'((?=.*current)|(?!.*non[- ]?current))(?=.*(Long-)?Term Debt|Loans and notes payable)',
                    'Accounts Payable, Current': r'(?=.*Payable)((?=.*current)|(?!.*non[- ]?current))',
                    'Operating Lease, Liability, Current': r'(?=.*Operating lease liabilities)((?=.*current)|(?!.*non[- ]?current))',
                    'Current Deferred Revenues': r'(?=.*(Deferred Revenue)|(Short-term unearned revenue))((?=.*current)|(?!.*non[- ]?current))',
                    'Employee-related Liabilities, Current': r'(?=.*Accrued Compensation)',
                    'Accrued Income Taxes': r'Accrued(?=.*Income)(?=.*Taxes)',
                    'Accrued Liabilities, Current': r'(?=.*Accrued)(?=.*(Expense|Liabilities))',
                    'Income Taxes Payable': r'(?=.*Income taxes payable)|(?=.*Short-term Income taxes)',
                    'Other Current Liabilities': r'(?=.*Other liabilities)((?=.*current)|(?!.*non[- ]?current))',
                    'Total Current Liabilities': r'(?=.*Total Current Liabilities)',
                },
                'Non Current Liabilities': {
                    'Deferred Tax Liabilities': r'(Deferred(?=.*Income)(?=.*Taxes))|(Deferred tax liabilities)',
                    # this debt is due after one year in contrast to current maturities which are due within this year
                    'Long-term Debt, Noncurrent Maturities': r'(?=.*Long-term (borrowings|debt))(?!.*within)((?!.*current.*[_])|(?=.*non[- ]?current))',
                    'Operating Lease, Liability, Noncurrent': r'(?=.*Operating lease (liabilities|liability))((?!.*current.*[_])|(?=.*non[- ]?current))',
                    'Liability, Defined Benefit Plan, Noncurrent': r'Employee related obligations',
                    'Accrued Income Taxes, Noncurrent': r'(Long-term ((income taxes)|(taxes payable)))',
                    'Deferred Revenue, Noncurrent': r'(?=.*Deferred Revenue)((?!.*current)|(?=.*non[- ]?current))',
                    'Long-Term Unearned Revenue': r'(?=.*unearned)(?=.*revenue)((?!.*current)|(?=.*non[- ]?current)|(?=.*long[- ]?term))',
                    'Other Liabilities, Noncurrent': r'(?=.*Other(?!.*[_:]))(?=.*liabilities(?!.*[_:]))((?!.*current)|(?=.*non[- ]?current))',
                    'Total Long-Term Liabilities': r'(?=.*Non-current liabilities)' # total liabilities - total current liabilities
                },
                'Total Liabilities': r'(?=.*Total Liabilities)(?!.*Equity(?!.*[_]))'
            },
            'Shareholders\' Equity': {
                'Preferred Stock, Value, Issued': r'(?=.*Preferred stock)(?!.*treasury)',
                'Common Stock and Additional Paid in Capital': {
                    'Common Stock, Value, Issued': r'(?=.*Common stock)(?!.*treasury)(?!.*additional paid[- ]in capital)',
                    'Additional Paid in Capital': r'(?!.*Common stock)(?=.*additional paid[- ]in capital)',
                    'Common Stocks, Including Additional Paid in Capital': r'(?=.*Common stock and additional paid[- ]in capital)',
                'Weighted Average Number of Shares Outstanding, Basic': r'(?=.*shares)(?=.*basic)(?!.*earnings(?!.*[_]))',
                'Weighted Average Number Diluted Shares Outstanding Adjustment': r'(?=.*dilutive)(?=.*effect(?!.*[_:]))',
                'Weighted Average Number of Shares Outstanding, Diluted': r'(?=.*shares)(?=.*diluted)(?!.*earnings(?!.*[_]))',
                },

                'Treasury Stock, Value': r'Treasury stock',
                'Retained Earnings (Accumulated Deficit)': r'(?=.*Accumulated deficit)|(Retained earnings)',
                'Accumulated Other Comprehensive Income (Loss)': r'(?=.*Accumulated other comprehensive (income|loss))',
                'Deferred Stock Compensation': r'(?=.*Deferred stock compensation)',
                'Minority Interest': r'(?=.*Noncontrolling interests)',
                'Stockholders\' Equity Attributable to Parent': r'(?=.*Total (shareholders|stockholders)[’\'] equity)',
            },
            'Total Liabilities and Shareholders\' Equity': r'(?=.*Total Liabilities)(?=.*Equity)'
        },
    },
    'Income Statement': {
        'Revenues': {
            # 'Service Sales': '(?=.*Sales)(?=.*Service(?!.*[_:]))(?!.*Cost)(?!.*Other(?!.*[_:]))',
            # 'Product Sales': '(?=.*Sales)(?=.*Product(?!.*[_:]))(?!.*Cost)(?!.*Other(?!.*[_:]))',
            'Net Sales': r'(?=.*(Net sales|Revenue)(?!.*[_:]))(?!.*Cost)',
            'Noninterest Income': r'(?=.*Non[- ]?interest (revenue|income))',
        },

        'Costs and Expenses': {
            'Cost of Goods and Services Sold': r'(?=.*Cost of (revenue|sales|goods|services)(?!.*[_:]))',
            'Provision for Loan, Lease, and Other Losses': r'(?=.*Provision for credit losses)',
            'Operating Expenses': {
                'Research and Development Expense': r'(?=.*(Research|Technology) and development)',
                'Selling, General and Administrative': {
                    'Marketing Expense': r'(?!.*(Sales|selling))(?=.*Marketing)',
                    'Selling and Marketing Expense': r'(?=.*(Sales|Selling))(?=.*Marketing)',
                    'General and Administrative Expense': r'(?=.*General)(?=.*Administrative)(?!.*Selling)',
                    'Selling, General and Administrative': r'(?=.*Selling, general and administrative)'
                },
                'Other Operating Expenses': r'$^', # TODO
                'EBITDA': r'$^',
                'Depreciation, Depletion and Amortization, Nonproduction': r'(?!.*accumulated)(?=.*Depreciation(?!.*[_:]))(?=.*amortization(?!.*[_:]))',
                'Total Operating Expenses': r'(?=.*Total operating expenses)'
            },
            'Costs and Expenses': r'(?=.*Total costs and expenses)'
        },

        'Operating Income (Loss) / EBIT': r'(?=.*income(?!.*[_]))(?=.*operati(ng|ons)(?!.*[_]))',
        'Non-Operating Income (Expense)': {
            'Interest Income': r'(?=.*Interest(?!.*[_:]))(?!.*dividend(?!.*[_:]))(?=.*income(?!.*[_:]))(?!.*net(?!.*[_:]))',
            'Interest and Dividend Income': r'(?=.*Interest(?!.*[_:]))(?=.*dividend(?!.*[_:]))(?=.*income(?!.*[_:]))(?!.*net(?!.*[_:]))',
            'Interest Expense': r'(?=.*Interest expense(?!.*[_:]))(?!.*net(?!.*[_:]))',
            'Interest Income (Expense), Net': r'(?=.*Interest income(?!.*[_:]))(?=.*net(?!.*[_:]))',

            # hardcoded for Note 13.Interest and other income, net_Other
            # and Other income/(expense), net
            'Other Nonoperating Income (Expense)': '$^',
            # below is for Interest and other income, net
            # and Total other income/(expense), net
            'Non-Operating Income (Expense)': r'(?=.*other income(?!.*[_:]))(?=.*net(?!.*[_:]))',
        },

        'Income (Loss) before Income Taxes, Noncontrolling Interest': r'(?=.*(Income before (?=.*Provision for)?(?=.*(income )?taxes)|Pre-tax earnings))',
        'Income Tax Expense (Benefit)': r'(?=.*Provision for)(?=.*(income )?taxes)',
        'Net Income (Loss)': r'(?=.*Net (income|earnings|loss)$)',
        'Undistributed Earnings (Loss) Allocated to Participating Securities, Basic': r'(?=.*Net income attributable to participating securities)',
        'Net Income Loss Attributable to Noncontrolling (Minority) Interest': r'(?=.*Net Income Attributable to Noncontrolling Interest)',
        'Preferred Stock Dividends': r'(?=.*Preferred stock dividends)',
        'Net Income (Loss) Available to Common Stockholders, Basic': r'(?=.*Net (income|earnings) (attributable|applicable) to.*common (stockholders|shareholders))'
    },
    'Cash Flow Statement': {
        'Operating Activities': {
            'Net Cash Provided by (Used in) Operating Activities': r'(?=.*Operating activities(?!.*[_:]))(?=.*cash(?!.*[_:]))'
        },
        'Investing Activities': {
            'Net Cash Provided by (Used in) Investing Activities': r'(?=.*Investing activities(?!.*[_:]))(?=.*cash(?!.*[_:]))'
        },
        'Financing Activities': {
            'Net Cash Provided by (Used in) Financing Activities': r'(?=.*Financing activities(?!.*[_:]))(?=.*(net )?cash(?!.*[_:]))'
        }
    }
}
