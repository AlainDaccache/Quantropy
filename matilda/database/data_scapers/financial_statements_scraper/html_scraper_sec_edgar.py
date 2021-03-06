import math
import re
import traceback
import datetime
from time import sleep
import numpy as np
import requests
import unicodedata
from bs4 import BeautifulSoup, NavigableString
from pprint import pprint
from titlecase import titlecase
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
import matilda.database.data_scapers.financial_statements_scraper.financial_statements_scraper as main_scraper
from zope.interface import implementer

from matilda.database.data_preparation_helpers import flatten_dict


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
    soup = BeautifulSoup(edgar_resp, 'lxml')
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
        soup = BeautifulSoup(doc_resp, 'lxml')  # Find the XBRL link
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

        table_tag = soup.find('table', class_='tableFile', summary='Document Format Files')
        rows = table_tag.find_all('tr')
        for row in rows[1:]:
            cells = row.find_all('td')
            link = 'https://www.sec.gov' + cells[2].a['href']
            if 'htm' in cells[2].text and cells[3].text in ['10-K', '10-Q']:
                dates_and_links.append((period_of_report, link))

    return dates_and_links


def is_bold(row, alltext=False):
    soup = BeautifulSoup(str(row), features='lxml')
    bolded_row_text = soup.find_all(
        lambda tag: tag.name == 'b' or (
                tag.has_attr('style') and (re.search('bold|font-weight:700', str(tag['style']), re.IGNORECASE))))
    bolded_row_text = ' '.join([a.text for a in bolded_row_text]).strip()
    row_text = row.text.replace('\u200b', '').strip()
    if alltext:
        return len(bolded_row_text) > 0 and len(bolded_row_text) == len(row_text)
    else:
        return len(bolded_row_text) > 0


def is_colored(row):
    # TODO implement
    return False


def is_italic(row):
    soup = BeautifulSoup(str(row), features='lxml')
    italic = soup.find_all(lambda tag: tag.name == 'i')
    return len(italic) > 0


def is_centered(row):
    soup = BeautifulSoup(str(row), features='lxml')
    return len(soup.find_all(lambda tag: tag.name != 'table' and (
            (tag.has_attr('align') and 'center' in str(tag['align'])) or tag.has_attr(
        'style') and 'text-align:center' in str(tag['style'])))) > 0


def find_left_margin(reg_row, td):
    # https://www.w3schools.com/cssref/pr_margin.asp
    pattern_matches = [
        re.findall('(margin-left|padding-left|text-indent):(-?\d+)', str(td)),
        re.findall(r'margin:-?\d+pt -?\d+pt -?\d+pt (-?\d+)pt', str(td)),
        re.findall(r'margin:-?\d+pt (-?\d+)pt -?\d+pt', str(td)),
        re.findall(r'margin:-?\d+pt (-?\d+)pt', str(td)),
        re.findall(r'margin:(-?\d+)pt', str(td))]
    for match in pattern_matches:
        c1 = sum([float(m[-1]) for m in match]) if len(match) > 0 else 0
        match = re.search(r'( *)\w', reg_row[0])
        c2 = match.group().count(' ') if match else 0
        if max(c1, c2) == 0:
            continue
        else:
            return max(c1, c2)
    return 0


def find_table_meta(table):
    """
    Table title, multipler

    :param table:
    :return:
    """
    multiplier_pattern = re.compile('(thousands|millions|billions|percentage|millions.*thousands)', re.IGNORECASE)
    currency_pattern = re.compile('([$€¥£])', re.IGNORECASE)
    table_multiplier, emergency_title, found_another_table = '', 'No Table Title', False
    current_element, total_text = table.previous_element, ''

    while current_element is not None and not found_another_table:
        current_text = ''

        if len(table_multiplier) == 0:  # try getting the multiplier in the current element if we haven't found it yet
            pattern = re.search(multiplier_pattern,
                                current_element.text if not isinstance(current_element,
                                                                       NavigableString) else current_element)
            if pattern:
                table_multiplier = pattern.groups()[-1]

        if len(emergency_title) == 0 and re.search('The following table',
                                                   current_element.text if not isinstance(current_element,
                                                                                          NavigableString) else current_element,
                                                   re.IGNORECASE):
            emergency_title = current_element.text

        if isinstance(current_element, NavigableString):  # need to get styling of that element (to see if bold etc.)
            current_element = current_element.previous_element
            continue

        elif current_element.name in ['tr', 'td']:  # since we start at previous
            break

        elif (current_element.name in ['div', 'body', 'html'] and current_element.find('table')):
            current_element = current_element.previous_element
            continue

        elif (current_element.name in ['table', 'tbody'] and current_element.text in table.text):
            current_element = current_element.previous_element
            continue

        elif is_bold(current_element) or is_centered(current_element) or is_italic(
                current_element) or is_colored(current_element):

            current_text = current_element.text.strip()
            total_text = '{} {}'.format(current_text, total_text) if current_text not in total_text else total_text

        current_element = current_element.previous_element

    total_text = unicodedata.normalize("NFKD", total_text) \
        .replace('\u200b', '').replace('(', '').replace(')', '').replace('\n', ' ').strip()

    return (emergency_title, table_multiplier) if len(total_text) == 0 else (total_text, table_multiplier)


def normalization_iteration(regexes_dict,
                            iteration_count, input_dict, master_dict, visited_data_names, year,
                            flexible_sheet=False, flexible_entry=False):  # fix to False when scrapig non xbrl
    # make normalized category into a regex
    categories = [
        # Balance Sheet
        re.compile(r'((.*?_?)Current Assets)', re.IGNORECASE),
        re.compile('((.*?_?)Current Liabilities)', re.IGNORECASE),
        re.compile(r'((.*?_?)Non-? ?Current Assets)', re.IGNORECASE),
        re.compile('((.*?_?)Non-? ?Current Liabilities)', re.IGNORECASE),
        re.compile('((.*?)(?!.*Liabilities)Shareholders[’\'] Equity)', re.IGNORECASE),
        re.compile(r'((.*?_?)Assets)', re.IGNORECASE),
        re.compile('((.*?)Liabilities(?!.*Shareholders[’\'] Equity))', re.IGNORECASE),
        # Income Statement
        re.compile('((.*?)Revenues)', re.IGNORECASE),
        re.compile('((.*?)Operating Expenses)', re.IGNORECASE),
        re.compile('((.*?)Other (\(Non-Operating\) Income )?Expense)', re.IGNORECASE),
        # Cash Flow Statement
        re.compile('((.*?)Operating Activities(?!.*Net.*_))', re.IGNORECASE),
        re.compile('((.*?)Investing Activities(?!.*Net.*_))', re.IGNORECASE),
        re.compile('((.*?)Financing Activities(?!.*Net.*_))', re.IGNORECASE)
    ]

    for title, table in input_dict.items():

        for scraped_name, scraped_value in flatten_dict(table).items():
            found_and_done = False
            # for visited_data in visited_data_names[year]:
            for normalized_category, pattern_string in \
                    flatten_dict(regexes_dict['Financial Entries Regex']).items():
                if found_and_done:
                    break
                # if you're a flexible sheet, the sheet we're checking at least shouldn't match the other
                # concerning statements (i.e. depreciation and amortization's pattern in balance sheet regex
                # shouldn't match cash flow statement change in depreciation and amortization)
                # For now, we're only allowing balance sheet and income statement together (because of shares outstanding)
                if (flexible_sheet and (('Balance Sheet' in normalized_category.split('_')[0]
                                         and not re.search(r'{}'.format(regexes_dict['Cash Flow Statement Regex']),
                                                           title,
                                                           re.IGNORECASE))
                                        or ('Income Statement' in normalized_category.split('_')[0]
                                            and not re.search(r'{}'.format(regexes_dict['Cash Flow Statement Regex']),
                                                              title,
                                                              re.IGNORECASE))
                                        or ('Cash Flow Statement' in normalized_category.split('_')[0]
                                            and not re.search(
                                    r'{}|{}'.format(regexes_dict['Balance Sheet Regex'],
                                                    regexes_dict['Income Statement Regex']), title,
                                    re.IGNORECASE)))

                        # if you're not a flexible sheet, the sheet we're checking must match regex sheet
                        or ((not flexible_sheet)
                            and (('Balance Sheet' in normalized_category.split('_')[0] and re.search(
                                    regexes_dict['Balance Sheet Regex'], title, re.IGNORECASE))
                                 or ('Income Statement' in normalized_category.split('_')[0] and re.search(
                                            regexes_dict['Income Statement Regex'], title, re.IGNORECASE))
                                 or ('Cash Flow Statement' in normalized_category.split('_')[0] and re.search(
                                            regexes_dict['Cash Flow Statement Regex'], title, re.IGNORECASE))))):

                    # an entry is not flexible if it should match a hardcoded pattern
                    pattern_string = '^' + pattern_string
                    try:
                        re.search(pattern_string, title + '_' + scraped_name, re.IGNORECASE)
                    except:
                        pass
                    if ((not flexible_entry) and re.search(
                            pattern_string, title + '_' + scraped_name, re.IGNORECASE)):
                        # print('Found pattern match {} for scraped name {}'.format(pattern_string, scraped_name))

                        data_name = {'Iteration Count': str(iteration_count),
                                     'Hardcoded': True,
                                     'Table Title': title,
                                     'Scraped Name': scraped_name,
                                     'Whole Name': normalized_category,
                                     'Pattern String': pattern_string}

                        if math.isnan(master_dict[normalized_category]):
                            if year not in visited_data_names.keys():
                                visited_data_names[year] = []
                            pattern_matched = False
                            for el in visited_data_names[year]:  # if I already found it for this year, then skip
                                # thing is we want to prevent single pattern from matching many entries or an entry matching many patterns

                                if re.search(el['Pattern String'], scraped_name, re.IGNORECASE):
                                    # TODO: check following bug fix: you should find it this year, but the pattern should match same table title
                                    try:
                                        if re.search(el['Table Title'], title, re.IGNORECASE):
                                            pattern_matched = True
                                    except:
                                        traceback.print_exc()
                                        print('Unmatched Parenthesis:{}'.format(title))
                                        print('Unmatched Parenthesis:{}'.format(el['Table Title']))
                                    break
                            if not pattern_matched:
                                master_dict[normalized_category] = scraped_value
                                visited_data_names[year].append(data_name)  # that table takes ownership for the data
                            break

                    # otherwise it is flexible if it should just match the category (i.e. assets, other expenses...)

                    if flexible_entry:
                        if re.search('Operating Activities', scraped_name):
                            print('')
                        if found_and_done:
                            break

                        for cat in categories:
                            if found_and_done:
                                break
                            match = re.search(cat, normalized_category)
                            if match and re.search(cat, scraped_name):

                                # print(match.groups())
                                category = match.groups()[0]
                                already_have_it = False
                                for el in visited_data_names[year]:
                                    # make scraped name into a regex afterwards
                                    if re.search(el['Pattern String'], scraped_name, re.IGNORECASE):
                                        same_sheet = False
                                        for regex_title in [regexes_dict['Balance Sheet Regex'],
                                                            regexes_dict['Income Statement Regex'],
                                                            regexes_dict['Cash Flow Statement Regex']]:
                                            if re.search(regex_title, title, re.IGNORECASE) \
                                                    and re.search(regex_title, el['Table Title'], re.IGNORECASE):
                                                same_sheet = True

                                        if same_sheet:
                                            already_have_it = True

                                if not already_have_it:
                                    # TODO BIG CHANGE HERE
                                    name = titlecase(scraped_name.split('_')[-1])
                                    master_dict[category + '_' + name] = scraped_value
                                    name_regex = r''
                                    for word in scraped_name.split('_'):
                                        name_regex += r'(?=.*{}(?!.*[_]))'.format(word)
                                    visited_data_names[year].append({'Iteration Count': str(iteration_count),
                                                                     'Hardcoded': False,
                                                                     'Table Title': title,
                                                                     'Scraped Name': name,
                                                                     'Whole Name': category + '_' + name,
                                                                     'Pattern String': name_regex})

                                found_and_done = True
                                break
    return visited_data_names, master_dict


@implementer(main_scraper.FinancialStatementsParserInterface)
class HtmlParser:
    non_current, current = '((?=.*non[- ]?current)|(?=.*long-term))', '(?!.*non[- ]?current)(?=.*(current|short-term))'
    non_cash_flow, cash_flow = '(?!.*(Increase|Decrease|Change))', '(?=.*(Increase|Decrease|Change))'
    payments, proceeds = '(?=.*(Payments to Acquire|Purchases of|Payment)(?!.*[_:]))', '(?=.*(Proceeds from|Sales of)(?!.*[_:]))'
    operating_activities, financing_activities, investing_activities = '(?=.*(Operating|Operations))', '(?=.*Financing)', '(?=.*Investing)'

    financial_entries_regexes = {
        'Balance Sheet': {
            'Assets': {
                'Current Assets': {
                    'Cash and Short Term Investments': {
                        'Cash and Cash Equivalents': r'(?!.*marketable securities)(?=.*cash and cash equivalents(?!.*[_:]))(?!.*marketable securities){}'.format(
                            non_cash_flow),
                        'Marketable Securities Current': r'(?=.*(marketable securities|investment)|((?=.*Available[- ]for[- ]sale)(?=.*securities)))(?!.*cash and cash equivalents){}{}'.format(
                            current, non_cash_flow),
                        'Cash and Short Term Investments': r'(?=.*cash)(?=.*(marketable securities|short-term investments)){}'.format(
                            non_cash_flow)
                    },
                    'Accounts Receivable': {
                        # 'Gross Accounts Receivable': r'$^', # TODO
                        # 'Allowances for Doubtful Accounts': r'(?=.*Receivable)(?=.*allowances.*\$(\d+))',
                        # bug in this one (?=.*Receivable.*allowances).*(\$(\d+))*,
                        'Net Accounts Receivable': r'(?=.*Receivable)(?=.*(allowances|net|less)){}'.format(
                            non_cash_flow),
                    },
                    'Prepaid Expense, Current': r'((?=.*Prepaid expense)|(?=.*Prepaids)){}{}'.format(current,
                                                                                                     non_cash_flow),
                    'Inventory, Net': r'(?=.*Inventor(y|ies)(?!.*[_:])){}'.format(non_cash_flow),
                    'Income Taxes Receivable, Current': r'(?=.*Income taxes receivable){}'.format(non_cash_flow),
                    'Assets Held-for-sale': r'(?=.*Assets Held[- ]for[- ]sale){}'.format(non_cash_flow),
                    # taxes that have been already paid despite not yet having been incurred
                    'Deferred Tax Assets, Current': r'(?=.*(Deferred tax(es)? (assets)|(on income))|(Prepaid taxes)){}{}'.format(
                        current, non_cash_flow),
                    'Other Current Assets': r'$^',
                    'Total Current Assets': r'(?=.*Total(?!.*[_]))(?=.*Assets(?!.*[_:])){}{}'.format(current,
                                                                                                     non_cash_flow)
                },
                'Non Current Assets': {

                    'Marketable Securities Non Current': r'(?=.*marketable securities|investments){}{}'.format(
                        non_current,
                        non_cash_flow),
                    'Restricted Cash Non Current': r'(?=.*Restricted cash){}{}'.format(non_current, non_cash_flow),
                    'Property, Plant and Equipment': {
                        'Gross Property, Plant and Equipment': r'(?=.*(Property|Premise(s?)))(?=.*(Plant|Land))(?=.*Equipment)(?=.*(Gross|Before)){}'.format(
                            non_cash_flow),
                        'Accumulated Depreciation and Amortization': r'(?=.*((Property|Premise(s?))|Equipment))(?=.*accumulated depreciation(?!.*[_])){}'.format(
                            non_cash_flow),
                        'Property, Plant and Equipment, Net': r'(?=.*(Property|Premise(s?)))(?=.*(Plant|Land))?(?=.*Equipment)(?=.*(Net|Less|After)){}'.format(
                            non_cash_flow),
                    },
                    'Operating Lease Right-of-use Assets': r'(?=.*Operating lease right[- ]of[- ]use asset){}'.format(
                        non_cash_flow),
                    'Deferred Tax Assets Non Current': r'(?=.*deferred tax assets){}{}'.format(non_current,
                                                                                               non_cash_flow),
                    'Intangible Assets': {
                        'Goodwill': r'(?=.*Goodwill)(?!.*net)(?!.*Deferred Tax Liabilities){}'.format(non_cash_flow),
                        'Intangible Assets, Net (Excluding Goodwill)': r'(?=.*(other|net))(?=.*intangible assets(?!.*[_]))(?!.*(Amortization|Deferred Tax)){}'.format(
                            non_cash_flow),
                        'Total Intangible Assets': r'(?!.*other)(?!.*goodwill)(?!.*net)(?=.*intangible assets)(?!.*goodwill)(?!.*other)(?!.*net){}'.format(
                            non_cash_flow),
                    },
                    'Other Non Current Assets': r'(?=.*Other)(?=.*assets(?!.*[_])){}{}'.format(non_current,
                                                                                               non_cash_flow),
                    'Total Non Current Assets': r'(?=.*Total(?!.*[_]))(?=.*assets(?!.*[_])){}{}'.format(non_current,
                                                                                                        non_cash_flow),
                },
                'Total Assets': r'(?=.*Total Assets(?!.*[_:])){}'.format(non_cash_flow)
            },
            "Liabilities and Shareholders\' Equity": {
                'Liabilities': {
                    'Current Liabilities': {
                        # this is the short-term debt, i.e. the amount of a loan that is payable to the lender within one year.
                        'Long-term Debt, Current Maturities': r'(?=.*(Long-)?Term Debt|Loans and notes payable){}{}'.format(
                            current, non_cash_flow),
                        'Accounts Payable': r'(?=.*Accounts Payable){}'.format(non_cash_flow),
                        # always a current anyways
                        'Other Accounts Payable': r'(?=.*(Accounts|Partners) Payable){}'.format(non_cash_flow),
                        'Operating Lease, Liability, Current': r'(?=.*Liabilit(y|ies)(?!.*[_:]))(?=.*Operating lease){}{}'.format(
                            current, non_cash_flow),

                        'Employee-related Liabilities, Current': r'(?=.*Accrued Compensation){}{}'.format(current,
                                                                                                          non_cash_flow),
                        'Accrued Income Taxes': r'(?=.*Accrued)(?=.*Income)(?=.*Taxes){}{}'.format(current,
                                                                                                   non_cash_flow),
                        'Accrued Liabilities, Current': r'(?=.*Accrued)(?=.*(Expense|Liabilities)){}{}'.format(current,
                                                                                                               non_cash_flow),
                        'Deferred Revenue, Current': r'(?=.*(Deferred Revenue)|(Short-term unearned revenue)){}{}'.format(
                            current, non_cash_flow),
                        'Income Taxes Payable': r'((?=.*Income taxes payable)|(?=.*Short-term Income taxes)){}{}'.format(
                            current, non_cash_flow),
                        'Other Current Liabilities': r'(?=.*Other(?!.*[_:]))(?=.*liabilities(?!.*[_:])){}{}'.format(
                            current,
                            non_cash_flow),
                        'Total Current Liabilities': r'(?!.*Employee Related)(?!.*Other(?!.*[_:]))(?=.*Liabilities(?!.*[_:])){}{}'.format(
                            current, non_cash_flow),
                    },
                    'Non Current Liabilities': {
                        'Deferred Tax Liabilities': r'((?=.*Deferred(?=.*Income)(?=.*Taxes))|(?=.*Deferred tax liabilities)){}{}'.format(
                            non_current, non_cash_flow),
                        # this debt is due after one year in contrast to current maturities which are due within this year
                        'Long-term Debt, Noncurrent Maturities': r'(?=.*term debt)(?!.*within){}{}'.format(non_current,
                                                                                                           non_cash_flow),
                        'Operating Lease, Liability, Noncurrent': r'(?=.*Liabilit(y|ies)(?!.*[_:]))(?=.*Operating lease){}{}'.format(
                            non_current, non_cash_flow),
                        'Liability, Defined Benefit Plan, Noncurrent': r'(?=.*Employee related obligations){}{}'.format(
                            non_current, non_cash_flow),
                        'Accrued Income Taxes, Noncurrent': r'(Long-term ((income taxes)|(taxes payable))){}{}'.format(
                            non_current, non_cash_flow),
                        'Deferred Revenue, Noncurrent': r'(?=.*Deferred Revenue){}{}'.format(non_current,
                                                                                             non_cash_flow),
                        'Long-Term Unearned Revenue': r'(?=.*unearned)(?=.*revenue){}{}'.format(non_current,
                                                                                                non_cash_flow),
                        'Other Liabilities, Noncurrent': r'(?=.*Other(?!.*[_:]))(?=.*liabilities(?!.*[_:])){}{}'.format(
                            non_current, non_cash_flow),
                        'Total Non Current Liabilities': r'$^'
                    },
                    'Total Liabilities': r'(((?=.*Total Liabilities)(?!.*Equity(?!.*[_]))(?!.*Other(?!.*[_])))|(^_Liabilities$)){}'.format(
                        non_cash_flow)
                    # sometimes at the bottom there are two tabs, our code can't catch it i.e. Other non-current liabilities then tab Total non-current liabilities then tab Total liabilities
                },
                "Shareholders' Equity": {
                    'Preferred Stock, Value, Issued': r'(?=.*Preferred (stock|shares))(?!.*treasury)',
                    'Common Stock and Additional Paid in Capital': {
                        'Common Stock, Value, Issued': r'(?=.*Common (stock|shares)(?!.*[_]))(?!.*treasury)(?!.*additional paid[- ]in capital(?!.*[_]))(?!.*(beginning|change))',
                        'Additional Paid in Capital': r'(?=.*additional paid[- ]in capital(?!.*[_]))(?!.*Common stock(?!.*[_]))',
                        'Common Stocks, Including Additional Paid in Capital': r'(?=.*Common stock(?!.*[_]))(?=.*additional paid[- ]in capital(?!.*[_]))',
                        'Weighted Average Number of Shares Outstanding, Basic': r'(?=.*shares)(?=.*basic)(?!.*earnings(?!.*[_]))',
                        'Weighted Average Number Diluted Shares Outstanding Adjustment': r'(?=.*dilutive)(?=.*effect(?!.*[_:]))',
                        'Weighted Average Number of Shares Outstanding, Diluted': r'(?=.*shares)(?=.*diluted)(?!.*earnings(?!.*[_]))',
                    },

                    'Treasury Stock, Value': r'(?=.*Treasury stock)',
                    'Retained Earnings (Accumulated Deficit)': r'(?=.*Accumulated deficit)|(Retained earnings)(?!.*Beginning)',
                    'Accumulated Other Comprehensive Income (Loss)': r'(?=.*Accumulated other comprehensive (income|loss)(?!.*[_]))(?!.*Foreign Currency)(?!.*Beginning)',
                    'Deferred Stock Compensation': r'(?=.*Deferred stock compensation)',
                    'Stockholders\' Equity Attributable to Parent': r'(?=.*Total.*(shareholders|stockholders)[’\'] equity)(?!.*Liabilities(?!.*[_]))',
                    'Minority Interest': r'(?=.*Noncontrolling interest)',
                    'Stockholders\' Equity, Including Portion Attributable to Noncontrolling Interest': '(?!.*Before)(?=.*Noncontrolling interest)(?=.*Equity(?!.*[_]))(?!.*Liabilities(?!.*[_]))'
                },
                'Total Liabilities and Shareholders\' Equity': r'(?=.*Liabilities(?!.*[_:]))(?=.*Equity(?!.*[_:]))'
            },
        },
        'Income Statement': {
            'Revenues': {
                'Service Sales': '(?=.*Sales)(?=.*Service(?!.*[_:]))(?!.*Cost)(?!.*Other(?!.*[_:]))',
                'Product Sales': '(?=.*Sales)(?=.*Product(?!.*[_:]))(?!.*Cost)(?!.*Other(?!.*[_:]))',
                'Net Sales': r'(?=.*(Net sales|Revenue)(?!.*[_:]))(?!.*Cost)'
            },
            'Cost of Products': r'(?=.*Cost of Products)',
            'Cost of Services': r'(?=.*Cost of Services)',
            'Cost of Goods and Services Sold': r'(?=.*Cost of (revenue|sales)(?!.*[_:]))',
            'Gross Margin': r'$^',
            'Provision for Loan, Lease, and Other Losses': r'(?=.*Provision for credit losses)',
            'Operating Expenses': {
                'Research and Development Expense': r'(?=.*(Research|Technology) and development)',
                'Selling, General and Administrative': {
                    'Marketing Expense': r'(?!.*(Sales|selling))(?=.*Marketing)',
                    'Selling and Marketing Expense': r'(?=.*(Sales|Selling))(?=.*Marketing)',
                    'General and Administrative Expense': r'(?=.*General)(?=.*Administrative)(?!.*Selling)',
                    'Selling, General and Administrative Expense': r'(?=.*Selling, general and administrative)'
                },
                'Other Operating Expenses': r'$^',  # TODO
                'EBITDA': r'$^',
                'Total Operating Expenses': r'(?=.*Total operating expenses)'
            },
            'Costs and Expenses': r'(?=.*Costs and Expenses)',
            'Operating Income (Loss) / EBIT': r'(?=.*income(?!.*[_]))(?=.*operati(ng|ons)(?!.*[_]))(?!.*investments)',
            'Other (Non-Operating) Income (Expense)': {
                'Interest Income': r'(?!.*(Deferred|Finance Lease|Tax))(?=.*Interest(?!.*[_:]))(?!.*dividend(?!.*[_:]))(?=.*income(?!.*[_:]))(?!.*net(?!.*[_:]))',
                'Interest and Dividend Income': r'(?!.*(Deferred|Finance Lease|Tax))(?=.*Interest(?!.*[_:]))(?=.*dividend(?!.*[_:]))(?=.*income(?!.*[_:]))(?!.*net(?!.*[_:]))',
                'Interest Expense': r'(?!.*(Deferred|Finance Lease|Tax))(?=.*Interest expense(?!.*[_:]))(?!.*net(?!.*[_:]))',
                'Interest Income (Expense), Net': r'(?!.*(Deferred|Finance Lease|Tax))(?=.*Interest income(?!.*[_:]))(?=.*net(?!.*[_:]))',
                'Foreign Currency Transaction Gain (Loss)': r'(?=.*Foreign Currency Transaction Gain)',
                'Other Nonoperating Income (Expense)': '$^',
                # below is for 'Interest and other income, net' and 'Total other income/(expense), net'
                'Non-Operating Income (Expense)': r'(?!.*(Deferred|Finance Lease|Tax))(?=.*(other|(non-?operating)))(?=.*income(?!.*[_:]))'
            },

            'Income (Loss) before Income Taxes, Noncontrolling Interest': r'(((?=.*Income)(?=.*Before)(?=.*Provision for)?(?=.*(income )?taxes))|Pre-tax earnings)(?!.*(Domestic|Extraordinary|Foreign))',
            'Income Tax Expense (Benefit)': r'(((?=.*Provision for)(?=.*(income )?taxes))|(?=.*Income Tax Expense))(?!.*Before)',
            'Net Income (Loss), Including Portion Attributable to Noncontrolling Interest': r'(?=.*(Net income|earnings))(?=.*(including|before))(?=.*non-?controlling interest)',
            'Net Income (Loss) Attributable to Noncontrolling (Minority) Interest': r'(?=.*(Net income|earnings))(?=.*(attributable|allocated|applicable|available))(?=.*non-?controlling interest)',
            'Net Income (Loss) Attributable to Parent': r'(?=.*Net (income|earnings|loss)$)|(^_Net Income Loss$)',
            'Undistributed Earnings (Loss) Allocated to Participating Securities, Basic': r'(?=.*(Net income|earnings))(?=.*(attributable|allocated|applicable|available))(?=.*participating securities)',
            'Preferred Stock Dividends': r'(?=.*Preferred stock dividends)',
            'Net Income (Loss)': r'(?=.*(Net income|earnings))(?=.*(attributable|allocated|applicable|available))(?=.*common stockholders)?(?!.*non-?controlling interest)',
            'Earnings Per Share, Basic': '(?=.*Earnings per share)(?=.*basic)',
            'Earnings Per Share, Diluted': '(?=.*Earnings per share)(?=.*diluted)',

        },
        'Cash Flow Statement': {
            'Cash, Cash Equivalents, Restricted Cash and Restricted Cash Equivalents, Beginning Balance':
                '(?=.*Cash, cash equivalents,? and restricted cash(?!.*[_:]))(?=.*beginning(?!.*[_:]))',
            'Operating Activities': {
                'Net Income (Loss) Attributable to Parent': r'((?=.*Operating activities)(?=.*Net income(?!.*[_:]))|(?=.*Net Income Loss))',
                'Adjustments to Reconcile Net Income': {
                    'Depreciation, Depletion and Amortization': r'(?=.*depreciation(?!.*[_:]))(?=.*amortization(?!.*[_:]))(?!.*accumulated)',
                    'Share-based Payment Arrangement, Noncash Expense': r'(?=.*Share[- ]based compensation expense(?!.*[_:]))',
                    'Deferred Income Tax Expense (Benefit)': r'(?=.*Deferred income tax(?!.*[_:]))',
                    'Other Noncash Income (Expense)': r'({}(?=.*Other(?!.*[_:]))(?=.*Income))|(^_Other Noncash Income Expense$)'.format(
                        operating_activities)
                },
                'Change in Assets and Liabilities': {
                    'Increase (Decrease) in Accounts Receivable': r'({}|{})(?=.*Accounts receivable(?!.*[_:]))'.format(
                        cash_flow, operating_activities),
                    'Increase (Decrease) in Inventories': r'({}|{})(?=.*Inventories(?!.*[_:]))'.format(cash_flow,
                                                                                                       operating_activities),
                    'Increase (Decrease) in Other Receivables': r'({}|{})(?=.*Vendor non-trade receivables(?!.*[_:]))'.format(
                        cash_flow, operating_activities),
                    'Increase (Decrease) in Prepaid Expense and Other Assets': r'({}|{})(?=.*Prepaid( Deferred)? expense(?!.*[_:]))(?=.*other( current)? assets(?!.*[_:]))'.format(
                        cash_flow, operating_activities),
                    'Increase (Decrease) in Other Operating Assets': r'({}|{})(?=.*Other( operating)? assets(?!.*[_:]))(?!.*Prepaid)'.format(
                        cash_flow, operating_activities),
                    'Increase (Decrease) in Accounts Payable': r'({}|{})(?=.*Accounts payable(?!.*[_:]))'.format(
                        cash_flow,
                        operating_activities),
                    'Increase (Decrease) in Other Accounts Payable': r'({}|{})(?=.*(Partners|Other)( accounts)? payable(?!.*[_:]))'.format(
                        cash_flow, operating_activities),
                    'Increase (Decrease) in Accrued Liabilities': r'({}|{})(?=.*Accrued (expenses|liabilities)(?!.*[_:]))'.format(
                        cash_flow, operating_activities),
                    'Increase (Decrease) in Deferred Revenue, Liability': r'({}|{})(?=.*(Deferred revenue|Contract with Customer)(?!.*[_:]))'.format(
                        cash_flow, operating_activities),
                    'Increase (Decrease) in Other Operating Liabilities': '({}|{})(?=.*Other(( non-?current)|(operating))? liabilities(?!.*[_:]))'.format(
                        cash_flow, operating_activities),
                },
                'Net Cash Provided by (Used in) Operating Activities': r'(?=.*Operating activities(?!.*[_:]))(?=.*cash(?!.*[_:]))'
            },
            'Investing Activities': {
                'Payments to Acquire Marketable Securities, Available-for-sale': r'({}|{})(?=.*(marketable|debt|available[- ]for[- ]sale) securities(?!.*[_:]))'.format(
                    investing_activities, payments),
                'Proceeds from Maturities, Prepayments and Calls of Debt Securities, Available-for-sale': r'({}|{})(?=.*(marketable|debt|available[- ]for[- ]sale) securities(?!.*[_:]))(?=.*maturities)'.format(
                    investing_activities, proceeds),
                'Proceeds from Sale of Debt Securities, Available-for-sale': r'({}|{})(?=.*(marketable|debt|available[- ]for[- ]sale) securities(?!.*[_:]))'.format(
                    investing_activities, proceeds),
                'Payments to Acquire Property, Plant, and Equipment': '({}|{})(?=.*property(?!.*[_:]))(?=.*equipment(?!.*[_:]))'.format(
                    investing_activities, payments),
                'Payments to Acquire Businesses, Net of Cash Acquired': '({}|{})(?=.*business(?!.*[_:]))(?=.*(acquisition|acquire)(?!.*[_:]))'.format(
                    investing_activities, payments),
                'Payments to Acquire Other Investments': '({}|{})(?=.*non-marketable securities(?!.*[_:]))'.format(
                    investing_activities, payments),
                'Proceeds from Sale and Maturity of Other Investments': '({}|{})(?=.*non-marketable securities(?!.*[_:]))'.format(
                    investing_activities, proceeds),
                'Payments for (Proceeds from) Other Investing Activities': '({}|{}|{})(?=.*Other(?!.*[_:]))(?=.*Investing activities(?!.*[_:]))'.format(
                    investing_activities, proceeds, payments),
                'Net Cash Provided by (Used in) Investing Activities': r'(?=.*Investing activities(?!.*[_:]))(?=.*cash(?!.*[_:]))'
            },
            'Financing Activities': {
                'Proceeds from Issuance of Common Stock': r'({}|{})(?=.*issuance of common stock(?!.*[_:]))'.format(
                    proceeds, financing_activities),
                'Payment, Tax Withholding, Share-based Payment Arrangement': '({}|{})(?=.*tax(?!.*[_:]))(?=.*share(?!.*[_:]))(?=.*(compensation|settlement|arrangement))'.format(
                    payments, financing_activities),
                'Payments of Dividends': r'({}|{})(?=.*dividends(?!.*[_:]))'.format(payments, financing_activities),
                'Payments for Repurchase of Common Stock': '({}|{})(?=.*Repurchase(?!.*[_:]))(?=.*common stock(?!.*[_:]))'.format(
                    payments, financing_activities),
                'Proceeds from Issuance of Long-term Debt': '({}|{})(?=.*issuance of (long[- ])?term debt(?!.*[_:]))'.format(
                    proceeds, financing_activities),
                'Repayments of Long-term Debt': '({}|{})(?=.*(long[- ])?term debt(?!.*[_:]))'.format(payments,
                                                                                                     financing_activities),
                'Finance Lease, Principal Payments': '({}|{})(?=.*finance lease(?!.*[_:]))'.format(payments,
                                                                                                   financing_activities),
                'Proceeds from (Repayments of) Bank Overdrafts': '({}|{}|{})(?=.*overdraft(?!.*[_:]))'.format(proceeds,
                                                                                                              payments,
                                                                                                              financing_activities),
                'Proceeds from (Repayments of) Commercial Paper': '({}|{}|{})(?=.*Commercial paper(?!.*[_:]))'.format(
                    proceeds, payments, financing_activities),
                'Proceeds from (Payments for) Other Financing Activities': '({}|{}|{})(?=.*Financing activities(?!.*[_:]))(?=.*Other(?!.*[_:]))'.format(
                    proceeds, payments, financing_activities),
                'Net Cash Provided by (Used in) Financing Activities': r'(?=.*Financing activities(?!.*[_:]))(?=.*(net )?cash(?!.*[_:]))'
            },
            'Effect of Exchange Rate on Cash, Cash Equivalents, Restricted Cash and Restricted Cash Equivalents': r'(?=.*Effect Of Exchange Rate On Cash Cash Equivalents Restricted Cash And Restricted Cash Equivalents)',
            'Cash, Cash Equivalents, Restricted Cash and Restricted Cash Equivalents, Period Increase (Decrease), Including Exchange Rate Effect':
                '(?=.*(Increase|Decrease))(?=.*cash(?!.*[_:]))(?=.*cash equivalents(?!.*[_:]))(?=.*restricted cash(?!.*[_:]))',
            # we are hardcoding the Ending balance to be Cash, Cash Equivalents, Restricted Cash and Restricted Cash Equivalents in XBRL because we filtered the beginning balance (which can be taken from previous year)
            'Cash, Cash Equivalents, Restricted Cash and Restricted Cash Equivalents, Ending Balance':
                '(?!.*(Increase|Decrease))(?=.*Cash, cash equivalents,? and restricted cash(?!.*[_:]))(?=.*end(?!.*[_:]))|(^_Cash Cash Equivalents Restricted Cash And Restricted Cash Equivalents$)',
            'Supplemental': {}
        }
    }
    regex_patterns = {'Financial Entries Regex': financial_entries_regexes,
                      'Cash Flow Statement Regex': r'(Consolidated(.*?)cash flow)|(cash( ?)flow(s?) statement(s?))',
                      'Income Statement Regex': r'(Consolidated(.*?)statements of (income|earnings))|(income statement)|(CONSOLIDATED STATEMENTS OF OPERATIONS)',
                      'Balance Sheet Regex': r'(balance ?sheet|condition)'}

    def load_data_source(self, ticker: str) -> dict:
        cik = get_company_cik(ticker)
        doc_links_yearly = get_filings_urls_first_layer(cik, '10-K')
        doc_links_quarterly = get_filings_urls_first_layer(cik, '10-Q')
        filings_dictio_yearly = get_filings_urls_second_layer(doc_links_yearly)
        filings_dictio_quarterly = get_filings_urls_second_layer(doc_links_quarterly)
        return {'Yearly': filings_dictio_yearly, 'Quarterly': filings_dictio_quarterly}

    def scrape_tables(self, url: str, filing_date: datetime.datetime, filing_type: str) -> dict:
        global only_year
        response = requests.get(url)
        html = response.text
        soup = BeautifulSoup(html, 'lxml')
        '''BeautifulSoup Usage
        html = urllib2.urlopen(url).read()
        bs = BeautifulSoup(html)
        table = bs.find(lambda tag: tag.name=='table' and tag.has_attr('id') and tag['id']=="Table1") 
        rows = table.findAll(lambda tag: tag.name=='tr')'''
        all_in_one_dict = {'Yearly': {}, 'Quarterly': {}, '6 Months': {}, '9 Months': {}}

        month_abc_regex = r'Jan(?=uary)?|Feb(?=ruary)?|Mar(?=ch)?|Apr(?=il)?|May|Jun(?=e)?|Jul(?=y)?|Aug(?=ust)?|Sep(?=tember)?|Oct(?=ober)?|Nov(?=ember)?|Dec(?=ember)?'
        month_no_regex = r'1[0-2]|0?[1-9]'
        day_no_regex = r'3[01]|[12][0-9]|0?[1-9]'
        day_abc_regex = r'Mon(day)?|Tue(sday)?|Wed(nesday)?|Thur(sday)?|Fri(day)?|Sat(urday)?|Sun(day)?'
        year_regex_two = r'[0-9]{2}'
        year_regex_four = r'\d{4}'

        month_slash_day_slash_year_regex = r'((?:1[0-2]|0?[1-9])\/(?:3[01]|[12][0-9]|0?[1-9])\/(?:[0-9]{2})?[0-9]{2})'
        month_day_year_regex = r'({})\s+({}),?\s+({})'.format(month_abc_regex, day_no_regex, year_regex_two)
        flexible_month_day_year_regex = r'({}).*?({}).*?({})'.format(month_abc_regex, day_no_regex,
                                                                     year_regex_four)
        only_year_regex = r'^({})$'.format(year_regex_four)
        date_formats = r"(((1[0-2]|0?[1-9])\/(3[01]|[12][0-9]|0?[1-9])\/(?:[0-9]{2})?[0-9]{2})|((Jan(uary)?|Feb(ruary)?|Mar(ch)?|Apr(il)?|May|Jun(e)?|Jul(y)?|Aug(ust)?|Sep(tember)?|Oct(ober)?|Nov(ember)?|Dec(ember)?)\s+\d{1,2},\s+\d{4}))"

        if 'Inline XBRL Viewer' in soup.text:
            driver = webdriver.Chrome(ChromeDriverManager().install())
            driver.get(url)
            sleep(2)
            html = driver.page_source

            soup = BeautifulSoup(html, 'lxml')

        for table in soup.findAll('table'):
            columns = []
            dates = []
            header_found = False
            indented_list = []
            rows = table.find_all('tr')
            table_title, table_multiplier = find_table_meta(table=table)
            if table_multiplier == 'percentage':
                continue
            elif table_title == 'No Table Title':
                table_multiplier = 1

            first_level = ''  # that's for whether the table is Yearly of Quarterly
            for index, row in enumerate(rows):

                reg_row = [ele.text for ele in row.find_all(lambda tag: tag.name == 'td' or tag.name == 'th')]
                reg_row = [unicodedata.normalize("NFKD", x).replace('\u200b', '') for x in reg_row]
                current_left_margin = find_left_margin(reg_row, row.findAll('td')[0])
                reg_row = [x.strip() for x in reg_row]
                reg_row[0] = reg_row[0].replace(':', '').replace('\n', ' ') if len(reg_row) > 0 else reg_row[0]

                # first, we want to construct the column header of our dable. We skip
                # - the empty rows i.e. those that have no table data 'td' (or those for which the td's are empty)
                # [length 0]
                # - the descriptive rows (i.e. 'dollars in millions', 'fiscal year', etc.) [length 1]
                # We only keep the useful headers i.e. those that include 'Month', 'Quarter', 'Year', a date...

                if not header_found:
                    reg_row = list(filter(lambda x: x != "", reg_row))
                    max_date_index = 0
                    # if 'th' tag found or table data with bold, then found a potential header for the table
                    if len(row.find_all('th')) != 0 or is_bold(row):

                        # here, as a first step, we're crossing the elements of first rows (i.e.
                        # if there is June 30 in one row then 2018 and 2019 in other row, the columns
                        # become June 30 2018 and June 30 2019
                        if len(columns) == 0:
                            columns = reg_row
                        else:
                            # example: the same row has June 30     2018    2019
                            if len(reg_row) > 2 and not re.search(year_regex_four, reg_row[0]) \
                                    and not re.search(month_abc_regex, reg_row[1]):
                                for i in range(1, len(reg_row)):
                                    reg_row[i] = reg_row[0] + reg_row[i]
                                reg_row = reg_row[1:]

                            if len(columns) < len(reg_row):
                                ratio = int(len(reg_row) / len(columns))
                                col_len = len(columns)
                                for col_idx in range(col_len):
                                    copy = []
                                    for r in range(ratio):
                                        formatted_column = " ".join((columns[0] + ' ' + reg_row[0]).split())
                                        copy.append(formatted_column)
                                        reg_row.pop(0)
                                    columns.extend(copy)
                                    columns.pop(0)
                            else:
                                for r in reg_row:
                                    for col in range(len(columns)):
                                        columns[col] = columns[col] + ' ' + r

                        format_match = False
                        dates = []
                        only_year = False

                        # title can hold things like 'Years ended December 31', so extract date and add to columns
                        match_in_title = re.search(r'({}).*?({})'.format(month_abc_regex, day_no_regex), table_title)

                        for col in columns:
                            # Filing for June 30, 2019:
                            # Fiscal year 2019  September   December    March   June --> september and december are 2018

                            if match_in_title:
                                col = ' '.join(match_in_title.groups()) + ' ' + col

                            match = re.search(flexible_month_day_year_regex, col) or re.search(
                                month_slash_day_slash_year_regex, col) or re.search(only_year_regex, col)
                            if match:
                                for dts in ['%b %d %Y', '%m/%d/%y']:
                                    try:
                                        # print(match.groups())
                                        col_formatted_date = datetime.datetime.strptime(' '.join(match.groups()),
                                                                                        dts).date()
                                        col_formatted_date = datetime.datetime(col_formatted_date.year,
                                                                               col_formatted_date.month,
                                                                               col_formatted_date.day)
                                        # ascending = True if dates[0] < dates[1] else False
                                        if col_formatted_date > filing_date:
                                            col_formatted_date = datetime.datetime(col_formatted_date.year - 1,
                                                                                   col_formatted_date.month,
                                                                                   col_formatted_date.day)
                                        dates.append(col_formatted_date)
                                        format_match = True
                                        break
                                    except:
                                        pass

                        # relevant_indexes = [i for i, x in enumerate(columns) if not re.search(r'Six|Nine|Change', x, re.IGNORECASE)]
                        # if only_year:
                        #     try:
                        #         relevant_indexes = columns.index(str(filing_date.year))
                        #     except:
                        #         print('NOT IN LISTTTTTT {}'.format(table_title))
                        # print(relevant_indexes)
                        if len(columns) > 0 and format_match:
                            header_found = True
                            header_index = index
                            # first_bolded_index = next(i for i, v in enumerate(indented_list) if v[2])
                    else:
                        continue

                elif header_found and len(reg_row) > 0:

                    indices = [i for i, x in enumerate(reg_row) if re.search(r'\d', x)]
                    reg_row = [reg_row[0]] + [re.sub(r'(^-$)|(^—$)', '0', x) for x in reg_row[1:]]

                    reg_row = [reg_row[0]] + [re.sub(r'\(', '-', x) for x in reg_row[1:]]
                    reg_row = [reg_row[0]] + [re.sub("[^0-9-]", "", r) for r in reg_row[1:]]
                    reg_row = [reg_row[0]] + [re.sub("^-$", "", r) for r in reg_row[1:]]  # for NOT the minus sign
                    reg_row = [reg_row[0]] + [re.sub(r',', '', x) for x in reg_row[1:]]
                    reg_row = list(filter(lambda x: x != "", reg_row))

                    if len(''.join(reg_row).strip()) == 0:
                        continue

                    while len(indented_list) > 0 and current_left_margin <= indented_list[-1][0]:

                        if current_left_margin == indented_list[-1][0]:
                            # if last element of list is bold
                            if indented_list[-1][2] or indented_list[-1][1].isupper():
                                if is_bold(row, alltext=True) or row.text.isupper():  # if current row is bold
                                    # remove that last element of list (new bold overrides old bold)
                                    indented_list.pop()
                                    break  # and stop popping
                                else:
                                    break  # otherwise, just subentry so don't pop
                        indented_list.pop()  # pop (because the most recent category is the element itself so we want to replace it)

                    try:
                        # This is an edge case. Typically, companies would add an extra unnecessary tab at the end of
                        # a category. For example, in balance sheets, it will have
                        # Current Assets
                        #        Cash and Cash Equivalents
                        #        ...
                        #        Other Current Assets
                        #            Total Current Assets
                        # So Total Current Assets shouldn't be under Other Current Assets category, so we pop
                        for i in range(len(indented_list)):
                            if re.search(r'^{}$'.format(reg_row[0]
                                                                .split('Total ')[-1]
                                                                .replace('\(', '').replace('\)', '')),  # current entry
                                         indented_list[-i][1].replace('\(', '').replace('\)', ''),  # last category
                                         re.IGNORECASE):
                                indented_list.pop()
                    except Exception:
                        traceback.print_exc()
                        print(reg_row)

                    indented_list.append((current_left_margin, reg_row[0], is_bold(row, alltext=True)))
                    current_category = '_'.join([x[1] for x in indented_list])

                    if len(reg_row) > 1:  # not category column:
                        try:
                            for index, col in enumerate(columns):

                                if re.search(r'Three|Quarter', table_title + col, re.IGNORECASE):
                                    first_level = 'Quarterly'
                                elif re.search(r'Six', table_title + col, re.IGNORECASE):
                                    first_level = '6 Months'
                                elif re.search(r'Nine', table_title + col, re.IGNORECASE):
                                    first_level = '9 Months'
                                elif re.search(r'Change', table_title + col, re.IGNORECASE):
                                    continue
                                else:
                                    first_level = filing_type

                                for date in dates:
                                    if date not in all_in_one_dict[first_level].keys():
                                        all_in_one_dict[first_level][date] = {}
                                    if table_title not in all_in_one_dict[first_level][date].keys():
                                        all_in_one_dict[first_level][date][table_title] = {}
                                if only_year:
                                    # index = columns.index(str(filing_date.year))
                                    index = dates.index(filing_date)
                                if current_category not \
                                        in all_in_one_dict[first_level][dates[index]][table_title].keys():
                                    all_in_one_dict[first_level][dates[index]][table_title][current_category] = float(
                                        re.sub('^$', '0', reg_row[index + 1]))  # * table_multiplier
                                    # pprint(all_in_one_dict[first_level][dates[index]][table_title])
                                if only_year:
                                    break
                        except:
                            # print('EXCEPTION INDEX! for title {} and row {}, with col {}'.format(table_title, reg_row, col))
                            pass

        return all_in_one_dict

    def normalize_tables(self, regex_patterns, filing_date, input_dict, visited_data_names) -> (dict, dict):
        # pprint(input_dict)
        master_dict = {}

        for normalized_category, pattern_string in data_preparation_helpers.flatten_dict(
                regex_patterns['Financial Entries Regex']).items():
            master_dict[normalized_category] = np.nan

        visited_data_names, master_dict = normalization_iteration(regexes_dict=regex_patterns, iteration_count=0,
                                                                  input_dict=input_dict, master_dict=master_dict,
                                                                  visited_data_names=visited_data_names,
                                                                  year=filing_date, flexible_sheet=False,
                                                                  flexible_entry=False)

        # then we want to give priority to the elements that strictly match our regex patterns,
        # but not in the consolidated financial statements
        visited_data_names, master_dict = normalization_iteration(regexes_dict=regex_patterns, iteration_count=1,
                                                                  input_dict=input_dict, master_dict=master_dict,
                                                                  visited_data_names=visited_data_names,
                                                                  year=filing_date, flexible_sheet=True,
                                                                  flexible_entry=False)

        # finally, we want to give priority to the rest of the elements (i.e. those that do not
        # match our regex patterns) that are in the consolidated financial statements
        # TODO bug: duplicate entries despite pattern match check
        # TODO When creating new patterns in final normalization, remove what's inside parenthesis (better matching for other reports)
        visited_data_names, master_dict = normalization_iteration(regexes_dict=regex_patterns, iteration_count=2,
                                                                  input_dict=input_dict, master_dict=master_dict,
                                                                  visited_data_names=visited_data_names,
                                                                  year=filing_date, flexible_sheet=False,
                                                                  flexible_entry=True)
        # pprint(master_dict)
        # TODO Final Standardization, Fill in Differences!

        if np.isnan(master_dict["Balance Sheet_Liabilities and Shareholders' Equity_Liabilities_Total Liabilities"]):
            shareholders_equity_incl_minority = master_dict[
                "Balance Sheet_Liabilities and Shareholders' Equity_Shareholders' Equity_Stockholders' Equity, Including Portion Attributable to Noncontrolling Interest"]
            shareholders_equity = master_dict[
                "Balance Sheet_Liabilities and Shareholders' Equity_Shareholders' Equity_Stockholders' Equity Attributable to Parent"]
            master_dict["Balance Sheet_Liabilities and Shareholders' Equity_Liabilities_Total Liabilities"] = \
                master_dict['Balance Sheet_Assets_Total Assets'] - (shareholders_equity_incl_minority if not np.isnan(
                    shareholders_equity_incl_minority) else shareholders_equity)

        return visited_data_names, data_preparation_helpers.flatten_dict(
            data_preparation_helpers.unflatten(master_dict))


if __name__ == '__main__':
    testing = {}
    htmlParser = HtmlParser()
    financials_dictio = {}
    for sheet_period, sheet_dict in testing.items():
        visited_data_names = {}
        if sheet_period not in financials_dictio.keys():
            financials_dictio[sheet_period] = {}
        for year, title_dict in sheet_dict.items():
            if year not in financials_dictio[sheet_period].keys():
                financials_dictio[sheet_period][year] = {}
            visited_data_names, financials_dictio[sheet_period][year] = \
                htmlParser.normalize_tables(regex_patterns=HtmlParser.regex_patterns, filing_date=year,
                                            input_dict=title_dict, visited_data_names=visited_data_names)
        pprint(visited_data_names)
    pprint(financials_dictio)
