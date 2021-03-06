import traceback
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pprint import pprint

import requests
import re
from bs4 import BeautifulSoup, NavigableString
from zope.interface import implementer
import numpy as np

from matilda.database.data_preparation_helpers import flatten_dict
from matilda.database.data_scapers.financial_statements_scraper import financial_statements_scraper


def get_company_cik(ticker):
    URL = 'http://www.sec.gov/cgi-bin/browse-edgar?CIK={}&Find=Search&owner=exclude&action=getcompany'.format(ticker)
    response = requests.get(URL)
    CIK_RE = re.compile(r'.*CIK=(\d{10}).*')
    cik = CIK_RE.findall(response.text)[0]
    print('Company CIK for {} is {}'.format(ticker, cik))
    return cik


def get_filings_urls_first_layer(cik, filing_type):
    base_url = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={}&type={}".format(cik, filing_type)
    edgar_resp = requests.get(base_url).text
    print(base_url)
    soup = BeautifulSoup(edgar_resp, 'html.parser')
    table_tag = soup.find('table', class_='tableFile2')
    rows = table_tag.find_all('tr')
    doc_links = []
    for row in rows[1:]:
        cells = row.find_all('td')
        doc_links.append('https://www.sec.gov' + cells[1].a['href'])
    return doc_links


def get_filings_urls_second_layer(doc_links):
    dates_and_links = []
    for doc_link in doc_links:
        doc_resp = requests.get(doc_link).text  # Obtain HTML for document page
        soup = BeautifulSoup(doc_resp, 'html.parser')  # Find the XBRL link
        head_divs = soup.find_all('div', class_='infoHead')  # first, find period of report
        cell_index = next((index for (index, item) in enumerate(head_divs) if item.text == 'Period of Report'), -1)
        period_of_report = ''
        try:
            siblings = head_divs[cell_index].next_siblings
            for sib in siblings:
                if isinstance(sib, NavigableString):
                    continue
                else:
                    period_of_report = sib.text
                    break
        except:
            traceback.print_exc()

        # first, try finding a XML document
        table_tag = soup.find('table', class_='tableFile', summary='Data Files')
        if table_tag is not None:
            rows = table_tag.find_all('tr')
            for row_index, row in enumerate(rows[1:]):
                cells = row.find_all('td')
                link = 'https://www.sec.gov' + cells[2].a['href']
                if 'XML' in cells[3].text or 'INS' in cells[3].text:
                    dates_and_links.append((period_of_report, link))

    return dates_and_links


@implementer(financial_statements_scraper.FinancialStatementsParserInterface)
class XbrlParser:
    regex_patterns = {
        'Balance Sheet': {
            'Assets': {
                'Current Assets': {
                    'Cash and Short Term Investments': {
                        'Cash and Cash Equivalents': r'^Cash And Cash Equivalents At Carrying Value$',
                        'Marketable Securities Current': r'(^Available For Sale Securities Current'
                                                         r'|Available For Sale Securities Debt Securities'
                                                         r'|Marketable Securities Current$)',
                        'Cash and Short Term Investments': r'$^',
                    },
                    'Accounts Receivable': {
                        'Allowance for Doubtful Accounts': r'^Allowance For Doubtful Accounts Receivable Current$',
                        'Net Accounts Receivable': r'^Accounts Receivable Net Current$',
                        'Vendor Nontrade Receivables, Current': r'^Nontrade Receivables Current$'
                    },
                    'Prepaid Expense, Current': r'$^',
                    'Inventory, Net': r'^Inventory Net$',
                    'Income Taxes Receivable, Current': r'$^',
                    'Assets Held-for-sale': r'$^',
                    # taxes that have been already paid despite not yet having been incurred
                    'Deferred Tax Assets, Current': r'$^',
                    'Other Current Assets': r'^Other Assets Current$',
                    'Total Current Assets': r'^Assets Current$'
                },
                'Non Current Assets': {

                    'Marketable Securities Non Current': r'^Marketable Securities Noncurrent$',
                    'Restricted Cash Non Current': r'$^',
                    'Property, Plant and Equipment': {
                        'Gross Property, Plant and Equipment': r'^Property Plant And Equipment Gross$',
                        'Accumulated Depreciation and Amortization': r'^Accumulated Depreciation Depletion And Amortization Property Plant And Equipment$',
                        'Property, Plant and Equipment, Net': r'^Property Plant And Equipment Net$',
                    },
                    'Operating Lease Right-of-use Assets': r'$^',
                    'Deferred Tax Assets Non Current': r'$^',
                    'Intangible Assets': {
                        'Goodwill': r'^Goodwill$',
                        'Intangible Assets, Net (Excluding Goodwill)': r'^Intangible Assets Net Excluding Goodwill$',
                        'Total Intangible Assets': r'$^',
                    },
                    'Other Non Current Assets': r'^Other Assets Noncurrent$',
                    'Total Non Current Assets': r'^Assets Noncurrent$'
                },
                'Total Assets': r'^Assets$'
            },
            "Liabilities and Shareholders\' Equity": {
                'Liabilities': {
                    'Current Liabilities': {
                        # this is the short-term debt, i.e. the amount of a loan that is payable to the lender within one year.
                        'Long-term Debt, Current Maturities': r'^LongTermDebtCurrent$',
                        'Accounts Payable': r'^Accounts Payable Current$',
                        # always a current anyways
                        'Other Accounts Payable': r'^Accounts Payable Other Current$',
                        'Operating Lease, Liability, Current': r'$^',
                        'Employee-related Liabilities, Current': r'$^',
                        'Accrued Income Taxes': r'$^',
                        'Accrued Liabilities, Current': r'^Accrued Liabilities Current$',
                        'Deferred Revenue, Current': r'^Contract With Customer Liability Current$',
                        'Commercial Paper': r'^Commercial Paper$',
                        'Income Taxes Payable': r'$^',
                        'Other Current Liabilities': r'^Other Liabilities Current$',
                        'Total Current Liabilities': r'^Liabilities Current$',
                    },
                    'Non Current Liabilities': {
                        'Deferred Tax Liabilities': r'$^',
                        # this debt is due after one year in contrast to current maturities which are due within this year
                        'Long-term Debt, Noncurrent Maturities': r'^Long Term Debt Noncurrent$',
                        'Operating Lease, Liability, Noncurrent': r'$^',
                        'Liability, Defined Benefit Plan, Noncurrent': r'$^',
                        'Accrued Income Taxes, Noncurrent': r'$^',
                        'Deferred Revenue, Noncurrent': r'$^',
                        'Long-Term Unearned Revenue': r'$^',
                        'Other Liabilities, Noncurrent': r'^Other Liabilities Noncurrent$',
                        'Total Non Current Liabilities': r'^Liabilities Noncurrent$'
                    },
                    'Total Liabilities': r'^Liabilities$'
                    # sometimes at the bottom there are two tabs, our code can't catch it i.e. Other non-current liabilities then tab Total non-current liabilities then tab Total liabilities
                },
                "Shareholders' Equity": {
                    'Preferred Stock, Value, Issued': r'$^',
                    'Common Stock and Additional Paid in Capital': {
                        'Common Stock, Value, Issued': r'^Common Stock Value$',
                        'Additional Paid in Capital': r'^Additional Paid In Capital$',
                        'Common Stocks, Including Additional Paid in Capital': r'^Common Stocks Including Additional Paid In Capital$',
                        'Weighted Average Number of Shares Outstanding, Basic': r'^Weighted Average Number Of Shares Outstanding Basic$ ',
                        'Weighted Average Number Diluted Shares Outstanding Adjustment': r'$^',
                        'Weighted Average Number of Shares Outstanding, Diluted': r'^Weighted Average Number Of Diluted Shares Outstanding$',
                    },

                    'Treasury Stock, Value': r'$^',
                    'Retained Earnings (Accumulated Deficit)': r'^Retained Earnings Accumulated Deficit$',
                    'Accumulated Other Comprehensive Income (Loss)': r'^Accumulated Other Comprehensive Income Loss Net Of Tax$',
                    'Deferred Stock Compensation': r'$^',
                    'Stockholders\' Equity Attributable to Parent': r'$^',
                    'Minority Interest': r'$^',
                    'Stockholders\' Equity, Including Portion Attributable to Noncontrolling Interest': '(?!.*Before)(?=.*Noncontrolling interest)(?=.*Equity(?!.*[_]))(?!.*Liabilities(?!.*[_]))'
                },
                'Total Liabilities and Shareholders\' Equity': r'^Liabilities And Stockholders Equity$'
            },
        },
        'Income Statement': {
            'Revenues': {
                'Service Sales': r'$^',
                'Product Sales': r'$^',
                'Net Sales': r'^(Revenue From Contract With Customer Excluding Assessed Tax|Sales Revenue Net)$'
            },
            'Cost of Goods and Services Sold': {
                'Cost of Products': r'^(Cost Of Goods And Services Sold ProductMember|Revenue From Contract With Customer Excluding Assessed Tax ProductMember)$',
                'Cost of Services': r'^(Cost Of Goods And Services Sold ServiceMember|Revenue From Contract With Customer Excluding Assessed Tax ServiceMember)$',
                'Cost of Goods and Services Sold': r'^(Cost Of Revenue|Cost Of Goods And Services Sold)$',
                'Gross Margin': r'^Gross Profit$',
            },
            'Provision for Loan, Lease, and Other Losses': r'$^',
            'Operating Expenses': {
                'Research and Development Expense': r'^Research And Development Expense$',
                'Selling, General and Administrative': {
                    'Marketing Expense': r'$^',
                    'Selling and Marketing Expense': r'^Selling And Marketing Expense$',
                    'General and Administrative Expense': r'^General And Administrative Expense$',
                    'Selling, General and Administrative Expense': r'^Selling General And Administrative Expense$'
                },
                'Other Operating Expenses': r'$^',  # TODO
                'EBITDA': r'$^',
                'Total Operating Expenses': r'^Operating Expenses$'
            },
            'Costs and Expenses': r'^Costs And Expenses$',
            'Operating Income (Loss) / EBIT': r'^Operating Income Loss$',
            'Other (Non-Operating) Income (Expense)': {
                'Interest Income': r'^Investment Income Interest$',
                'Interest and Dividend Income': r'$^',
                'Interest Expense': r'^Interest Expense$',
                'Interest Income (Expense), Net': r'$^',
                'Foreign Currency Transaction Gain (Loss)': r'^Foreign Currency Transaction Gain Loss Before Tax$',
                'Other Nonoperating Income (Expense)': '^Other Nonoperating Income Expense$',
                # below is for 'Interest and other income, net' and 'Total other income/(expense), net'
                'Non-Operating Income (Expense)': r'^Nonoperating Income Expense$'
            },

            'Income (Loss) before Income Taxes, Noncontrolling Interest': r'^Income Loss From Continuing Operations Before Income Taxes Extraordinary Items Noncontrolling Interest$',
            'Income Tax Expense (Benefit)': r'^Income Tax Expense Benefit$',
            'Net Income (Loss), Including Portion Attributable to Noncontrolling Interest': r'$^',
            'Net Income (Loss) Attributable to Noncontrolling (Minority) Interest': r'$^',
            'Net Income (Loss) Attributable to Parent': r'^Net Income Loss$',
            'Undistributed Earnings (Loss) Allocated to Participating Securities, Basic': r'^Undistributed Earnings Loss Allocated To Participating Securities Basic$',
            'Preferred Stock Dividends': r'$^',
            'Net Income (Loss) Available to Common Stockholders, Basic': r'^Net Income Loss Available To Common Stockholders Basic$',
            'Other Comprehensive Income (Loss)': r'$^',
            'Comprehensive Income (Loss), Net of Tax, Attributable to Parent': r'$^',
            'Earnings Per Share, Basic': '^Earnings Per Share Basic$',
            'Earnings Per Share, Diluted': '^Earnings Per Share Diluted$',

        },
        'Cash Flow Statement': {
            'Cash, Cash Equivalents, Restricted Cash and Restricted Cash Equivalents, Beginning Balance':
                '$^',
            'Operating Activities': {
                'Net Income (Loss) Attributable to Parent': r'$^',
                'Adjustments to Reconcile Net Income': {
                    'Depreciation, Depletion and Amortization': r'$^',
                    'Share-based Payment Arrangement, Noncash Expense': r'$^',
                    'Deferred Income Tax Expense (Benefit)': r'$^',
                    'Other Noncash Income (Expense)': r'$^'
                },
                'Change in Assets and Liabilities': {
                    'Increase (Decrease) in Accounts Receivable': r'$^',
                    'Increase (Decrease) in Inventories': r'$^',
                    'Increase (Decrease) in Other Receivables': r'$^',
                    'Increase (Decrease) in Prepaid Expense and Other Assets': r'$^',
                    'Increase (Decrease) in Other Operating Assets': r'$^',
                    'Increase (Decrease) in Accounts Payable': r'$^',
                    'Increase (Decrease) in Other Accounts Payable': r'$^',
                    'Increase (Decrease) in Accrued Liabilities': r'$^',
                    'Increase (Decrease) in Deferred Revenue, Liability': r'$^',
                    'Increase (Decrease) in Other Operating Liabilities': r'$^'
                },
                'Net Cash Provided by (Used in) Operating Activities': r'$^'
            },
            'Investing Activities': {
                'Payments to Acquire Marketable Securities, Available-for-sale': r'$^',
                'Proceeds from Maturities, Prepayments and Calls of Debt Securities, Available-for-sale': r'$^',
                'Proceeds from Sale of Debt Securities, Available-for-sale': r'$^',
                'Payments to Acquire Property, Plant, and Equipment': r'$^',
                'Payments to Acquire Businesses, Net of Cash Acquired': r'$^',
                'Payments to Acquire Other Investments': r'$^',
                'Proceeds from Sale and Maturity of Other Investments': r'$^',
                'Payments for (Proceeds from) Other Investing Activities': r'$^',
                'Net Cash Provided by (Used in) Investing Activities': r'$^'
            },
            'Financing Activities': {
                'Proceeds from Issuance of Common Stock': r'$^',
                'Payment, Tax Withholding, Share-based Payment Arrangement': r'$^',
                'Payments of Dividends': r'$^',
                'Payments for Repurchase of Common Stock': r'$^',
                'Proceeds from Issuance of Long-term Debt': r'$^',
                'Repayments of Long-term Debt': r'$^',
                'Finance Lease, Principal Payments': r'$^',
                'Proceeds from (Repayments of) Bank Overdrafts': r'$^',
                'Proceeds from (Repayments of) Commercial Paper': r'$^',
                'Proceeds from (Payments for) Other Financing Activities': r'$^',
                'Net Cash Provided by (Used in) Financing Activities': r'$^'
            },
            'Effect of Exchange Rate on Cash, Cash Equivalents, Restricted Cash and Restricted Cash Equivalents': r'$^',
            'Cash, Cash Equivalents, Restricted Cash and Restricted Cash Equivalents, Period Increase (Decrease), Including Exchange Rate Effect': r'$^',
            # we are hardcoding the Ending balance to be Cash, Cash Equivalents, Restricted Cash and Restricted Cash Equivalents in XBRL because we filtered the beginning balance (which can be taken from previous year)
            'Cash, Cash Equivalents, Restricted Cash and Restricted Cash Equivalents, Ending Balance': r'$^',
            'Supplemental': {}
        }
    }

    def load_data_source(self, ticker: str) -> dict:
        """Load in the file links"""
        cik = get_company_cik(ticker)
        doc_links_yearly = get_filings_urls_first_layer(cik, '10-K')
        doc_links_quarterly = get_filings_urls_first_layer(cik, '10-Q')
        filings_dictio_yearly = get_filings_urls_second_layer(doc_links_yearly)
        filings_dictio_quarterly = get_filings_urls_second_layer(doc_links_quarterly)
        return {'Yearly': filings_dictio_yearly, 'Quarterly': filings_dictio_quarterly}

    def scrape_tables(self, url: str, filing_date: datetime, filing_type: str) -> dict:
        """Extract tables from the currently loaded file."""
        current_quarter = ''
        response = requests.get(url).text
        elements = ET.fromstring(response)
        all_in_one_dict = {'Yearly': {filing_date: {'': {}}}, 'Quarterly': {filing_date: {'': {}}},
                           '6 Months': {filing_date: {'': {}}}, '9 Months': {filing_date: {'': {}}}}

        # First, get all the us-gaap xbrl tags (that correspond to the current year or quarter)
        found_current_quarter = False
        for element in elements.iter():
            if 'context' in element.tag and not found_current_quarter:
                pattern = re.search('(Q\d)', element.attrib['id'])
                if pattern:
                    current_quarter = pattern.groups()[-1]
                    found_current_quarter = True
            if 'contextRef' in element.attrib.keys():
                tag_name = re.sub(r"(\w)([A-Z])", r"\1 \2", element.tag.split('}')[1])
                try:
                    tag_value = int(element.text)
                except:
                    continue

                axis_pattern = re.search(r'ProductOrServiceAxis_us-gaap_(.*)', element.attrib['contextRef'],
                                         re.IGNORECASE)
                if axis_pattern:
                    tag_name = tag_name + ' ' + axis_pattern.groups()[-1]
                if ('Axis' not in element.attrib['contextRef']) or axis_pattern:
                    period = filing_type

                    # first pattern for date and period
                    date_pattern_yyyymmdd = re.search(r'(........)-{}'.format(filing_date.strftime('%Y%m%d')),
                                                      element.attrib['contextRef'])
                    if date_pattern_yyyymmdd:
                        prior_date = date_pattern_yyyymmdd.groups()[-1]
                        prior_date = datetime.strptime(prior_date, '%Y%m%d')
                        if filing_date > prior_date + timedelta(days=270):
                            period = '9 Months'
                        elif filing_date > prior_date + timedelta(days=180):
                            period = '6 Months'
                        all_in_one_dict[period][filing_date][''][tag_name] = tag_value

                    # second pattern for date and period
                    date_pattern_FDYYYYQd = re.search(r'FD{}{}(...)?'.format(filing_date.year, current_quarter),
                                                      element.attrib['contextRef'])
                    if date_pattern_FDYYYYQd and found_current_quarter:
                        period = date_pattern_FDYYYYQd.groups()[-1]
                        if period == 'YTD':
                            period = 'Yearly'
                        elif period == 'QTD':
                            period = 'Quarterly'
                        all_in_one_dict[period][filing_date][''][tag_name] = tag_value

                    # third pattern for date and period
                    date_pattern_FIYYYQd = re.search(r'FI{}{}'.format(filing_date.year, current_quarter),
                                                     element.attrib['contextRef'])
                    if date_pattern_FIYYYQd and found_current_quarter:
                        period = 'Yearly'
                        all_in_one_dict[period][filing_date][''][tag_name] = tag_value

                    # fourth pattern for date and period i.e. 'STD_364_20150926'
                    date_pattern_STD_delta_yyymmdd = re.search(r'STD_(\d+)_{}'.format(filing_date.strftime('%Y%m%d')),
                                                               element.attrib['contextRef'])
                    if date_pattern_STD_delta_yyymmdd:
                        period_unformatted = date_pattern_STD_delta_yyymmdd.groups()[-1]
                        if period_unformatted == '364' or period_unformatted == '0':
                            period = 'Yearly'
                        else:
                            period = 'Quarterly'

                        all_in_one_dict[period][filing_date][''][tag_name] = tag_value
        return all_in_one_dict

    def normalize_tables(self, filing_date, input_dict, visited_data_names) -> (dict, dict):
        """Standardize tables to match across years and companies"""
        master_dict = {}
        for normalized_category, pattern_string in flatten_dict(self.regex_patterns).items():
            master_dict[normalized_category] = np.nan

        for title, table in input_dict.items():
            for scraped_name, scraped_value in flatten_dict(table).items():
                for normalized_category, pattern_string in flatten_dict(self.regex_patterns).items():
                    if re.search(pattern_string, scraped_name, re.IGNORECASE):
                        master_dict[normalized_category] = scraped_value
                        break
        pprint(master_dict)
        return {}, master_dict

#
# if __name__ == '__main__':
#     facebook = DataView('FB', '2019-12-31', '10-K')
#     facebook.traverse_tree('StatementOfFinancialPositionClassified')
