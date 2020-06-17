import collections
import re
import traceback
from pprint import pprint
from re import Pattern
import pandas as pd
import requests
import unicodedata
from bs4 import BeautifulSoup, NavigableString
import sec_scraping.regex_patterns as fin_reg
import sec_scraping.unit_tests as test

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


def is_bold(row, intable, alltext=False):
    # print(row['style'])
    bolded_row_text = row.find_all(lambda tag: tag.name == 'b' or (tag.has_attr('style') and 'bold' in str(tag['style'])))

    bolded_row_text = ''.join([a.text for a in bolded_row_text]).strip()
    row_text = row.text.strip()
    if intable:
        isbold = len(row.find_all('b')) > 0 or re.search('bold', str(row))
        if alltext:
            return isbold and len(bolded_row_text) == len(row_text)
        else:
            return isbold
    # or len(row.find_all('span', {'style': re.compile(r'bold')})) > 0 \
    # or len(row.find_all('font', {'style': re.compile(r'bold')})) > 0
    else:
        return len(row.find_all(lambda tag: tag.name == 'table' and tag.has_attr('style') and re.search('bold', str(tag))))== 0


# TODO
def is_italic(row):
    return len(row.find_all(lambda tag: tag.name=='i')) > 0


def find_left_margin(reg_row, td):
    current_left_margin = 0
    pattern_match = re.search('(margin-left|padding-left):(\d+)', str(td))
    if pattern_match:
        return int(pattern_match.groups()[-1])

    # TODO find better way
    else: # other times it has a '' before the text
        for i in range(len(reg_row)):
            if reg_row[i] == '':
                current_left_margin += 1
            else:
                break

    return current_left_margin

def find_table_title(table):
    current_element = table
    while (table.text == current_element.text and current_element.name == 'table') or current_element != 'table':
        current_element = current_element.previous_element
        # sometimes the previous element is a new line metacharacter (&nbsp or encoded as '\n') so skip
        while isinstance(current_element, NavigableString):
            current_element = current_element.previous_element
        if is_bold(current_element, intable=False):
            # sometimes the previous element is a detail of the title (i.e. (in thousands)), usually bracketed
                if re.search('^\((.*?)\)\*?$', current_element.text.strip()) \
                        or current_element.text.strip() == ''\
                        or re.search(fin_reg.date_regex, current_element.text.strip())\
                        or (current_element.name == 'font' and re.search('^div$|^p$', current_element.parent.name)): #
                    continue
                else:
                    return current_element.text
    return None

# TODO override table multiplier if in row label it's written 'thousands' etc.
def find_table_unit(table):
    unit_dict = {'thousands': 1000, 'millions': 1000000, 'billions': 1000000000}
    for unit in unit_dict.keys():
        if unit in table.text: # TODO, unit might also be outside the table, above it (but below [and including] title)
            return unit_dict[unit]
    return unit_dict['millions'] # default


def flatten_dict(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.abc.MutableMapping):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def normalize_tables(input_dict):
    master_dict = {}
    for scraped_name, scraped_value in flatten_dict(input_dict).items():
        found_match = False
        # TODO HARDCODED FIX, SOMETIMES BIG PARAGRAPHS ABOVE TABLE INCLUDE THE WORD 'BALANCE SHEET' etc.
        if len(scraped_name.split('_')[0]) > 100:
            continue
        for normalized_category, pattern in flatten_dict(fin_reg.financial_entries_regex_dict).items():
            if isinstance(pattern, Pattern):
                pattern_match = re.search(pattern, scraped_name)
                # first we want to give priority to the elements in the consolidated financial statements
                if pattern_match and (re.search(fin_reg.balance_sheet_regex, scraped_name, re.IGNORECASE)
                                      or re.search(fin_reg.income_statement_regex, scraped_name, re.IGNORECASE)
                                      or re.search(fin_reg.cash_flow_statement_regex, scraped_name, re.IGNORECASE)):
                    found_match = True

                    # this takes care of having two entries for marketable securities, accounts receivables as in Goldman Sachs
                    # so if the entry is already in the master dict, then we add to it (as in we've found before same entry, so we add to it)
                    # TODO: this should be from consolidated data
                    if normalized_category in master_dict.keys():
                        master_dict[normalized_category] += int(scraped_value) if scraped_value != '—' else 0
                    else:
                        try:
                            master_dict[normalized_category] = int(scraped_value) if scraped_value != '—' else 0
                        except:
                            pass
                    if 'Allowances for Doubtful Accounts' in normalized_category:
                        master_dict[normalized_category] = pattern_match.groups()[-1]

                    # if 'Cash Flow Statement' in normalized_category: # TODO beware _ and : normalize!
                    #     master_dict[normalized_category+'_'+pattern_match.string.split(':')[-1]] = scraped_value

        if not found_match and (re.search(fin_reg.balance_sheet_regex, scraped_name, re.IGNORECASE)
                                or re.search(fin_reg.income_statement_regex, scraped_name, re.IGNORECASE)
                                or re.search(fin_reg.cash_flow_statement_regex, scraped_name, re.IGNORECASE)):
            print('No match for ' + scraped_name)

    for scraped_name, scraped_value in flatten_dict(input_dict).items():
        for normalized_category, pattern in flatten_dict(fin_reg.financial_entries_regex_dict).items():
            if isinstance(pattern, Pattern):
                if re.search(pattern, scraped_name) and not (re.search(fin_reg.balance_sheet_regex, scraped_name, re.IGNORECASE)
                                                             or re.search(fin_reg.income_statement_regex, scraped_name, re.IGNORECASE)
                                                             or re.search(fin_reg.cash_flow_statement_regex, scraped_name, re.IGNORECASE)):
                    # TODO: this should be from consolidated data
                    if normalized_category not in master_dict.keys():
                        master_dict[normalized_category] = float(re.sub('[-—–]', '0', scraped_value))
                        # scraped_value.replace('-', '0').replace('—', '0').replace('–', '0'))
                        # master_dict[normalized_category] = int(scraped_value) if scraped_value != '—' else 0

    # pprint(master_dict)

    balance_sheet = {i: master_dict[i] for i in master_dict.keys() if re.search(r'Balance Sheet', i)}
    income_statement = {i: master_dict[i] for i in master_dict.keys() if re.search(r'Income Statement', i)}
    cash_flow_statement = {i: master_dict[i] for i in master_dict.keys() if re.search(r'Cash Flow Statement', i)}
    return master_dict

def scrape_txt_tables_from_url(url):
    pass

def scrape_xbrl_tables_from_url(url):
    pass

def scrape_html_tables_from_url(url):

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    not_useful = [] # for debugging
    all_in_one_dict = {}

    # TODO GOLDMAN SACHS debug page 76 https://www.sec.gov/Archives/edgar/data/886982/000095012310018464/y81914e10vk.htm

    for table in soup.findAll('table'):

        columns = []
        header_found = False
        current_category = ''
        previous_left_margin = 0
        indented_list = []
        rows = table.find_all('tr')

        table_title = unicodedata.normalize("NFKD",
                                            find_table_title(table)).strip().replace('\n', '')

        table_multiplier = find_table_unit(table)
        # print(table_multiplier)

        for index, row in enumerate(rows):

            reg_row = [ele.text.strip() for ele in row.find_all('td')]
            reg_row = [unicodedata.normalize("NFKD", x) for x in reg_row]

            if not header_found:

                if len(reg_row) == 0:
                    reg_row = [ele.text.strip() for ele in row.find_all('th')]

                # first, we want to reach the header of the table, so we skip
                # - the empty rows i.e. those that have no table data 'td' (or those for which the td's are empty) [length 0]
                # - the descriptive rows (i.e. 'dollars in millions', 'fiscal year', etc.) [length 1]
                reg_row = list(filter(lambda x: x != "", reg_row))  # remove empty strings (table datas) from list
                reg_row = [re.sub(r'\n', '', x) for x in reg_row]

                if len(reg_row) <= 1:
                    continue

                # if 'th' tag found or table data with bold, then found the header of the table
                elif (len(row.find_all('th')) != 0 or is_bold(row, intable=True)) and not header_found:
                    header_found = True
                    # lambda tag: tag.name=='table' and tag.has_attr('id') and tag['id']=="Table1"
                    # make sure that table has a date header
                    reg_row = list(filter(fin_reg.date_regex.search, reg_row))

                    # if the table does not have a date as its headers, we're not interested in it, so move on to the next table
                    if len(reg_row) == 0:
                        # look ahead one row, maybe date in next, as long as bold (check Goldman Sachs example)
                        try:
                            if is_bold(rows[index+1], intable=True):
                                header_found = False
                                continue
                            not_useful.append(table_title)
                            break
                        except BaseException: # exception because no more next row, so move to next table
                            not_useful.append(table_title)
                            break

                    # otherwise, it is a relevant table, so we go to the next row
                    else:

                        if table_title not in all_in_one_dict.keys():
                            all_in_one_dict[table_title] = {}
                        # print(table)
                        # TODO have to skip yearly table if we're interested in quarterly statements and vice versa
                        #  then, we want only the tables for which two consecutive columns are separated by more than a quarter (for yearly)

                        # TODO better normalize date format (but can just use filing date)
                        columns = ['Keys'] + [re.sub(r'[,\d] |[, ]', ' ', x) for x in reg_row]
                        continue

            if header_found:

                reg_row = [ele.text.strip() for ele in row.find_all('td')]
                if len(reg_row) == 0:
                    continue

                current_left_margin = find_left_margin(reg_row, row.findAll('td')[0])

                # if it's a line
                if len(row.find_all(lambda tag: tag.has_attr('style') and ('border-bottom:solid' in tag['style']
                                                                           or 'border-top:solid' in tag['style']))) > 0:
                    continue
                # empty line
                elif len(''.join(reg_row).strip()) == 0:
                    continue

                try:
                    while current_left_margin <= indented_list[-1][0]:
                        # if there is bold, then master category
                        if current_left_margin == indented_list[-1][0]:
                            # TODO TEST MORE
                            if indented_list[-1][2]: # if last element of list is bold
                                if is_bold(row, intable=True, alltext=True): # if current row is bold
                                    # first_bolded_index = next(i for i, v in enumerate(indented_list) if v[2])
                                    # if first_bolded_index != len(indented_list)-1:
                                    #     indented_list.pop(first_bolded_index)
                                    indented_list.pop() # remove that last element of list
                                    break # and stop popping
                                else:
                                    break # otherwise, just subentry so don't pop
                        indented_list.pop()
                except:
                    pass

                reg_row = list(filter(lambda x: x != "", reg_row))  # remove empty strings (table datas) from list
                # remove table datas with '$', for some reason ')' gets its own table data, as well as ''

                try:
                    reg_row[0] = reg_row[0].replace(':', '').replace('\n', ' ')
                    reg_row = [reg_row[0]] + [re.sub(r'\(', '-', x) for x in reg_row[1:]]
                    reg_row = [reg_row[0]] + [re.sub(r',', '', x) for x in reg_row[1:]]
                    regex = re.compile(r'[^\$|^$|)]')
                    reg_row = [reg_row[0]] + list(filter(regex.search, reg_row[1:]))

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

                    indented_list.append((current_left_margin, reg_row[0], is_bold(row, intable=True, alltext=True)))
                except:
                    pass # usually shaded lines

                current_category = ':'.join([x[1] for x in indented_list])

                if len(reg_row) > 1: # not category column:
                    if current_category not in all_in_one_dict[table_title].keys():
                        all_in_one_dict[table_title][current_category] = reg_row[1]
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


def testing():
    url = 'https://www.sec.gov/Archives/edgar/data/789019/000119312508162768/d10k.htm'
    all_in_one_dict = scrape_html_tables_from_url(url)
    pprint(all_in_one_dict)
    df = pd.DataFrame(flatten_dict(all_in_one_dict).items(), columns=['Keys', 'Current Year']).set_index(['Keys'])
    pd.set_option('display.max_rows', 1000)
    normalize_tables(all_in_one_dict)

if __name__ == '__main__':
    financials_dictio = {}
    filings_dictio = get_filings_urls_second_layer('AAPL', '10-K')
    pprint(filings_dictio)
    for key, value in filings_dictio.items():
        for filing_date, link in value:
            try:
                financials_dictio[filing_date] = normalize_tables(scrape_tables_from_url(link))
            except Exception:
                traceback.print_exc()
    # pprint(financials_dictio)

    financials_dictio = {k: v for k, v in financials_dictio.items() if v is not None}
    # pprint(financials_dictio)

    balance_sheet_dict, income_statement_dict, cash_flow_statement_dict = {}, {}, {}
    columns = list(financials_dictio.keys())
    for key, value in financials_dictio.items():
        balance_sheet_dict[key] = {}
        income_statement_dict[key] = {}
        cash_flow_statement_dict[key] = {}
        for kk, vv in value.items():
            if re.search(fin_reg.balance_sheet_regex, kk, re.IGNORECASE):
                balance_sheet_dict[key][kk.split('_')[-1]] = vv
            elif re.search(fin_reg.income_statement_regex, kk, re.IGNORECASE):
                income_statement_dict[key][kk.split('_')[-1]] = vv
            elif re.search(fin_reg.cash_flow_statement_regex, kk, re.IGNORECASE):
                cash_flow_statement_dict[key][kk.split('_')[-1]] = vv

    print(pd.DataFrame.from_dict(balance_sheet_dict).to_string())
    # testing()
