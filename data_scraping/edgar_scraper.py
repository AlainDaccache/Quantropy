import collections
import math
import os
import re
import traceback
from datetime import datetime
from pprint import pprint
from time import sleep
import numpy as np
import pandas as pd
import requests
import unicodedata
from bs4 import BeautifulSoup, NavigableString
import data_scraping.regex_patterns as fin_reg
import data_scraping.unit_tests as test
import pandas_datareader.data as web
import config
import data_scraping.excel_helpers as excel
from pprint import pprint
import tabula

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
        'XBRL Links': [], # for new submissions
        'HTML Links': [], # if no XML, then we put HTML (for older submissions).
        'TXT Links': [] # if no HTML, then we put TXT (for even older submissions)
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
        siblings = head_divs[cell_index].next_siblings
        for sib in siblings:
            if isinstance(sib, NavigableString):
                continue
            else:
                period_of_report = sib.text
                break

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
        no_xml_link = True # TODO this is to include XML links as HTMLs to test HTML scraping, so remove when done
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
    try:
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
    file = 'https://blfblob.blob.core.windows.net/files/Library/Assets/Gallery/BLF/Publications/Annual%20Reports/BLF%20Reports/Download%202014%20Annual%20Report/2014-Annual-Report-Interactive%20version.pdf'
    tables = tabula.read_pdf(file, pages="4", multiple_tables=True)
    pprint(table.to_string() for table in tables)


def scrape_txt_tables_from_url(url):
    pass


def scrape_xbrl_tables_from_url(url):
    pass


def scrape_html_tables_from_url(url):

    response = requests.get(url)
    table = '''
    <div style="padding-left:0px;text-indent:0px;line-height:normal;padding-top:10px;"><table cellpadding="0" cellspacing="0" style="font-family:Times New Roman;font-size:10pt;margin-left:auto;margin-right:auto;width:100%;border-collapse:collapse;text-align:left;"><tbody><tr><td colspan="16"></td></tr><tr><td style="width:57%;"></td><td style="width:1%;"></td><td style="width:8%;"></td><td style="width:1%;"></td><td style="width:1%;"></td><td style="width:1%;"></td><td style="width:8%;"></td><td style="width:1%;"></td><td style="width:1%;"></td><td style="width:1%;"></td><td style="width:8%;"></td><td style="width:1%;"></td><td style="width:1%;"></td><td style="width:1%;"></td><td style="width:8%;"></td><td style="width:1%;"></td></tr><tr><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="7" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:center;font-size:8pt;"><font style="font-family:Arial;font-size:8pt;font-weight:bold;">Three Months Ended</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="7" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:center;font-size:8pt;"><font style="font-family:Arial;font-size:8pt;font-weight:bold;">Six Months Ended</font></div></td></tr><tr><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="7" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;border-bottom:1px solid #000000;"><div style="text-align:center;font-size:8pt;"><font style="font-family:Arial;font-size:8pt;font-weight:bold;">June 30,</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="7" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;border-bottom:1px solid #000000;"><div style="text-align:center;font-size:8pt;"><font style="font-family:Arial;font-size:8pt;font-weight:bold;">June 30,</font></div></td></tr><tr><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="3" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;border-bottom:1px solid #000000;"><div style="text-align:center;font-size:8pt;"><font style="font-family:Arial;font-size:8pt;font-weight:bold;">2015</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="3" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;border-bottom:1px solid #000000;"><div style="text-align:center;font-size:8pt;"><font style="font-family:Arial;font-size:8pt;font-weight:bold;">2016</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="3" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;border-bottom:1px solid #000000;"><div style="text-align:center;font-size:8pt;"><font style="font-family:Arial;font-size:8pt;font-weight:bold;">2015</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="3" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;border-bottom:1px solid #000000;"><div style="text-align:center;font-size:8pt;"><font style="font-family:Arial;font-size:8pt;font-weight:bold;">2016</font></div></td></tr><tr><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="15" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:center;font-size:8pt;"><font style="font-family:Arial;font-size:8pt;font-weight:bold;">(unaudited)</font></div></td></tr><tr><td style="vertical-align:bottom;background-color:#cceeff;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">Revenues</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;background-color:#cceeff;"><div style="text-align:left;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">$</font></div></td><td style="vertical-align:bottom;background-color:#cceeff;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">17,727</font></div></td><td style="vertical-align:bottom;background-color:#cceeff;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;background-color:#cceeff;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;background-color:#cceeff;"><div style="text-align:left;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">$</font></div></td><td style="vertical-align:bottom;background-color:#cceeff;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">21,500</font></div></td><td style="vertical-align:bottom;background-color:#cceeff;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;background-color:#cceeff;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;background-color:#cceeff;"><div style="text-align:left;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">$</font></div></td><td style="vertical-align:bottom;background-color:#cceeff;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">34,985</font></div></td><td style="vertical-align:bottom;background-color:#cceeff;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;background-color:#cceeff;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;background-color:#cceeff;"><div style="text-align:left;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">$</font></div></td><td style="vertical-align:bottom;background-color:#cceeff;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">41,757</font></div></td><td style="vertical-align:bottom;background-color:#cceeff;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td></tr><tr><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">Costs and expenses:</font></div></td><td colspan="3" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="3" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="3" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="3" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td></tr><tr><td style="vertical-align:bottom;background-color:#cceeff;padding-left:20px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">Cost of revenues</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#cceeff;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">6,583</font></div></td><td style="vertical-align:bottom;background-color:#cceeff;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;background-color:#cceeff;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#cceeff;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">8,130</font></div></td><td style="vertical-align:bottom;background-color:#cceeff;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;background-color:#cceeff;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#cceeff;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">12,939</font></div></td><td style="vertical-align:bottom;background-color:#cceeff;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;background-color:#cceeff;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#cceeff;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">15,778</font></div></td><td style="vertical-align:bottom;background-color:#cceeff;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td></tr><tr><td style="vertical-align:bottom;padding-left:20px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">Research and development</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">2,789</font></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">3,363</font></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">5,542</font></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">6,730</font></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td></tr><tr><td style="vertical-align:bottom;background-color:#cceeff;padding-left:20px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">Sales and marketing</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#cceeff;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">2,080</font></div></td><td style="vertical-align:bottom;background-color:#cceeff;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;background-color:#cceeff;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#cceeff;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">2,415</font></div></td><td style="vertical-align:bottom;background-color:#cceeff;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;background-color:#cceeff;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#cceeff;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">4,145</font></div></td><td style="vertical-align:bottom;background-color:#cceeff;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;background-color:#cceeff;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#cceeff;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">4,802</font></div></td><td style="vertical-align:bottom;background-color:#cceeff;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td></tr><tr><td style="vertical-align:bottom;padding-left:20px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">General and administrative</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;border-bottom:1px solid #000000;"><div style="text-align:right;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">1,450</font></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;border-bottom:1px solid #000000;"><div style="text-align:right;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">1,624</font></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;border-bottom:1px solid #000000;"><div style="text-align:right;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">3,087</font></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;border-bottom:1px solid #000000;"><div style="text-align:right;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">3,137</font></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td></tr><tr><td style="vertical-align:bottom;background-color:#cceeff;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">Total costs and expenses</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#cceeff;padding-left:2px;padding-top:2px;padding-bottom:2px;border-top:1px solid #000000;border-bottom:1px solid #000000;"><div style="text-align:right;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">12,902</font></div></td><td style="vertical-align:bottom;background-color:#cceeff;border-top:1px solid #000000;border-bottom:1px solid #000000;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;background-color:#cceeff;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#cceeff;padding-left:2px;padding-top:2px;padding-bottom:2px;border-top:1px solid #000000;border-bottom:1px solid #000000;"><div style="text-align:right;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">15,532</font></div></td><td style="vertical-align:bottom;background-color:#cceeff;border-top:1px solid #000000;border-bottom:1px solid #000000;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;background-color:#cceeff;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#cceeff;padding-left:2px;padding-top:2px;padding-bottom:2px;border-top:1px solid #000000;border-bottom:1px solid #000000;"><div style="text-align:right;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">25,713</font></div></td><td style="vertical-align:bottom;background-color:#cceeff;border-top:1px solid #000000;border-bottom:1px solid #000000;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;background-color:#cceeff;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#cceeff;padding-left:2px;padding-top:2px;padding-bottom:2px;border-top:1px solid #000000;border-bottom:1px solid #000000;"><div style="text-align:right;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">30,447</font></div></td><td style="vertical-align:bottom;background-color:#cceeff;border-top:1px solid #000000;border-bottom:1px solid #000000;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td></tr><tr><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">Income from operations</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;border-top:1px solid #000000;"><div style="text-align:right;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">4,825</font></div></td><td style="vertical-align:bottom;border-top:1px solid #000000;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;border-top:1px solid #000000;"><div style="text-align:right;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">5,968</font></div></td><td style="vertical-align:bottom;border-top:1px solid #000000;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;border-top:1px solid #000000;"><div style="text-align:right;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">9,272</font></div></td><td style="vertical-align:bottom;border-top:1px solid #000000;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;border-top:1px solid #000000;"><div style="text-align:right;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">11,310</font></div></td><td style="vertical-align:bottom;border-top:1px solid #000000;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td></tr><tr><td style="vertical-align:bottom;background-color:#cceeff;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">Other income (expense), net</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#cceeff;padding-left:2px;padding-top:2px;padding-bottom:2px;border-bottom:1px solid #000000;"><div style="text-align:right;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">131</font></div></td><td style="vertical-align:bottom;background-color:#cceeff;border-bottom:1px solid #000000;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;background-color:#cceeff;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#cceeff;padding-left:2px;padding-top:2px;padding-bottom:2px;border-bottom:1px solid #000000;"><div style="text-align:right;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">151</font></div></td><td style="vertical-align:bottom;background-color:#cceeff;border-bottom:1px solid #000000;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;background-color:#cceeff;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#cceeff;padding-left:2px;padding-top:2px;padding-bottom:2px;border-bottom:1px solid #000000;"><div style="text-align:right;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">288</font></div></td><td style="vertical-align:bottom;background-color:#cceeff;border-bottom:1px solid #000000;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;background-color:#cceeff;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#cceeff;padding-left:2px;padding-top:2px;padding-bottom:2px;border-bottom:1px solid #000000;"><div style="text-align:right;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">(62</font></div></td><td style="vertical-align:bottom;background-color:#cceeff;padding-right:2px;padding-top:2px;padding-bottom:2px;border-bottom:1px solid #000000;"><div style="text-align:left;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">)</font></div></td></tr><tr><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">Income before income taxes </font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;border-top:1px solid #000000;"><div style="text-align:right;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">4,956</font></div></td><td style="vertical-align:bottom;border-top:1px solid #000000;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;border-top:1px solid #000000;"><div style="text-align:right;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">6,119</font></div></td><td style="vertical-align:bottom;border-top:1px solid #000000;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;border-top:1px solid #000000;"><div style="text-align:right;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">9,560</font></div></td><td style="vertical-align:bottom;border-top:1px solid #000000;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;border-top:1px solid #000000;"><div style="text-align:right;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">11,248</font></div></td><td style="vertical-align:bottom;border-top:1px solid #000000;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td></tr><tr><td style="vertical-align:bottom;background-color:#cceeff;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">Provision for income taxes</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#cceeff;padding-left:2px;padding-top:2px;padding-bottom:2px;border-bottom:1px solid #000000;"><div style="text-align:right;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">1,025</font></div></td><td style="vertical-align:bottom;background-color:#cceeff;border-bottom:1px solid #000000;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;background-color:#cceeff;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#cceeff;padding-left:2px;padding-top:2px;padding-bottom:2px;border-bottom:1px solid #000000;"><div style="text-align:right;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">1,242</font></div></td><td style="vertical-align:bottom;background-color:#cceeff;border-bottom:1px solid #000000;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;background-color:#cceeff;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#cceeff;padding-left:2px;padding-top:2px;padding-bottom:2px;border-bottom:1px solid #000000;"><div style="text-align:right;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">2,114</font></div></td><td style="vertical-align:bottom;background-color:#cceeff;border-bottom:1px solid #000000;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;background-color:#cceeff;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#cceeff;padding-left:2px;padding-top:2px;padding-bottom:2px;border-bottom:1px solid #000000;"><div style="text-align:right;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">2,164</font></div></td><td style="vertical-align:bottom;background-color:#cceeff;border-bottom:1px solid #000000;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td></tr><tr><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">Net income</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;border-top:1px solid #000000;"><div style="text-align:left;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">$</font></div></td><td style="vertical-align:bottom;padding-top:2px;padding-bottom:2px;border-top:1px solid #000000;"><div style="text-align:right;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">3,931</font></div></td><td style="vertical-align:bottom;border-top:1px solid #000000;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;border-top:1px solid #000000;"><div style="text-align:left;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">$</font></div></td><td style="vertical-align:bottom;padding-top:2px;padding-bottom:2px;border-top:1px solid #000000;"><div style="text-align:right;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">4,877</font></div></td><td style="vertical-align:bottom;border-top:1px solid #000000;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;border-top:1px solid #000000;"><div style="text-align:left;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">$</font></div></td><td style="vertical-align:bottom;padding-top:2px;padding-bottom:2px;border-top:1px solid #000000;"><div style="text-align:right;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">7,446</font></div></td><td style="vertical-align:bottom;border-top:1px solid #000000;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;border-top:1px solid #000000;"><div style="text-align:left;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">$</font></div></td><td style="vertical-align:bottom;padding-top:2px;padding-bottom:2px;border-top:1px solid #000000;"><div style="text-align:right;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">9,084</font></div></td><td style="vertical-align:bottom;border-top:1px solid #000000;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td></tr><tr><td style="vertical-align:bottom;background-color:#cceeff;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">Less: Adjustment Payment to Class C capital stockholders</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#cceeff;padding-left:2px;padding-top:2px;padding-bottom:2px;border-top:3px double #000000;border-bottom:1px solid #000000;"><div style="text-align:right;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">522</font></div></td><td style="vertical-align:bottom;background-color:#cceeff;border-top:3px double #000000;border-bottom:1px solid #000000;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;background-color:#cceeff;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#cceeff;padding-left:2px;padding-top:2px;padding-bottom:2px;border-top:3px double #000000;border-bottom:1px solid #000000;"><div style="text-align:right;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">0</font></div></td><td style="vertical-align:bottom;background-color:#cceeff;border-top:3px double #000000;border-bottom:1px solid #000000;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;background-color:#cceeff;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#cceeff;padding-left:2px;padding-top:2px;padding-bottom:2px;border-top:3px double #000000;border-bottom:1px solid #000000;"><div style="text-align:right;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">522</font></div></td><td style="vertical-align:bottom;background-color:#cceeff;border-top:3px double #000000;border-bottom:1px solid #000000;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;background-color:#cceeff;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#cceeff;padding-left:2px;padding-top:2px;padding-bottom:2px;border-top:3px double #000000;border-bottom:1px solid #000000;"><div style="text-align:right;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">0</font></div></td><td style="vertical-align:bottom;background-color:#cceeff;border-top:3px double #000000;border-bottom:1px solid #000000;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td></tr><tr><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">Net income available to all stockholders</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;border-bottom:3px double #000000;"><div style="text-align:left;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">$</font></div></td><td style="vertical-align:bottom;padding-top:2px;padding-bottom:2px;border-bottom:3px double #000000;"><div style="text-align:right;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">3,409</font></div></td><td style="vertical-align:bottom;border-bottom:3px double #000000;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;border-bottom:3px double #000000;"><div style="text-align:left;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">$</font></div></td><td style="vertical-align:bottom;padding-top:2px;padding-bottom:2px;border-bottom:3px double #000000;"><div style="text-align:right;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">4,877</font></div></td><td style="vertical-align:bottom;border-bottom:3px double #000000;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;border-bottom:3px double #000000;"><div style="text-align:left;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">$</font></div></td><td style="vertical-align:bottom;padding-top:2px;padding-bottom:2px;border-bottom:3px double #000000;"><div style="text-align:right;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">6,924</font></div></td><td style="vertical-align:bottom;border-bottom:3px double #000000;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;border-bottom:3px double #000000;"><div style="text-align:left;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">$</font></div></td><td style="vertical-align:bottom;padding-top:2px;padding-bottom:2px;border-bottom:3px double #000000;"><div style="text-align:right;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">9,084</font></div></td><td style="vertical-align:bottom;border-bottom:3px double #000000;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td></tr><tr><td style="vertical-align:bottom;background-color:#cceeff;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;height:20px;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="3" style="vertical-align:bottom;background-color:#cceeff;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;border-top:3px double #000000;"><div style="overflow:hidden;height:20px;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;background-color:#cceeff;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;height:20px;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="3" style="vertical-align:bottom;background-color:#cceeff;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;border-top:3px double #000000;"><div style="overflow:hidden;height:20px;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;background-color:#cceeff;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;height:20px;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="3" style="vertical-align:bottom;background-color:#cceeff;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;border-top:3px double #000000;"><div style="overflow:hidden;height:20px;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;background-color:#cceeff;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;height:20px;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="3" style="vertical-align:bottom;background-color:#cceeff;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;border-top:3px double #000000;"><div style="overflow:hidden;height:20px;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td></tr><tr><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">Basic net income per share of Class A and B common stock</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">$</font></div></td><td style="vertical-align:bottom;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">4.99</font></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">$</font></div></td><td style="vertical-align:bottom;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">7.11</font></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">$</font></div></td><td style="vertical-align:bottom;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">10.15</font></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">$</font></div></td><td style="vertical-align:bottom;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">13.23</font></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td></tr><tr><td style="vertical-align:bottom;background-color:#cceeff;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">Basic net income per share of Class C capital stock</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;background-color:#cceeff;"><div style="text-align:left;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">$</font></div></td><td style="vertical-align:bottom;background-color:#cceeff;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">6.51</font></div></td><td style="vertical-align:bottom;background-color:#cceeff;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;background-color:#cceeff;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;background-color:#cceeff;"><div style="text-align:left;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">$</font></div></td><td style="vertical-align:bottom;background-color:#cceeff;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">7.11</font></div></td><td style="vertical-align:bottom;background-color:#cceeff;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;background-color:#cceeff;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;background-color:#cceeff;"><div style="text-align:left;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">$</font></div></td><td style="vertical-align:bottom;background-color:#cceeff;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">11.68</font></div></td><td style="vertical-align:bottom;background-color:#cceeff;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;background-color:#cceeff;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;background-color:#cceeff;"><div style="text-align:left;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">$</font></div></td><td style="vertical-align:bottom;background-color:#cceeff;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">13.23</font></div></td><td style="vertical-align:bottom;background-color:#cceeff;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td></tr><tr><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;height:20px;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="3" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;height:20px;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;height:20px;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="3" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;height:20px;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;height:20px;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="3" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;height:20px;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;height:20px;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="3" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;height:20px;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td></tr><tr><td style="vertical-align:bottom;background-color:#cceeff;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">Diluted net income per share of Class A and B common stock</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;background-color:#cceeff;"><div style="text-align:left;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">$</font></div></td><td style="vertical-align:bottom;background-color:#cceeff;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">4.93</font></div></td><td style="vertical-align:bottom;background-color:#cceeff;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;background-color:#cceeff;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;background-color:#cceeff;"><div style="text-align:left;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">$</font></div></td><td style="vertical-align:bottom;background-color:#cceeff;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">7.00</font></div></td><td style="vertical-align:bottom;background-color:#cceeff;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;background-color:#cceeff;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;background-color:#cceeff;"><div style="text-align:left;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">$</font></div></td><td style="vertical-align:bottom;background-color:#cceeff;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">10.03</font></div></td><td style="vertical-align:bottom;background-color:#cceeff;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;background-color:#cceeff;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;background-color:#cceeff;"><div style="text-align:left;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">$</font></div></td><td style="vertical-align:bottom;background-color:#cceeff;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">13.01</font></div></td><td style="vertical-align:bottom;background-color:#cceeff;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td></tr><tr><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">Diluted net income per share of Class C capital stock</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">$</font></div></td><td style="vertical-align:bottom;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">6.43</font></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">$</font></div></td><td style="vertical-align:bottom;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">7.00</font></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">$</font></div></td><td style="vertical-align:bottom;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">11.53</font></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">$</font></div></td><td style="vertical-align:bottom;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:10pt;"><font style="font-family:Arial;font-size:10pt;">13.01</font></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td></tr></tbody></table></div>
    '''
    soup = BeautifulSoup(response.text, 'html.parser')
    all_in_one_dict = {}

    for table in soup.findAll('table'):
        columns = []
        dates = []
        header_found = False
        indented_list = []
        rows = table.find_all('tr')
        header_index = 0
        table_title, table_currency, table_multiplier = '', '', ''

        for index, row in enumerate(rows):

            reg_row = [ele.text.strip() for ele in row.find_all(lambda tag: tag.name == 'td' or tag.name == 'th')]
            reg_row = [unicodedata.normalize("NFKD", x) for x in reg_row]
            reg_row[0] = reg_row[0].replace(':', '').replace('\n', ' ') if len(reg_row) > 0 else reg_row[0]




            # first, we want to reach the header of the table, so we skip
            # - the empty rows i.e. those that have no table data 'td' (or those for which the td's are empty) [length 0]
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
                    try:

                        # first_bolded_index = next(i for i, v in enumerate(indented_list) if v[2])

                        dates = [int(re.search(r'^(?:.*?)((?:19|20)\d{2})(?:.*?)$', x).groups()[0])
                                 for x in columns
                                 if re.search(r'^(?:.*?)((?:19|20)\d{2})(?:.*?)$', x)]
                        max_year = max(dates)
                        current_date_index = next(i for i, v in enumerate(columns) if re.search('^(?!.*six)(?=.*{})'.format(max_year), v, re.IGNORECASE))
                    except:
                        continue

                    header_index = index

                    # sometimes same title (i.e. if table is split in two pages, they repeat page title twice
                    table_multiplier, table_currency = find_meta_table_info(table)
                    table_title = unicodedata.normalize("NFKD",  find_table_title(table)).strip().replace('\n', '')
                    if table_multiplier == 'percentage':
                        break

                    if table_title not in all_in_one_dict.keys():
                        all_in_one_dict[table_title] = {}

                    if len(dates) > 0:
                        header_found = True

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
                reg_row = [reg_row[0]] + [re.sub("[^0-9\-]", "", r) for r in reg_row[1:]]
                reg_row = [reg_row[0]] + [re.sub("^-$", "", r) for r in reg_row[1:]] # for NOT the minus sign
                reg_row = [reg_row[0]] + [re.sub(r',', '', x) for x in reg_row[1:]]
                reg_row = list(filter(lambda x: x != "", reg_row))
                # if len(reg_row) < len(indices): # TODO for now, skipping when there is a missing value
                #     continue
                # print(indices)


            # if re.compile('%.|.%'), catch index to skip all column
                # if it's a line
                if len(row.find_all(lambda tag: tag.has_attr('style') and ('border-bottom:solid' in tag['style']
                                                                           or 'border-top:solid' in tag['style']))) > 0:
                    continue
                # empty line
                elif len(''.join(reg_row).strip()) == 0:
                    continue
                current_left_margin = 0
                try:
                    current_left_margin = find_left_margin(reg_row, row.findAll('td')[0])
                except:
                    traceback.print_exc()
                while len(indented_list) > 0 and current_left_margin <= indented_list[-1][0]:
                    # if there is bold, then master category
                    if current_left_margin == indented_list[-1][0]:
                        # TODO TEST MORE
                        # TOOD if the element finishes with ':', then category. if indented_list[-1][1].
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
                            if dates[0] > dates[-1]:
                                max_date_index = 1
                            else:
                                max_date_index = -1
                            all_in_one_dict[table_title][current_category] = float(re.sub('^$', '0', reg_row[max_date_index])) # TODO FIX

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
def normalization_first_level(input_dict, filing_type):
    pprint(input_dict)
    master_dict = {} # do OrderedDict()
    for normalized_category, pattern_string in flatten_dict(fin_reg.financial_entries_regex_dict).items():
        master_dict[normalized_category] = np.nan
    visited_data_names = []
    for title, table in input_dict.items():

        for scraped_name, scraped_value in flatten_dict(table).items():
            found_match = False # JUST FOR DEBUGGING PURPOSES

            for normalized_category, pattern_string in flatten_dict(fin_reg.financial_entries_regex_dict).items():

                if ('Balance Sheet' in normalized_category.split('_')[0] and re.search(fin_reg.balance_sheet_regex, title, re.IGNORECASE))\
                        or ('Income Statement' in normalized_category.split('_')[0] and re.search(fin_reg.income_statement_regex, title, re.IGNORECASE))\
                        or ('Cash Flow Statement' in normalized_category.split('_')[0] and re.search(fin_reg.cash_flow_statement_regex, title, re.IGNORECASE) ):
                    # first we want to give priority to the elements in the consolidated financial statements


                    if re.search('^(?!.*{})'.format('Year' if filing_type=='10-Q' else 'Quarter') + pattern_string, title+'_'+scraped_name, re.IGNORECASE):
                        found_match = True # for debugging, can remove later

                        # The idea is that if we go to another table and we have a value similar to one we already have on the sheet,
                        # i do not want to include it (because its a duplicate). But if the value is similar in the same sheet, then
                        # i want to add it to the already existing value
                        if math.isnan(master_dict[normalized_category]):
                            visited_data_names.append(title+'_'+pattern_string)
                        if title+'_'+pattern_string in visited_data_names:
                            master_dict[normalized_category] = np.nan_to_num(master_dict[normalized_category]) + scraped_value

                        if 'Allowances for Doubtful Accounts' in normalized_category:
                            groups = re.search(pattern_string, scraped_name, re.IGNORECASE).groups()
                            master_dict[normalized_category] = float(groups[-1])
                            continue
                        else:
                            break

            if not found_match and (re.search(fin_reg.balance_sheet_regex, scraped_name, re.IGNORECASE)
                                    or re.search(fin_reg.income_statement_regex, scraped_name, re.IGNORECASE)
                                    or re.search(fin_reg.cash_flow_statement_regex, scraped_name, re.IGNORECASE)):
                print('No match for ' + scraped_name)

    return master_dict

def normalization_second_level(input_dict, master_dict, filing_type):
    # OTher normalizations should only work on null (0, empty) values! Cannot fill twice from different tables otherwise will add up
    #                 for cat in normalized_category.split('_')[1:-1]:
    #                     category_regexed.append('(?=.*{})'.format(cat))
    #                 # last_cat = normalized_category.split('_')[-1]
    #                 pattern_string = r'(' + '|'.join(category_regexed) + r').*^' + pattern_string

    visited_data_names = []
    for title, table in input_dict.items():

        for scraped_name, scraped_value in flatten_dict(table).items():

            for normalized_category, pattern_string in flatten_dict(fin_reg.financial_entries_regex_dict).items():

                if not re.search(fin_reg.balance_sheet_regex, title, re.IGNORECASE) \
                        and not re.search(fin_reg.income_statement_regex, title, re.IGNORECASE) \
                        and not re.search(fin_reg.cash_flow_statement_regex, title, re.IGNORECASE):
                    # first we want to give priority to the elements in the consolidated financial statements

                    if re.search('^(?!.*{})'.format('Year' if filing_type=='10-Q' else 'Quarter') + pattern_string, title+'_'+scraped_name, re.IGNORECASE):
                        # The idea is that if we go to another table and we have a value similar to one we already have on the sheet,
                        # i do not want to include it (because its a duplicate). But if the value is similar in the same sheet, then
                        # i want to add it to the already existing value
                        if math.isnan(master_dict[normalized_category]):
                            visited_data_names.append(title+'_'+pattern_string)
                            if title+'_'+pattern_string in visited_data_names:
                                master_dict[normalized_category] = np.nan_to_num(master_dict[normalized_category]) + scraped_value

    return master_dict


def normalizatation_third_level(input_dict, filing_type):
    pass


def normalize_tables(input_dict, filing_type):
    master_dict = normalization_first_level(input_dict, filing_type)
    master_dict = normalization_second_level(input_dict, master_dict, filing_type)
    # master_dict = normalizatation_third_level(master_dict)

    master_dict['Balance Sheet_Assets_Current Assets_Accounts Receivable_Gross Accounts Receivable'] = \
        master_dict['Balance Sheet_Assets_Current Assets_Accounts Receivable_Net Accounts Receivable'] + \
        master_dict['Balance Sheet_Assets_Current Assets_Accounts Receivable_Allowances for Doubtful Accounts'] + \
        master_dict['Balance Sheet_Assets_Current Assets_Accounts Receivable_Other Receivables']


    # balance_sheet = {i: master_dict[i] for i in master_dict.keys() if re.search(r'Balance Sheet', i)}
    # income_statement = {i: master_dict[i] for i in master_dict.keys() if re.search(r'Income Statement', i)}
    # cash_flow_statement = {i: master_dict[i] for i in master_dict.keys() if re.search(r'Cash Flow Statement', i)}
    return master_dict


def testing():
    url = 'https://www.sec.gov/Archives/edgar/data/1288776/000165204416000012/goog10-k2015.htm#s2E5F35311DA23B0DA721CA5152B6CA6D'
    # all_in_one_dict = scrape_html_tables_from_url(url)
    # pprint(all_in_one_dict)
    # all_in_one_dict = test.aapl_dict
    # pprint(all_in_one_dict)
    gs_dict = {}
    pprint(normalize_tables(gs_dict, filing_type='10-K'))


def scrape_financial_statements(ticker, filing_type):
    financials_dictio = {}
    cik = get_company_cik(ticker)
    doc_links = get_filings_urls_first_layer(cik, filing_type)
    filings_dictio = get_filings_urls_second_layer(filing_type, doc_links)
    pprint(filings_dictio)
    names = ['{} {}'.format(name, filing_type) for name in [config.balance_sheet_name, config.income_statement_name, config.cash_flow_statement_name]]
    output = pd.Series()
    for sheet_name in names:
        output[sheet_name] = (excel.read_dates_from_csv(ticker, sheet_name),
                              excel.read_df_from_csv(ticker, sheet_name))
    existing_dates_with_df = excel.read_dates_from_csv(ticker, names)
    # output[sheet_name] = (dates, df)

    if len(existing_dates_with_df) > 0:
        missing_dates_links = [(x, y) for x, y in filings_dictio['HTML Links']
                               if datetime.strptime(x, '%Y-%m-%d') not in existing_dates_with_df[names[0]][0]]
    else:
        missing_dates_links = [(x, y) for x, y in filings_dictio['HTML Links']]

    for index, (filing_date, link) in enumerate(missing_dates_links):
        try:
            print(filing_date, link)
            financials_dictio[filing_date] = normalize_tables(scrape_tables_from_url(link), filing_type=filing_type)
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

    if not os.path.exists(config.financial_statements_folder_path):
        os.makedirs(config.financial_statements_folder_path)

    financial_statements_file_path = "{}/{}.xlsx".format(config.financial_statements_folder_path, ticker)

    for sheet_name, dict in zip(names,
                                [balance_sheet_dict, income_statement_dict, cash_flow_statement_dict]):
        df = pd.DataFrame.from_dict(dict)
        if len(existing_dates_with_df) > 0:
            df = pd.concat([df, existing_dates_with_df[sheet_name][1]], axis=1).fillna(0)
        df.dropna(axis=0, how='all', inplace=True)
        df = df.loc[:, df.any()]
        excel.save_into_csv(ticker, df, sheet_name)


def scrape_stock_prices(stock, start=datetime(1970, 1, 1), end=datetime.now()):
    df = web.DataReader(stock.replace('.', '-'), data_source='yahoo', start=start, end=end)
    # df['Date']
    excel.save_into_csv(stock, df, config.stock_prices_sheet_name)


if __name__ == '__main__':
    company_tickers = ['AAPL', 'GOOG', 'FB', 'AMZN', 'TSLA', 'NFLX',
                       'MS', 'JPM', 'WFC', 'C', 'BAC',
                       'KO', 'PG', 'JNJ', 'PEP', 'VZ', 'GS']
    for ticker in company_tickers:
        scrape_stock_prices(ticker)
        scrape_financial_statements(ticker, '10-K')
    # testing()