import traceback
import xml.etree.ElementTree as ET
from datetime import datetime
import requests
import re
from bs4 import BeautifulSoup, NavigableString
from zope.interface import implementer
import numpy as np
from historical_data_collection import excel_helpers
from historical_data_collection.financial_statements_scraper import financial_statements_scraper


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
                        'Marketable Securities Current': r'^(Available For Sale Securities Current|Available For Sale Securities Debt Securities)$',
                        'Cash and Short Term Investments': r'$^',
                    },
                    'Accounts Receivable': {
                        'Net Accounts Receivable': r'^Accounts Receivable Net Current$',
                    },
                    'Prepaid Expense, Current': r'$^',
                    'Inventory, Net': r'Inventory Net',
                    'Income Taxes Receivable, Current': r'',
                    'Assets Held-for-sale': r'$^',
                    # taxes that have been already paid despite not yet having been incurred
                    'Deferred Tax Assets, Current': r'',
                    'Other Current Assets': r'',
                    'Total Current Assets': r''
                },
                'Non Current Assets': {

                    'Marketable Securities Non Current': r'',
                    'Restricted Cash Non Current': r'',
                    'Property, Plant and Equipment': {
                        'Gross Property, Plant and Equipment': r'',
                        'Accumulated Depreciation and Amortization': r'',
                        'Property, Plant and Equipment, Net': r'',
                    },
                    'Operating Lease Right-of-use Assets': r'',
                    'Deferred Tax Assets Non Current': r'',
                    'Intangible Assets': {
                        'Goodwill': r'',
                        'Intangible Assets, Net (Excluding Goodwill)': r'',
                        'Total Intangible Assets': r'',
                    },
                    'Other Non Current Assets': r'',
                    'Total Non Current Assets': r''
                },
                'Total Assets': r''
            },
            "Liabilities and Shareholders\' Equity": {
                'Liabilities': {
                    'Current Liabilities': {
                        # this is the short-term debt, i.e. the amount of a loan that is payable to the lender within one year.
                        'Long-term Debt, Current Maturities': r'',
                        'Accounts Payable': r'',
                        # always a current anyways
                        'Other Accounts Payable': r'',
                        'Operating Lease, Liability, Current': r'',
                        'Current Deferred Revenues': r'',
                        'Employee-related Liabilities, Current': r'',
                        'Accrued Income Taxes': r'',
                        'Accrued Liabilities, Current': r'',
                        'Deferred Revenue, Current': r'',
                        'Income Taxes Payable': r'',
                        'Other Current Liabilities': r'',
                        'Total Current Liabilities': r'',
                    },
                    'Non Current Liabilities': {
                        'Deferred Tax Liabilities': r'',
                        # this debt is due after one year in contrast to current maturities which are due within this year
                        'Long-term Debt, Noncurrent Maturities': r'',
                        'Operating Lease, Liability, Noncurrent': r'',
                        'Liability, Defined Benefit Plan, Noncurrent': r'',
                        'Accrued Income Taxes, Noncurrent': r'',
                        'Deferred Revenue, Noncurrent': r'',
                        'Long-Term Unearned Revenue': r'',
                        'Other Liabilities, Noncurrent': r'',
                        'Total Non Current Liabilities': r''
                    },
                    'Total Liabilities': r''
                    # sometimes at the bottom there are two tabs, our code can't catch it i.e. Other non-current liabilities then tab Total non-current liabilities then tab Total liabilities
                },
                "Shareholders' Equity": {
                    'Preferred Stock, Value, Issued': r'',
                    'Common Stock and Additional Paid in Capital': {
                        'Common Stock, Value, Issued': r'',
                        'Additional Paid in Capital': r'',
                        'Common Stocks, Including Additional Paid in Capital': r'',
                        'Weighted Average Number of Shares Outstanding, Basic': r'',
                        'Weighted Average Number Diluted Shares Outstanding Adjustment': r'',
                        'Weighted Average Number of Shares Outstanding, Diluted': r'',
                    },

                    'Treasury Stock, Value': r'',
                    'Retained Earnings (Accumulated Deficit)': r'',
                    'Accumulated Other Comprehensive Income (Loss)': r'',
                    'Deferred Stock Compensation': r'',
                    'Stockholders\' Equity Attributable to Parent': r'',
                    'Minority Interest': r'',
                    'Stockholders\' Equity, Including Portion Attributable to Noncontrolling Interest': '(?!.*Before)(?=.*Noncontrolling interest)(?=.*Equity(?!.*[_]))(?!.*Liabilities(?!.*[_]))'
                },
                'Total Liabilities and Shareholders\' Equity': r''
            },
        },
        'Income Statement': {
            'Revenues': {
                'Service Sales': r'',
                'Product Sales': r'',
                'Net Sales': r''
            },
            'Cost of Products': r'',
            'Cost of Services': r'',
            'Cost of Goods and Services Sold': r'',
            'Gross Margin': r'',
            'Provision for Loan, Lease, and Other Losses': r'',
            'Operating Expenses': {
                'Research and Development Expense': r'',
                'Selling, General and Administrative': {
                    'Marketing Expense': r'',
                    'Selling and Marketing Expense': r'',
                    'General and Administrative Expense': r'',
                    'Selling, General and Administrative': r''
                },
                'Other Operating Expenses': r'',  # TODO
                'EBITDA': r'',
                'Total Operating Expenses': r''
            },
            'Costs and Expenses': r'',
            'Operating Income (Loss) / EBIT': r'',
            'Other (Non-Operating) Income (Expense)': {
                'Interest Income': r'',
                'Interest and Dividend Income': r'',
                'Interest Expense': r'',
                'Interest Income (Expense), Net': r'',
                'Foreign Currency Transaction Gain (Loss)': r'',
                'Other Nonoperating Income (Expense)': '$^',
                # below is for 'Interest and other income, net' and 'Total other income/(expense), net'
                'Non-Operating Income (Expense)': r''
            },

            'Income (Loss) before Income Taxes, Noncontrolling Interest': r'',
            'Income Tax Expense (Benefit)': r'',
            'Net Income (Loss), Including Portion Attributable to Noncontrolling Interest': r'',
            'Net Income (Loss) Attributable to Noncontrolling (Minority) Interest': r'',
            'Net Income (Loss) Attributable to Parent': r'',
            'Undistributed Earnings (Loss) Allocated to Participating Securities, Basic': r'',
            'Preferred Stock Dividends': r'',
            'Net Income (Loss) Available to Common Stockholders, Basic': r'',
            'Other Comprehensive Income (Loss)': r'',
            'Comprehensive Income (Loss), Net of Tax, Attributable to Parent': r''

        },
        'Cash Flow Statement': {
            'Cash, Cash Equivalents, Restricted Cash and Restricted Cash Equivalents, Beginning Balance':
                '(?=.*Cash, cash equivalents,? and restricted cash(?!.*[_:]))(?=.*beginning(?!.*[_:]))',
            'Operating Activities': {
                'Net Income (Loss) Attributable to Parent': r'',
                'Adjustments to Reconcile Net Income': {
                    'Depreciation, Depletion and Amortization': r'',
                    'Share-based Payment Arrangement, Noncash Expense': r'',
                    'Deferred Income Tax Expense (Benefit)': r'',
                    'Other Noncash Income (Expense)': r''
                },
                'Change in Assets and Liabilities': {
                    'Increase (Decrease) in Accounts Receivable': r'',
                    'Increase (Decrease) in Inventories': r'',
                    'Increase (Decrease) in Other Receivables': r'',
                    'Increase (Decrease) in Prepaid Expense and Other Assets': r'',
                    'Increase (Decrease) in Other Operating Assets': r'',
                    'Increase (Decrease) in Accounts Payable': r'',
                    'Increase (Decrease) in Other Accounts Payable': r'',
                    'Increase (Decrease) in Accrued Liabilities': r'',
                    'Increase (Decrease) in Deferred Revenue, Liability': r'',
                    'Increase (Decrease) in Other Operating Liabilities': r''
                },
                'Net Cash Provided by (Used in) Operating Activities': r''
            },
            'Investing Activities': {
                'Payments to Acquire Marketable Securities, Available-for-sale': r'',
                'Proceeds from Maturities, Prepayments and Calls of Debt Securities, Available-for-sale': r'',
                'Proceeds from Sale of Debt Securities, Available-for-sale': r'',
                'Payments to Acquire Property, Plant, and Equipment': r'',
                'Payments to Acquire Businesses, Net of Cash Acquired': r'',
                'Payments to Acquire Other Investments': r'',
                'Proceeds from Sale and Maturity of Other Investments': r'',
                'Payments for (Proceeds from) Other Investing Activities': r'',
                'Net Cash Provided by (Used in) Investing Activities': r''
            },
            'Financing Activities': {
                'Proceeds from Issuance of Common Stock': r'',
                'Payment, Tax Withholding, Share-based Payment Arrangement': r'',
                'Payments of Dividends': r'',
                'Payments for Repurchase of Common Stock': r'',
                'Proceeds from Issuance of Long-term Debt': r'',
                'Repayments of Long-term Debt': r'',
                'Finance Lease, Principal Payments': r'',
                'Proceeds from (Repayments of) Bank Overdrafts': r'',
                'Proceeds from (Repayments of) Commercial Paper': r'',
                'Proceeds from (Payments for) Other Financing Activities': r'',
                'Net Cash Provided by (Used in) Financing Activities': r''
            },
            'Effect of Exchange Rate on Cash, Cash Equivalents, Restricted Cash and Restricted Cash Equivalents': r'',
            'Cash, Cash Equivalents, Restricted Cash and Restricted Cash Equivalents, Period Increase (Decrease), Including Exchange Rate Effect': r'',
            # we are hardcoding the Ending balance to be Cash, Cash Equivalents, Restricted Cash and Restricted Cash Equivalents in XBRL because we filtered the beginning balance (which can be taken from previous year)
            'Cash, Cash Equivalents, Restricted Cash and Restricted Cash Equivalents, Ending Balance': r'',
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
        response = requests.get(url).text
        elements = ET.fromstring(response)
        all_in_one_dict = {'Yearly': {filing_date: {'': {}}}, 'Quarterly': {filing_date: {'': {}}}}

        # First, get all the us-gaap xbrl tags (that correspond to the current year or quarter)
        for element in elements.iter():
            if 'contextRef' in element.attrib.keys():
                tag_name = re.sub(r"(\w)([A-Z])", r"\1 \2", element.tag.split('}')[1])
                try:
                    tag_value = int(element.text)
                except:
                    continue
                if str(filing_date.year) in element.attrib['contextRef'] \
                        and 'Axis' not in element.attrib['contextRef']:
                    print(tag_name)
                    all_in_one_dict[filing_type][filing_date][''][tag_name] = tag_value

        return all_in_one_dict

    def normalize_tables(self, regex_patterns, filing_date, input_dict, visited_data_names) -> (dict, dict):
        """Standardize tables to match across years and companies"""
        master_dict = {}
        for normalized_category, pattern_string in excel_helpers.flatten_dict(regex_patterns).items():
            master_dict[normalized_category] = np.nan

        for title, table in input_dict.items():
            for scraped_name, scraped_value in excel_helpers.flatten_dict(table).items():
                for normalized_category, pattern_string in excel_helpers.flatten_dict(regex_patterns).items():
                    if re.search(pattern_string, scraped_name, re.IGNORECASE):
                        master_dict[normalized_category] = scraped_value
                        break

        return {}, master_dict
