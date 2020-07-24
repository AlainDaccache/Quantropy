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


# TODO: Sometimes only year format is available, current implementation skips
# TODO: What if both quarterly and yearly are in same table? first_level is wrong
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


def get_filings_urls_second_layer(doc_links):
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
                if 'htm' in cells[2].text and cells[3].text in ['10-K', '10-Q']:
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


def scrape_html_tables_from_url(url, filing_date):
    # url = 'https://www.sec.gov/Archives/edgar/data/789019/000156459019027952/msft-10k_20190630.htm'
    response = requests.get(url)
    table = '''<div style="line-height:120%;text-align:justify;font-size:10pt;"><div style="padding-left:0px;text-indent:0px;line-height:normal;padding-top:10px;"><table cellpadding="0" cellspacing="0" style="font-family:Times New Roman;font-size:10pt;width:100%;border-collapse:collapse;text-align:left;"><tbody><tr><td colspan="8"></td></tr><tr><td style="width:71%;"></td><td style="width:1%;"></td><td style="width:12%;"></td><td style="width:1%;"></td><td style="width:1%;"></td><td style="width:1%;"></td><td style="width:12%;"></td><td style="width:1%;"></td></tr><tr><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="3" style="vertical-align:bottom;border-bottom:1px solid #000000;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:center;font-size:8pt;"><span style="font-family:Helvetica,sans-serif;font-size:8pt;font-weight:bold;">March&nbsp;28, <br>2020</span></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="3" style="vertical-align:bottom;border-bottom:1px solid #000000;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:center;font-size:8pt;"><span style="font-family:Helvetica,sans-serif;font-size:8pt;font-weight:bold;">September&nbsp;28, <br>2019</span></div></td></tr><tr><td colspan="8" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:center;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;font-weight:bold;">ASSETS:</span></div></td></tr><tr><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">Current assets:</span></div></td><td colspan="3" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="3" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td></tr><tr><td style="vertical-align:bottom;padding-left:28px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">Cash and cash equivalents</span></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">$</span></div></td><td style="vertical-align:bottom;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-197" name="us-gaap:CashAndCashEquivalentsAtCarryingValue" contextref="FI2020Q2" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d14255321e576-wk-Fact-8C3204B18D3655AF86F281C303FE6118" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">40,174</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">$</span></div></td><td style="vertical-align:bottom;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-198" name="us-gaap:CashAndCashEquivalentsAtCarryingValue" contextref="FI2019Q4" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d14255321e595-wk-Fact-D59FA7F3EC1C582AA82D244CA59B999F" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">48,844</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td></tr><tr><td style="vertical-align:bottom;background-color:#efefef;padding-left:28px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">Marketable securities</span></div></td><td colspan="2" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-199" name="us-gaap:MarketableSecuritiesCurrent" contextref="FI2020Q2" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d14255321e610-wk-Fact-DF3FE254FA515C32A9A60C2C515DF270" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">53,877</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="2" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-200" name="us-gaap:MarketableSecuritiesCurrent" contextref="FI2019Q4" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d14255321e629-wk-Fact-C417FADB846655B0A409C687212DC1A6" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">51,713</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td></tr><tr><td style="vertical-align:bottom;padding-left:28px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">Accounts receivable, net</span></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-201" name="us-gaap:AccountsReceivableNetCurrent" contextref="FI2020Q2" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d14255321e649-wk-Fact-F55B1E43E0C252788CB0543C656A01D5" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">15,722</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-202" name="us-gaap:AccountsReceivableNetCurrent" contextref="FI2019Q4" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d14255321e668-wk-Fact-05EA8CE552E55C0FACBFD4AAB983868E" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">22,926</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td></tr><tr><td style="vertical-align:bottom;background-color:#efefef;padding-left:28px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">Inventories</span></div></td><td colspan="2" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-203" name="us-gaap:InventoryNet" contextref="FI2020Q2" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d14255321e688-wk-Fact-942C57972057520699258C9A50E0725D" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">3,334</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="2" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-204" name="us-gaap:InventoryNet" contextref="FI2019Q4" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d14255321e707-wk-Fact-67B05D6BA7BA5C73B3AB04C526D39829" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">4,106</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td></tr><tr><td style="vertical-align:bottom;padding-left:28px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">Vendor non-trade receivables</span></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-205" name="us-gaap:NontradeReceivablesCurrent" contextref="FI2020Q2" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d14255321e727-wk-Fact-D0A15984FD305EF6BFADF203348E89BD" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">14,955</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-206" name="us-gaap:NontradeReceivablesCurrent" contextref="FI2019Q4" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d14255321e746-wk-Fact-039722E28B7A525CA70FB73EA2D97A32" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">22,878</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td></tr><tr><td style="vertical-align:bottom;background-color:#efefef;padding-left:28px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">Other current assets</span></div></td><td colspan="2" style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-207" name="us-gaap:OtherAssetsCurrent" contextref="FI2020Q2" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d14255321e766-wk-Fact-AABF14FCA349559C92AC217986ABBD3B" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">15,691</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="2" style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-208" name="us-gaap:OtherAssetsCurrent" contextref="FI2019Q4" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d14255321e785-wk-Fact-2854320E75865F2E8B0753CE1C7ED070" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">12,352</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td></tr><tr><td style="vertical-align:bottom;padding-left:52px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">Total current assets</span></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-209" name="us-gaap:AssetsCurrent" contextref="FI2020Q2" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d14255321e805-wk-Fact-79F8EF6B68BA5360B157C50EC221B483" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">143,753</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-210" name="us-gaap:AssetsCurrent" contextref="FI2019Q4" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d14255321e824-wk-Fact-4B02664A541A5E6CA6874825206AA937" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">162,819</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td></tr><tr><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;height:18px;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="3" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;height:18px;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;height:18px;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="3" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;height:18px;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td></tr><tr><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">Non-current assets:</span></div></td><td colspan="3" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="3" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td></tr><tr><td style="vertical-align:bottom;background-color:#efefef;padding-left:28px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">Marketable securities</span></div></td><td colspan="2" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-211" name="us-gaap:MarketableSecuritiesNoncurrent" contextref="FI2020Q2" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d14255321e927-wk-Fact-FA74C0E354295BA7B1649861A00283C4" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">98,793</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="2" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-212" name="us-gaap:MarketableSecuritiesNoncurrent" contextref="FI2019Q4" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d14255321e946-wk-Fact-7BAA54CCDC105E3D90AC1A81D7943ECB" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">105,341</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td></tr><tr><td style="vertical-align:bottom;padding-left:28px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">Property, plant and equipment, net</span></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-213" name="us-gaap:PropertyPlantAndEquipmentNet" contextref="FI2020Q2" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d14255321e966-wk-Fact-B39277A82AB059FC91AD8EC34D495CBB" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">35,889</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-214" name="us-gaap:PropertyPlantAndEquipmentNet" contextref="FI2019Q4" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d14255321e985-wk-Fact-A54B290160905F69B2F3815DB90BCB59" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">37,378</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td></tr><tr><td style="vertical-align:bottom;background-color:#efefef;padding-left:28px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">Other non-current assets</span></div></td><td colspan="2" style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-215" name="us-gaap:OtherAssetsNoncurrent" contextref="FI2020Q2" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d14255321e1005-wk-Fact-0303BB1352115AB982CE87949E521E30" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">41,965</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="2" style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-216" name="us-gaap:OtherAssetsNoncurrent" contextref="FI2019Q4" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d14255321e1024-wk-Fact-0A39E82CE6EA586CAF5704771F2A6213" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">32,978</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td></tr><tr><td style="vertical-align:bottom;padding-left:52px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">Total non-current assets</span></div></td><td colspan="2" style="vertical-align:bottom;border-bottom:1px solid #000000;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-217" name="us-gaap:AssetsNoncurrent" contextref="FI2020Q2" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d14255321e1044-wk-Fact-2B35E799FA0958B4B591083358E5F9F5" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">176,647</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="2" style="vertical-align:bottom;border-bottom:1px solid #000000;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-218" name="us-gaap:AssetsNoncurrent" contextref="FI2019Q4" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d14255321e1063-wk-Fact-108F7010C1F656CAB094B9CA66532010" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">175,697</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td></tr><tr><td style="vertical-align:bottom;background-color:#efefef;padding-left:76px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">Total assets</span></div></td><td style="vertical-align:bottom;border-bottom:3px double #000000;padding-left:2px;padding-top:2px;padding-bottom:2px;background-color:#efefef;"><div style="text-align:left;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">$</span></div></td><td style="vertical-align:bottom;border-bottom:3px double #000000;background-color:#efefef;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-219" name="us-gaap:Assets" contextref="FI2020Q2" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d14255321e1088-wk-Fact-C7E02AEB2DCC58A285CDC1D0710D59F3" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">320,400</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;border-bottom:3px double #000000;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td style="vertical-align:bottom;border-bottom:3px double #000000;padding-left:2px;padding-top:2px;padding-bottom:2px;background-color:#efefef;"><div style="text-align:left;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">$</span></div></td><td style="vertical-align:bottom;border-bottom:3px double #000000;background-color:#efefef;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-220" name="us-gaap:Assets" contextref="FI2019Q4" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d14255321e1107-wk-Fact-5521FA70522A5AD39F93C3D5FD4DA3C7" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">338,516</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;border-bottom:3px double #000000;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td></tr><tr><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;height:18px;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="3" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;height:18px;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;height:18px;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="3" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;height:18px;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td></tr><tr><td colspan="8" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:center;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;font-weight:bold;">LIABILITIES AND SHAREHOLDERS’ EQUITY:</span></div></td></tr><tr><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">Current liabilities:</span></div></td><td colspan="3" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="3" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td></tr><tr><td style="vertical-align:bottom;background-color:#efefef;padding-left:28px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">Accounts payable</span></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;background-color:#efefef;"><div style="text-align:left;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">$</span></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-221" name="us-gaap:AccountsPayableCurrent" contextref="FI2020Q2" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d14255321e1250-wk-Fact-3C8F1FF969A55747890D646EB910994A" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">32,421</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;background-color:#efefef;"><div style="text-align:left;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">$</span></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-222" name="us-gaap:AccountsPayableCurrent" contextref="FI2019Q4" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d14255321e1269-wk-Fact-F28A1E7201F7597490F95CADC144312F" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">46,236</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td></tr><tr><td style="vertical-align:bottom;padding-left:28px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">Other current liabilities</span></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-223" name="us-gaap:OtherLiabilitiesCurrent" contextref="FI2020Q2" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d14255321e1284-wk-Fact-FB74DD22390454A486B01C8830FECDF3" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">37,324</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-224" name="us-gaap:OtherLiabilitiesCurrent" contextref="FI2019Q4" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d14255321e1303-wk-Fact-6EEA82E31ADE5FB786E45AB53D9E2946" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">37,720</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td></tr><tr><td style="vertical-align:bottom;background-color:#efefef;padding-left:28px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">Deferred revenue</span></div></td><td colspan="2" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-225" name="us-gaap:ContractWithCustomerLiabilityCurrent" contextref="FI2020Q2" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d14255321e1324-wk-Fact-96913D7AE03A5EE78B1E933C29469FCE" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">5,928</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="2" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-226" name="us-gaap:ContractWithCustomerLiabilityCurrent" contextref="FI2019Q4" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d14255321e1343-wk-Fact-11170ED739605717A43DDC6B6197199C" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">5,522</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td></tr><tr><td style="vertical-align:bottom;padding-left:28px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">Commercial paper and repurchase agreement</span></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-227" name="us-gaap:OtherShortTermBorrowings" contextref="FI2020Q2" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d14255321e1363-wk-Fact-7093D49D2A5B52E7ABCD001ACAEFB3E0" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">10,029</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-228" name="us-gaap:OtherShortTermBorrowings" contextref="FI2019Q4" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d14255321e1382-wk-Fact-D15708FE2A5B566A88F7E6D142D43246" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">5,980</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td></tr><tr><td style="vertical-align:bottom;background-color:#efefef;padding-left:28px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">Term debt</span></div></td><td colspan="2" style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-229" name="us-gaap:LongTermDebtCurrent" contextref="FI2020Q2" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d14255321e1402-wk-Fact-15D6725029F35B23A8B55E8B77F41632" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">10,392</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="2" style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-230" name="us-gaap:LongTermDebtCurrent" contextref="FI2019Q4" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d14255321e1421-wk-Fact-A709FCA7592F5B3A9A224A2D7689195B" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">10,260</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td></tr><tr><td style="vertical-align:bottom;padding-left:52px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">Total current liabilities</span></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-231" name="us-gaap:LiabilitiesCurrent" contextref="FI2020Q2" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d14255321e1441-wk-Fact-BDBB9A3A66A551D0B1B363B904513BF2" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">96,094</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-232" name="us-gaap:LiabilitiesCurrent" contextref="FI2019Q4" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d14255321e1460-wk-Fact-E5BC069EA86D5DD7B1D0C8FE21ADA59C" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">105,718</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td></tr><tr><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;height:18px;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="3" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;height:18px;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;height:18px;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="3" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;height:18px;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td></tr><tr><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">Non-current liabilities:</span></div></td><td colspan="3" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="3" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td></tr><tr><td style="vertical-align:bottom;background-color:#efefef;padding-left:28px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">Term debt</span></div></td><td colspan="2" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-233" name="us-gaap:LongTermDebtNoncurrent" contextref="FI2020Q2" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d14255321e1562-wk-Fact-BBD6F9C987FE5E41801D6A32A32B8DDA" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">89,086</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="2" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-234" name="us-gaap:LongTermDebtNoncurrent" contextref="FI2019Q4" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d14255321e1581-wk-Fact-13B5609A3A2A5D4292A4C94775C189CF" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">91,807</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td></tr><tr><td style="vertical-align:bottom;padding-left:28px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">Other non-current liabilities</span></div></td><td colspan="2" style="vertical-align:bottom;border-bottom:1px solid #000000;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-235" name="us-gaap:OtherLiabilitiesNoncurrent" contextref="FI2020Q2" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d14255321e1601-wk-Fact-D9D81420157253BA882D1652E72C3109" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">56,795</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="2" style="vertical-align:bottom;border-bottom:1px solid #000000;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-236" name="us-gaap:OtherLiabilitiesNoncurrent" contextref="FI2019Q4" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d14255321e1620-wk-Fact-EDD34A2B2068557285F8777811EDC64E" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">50,503</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td></tr><tr><td style="vertical-align:bottom;background-color:#efefef;padding-left:52px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">Total non-current liabilities</span></div></td><td colspan="2" style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-237" name="us-gaap:LiabilitiesNoncurrent" contextref="FI2020Q2" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d14255321e1640-wk-Fact-2C08B1CD79E05DF4933AD5DE68F0DC33" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">145,881</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="2" style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-238" name="us-gaap:LiabilitiesNoncurrent" contextref="FI2019Q4" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d14255321e1659-wk-Fact-9C09CCC5C8625DC8A8554D89C01FD074" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">142,310</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td></tr><tr><td style="vertical-align:bottom;padding-left:76px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">Total liabilities</span></div></td><td colspan="2" style="vertical-align:bottom;border-bottom:1px solid #000000;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-239" name="us-gaap:Liabilities" contextref="FI2020Q2" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d14255321e1679-wk-Fact-C83DA5CB46A95507884711ECC02F9255" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">241,975</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="2" style="vertical-align:bottom;border-bottom:1px solid #000000;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-240" name="us-gaap:Liabilities" contextref="FI2019Q4" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d14255321e1698-wk-Fact-F3FD82C3259A55F4B8BB9669B14B537F" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">248,028</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td></tr><tr><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;height:18px;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="3" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;border-top:1px solid #000000;"><div style="overflow:hidden;height:18px;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;height:18px;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="3" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;border-top:1px solid #000000;"><div style="overflow:hidden;height:18px;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td></tr><tr><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">Commitments and contingencies</span></div></td><td colspan="3" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-241" name="us-gaap:CommitmentsAndContingencies" contextref="FI2020Q2" unitref="usd" xsi:nil="true" scale="0" format="ixt:nocontent" data-original-id="d14255321e1760-wk-Fact-ED335E1B43C155168348A840AB599D61" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false"></ix:nonfraction></span></span><br></span></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="3" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-242" name="us-gaap:CommitmentsAndContingencies" contextref="FI2019Q4" unitref="usd" xsi:nil="true" scale="0" format="ixt:nocontent" data-original-id="d14255321e1779-wk-Fact-0CC7B321277252F0996A882EB3D5E26E" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false"></ix:nonfraction></span></span><br></span></div></td></tr><tr><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;height:18px;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="3" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;height:18px;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;height:18px;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="3" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;height:18px;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td></tr><tr><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">Shareholders’ equity:</span></div></td><td colspan="3" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="3" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td></tr><tr><td style="vertical-align:bottom;background-color:#efefef;padding-left:28px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">Common stock and additional paid-in capital, $0.00001 par value: 12,600,000 shares authorized; 4,323,987 and 4,443,236 shares issued and outstanding, respectively</span></div></td><td colspan="2" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-243" name="us-gaap:CommonStocksIncludingAdditionalPaidInCapital" contextref="FI2020Q2" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d14255321e1881-wk-Fact-A08CFA13459259A181C7CB27E2E30DBF" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">48,032</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="2" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-244" name="us-gaap:CommonStocksIncludingAdditionalPaidInCapital" contextref="FI2019Q4" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d14255321e1900-wk-Fact-052187EB1028514CBBB1CFA2F54F7FB4" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">45,174</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td></tr><tr><td style="vertical-align:bottom;padding-left:28px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">Retained earnings</span></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-245" name="us-gaap:RetainedEarningsAccumulatedDeficit" contextref="FI2020Q2" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d14255321e1920-wk-Fact-3A3C5C6E9F2E573F83922BE9D6127E51" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">33,182</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-246" name="us-gaap:RetainedEarningsAccumulatedDeficit" contextref="FI2019Q4" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d14255321e1939-wk-Fact-E8768CA77ABA5B9B9F91AF81586A647A" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">45,898</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td></tr><tr><td style="vertical-align:bottom;background-color:#efefef;padding-left:28px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">Accumulated other comprehensive income/(loss)</span></div></td><td colspan="2" style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span>(<span><ix:nonfraction id="fact-identifier-247" name="us-gaap:AccumulatedOtherComprehensiveIncomeLossNetOfTax" contextref="FI2020Q2" unitref="usd" decimals="-6" scale="6" sign="-" format="ixt:numdotdecimal" data-original-id="d14255321e1959-wk-Fact-AE20ACA0267258488DCC9CAC126B3AEA" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="true" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">2,789</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;padding-right:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">)</span></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="2" style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span>(<span><ix:nonfraction id="fact-identifier-248" name="us-gaap:AccumulatedOtherComprehensiveIncomeLossNetOfTax" contextref="FI2019Q4" unitref="usd" decimals="-6" scale="6" sign="-" format="ixt:numdotdecimal" data-original-id="d14255321e1979-wk-Fact-C419514228405F55B7585486AF0113C6" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="true" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">584</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;padding-right:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">)</span></div></td></tr><tr><td style="vertical-align:bottom;padding-left:52px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">Total shareholders’ equity</span></div></td><td colspan="2" style="vertical-align:bottom;border-bottom:1px solid #000000;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-249" name="us-gaap:StockholdersEquity" contextref="FI2020Q2" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d14255321e2000-wk-Fact-E3C7C1E507D3585FB0DB5B6C3EDFBEB7" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">78,425</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="2" style="vertical-align:bottom;border-bottom:1px solid #000000;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-250" name="us-gaap:StockholdersEquity" contextref="FI2019Q4" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d14255321e2019-wk-Fact-9DF34F6894A259AFB655D00DE12B7AAF" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">90,488</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td></tr><tr><td style="vertical-align:bottom;background-color:#efefef;padding-left:76px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">Total liabilities and shareholders’ equity</span></div></td><td style="vertical-align:bottom;border-bottom:3px double #000000;padding-left:2px;padding-top:2px;padding-bottom:2px;background-color:#efefef;"><div style="text-align:left;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">$</span></div></td><td style="vertical-align:bottom;border-bottom:3px double #000000;background-color:#efefef;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-251" name="us-gaap:LiabilitiesAndStockholdersEquity" contextref="FI2020Q2" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d14255321e2044-wk-Fact-67D1864F227A56788561EC179AD56803" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">320,400</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;border-bottom:3px double #000000;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td style="vertical-align:bottom;border-bottom:3px double #000000;padding-left:2px;padding-top:2px;padding-bottom:2px;background-color:#efefef;"><div style="text-align:left;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">$</span></div></td><td style="vertical-align:bottom;border-bottom:3px double #000000;background-color:#efefef;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-252" name="us-gaap:LiabilitiesAndStockholdersEquity" contextref="FI2019Q4" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d14255321e2063-wk-Fact-9880264D2DA65A79A59D82A64BAEB0E5" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">338,516</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;border-bottom:3px double #000000;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td></tr></tbody></table></div></div>'''
    soup = BeautifulSoup(response.text, 'html.parser')
    all_in_one_dict = {'Yearly': {},
                       'Quarterly': {},
                       '6 Months': {},
                       '9 Months': {}}

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
        soup = BeautifulSoup(html, 'html.parser')

    for table in soup.findAll('table'):

        columns = []
        dates = []
        header_found = False
        indented_list = []
        rows = table.find_all('tr')
        table_title, table_currency, table_multiplier = '', '', ''
        first_level = ''  # that's for whether the table is yearly of quarterly
        for index, row in enumerate(rows):

            reg_row = [ele.text for ele in row.find_all(lambda tag: tag.name == 'td' or tag.name == 'th')]
            reg_row = [unicodedata.normalize("NFKD", x) for x in reg_row]
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
                    if len(columns) == 0:
                        columns = reg_row
                    else:
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

                    # sometimes same title (i.e. if table is split in two pages, they repeat page title twice
                    table_multiplier, table_currency = find_meta_table_info(table)
                    table_title = unicodedata.normalize("NFKD", find_table_title(table)).strip().replace('\n', '')
                    if table_multiplier == 'percentage':
                        break
                    format_match = False
                    dates = []
                    only_year = False
                    for col in columns:
                        # Filing for June 30, 2019:
                        # Fiscal year 2019  September   December    March   June --> september and december are 2018
                        if only_year:
                            break
                        match = re.search(flexible_month_day_year_regex, col) or re.search(
                            month_slash_day_slash_year_regex, col) or re.search(only_year_regex, col)
                        if match:
                            for dts in ['%b %d %Y', '%m/%d/%y', '%Y']:
                                try:
                                    if re.search(only_year_regex, col):
                                        dates.append(filing_date)
                                        format_match = True
                                        only_year = True
                                        break
                                    # print(match.groups())
                                    col_formatted_date = datetime.strptime(' '.join(match.groups()), dts).date()
                                    col_formatted_date = datetime(col_formatted_date.year, col_formatted_date.month,
                                                                  col_formatted_date.day)
                                    # ascending = True if dates[0] < dates[1] else False
                                    if col_formatted_date > filing_date:
                                        col_formatted_date = datetime(col_formatted_date.year - 1,
                                                                      col_formatted_date.month,
                                                                      col_formatted_date.day)
                                    dates.append(col_formatted_date)
                                    format_match = True
                                    break
                                except:
                                    continue

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

                        # first_relevant_index = next((index for (index, item) in enumerate(columns) if
                        #                              not re.search(r'Six|Nine', item, re.IGNORECASE)), 0)
                        # last_relevant_index = next((index - 1 for (index, item) in enumerate(columns) if
                        #                             re.search(r'Six|Nine', item, re.IGNORECASE)), len(columns) - 1)
                        for index, col in enumerate(columns):
                            if only_year:
                                relevant_index = columns.index(str(filing_date.year))
                                break
                            if re.search(r'Three|Quarter', table_title + col, re.IGNORECASE):
                                first_level = 'Quarterly'
                            elif re.search(r'Six', table_title + col, re.IGNORECASE):
                                first_level = '6 Months'
                            elif re.search(r'Nine', table_title + col, re.IGNORECASE):
                                first_level = '9 Months'
                            elif re.search(r'Change', table_title + col, re.IGNORECASE):
                                continue
                            else:
                                first_level = 'Yearly'

                            for date in dates:
                                if date not in all_in_one_dict[first_level].keys():
                                    all_in_one_dict[first_level][date] = {}
                                if table_title not in all_in_one_dict[first_level][date].keys():
                                    all_in_one_dict[first_level][date][table_title] = {}
                            if current_category not in all_in_one_dict[first_level][dates[index]][table_title].keys():
                                all_in_one_dict[first_level][dates[index]][table_title][current_category] = float(
                                    re.sub('^$', '0', reg_row[index + 1]))

                except:
                    print('EXCEPTION INDEX! for {}'.format(table_title))
    # pprint(not_useful)
    return all_in_one_dict


def scrape_tables_from_url(url, filing_date):
    extension = url.split('.')[-1]

    if extension == 'xml':
        return scrape_xbrl_tables_from_url(url)
    elif extension == 'htm':
        return scrape_html_tables_from_url(url, filing_date)
    elif extension == 'txt':
        return scrape_txt_tables_from_url(url)


def normalization_iteration(iteration_count, input_dict, master_dict, visited_data_names, year,
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
                    pattern_string = '^' + pattern_string
                    if ((not flexible_entry) and re.search(
                            pattern_string, title + '_' + scraped_name, re.IGNORECASE)):
                        # print('Found pattern match {} for scraped name {}'.format(pattern_string, scraped_name))

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


def normalize_tables(input_dict, visited_data_names, year):
    # pprint(input_dict)
    master_dict = {}

    # TODO maybe should save all data_names to further compare across years? (the flexible entries)

    for normalized_category, pattern_string in flatten_dict(fin_reg.financial_entries_regex_dict).items():
        master_dict[normalized_category] = np.nan

    # first we want to give priority to the elements that strictly match our regex patterns,
    # and that are in the consolidated financial statements
    visited_data_names, master_dict = normalization_iteration(0, input_dict, master_dict,
                                                              visited_data_names, year, flexible_sheet=False,
                                                              flexible_entry=False)

    # then we want to give priority to the elements that strictly match our regex patterns,
    # but not in the consolidated financial statements
    visited_data_names, master_dict = normalization_iteration(1, input_dict, master_dict,
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


def scrape_financial_statements(ticker, how_many_periods=2):
    dictio = {}
    cik = get_company_cik(ticker)
    doc_links_yearly = get_filings_urls_first_layer(cik, '10-K')
    doc_links_quarterly = get_filings_urls_first_layer(cik, '10-Q')

    filings_dictio_yearly = get_filings_urls_second_layer(doc_links_yearly)
    year_dates = set([tuple_1
                      for key, value in filings_dictio_yearly.items()
                      for tuple_1, tuple_2 in value])
    filing_dictio = get_filings_urls_second_layer(doc_links_quarterly)
    for title, links_list in filings_dictio_yearly.items():
        filing_dictio[title].extend(links_list)

    pprint(filing_dictio)

    sheet_names = [config.balance_sheet_name, config.income_statement_name, config.cash_flow_statement_name]
    missing_dates_links = []
    for sheet_name in sheet_names:
        existing_dates = excel.read_dates_from_csv(ticker, sheet_name)
        for x, y in filing_dictio['HTML Links']:
            formatted_date = datetime.strptime(x, '%Y-%m-%d')
            if formatted_date not in existing_dates and formatted_date not in [x for x, y in missing_dates_links]:
                missing_dates_links.append((formatted_date, y))

    missing_dates_links.sort(key=lambda tup: tup[0], reverse=True)
    print(missing_dates_links)
    for index, (filing_date, link) in enumerate(missing_dates_links):
        try:
            if index > 0:
                break
            print(filing_date, link)
            # scrape_tables_from_url(link)
            output = scrape_tables_from_url(link, filing_date)
            for sheet_period, sheet_dict in output.items():
                if sheet_period not in dictio.keys():
                    dictio[sheet_period] = {}
                for year, title_dict in sheet_dict.items():
                    # if we don't have the year in our dictio that collects everything, just add all and go to next year of the output
                    if year not in dictio[sheet_period].keys():
                        dictio[sheet_period][year] = title_dict
                        continue

                    #  else, we have a year, so we add up those two dicts together
                    for title, last_layer in title_dict.items():  # title / key:float
                        if title not in dictio[sheet_period][year].keys():
                            dictio[sheet_period][year][title] = last_layer

                        else:
                            dictio[sheet_period][year][title].update(last_layer)

        except Exception:
            traceback.print_exc()
    pprint(dictio)
    financials_dictio = {}
    visited_data_names = {}
    for sheet_period, sheet_dict in dictio.items():
        if sheet_period not in financials_dictio.keys():
            financials_dictio[sheet_period] = {}
        for year, title_dict in sheet_dict.items():
            if year not in financials_dictio[sheet_period].keys():
                financials_dictio[sheet_period][year] = {}
            visited_data_names, financials_dictio[sheet_period][year] = normalize_tables(title_dict, visited_data_names,

                                                                                         year)
    path = '{}/{}.xlsx'.format(config.FINANCIAL_STATEMENTS_DIR_PATH, ticker)

    for sheet_name in sheet_names:
        first_balance_sheet_df = pd.DataFrame()
        visited_first_balance_sheet = False
        for sheet_period, sheet_dict in financials_dictio.items():

            diction = collections.OrderedDict(
                {i.strftime('%Y-%m-%d'): {(j.split('_')[1], j.split('_')[-1] if j.split('_')[1] != j.split('_')[
                    -1] else ' ') if 'Balance Sheet' not in sheet_name
                                          else (
                    (j.split('_')[1], j.split('_')[2] if (len(j.split('_')) > 2) else ' ',
                     j.split('_')[-1] if j.split('_')[1] != j.split('_')[-1] else ''))
                                          : sheet_dict[i][j]
                                          for j in sheet_dict[i].keys() if j.split('_')[0] in sheet_name
                                          # sheet name
                                          } for i in sheet_dict.keys()})  # date

            if sheet_name == config.balance_sheet_name and not visited_first_balance_sheet:
                first_balance_sheet_df = pd.DataFrame.from_dict(diction)
                print(first_balance_sheet_df.to_string())
                visited_first_balance_sheet = True
            else:
                df = pd.DataFrame.from_dict(diction)

                if sheet_name == config.balance_sheet_name:
                    if visited_first_balance_sheet:
                        print(df.to_string())
                        df = pd.concat([first_balance_sheet_df, df], axis=0)
                        print(df.to_string())
                        df.groupby(lambda x: x, axis=1).max()
                        df_yearly = df[[x for x in df.columns if x in year_dates]]
                        for datafrme, period in zip([df_yearly, df], ['Yearly', 'Quarterly']):
                            datafrme = datafrme.reindex(sorted(datafrme.columns, reverse=True), axis=1)
                            datafrme.dropna(axis=0, how='all', inplace=True)
                            datafrme = datafrme.loc[:, datafrme.any()]
                            if not datafrme.empty:
                                # excel.save_into_csv(path, '{} {}'.format('Yearly', sheet_name).upper(), sheet_name)
                                excel.save_into_csv(path, datafrme, '{} ({})'.format(sheet_name, period))
                    break

                df = df.reindex(sorted(df.columns, reverse=True), axis=1)
                df.dropna(axis=0, how='all', inplace=True)
                df = df.loc[:, df.any()]
                if not df.empty:
                    # excel.save_into_csv(path, '{} {}'.format(sheet_period, sheet_name).upper(), sheet_name)
                    excel.save_into_csv(path, df, '{} ({})'.format(sheet_name, sheet_period))


def get_stock_prices(stock, start=datetime(1970, 1, 1), end=datetime.now()):
    df = excel.read_df_from_csv(stock, config.stock_prices_sheet_name)
    if df.empty:
        df = web.DataReader(stock.replace('.', '-'), data_source='yahoo', start=start, end=end)
        df['Pct Change'] = df['Adj Close'].pct_change()
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


def testing():
    pprint(scrape_html_tables_from_url(
        'https://www.sec.gov/ix?doc=/Archives/edgar/data/320193/000032019319000119/a10-k20199282019.htm',
        datetime(2020, 3, 28)))


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
        scrape_financial_statements(ticker)
    # scrape_financial_statements(ticker, '10-Q')

    # ff_factors = get_beta_factors()
    # print(ff_factors)
    # testing()
    # scrape_pdf()
    # save_factors_data(momentum_factor_url_daily)
