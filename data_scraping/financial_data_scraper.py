import collections
import math
import os
import re
import traceback
import urllib.request
import zipfile
from datetime import datetime, timedelta
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
import data_scraping.excel_helpers as excel
from pprint import pprint
import tabula
import ta
import config
from titlecase import titlecase
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver


# TODO format excel for categories (re-format multi-index)


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
    pattern_match = re.findall('(margin-left|padding-left):(\d+)', str(td))
    if len(pattern_match) > 0:
        return sum([float(m[-1]) for m in pattern_match])

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
    file = 'https://reports.shell.com/annual-report/2019/servicepages/downloads/files/shell_annual_report_2019.pdf'
    tables = tabula.read_pdf(file, pages=196)
    pprint(table.to_string() for table in tables)


def scrape_txt_tables_from_url(url):
    pass


def scrape_xbrl_tables_from_url(url):
    pass


def scrape_html_tables_from_url(url):

    response = requests.get(url)
    table = '''<div style="line-height:120%;padding-top:16px;text-align:center;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;font-weight:bold;">CONSOLIDATED STATEMENTS OF CASH FLOWS</font></div>
    <div style="line-height:120%;text-align:center;font-size:10pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">(In millions)</font><div style="padding-left:0px;text-indent:0px;line-height:normal;padding-top:10px;"><table cellpadding="0" cellspacing="0" style="font-family:Times New Roman;font-size:10pt;margin-left:auto;margin-right:auto;width:100%;border-collapse:collapse;text-align:left;"><tbody><tr><td colspan="12"></td></tr><tr><td style="width:59%;"></td><td style="width:1%;"></td><td style="width:11%;"></td><td style="width:1%;"></td><td style="width:1%;"></td><td style="width:1%;"></td><td style="width:11%;"></td><td style="width:1%;"></td><td style="width:1%;"></td><td style="width:1%;"></td><td style="width:11%;"></td><td style="width:1%;"></td></tr><tr><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="11" style="vertical-align:bottom;border-bottom:1px solid #000000;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:center;font-size:8pt;"><font style="font-family:Helvetica,sans-serif;font-size:8pt;font-weight:bold;">Years ended</font></div></td></tr><tr><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="3" style="vertical-align:bottom;border-bottom:1px solid #000000;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:center;font-size:8pt;"><font style="font-family:Helvetica,sans-serif;font-size:8pt;font-weight:bold;">September&nbsp;29, <br>2018</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="3" style="vertical-align:bottom;border-bottom:1px solid #000000;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:center;font-size:8pt;"><font style="font-family:Helvetica,sans-serif;font-size:8pt;font-weight:bold;">September&nbsp;30, <br>2017</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="3" style="vertical-align:bottom;border-bottom:1px solid #000000;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:center;font-size:8pt;"><font style="font-family:Helvetica,sans-serif;font-size:8pt;font-weight:bold;">September&nbsp;24, <br>2016</font></div></td></tr><tr><td style="vertical-align:top;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">Cash and cash equivalents, beginning of the year</font></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;padding-left:2px;padding-top:2px;padding-bottom:2px;border-top:1px solid #000000;"><div style="text-align:left;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">$</font></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;padding-top:2px;padding-bottom:2px;border-top:1px solid #000000;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">20,289</font></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;border-top:1px solid #000000;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;padding-left:2px;padding-top:2px;padding-bottom:2px;border-top:1px solid #000000;"><div style="text-align:left;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">$</font></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;padding-top:2px;padding-bottom:2px;border-top:1px solid #000000;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">20,484</font></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;border-top:1px solid #000000;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;padding-left:2px;padding-top:2px;padding-bottom:2px;border-top:1px solid #000000;"><div style="text-align:left;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">$</font></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;padding-top:2px;padding-bottom:2px;border-top:1px solid #000000;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">21,120</font></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;border-top:1px solid #000000;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td></tr><tr><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">Operating activities:</font></div></td><td colspan="3" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="3" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="3" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td></tr><tr><td style="vertical-align:top;padding-left:12px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">Net income</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">59,531</font></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">48,351</font></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">45,687</font></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td></tr><tr><td style="vertical-align:top;background-color:#efefef;padding-left:12px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">Adjustments to reconcile net income to cash generated by operating activities:</font></div></td><td colspan="3" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="3" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="3" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td></tr><tr><td style="vertical-align:top;padding-left:28px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">Depreciation and amortization</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">10,903</font></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">10,157</font></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">10,505</font></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td></tr><tr><td style="vertical-align:top;background-color:#efefef;padding-left:28px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">Share-based compensation expense</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">5,340</font></div></td><td style="vertical-align:bottom;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">4,840</font></div></td><td style="vertical-align:bottom;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">4,210</font></div></td><td style="vertical-align:bottom;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td></tr><tr><td style="vertical-align:top;padding-left:28px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">Deferred income tax expense/(benefit)</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">(32,590</font></div></td><td style="vertical-align:bottom;padding-right:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">)</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">5,966</font></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">4,938</font></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td></tr><tr><td style="vertical-align:top;background-color:#efefef;padding-left:28px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">Other</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">(444</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-right:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">)</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">(166</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-right:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">)</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">486</font></div></td><td style="vertical-align:bottom;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td></tr><tr><td style="vertical-align:top;padding-left:12px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">Changes in operating assets and liabilities:</font></div></td><td colspan="3" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="3" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="3" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td></tr><tr><td style="vertical-align:top;background-color:#efefef;padding-left:28px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">Accounts receivable, net</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">(5,322</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-right:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">)</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">(2,093</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-right:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">)</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">527</font></div></td><td style="vertical-align:bottom;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td></tr><tr><td style="vertical-align:top;padding-left:28px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">Inventories</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">828</font></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">(2,723</font></div></td><td style="vertical-align:bottom;padding-right:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">)</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">217</font></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td></tr><tr><td style="vertical-align:top;background-color:#efefef;padding-left:28px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">Vendor non-trade receivables</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">(8,010</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-right:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">)</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">(4,254</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-right:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">)</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">(51</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-right:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">)</font></div></td></tr><tr><td style="vertical-align:top;padding-left:28px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">Other current and non-current assets</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">(423</font></div></td><td style="vertical-align:bottom;padding-right:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">)</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">(5,318</font></div></td><td style="vertical-align:bottom;padding-right:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">)</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">1,055</font></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td></tr><tr><td style="vertical-align:top;background-color:#efefef;padding-left:28px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">Accounts payable</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">9,175</font></div></td><td style="vertical-align:bottom;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">8,966</font></div></td><td style="vertical-align:bottom;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">2,117</font></div></td><td style="vertical-align:bottom;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td></tr><tr><td style="vertical-align:top;padding-left:28px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">Deferred revenue</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">(44</font></div></td><td style="vertical-align:bottom;padding-right:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">)</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">(626</font></div></td><td style="vertical-align:bottom;padding-right:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">)</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">(1,554</font></div></td><td style="vertical-align:bottom;padding-right:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">)</font></div></td></tr><tr><td style="vertical-align:top;background-color:#efefef;padding-left:28px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">Other current and non-current liabilities</font></div></td><td colspan="2" style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">38,490</font></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">1,125</font></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">(1,906</font></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;padding-right:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">)</font></div></td></tr><tr><td style="vertical-align:top;padding-left:44px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">Cash generated by operating activities</font></div></td><td colspan="2" style="vertical-align:bottom;border-bottom:1px solid #000000;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">77,434</font></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;"><br></font></div></td><td colspan="2" style="vertical-align:bottom;border-bottom:1px solid #000000;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">64,225</font></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;"><br></font></div></td><td colspan="2" style="vertical-align:bottom;border-bottom:1px solid #000000;padding-left:2px;padding-top:2px;padding-bottom:2px;border-top:1px solid #000000;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">66,231</font></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;border-top:1px solid #000000;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td></tr><tr><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">Investing activities:</font></div></td><td colspan="3" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="3" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="3" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td></tr><tr><td style="vertical-align:top;padding-left:12px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">Purchases of marketable securities</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">(71,356</font></div></td><td style="vertical-align:bottom;padding-right:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">)</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">(159,486</font></div></td><td style="vertical-align:bottom;padding-right:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">)</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">(142,428</font></div></td><td style="vertical-align:bottom;padding-right:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">)</font></div></td></tr><tr><td style="vertical-align:top;background-color:#efefef;padding-left:12px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">Proceeds from maturities of marketable securities</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">55,881</font></div></td><td style="vertical-align:bottom;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">31,775</font></div></td><td style="vertical-align:bottom;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">21,258</font></div></td><td style="vertical-align:bottom;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td></tr><tr><td style="vertical-align:top;padding-left:12px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">Proceeds from sales of marketable securities</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">47,838</font></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">94,564</font></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">90,536</font></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td></tr><tr><td style="vertical-align:top;background-color:#efefef;padding-left:12px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">Payments for acquisition of property, plant and equipment</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">(13,313</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-right:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">)</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">(12,451</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-right:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">)</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">(12,734</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-right:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">)</font></div></td></tr><tr><td style="vertical-align:top;padding-left:12px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">Payments made in connection with business acquisitions, net</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">(721</font></div></td><td style="vertical-align:bottom;padding-right:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">)</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">(329</font></div></td><td style="vertical-align:bottom;padding-right:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">)</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">(297</font></div></td><td style="vertical-align:bottom;padding-right:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">)</font></div></td></tr><tr><td style="vertical-align:top;background-color:#efefef;padding-left:12px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">Purchases of non-marketable securities</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">(1,871</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-right:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">)</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">(521</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-right:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">)</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">(1,388</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-right:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">)</font></div></td></tr><tr><td style="vertical-align:top;padding-left:12px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">Proceeds from non-marketable securities</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">353</font></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">126</font></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">—</font></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td></tr><tr><td style="vertical-align:top;background-color:#efefef;padding-left:12px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">Other</font></div></td><td colspan="2" style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">(745</font></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;padding-right:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">)</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">(124</font></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;padding-right:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">)</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">(924</font></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;padding-right:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">)</font></div></td></tr><tr><td style="vertical-align:top;padding-left:44px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">Cash generated by/(used in) investing activities</font></div></td><td colspan="2" style="vertical-align:bottom;border-bottom:1px solid #000000;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">16,066</font></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;"><br></font></div></td><td colspan="2" style="vertical-align:bottom;border-bottom:1px solid #000000;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">(46,446</font></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;padding-right:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">)</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;"><br></font></div></td><td colspan="2" style="vertical-align:bottom;border-bottom:1px solid #000000;padding-left:2px;padding-top:2px;padding-bottom:2px;border-top:1px solid #000000;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">(45,977</font></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;padding-right:2px;padding-top:2px;padding-bottom:2px;border-top:1px solid #000000;"><div style="text-align:left;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">)</font></div></td></tr><tr><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">Financing activities:</font></div></td><td colspan="3" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="3" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="3" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td></tr><tr><td style="vertical-align:top;padding-left:12px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">Proceeds from issuance of common stock</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">669</font></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">555</font></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">495</font></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td></tr><tr><td style="vertical-align:top;background-color:#efefef;padding-left:12px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">Payments for taxes related to net share settlement of equity awards</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">(2,527</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-right:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">)</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">(1,874</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-right:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">)</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">(1,570</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-right:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">)</font></div></td></tr><tr><td style="vertical-align:top;padding-left:12px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">Payments for dividends and dividend equivalents</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">(13,712</font></div></td><td style="vertical-align:bottom;padding-right:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">)</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">(12,769</font></div></td><td style="vertical-align:bottom;padding-right:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">)</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">(12,150</font></div></td><td style="vertical-align:bottom;padding-right:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">)</font></div></td></tr><tr><td style="vertical-align:top;background-color:#efefef;padding-left:12px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">Repurchases of common stock</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">(72,738</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-right:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">)</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">(32,900</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-right:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">)</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">(29,722</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-right:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">)</font></div></td></tr><tr><td style="vertical-align:top;padding-left:12px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">Proceeds from issuance of term debt, net</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">6,969</font></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">28,662</font></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">24,954</font></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td></tr><tr><td style="vertical-align:top;background-color:#efefef;padding-left:12px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">Repayments of term debt</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">(6,500</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-right:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">)</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">(3,500</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-right:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">)</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">(2,500</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-right:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">)</font></div></td></tr><tr><td style="vertical-align:top;padding-left:12px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">Change in commercial paper, net</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">(37</font></div></td><td style="vertical-align:bottom;padding-right:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">)</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">3,852</font></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">(397</font></div></td><td style="vertical-align:bottom;padding-right:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">)</font></div></td></tr><tr><td style="vertical-align:top;background-color:#efefef;padding-left:44px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">Cash used in financing activities</font></div></td><td colspan="2" style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;border-top:1px solid #000000;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">(87,876</font></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;padding-right:2px;padding-top:2px;padding-bottom:2px;border-top:1px solid #000000;"><div style="text-align:left;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">)</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;"><br></font></div></td><td colspan="2" style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;border-top:1px solid #000000;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">(17,974</font></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;padding-right:2px;padding-top:2px;padding-bottom:2px;border-top:1px solid #000000;"><div style="text-align:left;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">)</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;"><br></font></div></td><td colspan="2" style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;border-top:1px solid #000000;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">(20,890</font></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;padding-right:2px;padding-top:2px;padding-bottom:2px;border-top:1px solid #000000;"><div style="text-align:left;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">)</font></div></td></tr><tr><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">Increase/(Decrease) in cash and cash equivalents</font></div></td><td colspan="2" style="vertical-align:bottom;border-bottom:1px solid #000000;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">5,624</font></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;border-bottom:1px solid #000000;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">(195</font></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;padding-right:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">)</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;border-bottom:1px solid #000000;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">(636</font></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;padding-right:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">)</font></div></td></tr><tr><td style="vertical-align:top;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">Cash and cash equivalents, end of the year</font></div></td><td style="vertical-align:bottom;border-bottom:3px double #000000;padding-left:2px;padding-top:2px;padding-bottom:2px;background-color:#efefef;"><div style="text-align:left;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">$</font></div></td><td style="vertical-align:bottom;border-bottom:3px double #000000;background-color:#efefef;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">25,913</font></div></td><td style="vertical-align:bottom;border-bottom:3px double #000000;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;"><br></font></div></td><td style="vertical-align:bottom;border-bottom:3px double #000000;padding-left:2px;padding-top:2px;padding-bottom:2px;background-color:#efefef;"><div style="text-align:left;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">$</font></div></td><td style="vertical-align:bottom;border-bottom:3px double #000000;background-color:#efefef;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">20,289</font></div></td><td style="vertical-align:bottom;border-bottom:3px double #000000;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;"><br></font></div></td><td style="vertical-align:bottom;border-bottom:3px double #000000;padding-left:2px;padding-top:2px;padding-bottom:2px;background-color:#efefef;border-top:1px solid #000000;"><div style="text-align:left;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">$</font></div></td><td style="vertical-align:bottom;border-bottom:3px double #000000;background-color:#efefef;padding-top:2px;padding-bottom:2px;border-top:1px solid #000000;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">20,484</font></div></td><td style="vertical-align:bottom;border-bottom:3px double #000000;background-color:#efefef;border-top:1px solid #000000;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td></tr><tr><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">Supplemental cash flow disclosure:</font></div></td><td colspan="3" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="3" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="3" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td></tr><tr><td style="vertical-align:top;background-color:#efefef;padding-left:12px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">Cash paid for income taxes, net</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;background-color:#efefef;"><div style="text-align:left;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">$</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">10,417</font></div></td><td style="vertical-align:bottom;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;background-color:#efefef;"><div style="text-align:left;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">$</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">11,591</font></div></td><td style="vertical-align:bottom;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;background-color:#efefef;"><div style="text-align:left;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">$</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">10,444</font></div></td><td style="vertical-align:bottom;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td></tr><tr><td style="vertical-align:top;padding-left:12px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">Cash paid for interest</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">$</font></div></td><td style="vertical-align:bottom;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">3,022</font></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">$</font></div></td><td style="vertical-align:bottom;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">2,092</font></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">$</font></div></td><td style="vertical-align:bottom;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:8.5pt;"><font style="font-family:Helvetica,sans-serif;font-size:8.5pt;">1,316</font></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td></tr></tbody></table></div></div>'''
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
                reg_row = [reg_row[0]] + [re.sub("[^0-9-]", "", r) for r in reg_row[1:]]
                reg_row = [reg_row[0]] + [re.sub("^-$", "", r) for r in reg_row[1:]] # for NOT the minus sign
                reg_row = [reg_row[0]] + [re.sub(r',', '', x) for x in reg_row[1:]]
                reg_row = list(filter(lambda x: x != "", reg_row))
                # if len(reg_row) < len(indices): # TODO for now, skipping when there is a missing value
                #     continue
                # print(indices)

            # if re.compile('%.|.%'), catch index to skip all column
                # if it's a line
                # if len(row.find_all(lambda tag: tag.has_attr('style')
                # and ('border-bottom:solid' in tag['style'] or 'border-top:solid' in tag['style']))) > 0:
                #     continue
                # empty line
                if len(''.join(reg_row).strip()) == 0:
                    continue
                current_left_margin = 0
                try:
                    current_left_margin = find_left_margin(reg_row, row.findAll('td')[0])
                except:
                    traceback.print_exc()
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
                                     indented_list[-i][1], # last category
                                     re.IGNORECASE):
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
def normalization_iteration(iteration_count, input_dict, master_dict, filing_type, visited_data_names=None, flexible_sheet=False, flexible_entry=False):

    for title, table in input_dict.items():

        for scraped_name, scraped_value in flatten_dict(table).items():

            for normalized_category, pattern_string in flatten_dict(fin_reg.financial_entries_regex_dict).items():

                if flexible_sheet or (not flexible_sheet and ('Balance Sheet' in normalized_category.split('_')[0] and re.search(fin_reg.balance_sheet_regex, title, re.IGNORECASE))\
                                      or ('Income Statement' in normalized_category.split('_')[0] and re.search(fin_reg.income_statement_regex, title, re.IGNORECASE))
                                      or ('Cash Flow Statement' in normalized_category.split('_')[0] and re.search(fin_reg.cash_flow_statement_regex, title, re.IGNORECASE))):

                    # an entry is not flexible if it should match a hardcoded pattern

                    if ((not flexible_entry) and re.search('^(?!.*{})'.format('Year' if filing_type=='10-Q' else 'Quarter') +
                                 pattern_string, title+'_'+scraped_name, re.IGNORECASE)):

                        data_name = {'Iteration Count': str(iteration_count),
                                     'Hardcoded': True,
                                     'Table Title': title,
                                     'Pattern String': pattern_string}

                        # The idea is that if we go to another table and we have a value similar to one we already have on the sheet,
                        # i do not want to -include it (because its a duplicate). But if the value is similar in the same sheet, then
                        # i want to add it to the already existing value
                        if math.isnan(master_dict[normalized_category]):
                            visited_data_names.append(data_name)
                        if data_name in visited_data_names:
                            master_dict[normalized_category] = np.nan_to_num(master_dict[normalized_category]) + scraped_value
                        break

                    # otherwise it is flexible if it should just match the category (i.e. current assets, operating expenses...)
                    if flexible_entry and re.search(normalized_category.split('_')[-2], scraped_name, re.IGNORECASE):
                        no_match = True
                        for data_name in visited_data_names:
                            if re.search(data_name['Pattern String'], pattern_string, re.IGNORECASE):
                                no_match = False
                                break
                        if no_match:
                            master_dict['_'.join(normalized_category.split('_')[:-1])+'_'+titlecase(scraped_name.split('_')[-1])] = scraped_value

                            visited_data_names.append({'Iteration Count': str(iteration_count),
                                                       'Hardcoded': False,
                                                       'Table Title': title,
                                                       'Pattern String': scraped_name})
                            break
                        # match = False
                        # for data_name in visited_data_names:
                        #     try:
                        #         if re.search(data_name['Table Title'].replace('(', '').replace(')', ''),
                        #                      r'{}'.format(title.replace('(', '').replace(')', '')), re.IGNORECASE) and \
                        #                 re.search(data_name['Pattern String'],
                        #                           r'{}'.format(scraped_name), re.IGNORECASE):
                        #             match = True
                        #     except:
                        #         traceback.print_exc()
                        #         print(data_name['Table Title'], data_name['Pattern String'])
                        # if not match:
                            # else, it might match word for word an entry that wasn't hardcoded
                            # for data_name in visited_data_names:
                            #     if not data_name['Hardcoded']:
                            #         pattern_name = titlecase(data_name['Pattern String'])
                            #         scraped_name_without_category = titlecase(scraped_name.split('_')[-1])
                            #         # TODO should probably compare category as well
                            #         if all(x in pattern_name for x in scraped_name_without_category.split()) \
                            #                 or all(x in scraped_name_without_category for x in pattern_name.split()):
                            #             scraped_name = pattern_name
                            #             break
                            # print('_'.join(normalized_category.split('_')[:-1])+'_'+titlecase(scraped_name.split('_')[-1]))
                            # master_dict['_'.join(normalized_category.split('_')[:-1])+'_'+titlecase(scraped_name.split('_')[-1])] = scraped_value
                            #
                            # visited_data_names.append({'Iteration Count': str(iteration_count),
                            #                            'Hardcoded': False,
                            #                            'Table Title': title,
                            #                            'Pattern String': titlecase(scraped_name.split('_')[-1])})
                        # else:
                        #     break

    return visited_data_names, master_dict

# def test():
#     if not match_found:
#         for unique_category in set([normalized_category.split('_')[-2] for normalized_category, _ in flatten_dict(fin_reg.financial_entries_regex_dict).items()])
#             if re.search(unique_category, scraped_name, re.IGNORECASE):
#                 master_dict[''.join(normalized_category.split('_')[:-1])+'_'+scraped_name.split('_')[-1]] = scraped_value


def normalize_tables(input_dict, filing_type, visited_data_names):

    master_dict = {}
    for normalized_category, pattern_string in flatten_dict(fin_reg.financial_entries_regex_dict).items():
        master_dict[normalized_category] = np.nan
    # pprint(input_dict)
    # first we want to give priority to the elements in the consolidated financial statements
    visited_data_names, master_dict = normalization_iteration(0, input_dict, master_dict, filing_type, visited_data_names, flexible_sheet=False, flexible_entry=False)
    visited_data_names, master_dict = normalization_iteration(1, input_dict, master_dict, filing_type, visited_data_names, flexible_sheet=False, flexible_entry=True)
    visited_data_names, master_dict = normalization_iteration(2, input_dict, master_dict, filing_type, visited_data_names, flexible_sheet=True, flexible_entry=False)
    pprint(master_dict)
    # balance_sheet = {i: master_dict[i] for i in master_dict.keys() if re.search(r'Balance Sheet', i)}
    # income_statement = {i: master_dict[i] for i in master_dict.keys() if re.search(r'Income Statement', i)}
    # cash_flow_statement = {i: master_dict[i] for i in master_dict.keys() if re.search(r'Cash Flow Statement', i)}
    # TODO If Interest Income/Expense in revenues, then readjust Net Sales (add back)
    return visited_data_names, flatten_dict(unflatten(master_dict))


def testing():
    # url = 'https://www.sec.gov/Archives/edgar/data/1018724/000101872419000004/amzn-20181231x10k.htm#sD176CF43DDC1589FB3C3D7F2EFA46F0A'
    # dict = scrape_html_tables_from_url(url)
    # pprint(dict)
    # pprint(normalize_tables(dict, filing_type='10-K', visited_data_names=[]))
    dict = {'2019-09-28':
                {'Balance Sheet':
                     {'Assets':
                          {'Current Assets': {'Cash and Short Term Investments': {'Cash and Cash Equivalents': {'Cash and Due from Banks': np.nan, 'Interest-bearing Deposits in Banks and Other Finp.nancial Institutions': np.nan, 'Restricted Cash Current': 119134.0, 'Other Cash and Cash Equivalents': np.nan, 'Cash and Cash Equivalents': 48844.0}, 'Marketable Securities Current': 51713.0, 'Cash and Short Term Investments': 205898.0}, 'Accounts Receivable': {'Gross Accounts Receivable': np.nan, 'Allowances for Doubtful Accounts': np.nan, 'Other Receivables': 22878.0, 'Net Accounts Receivable': 22926.0, 'Accounts Receivable, Net': 22926.0}, 'Prepaid Expense, Current': np.nan, 'Inventory, Net': 4106.0, 'Income Taxes Receivable, Current': np.nan, 'Assets Held-for-sale': np.nan, 'Deferred Tax Assets, Current': np.nan, 'Other Assets, Current': np.nan, 'Total Assets, Current': 162819.0, 'Marketable Securities': 105341.0, 'Inventories': 4106.0, 'Vendor Non-Trade Receivables': 22878.0, 'Other Current Assets': 12352.0, 'Total Current Assets': 162819.0, 'Property, Plant and Equipment, Net': 37378.0, 'Other Non-Current Assets': 32978.0, 'Total Non-Current Assets': 175697.0}, 'Non Current Assets': {'Marketable Securities Non Current': 105341.0, 'Restricted Cash Non Current': np.nan, 'Property, Plant and Equipment': {'Gross Property, Plant and Equipment': 95957.0, 'Accumulated Depreciation and Amortization': -58579.0, 'Property, Plant and Equipment, Net': 37378.0}, 'Operating Lease Right-of-use Assets': np.nan, 'Deferred Tax Assets Non Current': 71386.0, 'Intangible Assets': {'Goodwill': np.nan, 'Intangible Assets, Net (Excluding Goodwill)': np.nan, 'Total Intangible Assets': np.nan}, 'Other Non Current Assets': 32978.0, 'Total Non Current Assets': 514213.0}, 'Total Assets': 338516.0}, "Liabilities and Shareholders' Equity": {'Liabilities': {'Current Liabilities': {'Short-Term Debt': 5980.0, 'Long-term Debt, Current Maturities': 102067.0, 'Accounts Payable, Current': 46236.0, 'Operating Lease, Liability, Current': np.nan, 'Current Deferred Revenues': 5522.0, 'Employee-related Liabilities, Current': np.nan, 'Accrued Income Taxes': np.nan, 'Accrued Liabilities, Current': np.nan, 'Income Taxes Payable': np.nan, 'Other Current Liabilities': 37720.0, 'Total Current Liabilities': 105718.0, 'Accounts Payable': 46236.0, 'Deferred Revenue': 5522.0, 'Commercial Paper': 5980.0, 'Term Debt': 91807.0, 'Other Non-Current Liabilities': 50503.0, 'Total Non-Current Liabilities': 142310.0, 'Total Liabilities': 248028.0}, 'Non Current Liabilities': {'Deferred Tax Liabilities': np.nan, 'Long-term Debt, Noncurrent Maturities': np.nan, 'Operating Lease, Liability, Noncurrent': np.nan, 'Liability, Defined Benefit Plan, Noncurrent': np.nan, 'Accrued Income Taxes, Noncurrent': np.nan, 'Deferred Revenue, Noncurrent': np.nan, 'Long-Term Unearned Revenue': np.nan, 'Other Liabilities, Noncurrent': 50503.0, 'Total Long-Term Liabilities': 390338.0}, 'Total Liabilities': np.nan}, "Shareholders' Equity": {'Preferred Stock, Value, Issued': np.nan, 'Common Stock and Additional Paid in Capital': {'Common Stock, Value, Issued': -68130.0, 'Additional Paid in Capital': np.nan, 'Common Stocks, Including Additional Paid in Capital': 45174.0, 'Weighted Average Number of Shares Outstanding, Basic': 4617834.0, 'Weighted Average Number Diluted Shares Outstanding Adjustment': 31079.0, 'Weighted Average Number of Shares Outstanding, Diluted': 4648913.0}, 'Treasury Stock, Value': np.nan, 'Retained Earnings (Accumulated Deficit)': 45898.0, 'Accumulated Other Comprehensive Income (Loss)': -584.0, 'Deferred Stock Compensation': np.nan, 'Minority Interest': np.nan, "Stockholders' Equity Attributable to Parent": 90488.0}, "Total Liabilities and Shareholders' Equity": 338516.0}}}}
    df = pd.DataFrame.from_dict(dict, orient='index')
    print(df.to_string())


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


def scrape_financial_statements(ticker, filing_type):
    financials_dictio = {}
    cik = get_company_cik(ticker)
    doc_links = get_filings_urls_first_layer(cik, filing_type)
    filings_dictio = get_filings_urls_second_layer(filing_type, doc_links)
    pprint(filings_dictio)
    names = ['{} {}'.format(name, filing_type) for name in [config.balance_sheet_name, config.income_statement_name, config.cash_flow_statement_name]]
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

    visited_data_names = []
    for index, (filing_date, link) in enumerate(missing_dates_links):
        try:
            if index > 2:
                break
            print(filing_date, link)
            visited_data_names, financials_dictio[filing_date] = normalize_tables(scrape_tables_from_url(link),
                                                                                  filing_type,
                                                                                  visited_data_names)
        except Exception:
            traceback.print_exc()

    financials_dictio = {k: v for k, v in financials_dictio.items() if v is not None}
    balance_sheet_dict, income_statement_dict, cash_flow_statement_dict = {}, {}, {}
    for dictio, regex in zip([balance_sheet_dict, income_statement_dict, cash_flow_statement_dict],
                             [fin_reg.balance_sheet_regex, fin_reg.income_statement_regex, fin_reg.cash_flow_statement_regex]):
        flattened = {}
        for key, value in financials_dictio.items():
            flattened[key] = {} # dictio is each sheet, and key is for the date
            for kk, vv in value.items():
                if re.search(regex, kk, re.IGNORECASE): # that's for the sheet name
                    flattened[key][kk] = vv

        for key, value in flattened.items():
        #     dictio[key] = unflatten(value)
              dictio[key] = value

    financial_statements_file_path = "{}/{}.xlsx".format(config.FINANCIAL_STATEMENTS_DIR_PATH, ticker)

    for sheet_name, dict in zip(names,
                                [balance_sheet_dict, income_statement_dict, cash_flow_statement_dict]):
        df = pd.DataFrame.from_dict(dict, orient='index')
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
    df.index = df.index - timedelta(days=1)

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
    urllib.request.urlretrieve(url,'fama_french.zip')
    zip_file = zipfile.ZipFile('fama_french.zip', 'r')
    zip_file.extractall()
    zip_file.close()

    # TODO FIND MORE PYTHONIC WAY
    file_name = ''
    for f in [f for f in os.listdir('.') if os.path.isfile(f)]:
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
                       'MS', 'JPM', 'WFC', 'C', 'BAC',
                       'KO', 'PG', 'JNJ', 'PEP', 'VZ', 'GS']
    # testing()
    for ticker in company_tickers[:6]:
        # get_stock_prices(ticker)
        # get_technical_indicators(ticker)
        scrape_financial_statements(ticker, '10-K')
    # ff_factors = get_beta_factors()
    # print(ff_factors)
    # testing()
    # scrape_pdf()
    # save_factors_data(momentum_factor_url_daily)
