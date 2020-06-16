import collections
import re
import traceback
from pprint import pprint
import pandas as pd
import requests
import unicodedata
from bs4 import BeautifulSoup, NavigableString
from sec_scraping.scraping_regexes import date_regex
import sec_scraping.sec_scraping_unit_tests as test

'''
Beautiful BeautifulSoup Usage

html = urllib2.urlopen(url).read()
bs = BeautifulSoup(html)
table = bs.find(lambda tag: tag.name=='table' and tag.has_attr('id') and tag['id']=="Table1") 
rows = table.findAll(lambda tag: tag.name=='tr')
'''

def is_bold(row, intable, alltext=False):
    bolded_row_text = row.find_all(lambda tag: tag.has_attr('style') and re.search('bold', str(tag['style'])))
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
        return len(row.find_all(lambda tag: tag.name != 'table' and tag.has_attr('style') and re.search('bold', str(tag['style'])))) > 0

def is_italic(row):
    return len(row.find_all(lambda tag: tag.name=='b' or tag.name=='i')) > 0

def find_left_margin(td):
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

def find_table_title(current_element):
    # sometimes the previous element is a new line metacharacter (&nbsp or encoded as '\n') so skip
        if isinstance(current_element, NavigableString):
            return find_table_title(current_element.previous_element)
        elif current_element.name == 'div':
            return find_table_title(current_element.previous_element)
        # stop when you've found another table (don't want to confuse both titles)
        elif len(current_element.find_all('table')) > 0:
            # TODO some tables have titles above but they are in themselves tables
            for row in current_element.find('table').find_all('tr'):
                if len(re.findall(re.compile(r'\d{4}'), row.text)) > 1:
                    return None

        # found bold or italic element
        elif is_bold(current_element, intable=False):
            if is_italic(current_element):
                # sometimes the previous element is a detail of the title (i.e. (in thousands)), usually bracketed
                if re.search('^\((.*?)\)$', current_element.text.strip()): #
                    return find_table_title(current_element.previous_element)
                else:
                    return current_element.text
        else:
            return find_table_title(current_element.previous_element)

def find_table_unit(table):
    unit_dict = {'thousands': 1000, 'millions': 1000000, 'billions': 1000000000}
    for unit in unit_dict.keys():
        if unit in table.text: # TODO, unit might also be outside the table, above it (but below [and including] title)
            return unit_dict[unit]
    return unit_dict['millions'] # default


url = 'https://www.sec.gov/Archives/edgar/data/789019/000156459019027952/msft-10k_20190630.htm'
response = requests.get(url)
soup = BeautifulSoup(test.html_test12, 'html.parser')

not_useful = [] # for debugging
all_in_one_dict = {} # TODO gotta make nested dictionary, with table name -> category -> entry name: entry data for year

# TODO override table multiplier if in row label it's written 'thousands' etc.

# TODO debug page 76 https://www.sec.gov/Archives/edgar/data/886982/000095012310018464/y81914e10vk.htm

for table in soup.findAll('table'):

    columns = []
    header_found = False
    current_category = ''
    previous_left_margin = 0
    indented_list = []
    rows = table.find_all('tr')
    try:
        table_title = unicodedata.normalize("NFKD",
                                            find_table_title(table.previous_element)).strip().replace('\n', '')
    except: # when table title is none
        table_title = 'No Table Title'

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
                reg_row = list(filter(date_regex.search, reg_row))

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
            current_left_margin = find_left_margin(row.findAll('td')[0])

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

def flatten(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

pprint(all_in_one_dict)
df = pd.DataFrame(flatten(all_in_one_dict).items(), columns=['Keys', 'Current Year']).set_index(['Keys'])
pd.set_option('display.max_rows', 1000)
pprint(not_useful)
# print(df.to_string())

