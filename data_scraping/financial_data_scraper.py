import collections
import math
import os
import re
import traceback
import urllib.request
import zipfile
from datetime import datetime, timedelta
from time import sleep
import numpy as np
import pandas as pd
import requests
import unicodedata
from bs4 import BeautifulSoup, NavigableString
import data_scraping.regex_patterns as fin_reg
import data_scraping.unit_tests as test
import pandas_datareader.data as web
import data_scraping.excel_helpers as excel
from pprint import pprint
import tabula
import ta
import config
from titlecase import titlecase
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from typing import Dict, List, Union

'''
Beautiful BeautifulSoup Usage

html = urllib2.urlopen(url).read()
bs = BeautifulSoup(html)
table = bs.find(lambda tag: tag.name=='table' and tag.has_attr('id') and tag['id']=="Table1") 
rows = table.findAll(lambda tag: tag.name=='tr')
'''


# TODO: Save filings urls in txt files
# TODO: Check if normalization round three can take shares outstanding from income statements
# TODO: Make this into an interface
# TODO: Add ?!.*_ trick in regexes

# class ParserInterface:
#     def load_financial_statements_links(self, ticker: str) -> Dict[str, List[(str, str)]]:
#         pass
#
#     def parse_tables(self, link: str) -> Dict[str, Dict[str, float]]:
#         pass
#
#     def standardize_tables(self):
#         pass


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


def get_filings_urls_second_layer(filing_type, doc_links):
    links_dictionary = {
        'XBRL Links': [],  # for new submissions
        'HTML Links': [],  # if no XML, then we put HTML (for older submissions).
        'TXT Links': []  # if no HTML, then we put TXT (for even older submissions)
    }

    for doc_link in doc_links:
        # Obtain HTML for document page
        doc_resp = requests.get(doc_link).text
        # Find the XBRL link
        soup = BeautifulSoup(doc_resp, 'html.parser')
        # first, find period of report
        head_divs = soup.find_all('div', class_='infoHead')
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
        no_xml_link = True
        if table_tag is not None:
            rows = table_tag.find_all('tr')
            for row_index, row in enumerate(rows[1:]):
                cells = row.find_all('td')
                link = 'https://www.sec.gov' + cells[2].a['href']
                if 'XML' in cells[3].text or 'INS' in cells[3].text:
                    links_dictionary['XBRL Links'].append((period_of_report, link))
                    no_xml_link = False

        # if no XML document found, try finding html documents
        no_html_link = True
        no_xml_link = True  # this is to include XML links as HTMLs to test HTML scraping, so remove when done with xml
        if no_xml_link:
            table_tag = soup.find('table', class_='tableFile', summary='Document Format Files')
            rows = table_tag.find_all('tr')
            for row in rows[1:]:
                cells = row.find_all('td')
                link = 'https://www.sec.gov' + cells[2].a['href']
                if 'htm' in cells[2].text and cells[3].text == filing_type:
                    links_dictionary['HTML Links'].append((period_of_report, link))
                    no_html_link = False

        # if no HTML document found, then get the txt
        if no_html_link and no_xml_link:
            table_tag = soup.find('table', class_='tableFile', summary='Document Format Files')
            rows = table_tag.find_all('tr')
            for row in rows[1:]:
                cells = row.find_all('td')
                link = 'https://www.sec.gov' + cells[2].a['href']
                if cells[1].text == 'Complete submission text file':
                    links_dictionary['TXT Links'].append((period_of_report, link))

    return links_dictionary


def is_bold(row, alltext=False):
    soup = BeautifulSoup(str(row), features='html.parser')
    bolded_row_text = soup.find_all(
        lambda tag: tag.name == 'b' or (tag.has_attr('style') and 'bold' in str(tag['style'])))
    bolded_row_text = ' '.join([a.text for a in bolded_row_text]).strip()
    row_text = row.text.strip()
    if alltext:
        return len(bolded_row_text) > 0 and len(bolded_row_text) == len(row_text)
    else:
        return len(bolded_row_text) > 0


def is_italic(row):
    soup = BeautifulSoup(str(row), features='html.parser')
    italic = soup.find_all(lambda tag: tag.name == 'i')
    return len(italic) > 0


def is_centered(row):
    soup = BeautifulSoup(str(row), features='html.parser')
    return len(soup.find_all(lambda tag: tag.name != 'table' and (
            (tag.has_attr('align') and 'center' in str(tag['align'])) or tag.has_attr(
        'style') and 'text-align:center' in str(tag['style'])))) > 0


def find_left_margin(reg_row, td):
    pattern_match = re.findall('(margin-left|padding-left):(\d+)', str(td))
    c1 = sum([float(m[-1]) for m in pattern_match]) if len(pattern_match) > 0 else 0
    match = re.search(r'( *)\w', reg_row[0])
    c2 = match.group().count(' ') if match else 0
    return max(c1, c2)


# TODO MERGE FIND META TABLE INFO AND TABLE TITLE METHODS


def find_meta_table_info(table):
    table_multiplier, table_currency = '', ''
    multiplier_pattern = re.compile('(thousands|millions|billions|percentage)', re.IGNORECASE)
    currency_pattern = re.compile('([$€¥£])', re.IGNORECASE)
    current_element = table
    try:
        while current_element.previous_element is not None:

            if isinstance(current_element, NavigableString):
                current_element = current_element.previous_element
                continue

            if re.search(multiplier_pattern, current_element.text) and len(table_multiplier) == 0:
                table_multiplier = re.search(multiplier_pattern, current_element.text).groups()[-1]

            if re.search(currency_pattern, current_element.text) and len(table_currency) == 0:
                table_currency = re.search(currency_pattern, current_element.text).groups()[-1]

            current_element = current_element.previous_element
    except:
        traceback.print_exc()

    return table_multiplier, table_currency


def find_table_title(table):
    priority_title, emergency_title = '', ''
    current_element = table
    try:
        while (
                table.text == current_element.text and current_element.name == 'table') or current_element.name != 'table':

            current_element = current_element.previous_element
            # sometimes the previous element is a new line metacharacter (&nbsp or encoded as '\n') so skip

            while isinstance(current_element, NavigableString):
                current_element = current_element.previous_element

            while len(current_element.find_all(
                    lambda tag: tag.name == 'table' or tag.name == 'td' or tag.name == 'th')) > 0:
                while isinstance(current_element.previous_element, NavigableString):
                    current_element = current_element.previous_element.previous_element
                current_element = current_element.previous_element

            if is_bold(current_element) or is_centered(current_element) or is_italic(current_element):
                # sometimes the previous element is a detail of the title (i.e. (in thousands)), usually bracketed
                if re.search('^\((.*?)\)\*?$', current_element.text.strip()) \
                        or current_element.text.strip() == '' \
                        or re.search(fin_reg.date_regex, current_element.text.strip()) \
                        or (current_element.name == 'font' and re.search('^div$|^p$', current_element.parent.name)) \
                        or re.search('Form 10-K', current_element.text.strip(), re.IGNORECASE):
                    continue
                else:
                    return current_element.text

            elif re.search('The following table', current_element.text, re.IGNORECASE):
                emergency_title = current_element.text

        # if we reached here, then we haven't found bold/centered/italic
        if len(emergency_title) > 0:
            return emergency_title
        else:
            return 'No Table Title'
    except:
        return 'No Table Title'


def flatten_dict(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.abc.MutableMapping):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def scrape_pdf():
    file = 'https://reports.shell.com/annual-report/2019/servicepages/downloads/files/shell_annual_report_2019.pdf'
    tables = tabula.read_pdf(file, pages=196)
    pprint(table.to_string() for table in tables)


def scrape_txt_tables_from_url(url):
    pass


def scrape_xbrl_tables_from_url(url):
    pass


def scrape_html_tables_from_url(url):
    response = requests.get(url)
    table = ''''''
    soup = BeautifulSoup(response.text, 'html.parser')
    all_in_one_dict = {}

    if 'Inline XBRL Viewer' in soup.text:
        driver = webdriver.Chrome(ChromeDriverManager().install())
        driver.get(url)
        sleep(2)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

    for table in soup.findAll('table'):

        columns = []
        most_recent_column_index = 0
        dates = []
        header_found = False
        indented_list = []
        rows = table.find_all('tr')
        header_index = 0
        table_title, table_currency, table_multiplier = '', '', ''

        for index, row in enumerate(rows):

            reg_row = [ele.text for ele in row.find_all(lambda tag: tag.name == 'td' or tag.name == 'th')]
            reg_row = [unicodedata.normalize("NFKD", x) for x in reg_row]
            current_left_margin = find_left_margin(reg_row, row.findAll('td')[0])
            reg_row = [x.strip() for x in reg_row]
            reg_row[0] = reg_row[0].replace(':', '').replace('\n', ' ') if len(reg_row) > 0 else reg_row[0]

            # first, we want to reach the header of the table, so we skip
            # - the empty rows i.e. those that have no table data 'td' (or those for which the td's are empty)
            # [length 0]
            # - the descriptive rows (i.e. 'dollars in millions', 'fiscal year', etc.) [length 1]
            if not header_found and len(reg_row) > 1:
                reg_row = list(filter(lambda x: x != "", reg_row))
                max_date_index = 0
                # if 'th' tag found or table data with bold, then found a potential header for the table
                if len(row.find_all('th')) != 0 or is_bold(row):
                    if len(columns) == 0:
                        columns = reg_row
                    else:
                        ratio = int(len(reg_row) / len(columns))
                        col_len = len(columns)
                        for col_idx in range(col_len):
                            copy = []
                            for r in range(ratio):
                                copy.append(columns[0] + ' ' + reg_row[0])
                                reg_row.pop(0)
                            columns.extend(copy)
                            columns.pop(0)

                    # sometimes same title (i.e. if table is split in two pages, they repeat page title twice
                    table_multiplier, table_currency = find_meta_table_info(table)
                    table_title = unicodedata.normalize("NFKD", find_table_title(table)).strip().replace('\n', '')
                    if table_multiplier == 'percentage':
                        break

                    if len(columns) > 0 and re.search('\d{4}', columns[0]):
                        header_found = True
                        header_index = index
                        # first_bolded_index = next(i for i, v in enumerate(indented_list) if v[2])
                        dates = []
                        date_formats = r"(((1[0-2]|0?[1-9])\/(3[01]|[12][0-9]|0?[1-9])\/(?:[0-9]{2})?[0-9]{2})|((Jan(uary)?|Feb(ruary)?|Mar(ch)?|Apr(il)?|May|Jun(e)?|Jul(y)?|Aug(ust)?|Sep(tember)?|Oct(ober)?|Nov(ember)?|Dec(ember)?)\s+\d{1,2},\s+\d{4}))"
                        dts = ['%b %d, %Y', '%B %d, %Y']
                        for col in columns:
                            match = re.search(date_formats, col)
                            if match:
                                for dt in dts:
                                    try:
                                        dates.append(datetime.strptime(match.group(), dt).date())
                                        break
                                    except:
                                        pass

                        for date in dates:
                            if date not in all_in_one_dict.keys():
                                all_in_one_dict[date] = {}
                            if table_title not in all_in_one_dict[date].keys():
                                all_in_one_dict[date][table_title] = {}

                        most_recent_column_index = next((index for index, zips in enumerate(zip(dates, columns))
                                                         if (not re.search('six', zips[1], re.IGNORECASE))
                                                         and index == dates.index(max(dates))), 0)

                else:
                    continue

            # beware goldman sachs
            # possible subheader? (should be greater than one to avoid bolded category)
            # elif header_found and is_bold(row) and len(reg_row) > 1:
            #     for item in reg_row:
            #         for index, x in enumerate(reg_row):
            #             if x == item:
            #                 duplicate_index = index
            #                 break
            # slice = [max_date_index, max_date_index+duplicate_index-1]

            elif header_found and len(reg_row) > 0:

                indices = [i for i, x in enumerate(reg_row) if re.search(r'\d', x)]
                reg_row = [reg_row[0]] + [re.sub(r'\(', '-', x) for x in reg_row[1:]]
                reg_row = [reg_row[0]] + [re.sub("[^0-9-]", "", r) for r in reg_row[1:]]
                reg_row = [reg_row[0]] + [re.sub("^-$", "", r) for r in reg_row[1:]]  # for NOT the minus sign
                reg_row = [reg_row[0]] + [re.sub(r',', '', x) for x in reg_row[1:]]
                reg_row = list(filter(lambda x: x != "", reg_row))

                if len(''.join(reg_row).strip()) == 0:
                    continue

                while len(indented_list) > 0 and current_left_margin <= indented_list[-1][0]:

                    if current_left_margin == indented_list[-1][0]:

                        if indented_list[-1][2] or indented_list[-1][1].isupper():  # if last element of list is bold
                            if is_bold(row, alltext=True) or row.text.isupper():  # if current row is bold
                                # first_bolded_index = next(i for i, v in enumerate(indented_list) if v[2])
                                # if first_bolded_index != len(indented_list)-1:
                                #     indented_list.pop(first_bolded_index)
                                indented_list.pop()  # remove that last element of list
                                break  # and stop popping
                            else:
                                break  # otherwise, just subentry so don't pop
                    indented_list.pop()

                try:
                    # if re.search(r'Total', reg_row[0], re.IGNORECASE):
                    #     indented_list.pop()
                    for i in range(len(indented_list)):
                        if re.search(r'^{}$'.format(reg_row[0].split('Total ')[-1]),  # current entry
                                     indented_list[-i][1],  # last category
                                     re.IGNORECASE):
                            indented_list.pop()
                except Exception:
                    traceback.print_exc()

                indented_list.append((current_left_margin, reg_row[0], is_bold(row, alltext=True)))
                current_category = '_'.join([x[1] for x in indented_list])
                try:
                    if len(reg_row) > 1:  # not category column:
                        for i, j in zip(range(1, len(reg_row)),
                                        range(len(dates))):  # 1+ in order to skip the name (first element in reg_row)
                            if current_category not in all_in_one_dict[dates[j]][table_title].keys():
                                all_in_one_dict[dates[j]][table_title][current_category] = float(
                                    re.sub('^$', '0', reg_row[i]))

                except:
                    traceback.print_exc()
    # pprint(not_useful)
    return all_in_one_dict


def scrape_tables_from_url(url):
    extension = url.split('.')[-1]

    if extension == 'xml':
        return scrape_xbrl_tables_from_url(url)
    elif extension == 'htm':
        return scrape_html_tables_from_url(url)
    elif extension == 'txt':
        return scrape_txt_tables_from_url(url)


def normalization_iteration(iteration_count, input_dict, master_dict, filing_type, visited_data_names, year,
                            flexible_sheet=False, flexible_entry=False):
    for title, table in input_dict.items():

        for scraped_name, scraped_value in flatten_dict(table).items():

            for normalized_category, pattern_string in flatten_dict(fin_reg.financial_entries_regex_dict).items():

                # if you're a flexible sheet, the sheet we're checking at least shouldn't match the other concerning statements (i.e. depreciation and amortization's pattern in balance sheet regex shouldn't match cash flow statement change in depreciation and amortization)
                if (flexible_sheet and (('Balance Sheet' in normalized_category.split('_')[0]
                                         and not re.search(
                            r'{}|{}'.format(fin_reg.cash_flow_statement_regex, fin_reg.income_statement_regex), title,
                            re.IGNORECASE))
                                        or ('Income Statement' in normalized_category.split('_')[0]
                                            and not re.search(
                                    r'{}|{}'.format(fin_reg.cash_flow_statement_regex, fin_reg.balance_sheet_regex),
                                    title, re.IGNORECASE))
                                        or ('Cash Flow Statement' in normalized_category.split('_')[0]
                                            and not re.search(
                                    r'{}|{}'.format(fin_reg.balance_sheet_regex, fin_reg.income_statement_regex), title,
                                    re.IGNORECASE)))

                        # if you're not a flexible sheet, the sheet we're checking must match regex sheet
                        or ((not flexible_sheet)
                            and (('Balance Sheet' in normalized_category.split('_')[0] and re.search(
                                    fin_reg.balance_sheet_regex, title, re.IGNORECASE))
                                 or ('Income Statement' in normalized_category.split('_')[0] and re.search(
                                            fin_reg.income_statement_regex, title, re.IGNORECASE))
                                 or ('Cash Flow Statement' in normalized_category.split('_')[0] and re.search(
                                            fin_reg.cash_flow_statement_regex, title, re.IGNORECASE))))):

                    # an entry is not flexible if it should match a hardcoded pattern
                    pattern_string = '^(?!.*{})'.format('Year' if filing_type == '10-Q' else 'Quarter') + pattern_string
                    if ((not flexible_entry) and re.search(
                            pattern_string, title + '_' + scraped_name, re.IGNORECASE)):
                        print('Found pattern match {} for scraped name {}'.format(pattern_string, scraped_name))

                        data_name = {'Iteration Count': str(iteration_count),
                                     'Hardcoded': True,
                                     'Table Title': title,
                                     'Scraped Name': scraped_name,
                                     'Pattern String': pattern_string}

                        if math.isnan(master_dict[normalized_category]):
                            if year not in visited_data_names.keys():
                                visited_data_names[year] = []
                            pattern_matched = False
                            for el in visited_data_names[year]:
                                if re.search(el['Pattern String'], scraped_name, re.IGNORECASE):
                                    pattern_matched = True
                            if not pattern_matched:
                                master_dict[normalized_category] = scraped_value
                                visited_data_names[year].append(data_name)  # that table takes ownership for the data
                            break

                    # otherwise it is flexible if it should just match the category
                    # (i.e. current assets, operating expenses...)
                    if flexible_entry and re.search(normalized_category.split('_')[-2], scraped_name, re.IGNORECASE):
                        already_have_it = False
                        for el in visited_data_names[year]:

                            if re.search(el['Pattern String'], scraped_name, re.IGNORECASE):
                                same_sheet = False
                                for regex_title in [fin_reg.balance_sheet_regex, fin_reg.income_statement_regex,
                                                    fin_reg.cash_flow_statement_regex]:
                                    if re.search(regex_title, title, re.IGNORECASE) and re.search(regex_title,
                                                                                                  el['Table Title'],
                                                                                                  re.IGNORECASE):
                                        same_sheet = True

                                if same_sheet:
                                    already_have_it = True

                        if not already_have_it:
                            master_dict['_'.join(normalized_category.split('_')[:-1]) + '_' + titlecase(
                                scraped_name.split('_')[-1])] = scraped_value

                            visited_data_names[year].append({'Iteration Count': str(iteration_count),
                                                             'Hardcoded': False,
                                                             'Table Title': title,
                                                             'Scraped Name': scraped_name,
                                                             'Pattern String': scraped_name})
                        break

    return visited_data_names, master_dict


def normalize_tables(input_dict, filing_type, visited_data_names, year):
    # pprint(input_dict)
    master_dict = {}

    # TODO maybe should save all data_names to further compare across years? (the flexible entries)

    for normalized_category, pattern_string in flatten_dict(fin_reg.financial_entries_regex_dict).items():
        master_dict[normalized_category] = np.nan

    # first we want to give priority to the elements that strictly match our regex patterns,
    # and that are in the consolidated financial statements
    visited_data_names, master_dict = normalization_iteration(0, input_dict, master_dict, filing_type,
                                                              visited_data_names, year, flexible_sheet=False,
                                                              flexible_entry=False)

    # then we want to give priority to the elements that strictly match our regex patterns,
    # but not in the consolidated financial statements
    visited_data_names, master_dict = normalization_iteration(1, input_dict, master_dict, filing_type,
                                                              visited_data_names, year, flexible_sheet=True,
                                                              flexible_entry=False)

    # finally, we want to give priority to the rest of the elements (i.e. those that do not
    # match our regex patterns) that are in the consolidated financial statements
    # TODO bug: duplicate entries despite pattern match check
    # visited_data_names, master_dict = normalization_iteration(2, input_dict, master_dict, filing_type,
    #                                                           visited_data_names, year, flexible_sheet=False,
    #                                                           flexible_entry=True)

    # TODO Final Standardization, Fill in Differences!
    # If Interest Income/Expense in revenues, then readjust Net Sales (add back)
    # total noncurrent = total - total current  for assets, liabilities
    # if total noncurrent nan, else total = total current + total noncurrent

    master_dict['Balance Sheet_Assets_Non Current Assets_Total Non Current Assets'] = master_dict[
                                                                                          'Balance Sheet_Assets_Total Assets'] - \
                                                                                      master_dict[
                                                                                          'Balance Sheet_Assets_Current Assets_Total Current Assets']

    master_dict[
        'Balance Sheet_Liabilities and Shareholders\' Equity_Liabilities_Non Current Liabilities_Total Non Current Liabilities'] = \
        master_dict['Balance Sheet_Liabilities and Shareholders\' Equity_Liabilities_Total Liabilities'] - master_dict[
            'Balance Sheet_Liabilities and Shareholders\' Equity_Liabilities_Current Liabilities_Total Current Liabilities']

    return visited_data_names, flatten_dict(unflatten(master_dict))


def unflatten(dictionary):
    resultDict = dict()
    for key, value in dictionary.items():
        parts = key.split("_")
        d = resultDict
        for part in parts[:-1]:
            if part not in d:
                d[part] = dict()
            d = d[part]
        d[parts[-1]] = value
    return resultDict


def scrape_financial_statements(ticker, filing_type, how_many_periods=2):
    dictio = {}
    cik = get_company_cik(ticker)
    doc_links = get_filings_urls_first_layer(cik, filing_type)
    filings_dictio = get_filings_urls_second_layer(filing_type, doc_links)
    pprint(filings_dictio)
    names = ['{} {}'.format(name, filing_type) for name in
             [config.balance_sheet_name, config.income_statement_name, config.cash_flow_statement_name]]
    output = pd.Series()
    for sheet_name in names:
        financials_path = '{}/{}.xlsx'.format(config.FINANCIAL_STATEMENTS_DIR_PATH, ticker)
        output[sheet_name] = (excel.read_dates_from_csv(financials_path, sheet_name),
                              excel.read_df_from_csv(financials_path, sheet_name))
    existing_dates_with_df = excel.read_dates_from_csv(ticker, names)
    # output[sheet_name] = (dates, df)

    if len(existing_dates_with_df) > 0:
        missing_dates_links = [(x, y) for x, y in filings_dictio['HTML Links']
                               if datetime.strptime(x, '%Y-%m-%d') not in existing_dates_with_df[names[0]][0]]
    else:
        missing_dates_links = [(x, y) for x, y in filings_dictio['HTML Links']]

    for index, (filing_date, link) in enumerate(missing_dates_links):
        try:
            if (index > how_many_periods and filing_type=='10-K') or (index > how_many_periods * 4 and filing_type=='10-Q'):
                break
            print(filing_date, link)
            # scrape_tables_from_url(link)
            output = scrape_tables_from_url(link)

            for key, value in output.items():  # year / title

                if key not in dictio.keys():  # if we don't have the year in our dictio that collects everything, just add all and go to next year of the output
                    dictio[key] = value
                    continue

                #  else, we have a year, so we add up those two dicts together
                for kk, vv in value.items():  # title / key:float
                    if kk not in dictio[key].keys():
                        dictio[key][kk] = vv

                    else:
                        dictio[key][kk].update(vv)

        except Exception:
            traceback.print_exc()

    pprint(dictio)
    financials_dictio = {}
    visited_data_names = {}
    for key, value in dictio.items():
        visited_data_names, financials_dictio[key] = normalize_tables(value, filing_type, visited_data_names, key)

    financials_dictio = {k: v for k, v in financials_dictio.items() if v is not None}
    # pprint(financials_dictio)
    for sheet_name in names:

        diction = {i: {(j.split('_')[1], j.split('_')[-1] if j.split('_')[1] != j.split('_')[
            -1] else ' ') if 'Balance Sheet' not in sheet_name
                       else ((j.split('_')[1], j.split('_')[2] if (len(j.split('_')) > 2) else ' ',
                              j.split('_')[-1] if j.split('_')[1] != j.split('_')[-1] else ''))
                       : financials_dictio[i][j]
                       for j in financials_dictio[i].keys() if j.split('_')[0] in sheet_name  # sheet name
                       } for i in financials_dictio.keys()}  # date

        df = pd.DataFrame.from_dict(diction)
        df = df.reindex(sorted(df.columns, reverse=True), axis=1)
        if len(existing_dates_with_df) > 0:
            df = pd.concat([df, existing_dates_with_df[sheet_name][1]], axis=1).fillna(0)
        df.dropna(axis=0, how='all', inplace=True)
        df = df.loc[:, df.any()]
        path = '{}/{}.xlsx'.format(config.FINANCIAL_STATEMENTS_DIR_PATH, ticker)
        excel.save_into_csv(path, df, sheet_name)


def get_stock_prices(stock, start=datetime(1970, 1, 1), end=datetime.now()):
    df = excel.read_df_from_csv(stock, config.stock_prices_sheet_name)
    if df.empty:
        df = web.DataReader(stock.replace('.', '-'), data_source='yahoo', start=start, end=end)
        df['pct_change'] = df['Adj Close'].pct_change()
        path = '{}/{}.xlsx'.format(config.FINANCIAL_STATEMENTS_DIR_PATH, stock)
        excel.save_into_csv(path, df, config.stock_prices_sheet_name)
        return df
    return df


def get_technical_indicators(stock):
    df = excel.read_df_from_csv(stock, config.technical_indicators_name)
    if df.empty:
        df = get_stock_prices(stock)
        df = ta.add_all_ta_features(
            df, open="Open", high="High", low="Low", close="Adj Close", volume="Volume", fillna=True)
        path = '{}/{}.xlsx'.format(config.FINANCIAL_STATEMENTS_DIR_PATH, stock)
        excel.save_into_csv(path, df, config.technical_indicators_name)
        return df
    else:
        return df


def save_gnp_price_index():
    url = 'https://fred.stlouisfed.org/graph/fredgraph.csv?bgcolor=%23e1e9f0&chart_type=line&drp=0&fo=open%20sans&' \
          'graph_bgcolor=%23ffffff&height=450&mode=fred&recession_bars=on&txtcolor=%23444444&ts=12&tts=12&width=1168&nt' \
          '=0&thu=0&trc=0&show_legend=yes&show_axis_titles=yes&show_tooltip=yes&id=A001RG3A086NBEA&scale=left&cosd=1929' \
          '-01-01&coed=2019-01-01&line_color=%234572a7&link_values=false&line_style=solid&mark_type=none&mw=3&lw=2&ost=' \
          '-99999&oet=99999&mma=0&fml=a&fq=Annual&fam=avg&fgst=lin&fgsnd=2009-06-01&line_index=1&transformation=lin&vin' \
          'tage_date=2020-07-10&revision_date=2020-07-10&nd=1929-01-01'

    urllib.request.urlretrieve(url, 'temp.csv')
    df = pd.read_csv('temp.csv')
    df.columns = ['Date', 'GNP Price Index']
    df.set_index(df.columns[0], inplace=True)
    df.index = pd.to_datetime(df.index, format='%Y-%m-%d')
    # df.index = df.index - timedelta(days=1)

    with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
        print(df)

    existing_df = excel.read_df_from_csv(config.MACRO_DATA_FILE_PATH, config.yearly_factors)
    final_df = existing_df.merge(df, how='outer', left_index=True, right_index=True)
    excel.save_into_csv(config.MACRO_DATA_FILE_PATH, final_df, config.yearly_factors)
    os.remove('temp.csv')


three_factors_url_daily = ''
three_factors_url_weekly = ''
three_factors_url_monthly_yearly = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_Factors_CSV.zip"
five_factors_url_daily = ''
five_factors_url_weekly = ''
five_factors_url_monthly_yearly = ''
momentum_factor_url_daily = 'https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Momentum_Factor_daily_CSV.zip'
momentum_factor_url_monthly_yearly = 'https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Momentum_Factor_CSV.zip'
carhart_four_factor_url_monthly = 'https://breakingdownfinance.com/wp-content/uploads/2019/07/Carhart-4-factor-data.xlsx'


# TODO compile daily, weekly, monthly, yearly Fama French Factors (it also includes momentum)


def save_factors_data(url):
    urllib.request.urlretrieve(url, 'fama_french.zip')
    zip_file = zipfile.ZipFile('fama_french.zip', 'r')
    zip_file.extractall()
    zip_file.close()

    # TODO FIND MORE PYTHONIC WAY
    file_name = ''
    for f in [f for f in s.listdir('.') if os.path.isfile(f)]:
        if re.search('F-F', f):
            file_name = f
            break

    ff_factors = pd.read_csv(file_name, skiprows=3, index_col=0)
    # We want to find out the row with NULL value. We will skip these rows
    ff_row = np.array(ff_factors.isnull().any(1)).nonzero()
    for nrow in ff_row[0]:
        # Read the csv file again with skipped rows
        ff_factors = pd.read_csv('F-F_Research_Data_Factors.csv', skiprows=3, nrows=nrow, index_col=0)
        ff_factors.index = pd.to_datetime(ff_factors.index, format='%Y%m')
        ff_factors.index = ff_factors.index + pd.offsets.MonthEnd()
        ff_factors = ff_factors.apply(lambda x: x / 100)
        path = os.path.join(config.FACTORS_DIR_PATH, 'Factors.xlsx')
        excel.save_into_csv(path, ff_factors, config.monthly_factors)

    os.remove(file_name)
    os.remove('fama_french.zip')
    return ff_factors


def testing():
    dictio = {}
    pprint(normalize_tables(dictio, '10-K', []))


if __name__ == '__main__':

    if not os.path.exists(config.DATA_DIR_PATH):
        os.mkdir(config.DATA_DIR_PATH)
    if not os.path.exists(config.MARKET_TICKERS_DIR_PATH):
        os.mkdir(config.MARKET_TICKERS_DIR_PATH)
    if not os.path.exists(config.FINANCIAL_STATEMENTS_DIR_PATH):
        os.mkdir(config.FINANCIAL_STATEMENTS_DIR_PATH)
    if not os.path.exists(config.FACTORS_DIR_PATH):
        os.mkdir(config.FACTORS_DIR_PATH)

    company_tickers = ['AAPL', 'GOOG', 'FB', 'AMZN', 'TSLA', 'NFLX',
                       'KO', 'PG', 'JNJ', 'PEP', 'VZ',
                       'GS', 'MS', 'JPM', 'WFC', 'C', 'BAC']
    # testing()
    for ticker in company_tickers[:1]:
        # get_stock_prices(ticker)
        # get_technical_indicators(ticker)
        scrape_financial_statements(ticker, '10-K')
        # scrape_financial_statements(ticker, '10-Q')

    # ff_factors = get_beta_factors()
    # print(ff_factors)
    # testing()
    # scrape_pdf()
    # save_factors_data(momentum_factor_url_daily)
