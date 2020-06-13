import collections
from collections import OrderedDict
import re
from pprint import pprint
from re import Pattern
from sec_scraping.sec_scraping_unit_tests import all_in_one_dict_gilead

def flatten(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

master_dict = {}
pprint(flatten(all_in_one_dict_gilead))

# TODO to generalize further, each pattern is actually the name of the key
# case insensitive,
# starts with either title or name of parent category
# excludes words from other entries in category
# exclude : , etc. with any characters in between each word

balance_sheet_regex = r'Consolidated(.*?)(balance sheet|condition)'
cash_flow_statement_regex = r'Consolidated(.*?)cash flows'
financial_entries_regex_dict = {
    'Balance Sheet': {
        'Assets': {
            'Current Assets': {
                'Cash and Cash Equivalents': re.compile(r'({}|Current Assets)(.*?)Cash and cash equivalents(.*?)(?!^Marketable Securities$)'.format(balance_sheet_regex), re.IGNORECASE),
                'Marketable Securities Current': re.compile(r'({}|Current Assets)(.*?)Short-term marketable securities'.format(balance_sheet_regex), re.IGNORECASE),
                'Accounts Receivable': {
                    'Gross Accounts Receivable': 0,
                    'Allowances for Doubtful Accounts': re.compile(r'{}(.*?)net of allowances of \$'.format(balance_sheet_regex), re.IGNORECASE), # TODO extract
                    'Net Accounts Receivable': re.compile(r'({}|Current Assets)(.*?)Accounts receivable'.format(balance_sheet_regex), re.IGNORECASE),
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
        'Non-Operating Income (Expenses)': OrderedDict(),
        'Net Income (Loss)': 0,
        'Net Income Loss Attributable to Noncontrolling Interest': 0
    },
    'Cash Flow Statement': {
        'Operating Activities': re.compile(r'{}(.*?)Operating activities:(.*?)'.format(cash_flow_statement_regex), re.IGNORECASE),
        'Investing Activities': re.compile(r'{}(.*?)Investing activities:(.*?)'.format(cash_flow_statement_regex), re.IGNORECASE),
        'Financing Activities': re.compile(r'{}(.*?)Financing activities:(.*?)'.format(cash_flow_statement_regex), re.IGNORECASE),
    }
}

for scraped_name, scraped_value in flatten(all_in_one_dict_gilead).items():
    for normalized_category, pattern in flatten(financial_entries_regex_dict).items():

        if isinstance(pattern, Pattern):
            pattern_match = re.search(pattern, scraped_name)
            if pattern_match:
                master_dict[normalized_category] = scraped_value
                if 'Cash Flow Statement' in normalized_category: # TODO beware _ and : normalize!
                    master_dict[normalized_category+'_'+pattern_match.string.split(':')[-1]] = scraped_value

pprint(master_dict)

balance_sheet = {i: master_dict[i] for i in master_dict.keys() if re.search(r'Balance Sheet', i)}
income_statement = {i: master_dict[i] for i in master_dict.keys() if re.search(r'Income Statement', i)}
cash_flow_statement = {i: master_dict[i] for i in master_dict.keys() if re.search(r'Cash Flow Statement', i)}
pprint(balance_sheet)