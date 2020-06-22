import collections
import os
import re
import traceback
from pprint import pprint
import pandas as pd
import requests
import unicodedata
from bs4 import BeautifulSoup, NavigableString
import sec_scraping.regex_patterns as fin_reg
import sec_scraping.unit_tests as test

# TODO fill 0's with NaNs and order dataframe properly

# TODO Review regexes of balance sheet, more testing

# TODO implement 'Other' for each category. it is total of current category - anything in current category (and sub) not having 'total'

# TODO If Interest Income/Expense in revenues, then readjust Net Sales (add back)
'''
Beautiful BeautifulSoup Usage

html = urllib2.urlopen(url).read()
bs = BeautifulSoup(html)
table = bs.find(lambda tag: tag.name=='table' and tag.has_attr('id') and tag['id']=="Table1") 
rows = table.findAll(lambda tag: tag.name=='tr')
'''

def get_company_cik(ticker):
    URL = 'http://www.sec.gov/cgi-bin/browse-edgar?CIK={}&Find=Search&owner=exclude&action=getcompany'.format(ticker)
    response = requests.get(URL)
    CIK_RE = re.compile(r'.*CIK=(\d{10}).*')
    return CIK_RE.findall(response.text)[0]


def get_filings_urls_first_layer(ticker, filing_type):
    cik = get_company_cik(ticker)
    print('Company CIK for {} is {}'.format(ticker, cik))
    base_url = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={}&type={}".format(cik, filing_type)
    edgar_resp = requests.get(base_url).text
    print(base_url)
    soup = BeautifulSoup(edgar_resp, 'html.parser')
    table_tag = soup.find('table', class_='tableFile2')
    rows = table_tag.find_all('tr')
    filing_dates = []
    doc_links = []

    for row in rows[1:]:
        cells = row.find_all('td')
        filing_dates.append(cells[3].text)
        doc_links.append('https://www.sec.gov' + cells[1].a['href'])
    return filing_dates, doc_links


def get_filings_urls_second_layer(ticker, filing_type):
    links_dictionary = {
        'XBRL Links': [], # for new submissions
        'HTML Links': [], # if no XML, then we put HTML (for older submissions).
        'TXT Links': [] # if no HTML, then we put TXT (for even older submissions)
    }
    filing_dates, doc_links = get_filings_urls_first_layer(ticker, filing_type)

    for date, doc_link in zip(filing_dates, doc_links):
        # Obtain HTML for document page
        doc_resp = requests.get(doc_link).text
        # Find the XBRL link
        link = ''
        soup = BeautifulSoup(doc_resp, 'html.parser')

        # first, try finding a XML document
        table_tag = soup.find('table', class_='tableFile', summary='Data Files')
        no_xml_link = True
        if table_tag is not None:
            rows = table_tag.find_all('tr')
            for row in rows[1:]:
                cells = row.find_all('td')
                link = 'https://www.sec.gov' + cells[2].a['href']
                if 'XML' in cells[3].text or 'INS' in cells[3].text:
                    links_dictionary['XBRL Links'].append((date, link))
                    no_xml_link = False

        # if no XML document found, try finding html documents
        no_html_link = True
        no_xml_link = True # TODO this is to include XML links as HTMLs to test HTML scraping, so remove when done
        if no_xml_link:
            table_tag = soup.find('table', class_='tableFile', summary='Document Format Files')
            rows = table_tag.find_all('tr')
            for row in rows[1:]:
                cells = row.find_all('td')
                link = 'https://www.sec.gov' + cells[2].a['href']
                if 'htm' in cells[2].text and cells[3].text == filing_type:
                    links_dictionary['HTML Links'].append((date, link))
                    no_html_link = False

        # if no HTML document found, then get the txt
        if no_html_link and no_xml_link:
            table_tag = soup.find('table', class_='tableFile', summary='Document Format Files')
            rows = table_tag.find_all('tr')
            for row in rows[1:]:
                cells = row.find_all('td')
                link = 'https://www.sec.gov' + cells[2].a['href']
                if cells[1].text == 'Complete submission text file':
                    links_dictionary['TXT Links'].append((date, link))

    return links_dictionary


def is_bold(row, alltext=False):
    soup = BeautifulSoup(str(row), features='html.parser')
    bolded_row_text = soup.find_all(lambda tag: tag.name == 'b' or (tag.has_attr('style') and 'bold' in str(tag['style'])))
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
    return len(soup.find_all(lambda tag: tag.name != 'table' and ((tag.has_attr('align') and 'center' in str(tag['align'])) or tag.has_attr('style') and 'text-align:center' in str(tag['style'])))) > 0


def find_left_margin(reg_row, td):
    pattern_match = re.search('(margin-left|padding-left):(\d+)', str(td))
    if pattern_match:
        return int(pattern_match.groups()[-1])

    else: # other times it has a '' before the text
        return next((i for i, v in enumerate(reg_row) if v != ''), len(reg_row))

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

    while (table.text == current_element.text and current_element.name == 'table') or current_element.name != 'table':

        current_element = current_element.previous_element
        # sometimes the previous element is a new line metacharacter (&nbsp or encoded as '\n') so skip

        while isinstance(current_element, NavigableString):
            current_element = current_element.previous_element

        while len(current_element.find_all(lambda tag: tag.name == 'table' or tag.name == 'td' or tag.name == 'th')) > 0:
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

def flatten_dict(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.abc.MutableMapping):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def scrape_txt_tables_from_url(url):
    pass


def scrape_xbrl_tables_from_url(url):
    pass


def scrape_html_tables_from_url(url):

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    all_in_one_dict = {}

    for table in soup.findAll('table'):

        columns = []
        header_found = False
        indented_list = []
        rows = table.find_all('tr')
        header_index = 0
        table_title, table_currency, table_multiplier = '', '', ''

        for index, row in enumerate(rows):

            # Clean up each row's data
            reg_row = [ele.text.strip() for ele in row.find_all(lambda tag: tag.name == 'td' or tag.name == 'th')]
            reg_row = [unicodedata.normalize("NFKD", x) for x in reg_row]

            current_left_margin = find_left_margin(reg_row, row.findAll('td')[0])
            if len(reg_row) > 0:
                reg_row[0] = reg_row[0].replace(':', '').replace('\n', ' ')

            reg_row = list(filter(lambda x: x != "" and '%' not in x, reg_row))  # remove empty strings (table datas) from list
                                                                                 # as well as percentages

            # first, we want to reach the header of the table, so we skip
            # - the empty rows i.e. those that have no table data 'td' (or those for which the td's are empty) [length 0]
            # - the descriptive rows (i.e. 'dollars in millions', 'fiscal year', etc.) [length 1]
            if not header_found and len(reg_row) > 1:

                # if 'th' tag found or table data with bold, then found a potential header for the table
                if (len(row.find_all('th')) != 0 or is_bold(row)) and len(list(filter(fin_reg.date_regex.search, reg_row))) > 0:

                    # sometimes same title (i.e. if table is split in two pages, they repeat page title twice
                    table_multiplier, table_currency = find_meta_table_info(table)
                    table_title = unicodedata.normalize("NFKD",  find_table_title(table)).strip().replace('\n', '')

                    if table_multiplier == 'percentage':
                        break

                    if table_title not in all_in_one_dict.keys():
                        all_in_one_dict[table_title] = {}

                    header_found = True

                else:
                    continue

            elif header_found and len(reg_row) > 0:

                reg_row = [reg_row[0]] + [re.sub(r'\(', '-', x) for x in reg_row[1:]]
                reg_row = [reg_row[0]] + [re.sub("[^0-9\-]", "", r) for r in reg_row[1:]]
                reg_row = [reg_row[0]] + [re.sub("^-$", "", r) for r in reg_row[1:]] # for NOT the minus sign
                reg_row = [reg_row[0]] + [re.sub(r',', '', x) for x in reg_row[1:]]
                reg_row = list(filter(lambda x: x != "" and '%' not in x, reg_row))

                # if it's a line
                if len(row.find_all(lambda tag: tag.has_attr('style') and ('border-bottom:solid' in tag['style']
                                                                           or 'border-top:solid' in tag['style']))) > 0:
                    continue
                # empty line
                elif len(''.join(reg_row).strip()) == 0:
                    continue

                while len(indented_list) > 0 and current_left_margin <= indented_list[-1][0]:
                    # if there is bold, then master category
                    if current_left_margin == indented_list[-1][0]:
                        # TODO TEST MORE
                        if indented_list[-1][2]: # if last element of list is bold
                            if is_bold(row, alltext=True): # if current row is bold
                                # first_bolded_index = next(i for i, v in enumerate(indented_list) if v[2])
                                # if first_bolded_index != len(indented_list)-1:
                                #     indented_list.pop(first_bolded_index)
                                indented_list.pop() # remove that last element of list
                                break # and stop popping
                            else:
                                break # otherwise, just subentry so don't pop
                    indented_list.pop()

                try:
                    if len(indented_list) > 0:
                        if re.search(r'Total', reg_row[0], re.IGNORECASE):
                            # TODO test further
                            # while not re.search(r'^{}$'.format(reg_row[0].split('Total ', re.IGNORECASE)[1]), # current entry
                            #                     indented_list[-1][1], # last category
                            #                     re.IGNORECASE):
                            indented_list.pop()
                except Exception:
                    traceback.print_exc()

                indented_list.append((current_left_margin, reg_row[0], is_bold(row, alltext=True)))
                current_category = '_'.join([x[1] for x in indented_list])
                try:
                    if len(reg_row) > 1: # not category column:
                        if current_category not in all_in_one_dict[table_title].keys():
                            all_in_one_dict[table_title][current_category] = float(re.sub('^$', '0', reg_row[1])) # * table_multiplier (ugly)

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

# TODO maybe for first round of normalization ADD to the patterns the _ trick (but keep them r
def normalization_first_level(input_dict):
    pprint(input_dict)
    master_dict = {} # do OrderedDict()
    for normalized_category, pattern_string in flatten_dict(fin_reg.financial_entries_regex_dict).items():
        master_dict[normalized_category] = 0
    visited_data_names = []
    for title, table in input_dict.items():

        for scraped_name, scraped_value in flatten_dict(table).items():

            found_match = False # JUST FOR DEBUGGING PURPOSES

            for normalized_category, pattern_string in flatten_dict(fin_reg.financial_entries_regex_dict).items():

                if ('Balance Sheet' in normalized_category.split('_')[0] and re.search(fin_reg.balance_sheet_regex, title, re.IGNORECASE))\
                        or ('Income Statement' in normalized_category.split('_')[0] and re.search(fin_reg.income_statement_regex, title, re.IGNORECASE))\
                        or ('Cash Flow Statement' in normalized_category.split('_')[0] and re.search(fin_reg.cash_flow_statement_regex, title, re.IGNORECASE) ):
                    # first we want to give priority to the elements in the consolidated financial statements

                    if re.search('^' + pattern_string, scraped_name, re.IGNORECASE):
                        found_match = True # for debugging, can remove later

                        # The idea is that if we go to another table and we have a value similar to one we already have on the sheet,
                        # i do not want to include it (because its a duplicate). But if the value is similar in the same sheet, then
                        # i want to add it to the already existing value
                        if master_dict[normalized_category] == 0:
                            visited_data_names.append(title+pattern_string)
                        if title+pattern_string in visited_data_names:
                            master_dict[normalized_category] += scraped_value

                        if 'Allowances for Doubtful Accounts' in normalized_category:
                            master_dict[normalized_category] = float(re.search(pattern_string, scraped_name, re.IGNORECASE).groups()[-1])
                            continue
                        else:
                            break

            if not found_match and (re.search(fin_reg.balance_sheet_regex, scraped_name, re.IGNORECASE)
                                    or re.search(fin_reg.income_statement_regex, scraped_name, re.IGNORECASE)
                                    or re.search(fin_reg.cash_flow_statement_regex, scraped_name, re.IGNORECASE)):
                print('No match for ' + scraped_name)

    return master_dict

def normalization_second_level(input_dict):
    # OTher normalizations should only work on null (0, empty) values! Cannot fill twice from different tables otherwise will add up
    #                 for cat in normalized_category.split('_')[1:-1]:
    #                     category_regexed.append('(?=.*{})'.format(cat))
    #                 # last_cat = normalized_category.split('_')[-1]
    #                 pattern_string = r'(' + '|'.join(category_regexed) + r').*^' + pattern_string
    pass


def normalizatation_third_level(input_dict):
    pass


def normalize_tables(input_dict):
    master_dict = normalization_first_level(input_dict)
    # master_dict = normalization_second_level(master_dict)
    # master_dict = normalizatation_third_level(master_dict)

    master_dict['Balance Sheet_Assets_Current Assets_Accounts Receivable_Gross Accounts Receivable'] = \
        master_dict['Balance Sheet_Assets_Current Assets_Accounts Receivable_Net Accounts Receivable'] + \
        master_dict['Balance Sheet_Assets_Current Assets_Accounts Receivable_Allowances for Doubtful Accounts']

    # balance_sheet = {i: master_dict[i] for i in master_dict.keys() if re.search(r'Balance Sheet', i)}
    # income_statement = {i: master_dict[i] for i in master_dict.keys() if re.search(r'Income Statement', i)}
    # cash_flow_statement = {i: master_dict[i] for i in master_dict.keys() if re.search(r'Cash Flow Statement', i)}
    return master_dict


def testing():
    url = 'https://www.sec.gov/Archives/edgar/data/1326801/000132680119000009/fb-12312018x10k.htm'
    all_in_one_dict = scrape_html_tables_from_url(url)
    pprint(all_in_one_dict)
    # all_in_one_dict = test.aapl_dict
    # pprint(all_in_one_dict)
    gs_dict = {'Consolidated Statements of Financial Condition': {'Assets:Cash and cash equivalents': 130547.0,
                                                                  'Assets:Collateralized agreements:Securities borrowed (includes $23,142 and $78,189 at fair value)': 135285.0,
                                                                  'Assets:Collateralized agreements:Securities purchased under agreements to resell (includes $139,220 and $120,420 at fair value)': 139258.0,
                                                                  'Assets:Financial instruments owned (at fair value and includes $55,081 and $50,335 pledged as collateral)': 336161.0,
                                                                  'Assets:Other assets': 30640.0,
                                                                  'Assets:Receivables:Customer and other receivables (includes $3,189 and $3,526 at fair value)': 79315.0,
                                                                  'Assets:Receivables:Loans receivable': 80590.0,
                                                                  'Liabilities and shareholders’ equity:Collateralized financings:Other secured financings (includes $20,904 and $24,345 at fair value)': 21433.0,
                                                                  'Liabilities and shareholders’ equity:Collateralized financings:Securities loaned (includes $3,241 and $5,357 at fair value)': 11808.0,
                                                                  'Liabilities and shareholders’ equity:Collateralized financings:Securities sold under agreements to repurchase (at fair value)': 78723.0,
                                                                  'Liabilities and shareholders’ equity:Customer and other payables': 180235.0,
                                                                  'Liabilities and shareholders’ equity:Deposits (includes $21,060 and $22,902 at fair value)': 158257.0,
                                                                  'Liabilities and shareholders’ equity:Financial instruments sold, but not yet purchased (at fair value)': 108897.0,
                                                                  'Liabilities and shareholders’ equity:Other liabilities (includes $132 and $268 at fair value)': 17607.0,
                                                                  'Liabilities and shareholders’ equity:Unsecured long-term borrowings (includes $46,584 and $38,638 at fair value)': 224149.0,
                                                                  'Liabilities and shareholders’ equity:Unsecured short-term borrowings (includes $16,963 and $16,904 at fair value)': 40502.0,
                                                                  'Shareholders’ equity:Accumulated other comprehensive income/(loss)': 693.0,
                                                                  'Shareholders’ equity:Additional paid-in capital': 54005.0,
                                                                  'Shareholders’ equity:Common stock; 891,356,284 and 884,592,863 shares issued, and 367,741,973 and 374,808,805 shares outstanding': 9.0,
                                                                  'Shareholders’ equity:Nonvoting common stock; no shares issued and outstanding': 0.0,
                                                                  'Shareholders’ equity:Preferred stock; aggregate liquidation preference of $11,203 and $11,853': 11203.0,
                                                                  'Shareholders’ equity:Retained earnings': 100100.0,
                                                                  'Shareholders’ equity:Share-based awards': 2845.0,
                                                                  'Shareholders’ equity:Stock held in treasury, at cost; 523,614,313 and 509,784,060 shares': -78670.0,
                                                                  'Total assets': 931796.0,
                                                                  'Total liabilities': 841611.0,
                                                                  'Total liabilities and shareholders’ equity': 931796.0,
                                                                  'Total shareholders’ equity': 90185.0}}
    pprint(normalize_tables(all_in_one_dict))


if __name__ == '__main__':
    ticker = 'FB'
    financials_dictio = {}
    filings_dictio = get_filings_urls_second_layer(ticker, '10-K')
    pprint(filings_dictio)
    for key, value in filings_dictio.items():
        for filing_date, link in value:
            try:
                print(filing_date, link)
                financials_dictio[filing_date] = normalize_tables(scrape_tables_from_url(link))
            except Exception:
                traceback.print_exc()

    financials_dictio = {k: v for k, v in financials_dictio.items() if v is not None}
    balance_sheet_dict, income_statement_dict, cash_flow_statement_dict = {}, {}, {}

    for dictio, regex in zip([balance_sheet_dict, income_statement_dict, cash_flow_statement_dict],
                           [fin_reg.balance_sheet_regex, fin_reg.income_statement_regex, fin_reg.cash_flow_statement_regex]):
        for key, value in financials_dictio.items():
            dictio[key] = {}
            for kk, vv in value.items():
                if re.search(regex, kk, re.IGNORECASE):
                    dictio[key][kk.split('_')[-1]] = vv

    financial_statements_folder_path = 'Financial Statements'
    if not os.path.exists(financial_statements_folder_path):
        os.makedirs(financial_statements_folder_path)

    financial_statements_file_path = "{}/{}.xlsx".format(financial_statements_folder_path, ticker)
    writer = pd.ExcelWriter(financial_statements_file_path, engine='xlsxwriter')

    for sheet_name, dict in zip(['Balance Sheets', 'Income Statements', 'Cash Flow Statements'],
                                [balance_sheet_dict, income_statement_dict, cash_flow_statement_dict]):
        with open(financial_statements_file_path, "w") as csv:
            df = pd.DataFrame.from_dict(dict)
            df = df[(df.T != 0).any()]
            df.to_excel(writer, sheet_name=sheet_name)

    writer.save()
    writer.close()
    # testing()
