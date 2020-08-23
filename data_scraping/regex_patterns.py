import re

# TODO REVIEW THIS https://stackoverflow.com/questions/6259443/how-to-match-a-line-not-containing-a-word

date_regex = re.compile(r'^(0[1-9]|1[012])[- /.](0[1-9]|[12][0-9]|3[01])[- /.](19|20)\d\d$'  # match mm/dd/yyyy
                        r'|'
                        r'^(0[1-9]|[12][0-9]|3[01])[- /.](0[1-9]|1[012])[- /.](19|20)\d\d$'  # match dd-mm-yyyy
                        r'|'
                        r'^([^\s]+) (\d{2}),? ?(\d{4})$'  # match Month D, Yr (i.e. February 17, 2009 or February 17,2009)
                        r'|'
                        r'^\d{4}$'  # match year (i.e. 2011)
                        r'|'
                        'Fiscal\d{4}'
                        r'|'
                        r'^Change$'
                        r'|'
                        r'(\b\d{1,2}\D{0,3})?\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|(Nov|Dec)(?:ember)?)\D?(\d{1,2}\D?)?\D?((19[7-9]\d|20\d{2})|\d{2})')

balance_sheet_regex = r'(balance ?sheet|condition)'
cash_flow_statement_regex = r'(Consolidated(.*?)cash flow)|(cash( ?)flow(s?) statement(s?))'
income_statement_regex = r'(Consolidated(.*?)statements of (income|earnings))|(income statement)|(CONSOLIDATED STATEMENTS OF OPERATIONS)'

non_current = '((?=.*non[- ]?current)|(?=.*long-term))'
current = '(?!.*non[- ]?current)(?=.*(current|short-term))'

financial_entries_regex_dict = {
    'Balance Sheet': {
        'Assets': {
            'Current Assets': {
                'Cash and Short Term Investments': {
                    'Cash and Cash Equivalents': r'(?!.*marketable securities)(?=.*cash and cash equivalents(?!.*[_:]))(?!.*marketable securities)',
                    'Marketable Securities Current': r'(?!.*non[- ]?current)(?=.*(current|short-term))(?=.*(marketable securities|investment)|((?=.*Available-for-sale)(?=.*securities)))(?!.*cash and cash equivalents)',
                    'Cash and Short Term Investments': r'(?=.*cash)(?=.*(marketable securities|short-term investments))'
                },
                'Accounts Receivable': {
                    # 'Gross Accounts Receivable': r'$^', # TODO
                    # 'Allowances for Doubtful Accounts': r'(?=.*Receivable)(?=.*allowances.*\$(\d+))',
                    # bug in this one (?=.*Receivable.*allowances).*(\$(\d+))*,
                    'Net Accounts Receivable': r'(?=.*Receivable)(?=.*(allowances|net|less))',
                },
                'Prepaid Expense, Current': r'((?=.*Prepaid expenses)|(?=.*Prepaids))(?!.*(Change|Increase|Decrease))',
                'Inventory, Net': r'(?=.*Inventor(y|ies)(?!.*[_:]))',
                'Income Taxes Receivable, Current': r'(?=.*Income taxes receivable)',
                'Assets Held-for-sale': r'Assets Held[- ]for[- ]sale',
                # taxes that have been already paid despite not yet having been incurred
                'Deferred Tax Assets, Current': r'(?=.*(Deferred tax(es)? (assets)|(on income))|(Prepaid taxes)){}'.format(
                    current),
                'Other Current Assets': r'$^',
                'Total Current Assets': r'(?=.*Total(?!.*[_]))(?=.*Assets(?!.*[_:])){}'.format(current)
            },
            'Non Current Assets': {

                'Marketable Securities Non Current': r'(?=.*marketable securities|investments){}'.format(non_current),
                'Restricted Cash Non Current': r'(?=.*Restricted cash){}'.format(non_current),
                'Property, Plant and Equipment': {
                    'Gross Property, Plant and Equipment': r'(?=.*(Property|Premise(s?)))(?=.*(Plant|Land))(?=.*Equipment)(?=.*(Gross|Before))',
                    'Accumulated Depreciation and Amortization': r'(?=.*((Property|Premise(s?))|Equipment).*_)(?=.*accumulated depreciation(?!.*[_]))',
                    'Property, Plant and Equipment, Net': r'(?=.*(Property|Premise(s?)))(?=.*(Plant|Land))?(?=.*Equipment)(?=.*(Net|Less|After))',
                },
                'Operating Lease Right-of-use Assets': r'Operating lease right-?of-?use assets',
                'Deferred Tax Assets Non Current': r'(?=.*deferred tax assets){}'.format(non_current),
                'Intangible Assets': {
                    'Goodwill': r'(?!.*net)(?=.*Goodwill)(?!.*net)',
                    'Intangible Assets, Net (Excluding Goodwill)': r'(?=.*(other|net))(?=.*intangible assets(?!.*[_]))',
                    'Total Intangible Assets': r'(?!.*other)(?!.*goodwill)(?!.*net)(?=.*intangible assets)(?!.*goodwill)(?!.*other)(?!.*net)',
                },
                'Other Non Current Assets': r'(?=.*Other)(?=.*assets(?!.*[_])){}'.format(non_current),
                'Total Non Current Assets': r'(?=.*Total(?!.*[_]))(?=.*assets(?!.*[_])){}'.format(non_current),
            },
            'Total Assets': r'(?=.*Total Assets(?!.*[_:]))'
        },
        "Liabilities and Shareholders\' Equity": {
            'Liabilities': {
                'Current Liabilities': {
                    # this is the short-term debt, i.e. the amount of a loan that is payable to the lender within one year.
                    'Long-term Debt, Current Maturities': r'(?=.*(Long-)?Term Debt|Loans and notes payable){}'.format(
                        current),
                    'Accounts Payable': r'(?=.*(Accounts)?Payable)',
                    'Operating Lease, Liability, Current': r'(?=.*Liabilit(y|ies)(?!.*[_:]))(?=.*Operating lease){}'.format(current),
                    'Current Deferred Revenues': r'(?=.*(Deferred Revenue)|(Short-term unearned revenue)){}'.format(
                        current),
                    'Employee-related Liabilities, Current': r'(?=.*Accrued Compensation){}'.format(current),
                    'Accrued Income Taxes': r'Accrued(?=.*Income)(?=.*Taxes)',
                    'Accrued Liabilities, Current': r'(?=.*Accrued)(?=.*(Expense|Liabilities))',
                    'Contract with Customer, Liability, Current': r'(?=.*Deferred revenue and deposits)|(?=.*Contract With Customer Liability Current)',
                    'Income Taxes Payable': r'(?=.*Income taxes payable)|(?=.*Short-term Income taxes)',
                    'Other Current Liabilities': r'(?=.*Other(?!.*[_:]))(?=.*liabilities(?!.*[_:])){}'.format(current),
                    'Total Current Liabilities': r'(?!.*Other(?!.*[_:]))(?=.*Liabilities(?!.*[_:])){}'.format(current),
                },
                'Non Current Liabilities': {
                    'Deferred Tax Liabilities': r'(Deferred(?=.*Income)(?=.*Taxes))|(Deferred tax liabilities)',
                    # this debt is due after one year in contrast to current maturities which are due within this year
                    'Long-term Debt, Noncurrent Maturities': r'(?=.*term debt)(?!.*within){}'.format(non_current),
                    'Operating Lease, Liability, Noncurrent': r'(?=.*Liabilit(y|ies)(?!.*[_:]))(?=.*Operating lease){}'.format(non_current),
                    'Liability, Defined Benefit Plan, Noncurrent': r'Employee related obligations',
                    'Accrued Income Taxes, Noncurrent': r'(Long-term ((income taxes)|(taxes payable)))',
                    'Deferred Revenue, Noncurrent': r'(?=.*Deferred Revenue){}'.format(non_current),
                    'Long-Term Unearned Revenue': r'(?=.*unearned)(?=.*revenue)((?!.*current)|(?=.*non[- ]?current)|(?=.*long[- ]?term))',
                    'Other Liabilities, Noncurrent': r'(?=.*Other(?!.*[_:]))(?=.*liabilities(?!.*[_:]))((?!.*current)|(?=.*non[- ]?current))',
                    'Total Non Current Liabilities': r'$^'
                },
                'Total Liabilities': r'((?=.*Total Liabilities)(?!.*Equity(?!.*[_]))(?!.*Other(?!.*[_])))|(^Liabilities$)'
                # sometimes at the bottom there are two tabs, our code can't catch it i.e. Other non-current liabilities then tab Total non-current liabilities then tab Total liabilities
            },
            "Shareholders' Equity": {
                'Preferred Stock, Value, Issued': r'(?=.*Preferred (stock|shares))(?!.*treasury)',
                'Common Stock and Additional Paid in Capital': {
                    'Common Stock, Value, Issued': r'(?=.*Common (stock|shares)(?!.*[_]))(?!.*treasury)(?!.*additional paid[- ]in capital(?!.*[_]))(?!.*(beginning|change))',
                    'Additional Paid in Capital': r'(?=.*additional paid[- ]in capital(?!.*[_]))(?!.*Common stock(?!.*[_]))',
                    'Common Stocks, Including Additional Paid in Capital': r'(?=.*Common stock(?!.*[_]))(?=.*additional paid[- ]in capital(?!.*[_]))',
                    'Weighted Average Number of Shares Outstanding, Basic': r'(?=.*shares)(?!.*dilut(ed|ive))(?!.*earnings(?!.*[_]))',
                    'Weighted Average Number Diluted Shares Outstanding Adjustment': r'(?=.*dilutive)(?=.*effect(?!.*[_:]))',
                    'Weighted Average Number of Shares Outstanding, Diluted': r'(?=.*shares)(?=.*diluted)(?!.*earnings(?!.*[_]))',
                },

                'Treasury Stock, Value': r'(?=.*Treasury stock)',
                'Retained Earnings (Accumulated Deficit)': r'(?=.*Accumulated deficit)|(Retained earnings)(?!.*Beginning)',
                'Accumulated Other Comprehensive Income (Loss)': r'(?=.*Accumulated other comprehensive (income|loss)(?!.*[_]))(?!.*Beginning)',
                'Deferred Stock Compensation': r'(?=.*Deferred stock compensation)',
                'Stockholders\' Equity Attributable to Parent': r'(?=.*Total.*(shareholders|stockholders)[’\'] equity)(?!.*Liabilities(?!.*[_]))',
                'Minority Interest': r'(?=.*Noncontrolling interest)',
                'Stockholders\' Equity, Including Portion Attributable to Noncontrolling Interest': '(?=.*Noncontrolling interest)(?=.*Equity(?!.*[_]))(?!.*Liabilities(?!.*[_]))'
            },
            'Total Liabilities and Shareholders\' Equity': r'(?=.*Liabilities(?!.*[_:]))(?=.*Equity(?!.*[_:]))'
        },
    },
    'Income Statement': {
        'Revenues': {
            'Service Sales': '(?=.*Sales)(?=.*Service(?!.*[_:]))(?!.*Cost)(?!.*Other(?!.*[_:]))',
            'Product Sales': '(?=.*Sales)(?=.*Product(?!.*[_:]))(?!.*Cost)(?!.*Other(?!.*[_:]))',
            'Net Sales': r'(?=.*(Net sales|Revenue)(?!.*[_:]))(?!.*Cost)',
            'Noninterest Income': r'(?=.*Non[- ]?interest (revenue|income))',
        },
        'Cost of Products': r'(?=.*Cost of Products)',
        'Cost of Services': r'(?=.*Cost of Services)',
        'Cost of Goods and Services Sold': r'(?=.*Cost of (revenue|sales)(?!.*[_:]))',
        'Provision for Loan, Lease, and Other Losses': r'(?=.*Provision for credit losses)',
        'Operating Expenses': {
            'Research and Development Expense': r'(?=.*(Research|Technology) and development)',
            'Selling, General and Administrative': {
                'Marketing Expense': r'(?!.*(Sales|selling))(?=.*Marketing)',
                'Selling and Marketing Expense': r'(?=.*(Sales|Selling))(?=.*Marketing)',
                'General and Administrative Expense': r'(?=.*General)(?=.*Administrative)(?!.*Selling)',
                'Selling, General and Administrative': r'(?=.*Selling, general and administrative)'
            },
            'Other Operating Expenses': r'$^',  # TODO
            'EBITDA': r'$^',
            'Depreciation, Depletion and Amortization, Nonproduction': r'(?!.*accumulated)(?=.*Depreciation(?!.*[_:]))(?=.*amortization(?!.*[_:]))',
            'Total Operating Expenses': r'(?=.*Total operating expenses)'
        },
        'Operating Income (Loss) / EBIT': r'(?=.*income(?!.*[_]))(?=.*operati(ng|ons)(?!.*[_]))(?!.*investments)',
        'Other (Non-Operating) Income (Expense)': {
            'Interest Income': r'(?=.*Interest(?!.*[_:]))(?!.*dividend(?!.*[_:]))(?=.*income(?!.*[_:]))(?!.*net(?!.*[_:]))',
            'Interest and Dividend Income': r'(?=.*Interest(?!.*[_:]))(?=.*dividend(?!.*[_:]))(?=.*income(?!.*[_:]))(?!.*net(?!.*[_:]))',
            'Interest Expense': r'(?=.*Interest expense(?!.*[_:]))(?!.*net(?!.*[_:]))',
            'Interest Income (Expense), Net': r'(?=.*Interest income(?!.*[_:]))(?=.*net(?!.*[_:]))',
            # TODO We Will compute this one in the end
            'Other Nonoperating Income (Expense)': '(?=.*Other income(?!.*[_]))(?=.*net(?!.*[_]))(?!.*Total(?!.*[_]))',
            # below is for Interest and other income, net
            # and Total other income/(expense), net
            'Non-Operating Income (Expense)': r'(?=.*(other|non))(?=.*income(?!.*[_:]))',
        },

        'Income (Loss) before Income Taxes, Noncontrolling Interest': r'(?=.*(Income before (?=.*Provision for)?(?=.*(income )?taxes)|Pre-tax earnings))',
        'Income Tax Expense (Benefit)': r'(?=.*Provision for)(?=.*(income )?taxes)',
        'Net Income (Loss), Including Portion Attributable to Noncontrolling Interest': r'(?=.*Net income including noncontrolling interest)',
        'Net Income (Loss) Attributable to Noncontrolling (Minority) Interest': r'(?=.*Net (income|earnings) (attributable|applicable) to Noncontrolling Interest)',
        'Net Income (Loss)': r'(?=.*Net (income|earnings|loss)$)',
        'Undistributed Earnings (Loss) Allocated to Participating Securities, Basic': r'(?=.*Net income attributable to participating securities)',
        'Preferred Stock Dividends': r'(?=.*Preferred stock dividends)',
        'Net Income (Loss) Available to Common Stockholders, Basic': r'(?=.*Net (income|earnings) (attributable|applicable) to (?!.*Noncontrolling Interest))'
    },
    'Cash Flow Statement': {
        'Cash, Cash Equivalents, Restricted Cash and Restricted Cash Equivalents, Beginning Balance': '(?=.*Cash, cash equivalents and restricted cash, beginning(?!.*[_:]))',
        'Operating Activities': {
            'Net Income (Loss) Attributable to Parent': r'(?=.*Operating activities)(?=.*Net income(?!.*[_:]))',
            'Adjustments to Reconcile Net Income': {
                'Depreciation, Depletion and Amortization': r'(?=.*Operating activities)(?=.*depreciation(?!.*[_:]))(?=.*amortization(?!.*[_:]))',
                'Share-based Payment Arrangement, Noncash Expense': r'(?=.*Operating activities)(?=.*Share-based compensation expense(?!.*[_:]))',
                'Deferred Income Tax Expense (Benefit)': r'(?=.*Operating activities)(?=.*Deferred income tax(?!.*[_:]))',
                'Other Noncash Income (Expense)': r'(?=.*Operating activities)(?=.*Other(?!.*[_:]))',
                'Increase (Decrease) in Accounts Receivable': r'(?=.*Operating activities)(?=.*Accounts receivable(?!.*[_:]))',
                'Increase (Decrease) in Inventories': r'(?=.*Operating activities)(?=.*Inventories(?!.*[_:]))',
                'Increase (Decrease) in Other Receivables': r'(?=.*Operating activities)(?=.*Vendor non-trade receivables(?!.*[_:]))',
                'Increase (Decrease) in Prepaid Expense and Other Assets': r'(?=.*Operating activities)(?=.*Prepaid expenses and other current assets(?!.*[_:]))',
                'Increase (Decrease) in Other Operating Assets': r'(?=.*Operating activities)(?=.*Other assets(?!.*[_:]))',
                'Increase (Decrease) in Accounts Payable': r'(?=.*Operating activities)(?=.*Accounts payable(?!.*[_:]))',
                'Increase (Decrease) in Other Accounts Payable': r'(?=.*Operating activities)(?=.*Partners payable(?!.*[_:]))',
                'Increase (Decrease) in Accrued Liabilities': r'(?=.*Operating activities)(?=.*Accrued expenses and other current liabilities(?!.*[_:]))',
                'Increase (Decrease) in Contract with Customer, Liability': r'(?=.*Operating activities)(?=.*Deferred revenue(?!.*[_:]))',
                'Increase (Decrease) in Other Operating Liabilities': '(?=.*Operating activities)(?=.*Other liabilities(?!.*[_:]))',
            },
            'Net Cash Provided by (Used in) Operating Activities': r'(?=.*Operating activities(?!.*[_:]))(?=.*cash(?!.*[_:]))'
        },
        'Investing Activities': {
            'Payments to Acquire Debt Securities, Available-for-sale': r'(?=.*Investing activities)(?=.*(Purchases|Payments)(?!.*[_:]))(marketable securities(?!.*[_:]))',
            'Proceeds from Maturities, Prepayments and Calls of Debt Securities, Available-for-sale': r'(?=.*Investing activities)(?=.*maturities of marketable securities(?!.*[_:]))',
            'Proceeds from Sale of Debt Securities, Available-for-sale': r'(?=.*Investing activities)(?=.*sales of marketable securities(?!.*[_:]))',
            'Payments to Acquire Property, Plant, and Equipment': '(?=.*Investing activities)(?=.*(Payments|Purchases)(?!.*[_:]))(?=.*property(?!.*[_:]))(?=.*equipment(?!.*[_:]))',
            'Payments to Acquire Businesses, Net of Cash Acquired': '(?=.*Investing activities)(?=.*business(?!.*[_:]))(?=.*acquisitions(?!.*[_:]))',
            'Payments to Acquire Other Investments': '(?=.*Investing activities)(?=.*Purchases of non-marketable securities(?!.*[_:]))',
            'Proceeds from Sale and Maturity of Other Investments': '(?=.*Investing activities)(?=.*Proceeds from non-marketable securities(?!.*[_:]))',
            'Payments for (Proceeds from) Other Investing Activities': '(?=.*Investing activities)(?=.*Other(?!.*[_:]))',
            'Net Cash Provided by (Used in) Investing Activities': r'(?=.*Investing activities(?!.*[_:]))(?=.*cash(?!.*[_:]))'
        },
        'Financing Activities': {
            'Proceeds from Issuance of Common Stock': r'(?=.*Financing activities)(?=.*Proceeds from issuance of common stock(?!.*[_:]))',
            'Payment, Tax Withholding, Share-based Payment Arrangement': '(?=.*Financing activities)(?=.*taxes(?!.*[_:]))(?=.*(paid|payment)(?!.*[_:]))(?=.*equity award(?!.*[_:]))',
            'Payments of Dividends': r'(?=.*Financing activities)(?=.*dividends(?!.*[_:]))(?=.*(payments|paid)(?!.*[_:]))',
            'Payments for Repurchase of Common Stock': '(?=.*Financing activities)(?=.*Repurchases(?!.*[_:]))(?=.*common stock(?!.*[_:]))',
            'Proceeds from Issuance of Long-term Debt': '(?=.*Financing activities)(?=.*Proceeds(?!.*[_:]))(?=.*issuance of (long[- ])?term debt(?!.*[_:]))',
            'Repayments of Long-term Debt': '(?=.*Financing activities)(?=.*Repayments of(?!.*[_:]))(?=.*(long[- ])?term debt(?!.*[_:]))',
            'Finance Lease, Principal Payments': '(?=.*Financing activities)(?=.*Principal payments on finance leases(?!.*[_:]))',
            'Proceeds from (Repayments of) Bank Overdrafts': '(?=.*Financing activities)(?=.*Net change in overdraft in cash pooling entities(?!.*[_:]))',
            'Proceeds from (Repayments of) Commercial Paper': '(?=.*Financing activities)(?=.*Proceeds from\/\(Repayments of\) commercial paper, net(?!.*[_:]))',
            'Proceeds from (Payments for) Other Financing Activities': '(?=.*Financing activities)(?=.*Other(?!.*[_:]))',
            'Net Cash Provided by (Used in) Financing Activities': r'(?=.*Financing activities(?!.*[_:]))(?=.*(net )?cash(?!.*[_:]))'
        },
        'Cash, Cash Equivalents, Restricted Cash and Restricted Cash Equivalents, Period Increase (Decrease)': '(?=.*Increase\/\(Decrease\) in cash, cash equivalents and restricted cash(?!.*[_:]))',
        'Cash, Cash Equivalents, Restricted Cash and Restricted Cash Equivalents, Ending Balance': '(?=.*Cash, cash equivalents and restricted cash, end(?!.*[_:]))',
        'Supplemental': {}
    }
}
