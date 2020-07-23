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

# TODO: Sometimes only year is available

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
    table = '''<table cellpadding="0" cellspacing="0" style="font-family:Times New Roman;font-size:10pt;width:100%;border-collapse:collapse;text-align:left;"><tbody><tr><td colspan="8"></td></tr><tr><td style="width:71%;"></td><td style="width:1%;"></td><td style="width:12%;"></td><td style="width:1%;"></td><td style="width:1%;"></td><td style="width:1%;"></td><td style="width:12%;"></td><td style="width:1%;"></td></tr><tr><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="7" style="vertical-align:bottom;border-bottom:1px solid #000000;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:center;font-size:8pt;"><span style="font-family:Helvetica,sans-serif;font-size:8pt;font-weight:bold;">Three Months Ended</span></div></td></tr><tr><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="3" style="vertical-align:bottom;border-bottom:1px solid #000000;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:center;font-size:8pt;"><span style="font-family:Helvetica,sans-serif;font-size:8pt;font-weight:bold;">December&nbsp;28, <br>2019</span></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="3" style="vertical-align:bottom;border-bottom:1px solid #000000;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:center;font-size:8pt;"><span style="font-family:Helvetica,sans-serif;font-size:8pt;font-weight:bold;">December&nbsp;29, <br>2018</span></div></td></tr><tr><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">Net sales:</span></div></td><td colspan="3" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;border-top:1px solid #000000;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="3" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;border-top:1px solid #000000;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td></tr><tr><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">&nbsp;&nbsp;&nbsp;Products</span></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;background-color:#efefef;"><div style="text-align:left;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">$</span></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-81" name="us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax" contextref="FD2020Q1QTD_srt_ProductOrServiceAxis_us-gaap_ProductMember" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d57646671e572-wk-Fact-062DE03B5CEE5C4DA5E28AA7067660E7" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="false" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">79,104</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;background-color:#efefef;"><div style="text-align:left;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">$</span></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-82" name="us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax" contextref="FD2019Q1QTD_srt_ProductOrServiceAxis_us-gaap_ProductMember" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d57646671e591-wk-Fact-DC1CBABF38DE5DFB98392D97C6A6BA49" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="false" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">73,435</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td></tr><tr><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">&nbsp;&nbsp;&nbsp;Services</span></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-83" name="us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax" contextref="FD2020Q1QTD_srt_ProductOrServiceAxis_us-gaap_ServiceMember" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d57646671e606-wk-Fact-04F76F3E2B9E53B6AC3DACDEF6C1C1C5" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="false" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">12,715</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-84" name="us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax" contextref="FD2019Q1QTD_srt_ProductOrServiceAxis_us-gaap_ServiceMember" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d57646671e625-wk-Fact-D451D30D5D9856AE925543E1A18276AD" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="false" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">10,875</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td></tr><tr><td style="vertical-align:bottom;background-color:#efefef;padding-left:28px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">Total net sales</span></div></td><td colspan="2" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;border-top:1px solid #000000;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-85" name="us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax" contextref="FD2020Q1YTD" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d57646671e645-wk-Fact-86597C8511F35450B8FE851511A819A6" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">91,819</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;background-color:#efefef;border-top:1px solid #000000;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="2" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;border-top:1px solid #000000;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-86" name="us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax" contextref="FD2019Q1QTD" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d57646671e664-wk-Fact-08998C56722C53EF8C8AFDE7E1AA1C69" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">84,310</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;background-color:#efefef;border-top:1px solid #000000;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td></tr><tr><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;height:18px;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="3" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;height:18px;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;height:18px;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="3" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;height:18px;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td></tr><tr><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">Cost of sales:</span></div></td><td colspan="3" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="3" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td></tr><tr><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">&nbsp;&nbsp;&nbsp;Products</span></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-87" name="us-gaap:CostOfGoodsAndServicesSold" contextref="FD2020Q1QTD_srt_ProductOrServiceAxis_us-gaap_ProductMember" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d57646671e766-wk-Fact-E95D51008DC55CD09F2D6A0C38144696" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="false" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">52,075</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-88" name="us-gaap:CostOfGoodsAndServicesSold" contextref="FD2019Q1QTD_srt_ProductOrServiceAxis_us-gaap_ProductMember" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d57646671e785-wk-Fact-CA7EC93345765653B5ECB27B6BF12353" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="false" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">48,238</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td></tr><tr><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">&nbsp;&nbsp;&nbsp;Services</span></div></td><td colspan="2" style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-89" name="us-gaap:CostOfGoodsAndServicesSold" contextref="FD2020Q1QTD_srt_ProductOrServiceAxis_us-gaap_ServiceMember" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d57646671e805-wk-Fact-EBC0E9C503FF5DCC82787248A9A252B0" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="false" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">4,527</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="2" style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-90" name="us-gaap:CostOfGoodsAndServicesSold" contextref="FD2019Q1QTD_srt_ProductOrServiceAxis_us-gaap_ServiceMember" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d57646671e824-wk-Fact-2E04650ED96250F6A54FF7F308E9F771" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="false" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">4,041</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td></tr><tr><td style="vertical-align:bottom;padding-left:28px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">Total cost of sales</span></div></td><td colspan="2" style="vertical-align:bottom;border-bottom:1px solid #000000;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-91" name="us-gaap:CostOfGoodsAndServicesSold" contextref="FD2020Q1YTD" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d57646671e844-wk-Fact-B2C58DDE55EB5DE2842AC6C2F0D65392" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">56,602</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="2" style="vertical-align:bottom;border-bottom:1px solid #000000;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-92" name="us-gaap:CostOfGoodsAndServicesSold" contextref="FD2019Q1QTD" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d57646671e863-wk-Fact-DBCCD5CF4B315A05923AE34EE4D8FC7D" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">52,279</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td></tr><tr><td style="vertical-align:bottom;background-color:#efefef;padding-left:52px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">Gross margin</span></div></td><td colspan="2" style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-93" name="us-gaap:GrossProfit" contextref="FD2020Q1YTD" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d57646671e884-wk-Fact-19C42FB6B8C35394A5286F0F4885D997" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">35,217</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="2" style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-94" name="us-gaap:GrossProfit" contextref="FD2019Q1QTD" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d57646671e903-wk-Fact-4FCD7B4F413A5BD98ED5E68F6409504C" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">32,031</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td></tr><tr><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;height:18px;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="3" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;height:18px;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;height:18px;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="3" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;height:18px;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td></tr><tr><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">Operating expenses:</span></div></td><td colspan="3" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="3" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td></tr><tr><td style="vertical-align:bottom;padding-left:28px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">Research and development</span></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-95" name="us-gaap:ResearchAndDevelopmentExpense" contextref="FD2020Q1YTD" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d57646671e1005-wk-Fact-7B0BBC09E6AB5E16A5755C114402C592" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">4,451</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-96" name="us-gaap:ResearchAndDevelopmentExpense" contextref="FD2019Q1QTD" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d57646671e1024-wk-Fact-3E5FE68C6806582ABC60C6F883C9D8CB" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">3,902</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td></tr><tr><td style="vertical-align:bottom;background-color:#efefef;padding-left:28px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">Selling, general and administrative</span></div></td><td colspan="2" style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-97" name="us-gaap:SellingGeneralAndAdministrativeExpense" contextref="FD2020Q1YTD" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d57646671e1044-wk-Fact-70A6CCCDCC775999A85AF4940AB43ADF" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">5,197</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="2" style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-98" name="us-gaap:SellingGeneralAndAdministrativeExpense" contextref="FD2019Q1QTD" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d57646671e1063-wk-Fact-B43B72FE5E1655C189FED9248EC1CA0B" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">4,783</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td></tr><tr><td style="vertical-align:bottom;padding-left:52px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">Total operating expenses</span></div></td><td colspan="2" style="vertical-align:bottom;border-bottom:1px solid #000000;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-99" name="us-gaap:OperatingExpenses" contextref="FD2020Q1YTD" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d57646671e1083-wk-Fact-8241C862794A525DABCEF645F76E3582" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">9,648</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="2" style="vertical-align:bottom;border-bottom:1px solid #000000;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-100" name="us-gaap:OperatingExpenses" contextref="FD2019Q1QTD" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d57646671e1102-wk-Fact-AD44392EF5D858929F58E938AEF02820" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">8,685</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td></tr><tr><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;height:18px;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="3" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;border-top:1px solid #000000;"><div style="overflow:hidden;height:18px;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;height:18px;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="3" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;border-top:1px solid #000000;"><div style="overflow:hidden;height:18px;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td></tr><tr><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">Operating income</span></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-101" name="us-gaap:OperatingIncomeLoss" contextref="FD2020Q1YTD" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d57646671e1163-wk-Fact-835F60C2C4F15C63978897FC614F5C91" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">25,569</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-102" name="us-gaap:OperatingIncomeLoss" contextref="FD2019Q1QTD" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d57646671e1182-wk-Fact-F60245807C355398B38F36986E8A3B7E" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">23,346</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td></tr><tr><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">Other income/(expense), net</span></div></td><td colspan="2" style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-103" name="us-gaap:NonoperatingIncomeExpense" contextref="FD2020Q1YTD" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d57646671e1202-wk-Fact-C0817D7705F25BE198C4EA2954FD6B63" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">349</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="2" style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-104" name="us-gaap:NonoperatingIncomeExpense" contextref="FD2019Q1QTD" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d57646671e1221-wk-Fact-159777A4AB9152E48A53B62C6D6A4D83" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">560</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td></tr><tr><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">Income before provision for income taxes</span></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-105" name="us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest" contextref="FD2020Q1YTD" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d57646671e1241-wk-Fact-E15307104019595CBFC435E375744921" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">25,918</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-106" name="us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest" contextref="FD2019Q1QTD" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d57646671e1260-wk-Fact-51973D6CB59A502A94127381E7210118" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">23,906</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td></tr><tr><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">Provision for income taxes</span></div></td><td colspan="2" style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-107" name="us-gaap:IncomeTaxExpenseBenefit" contextref="FD2020Q1YTD" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d57646671e1280-wk-Fact-FEACE1086D675BA29E75E705314A6F31" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">3,682</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="2" style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-108" name="us-gaap:IncomeTaxExpenseBenefit" contextref="FD2019Q1QTD" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d57646671e1299-wk-Fact-DAED1F5874255A61A4321435BD264672" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">3,941</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td></tr><tr><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">Net income</span></div></td><td style="vertical-align:bottom;border-bottom:3px double #000000;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">$</span></div></td><td style="vertical-align:bottom;border-bottom:3px double #000000;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-109" name="us-gaap:NetIncomeLoss" contextref="FD2020Q1YTD" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d57646671e1325-wk-Fact-91EE59DD77D45F748BBA0107BDC0F304" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">22,236</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;border-bottom:3px double #000000;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td style="vertical-align:bottom;border-bottom:3px double #000000;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">$</span></div></td><td style="vertical-align:bottom;border-bottom:3px double #000000;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-110" name="us-gaap:NetIncomeLoss" contextref="FD2019Q1QTD" unitref="usd" decimals="-6" scale="6" format="ixt:numdotdecimal" data-original-id="d57646671e1344-wk-Fact-AEBE1BADC8A257848D68AC5E850D98D9" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">19,965</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;border-bottom:3px double #000000;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td></tr><tr><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;height:18px;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="3" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;height:18px;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;height:18px;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="3" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;height:18px;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td></tr><tr><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">Earnings per share:</span></div></td><td colspan="3" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="3" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td></tr><tr><td style="vertical-align:bottom;background-color:#efefef;padding-left:28px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">Basic</span></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;background-color:#efefef;"><div style="text-align:left;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">$</span></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-111" name="us-gaap:EarningsPerShareBasic" contextref="FD2020Q1YTD" unitref="usdPerShare" decimals="2" scale="0" format="ixt:numdotdecimal" data-original-id="d57646671e1446-wk-Fact-CE922FCB4816543AB8DAFDA9662D7973" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="false" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">5.04</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;background-color:#efefef;"><div style="text-align:left;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">$</span></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-112" name="us-gaap:EarningsPerShareBasic" contextref="FD2019Q1QTD" unitref="usdPerShare" decimals="2" scale="0" format="ixt:numdotdecimal" data-original-id="d57646671e1465-wk-Fact-214B2F13C0485BD9B8E159EA63773A73" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="false" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">4.22</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td></tr><tr><td style="vertical-align:bottom;padding-left:28px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">Diluted</span></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">$</span></div></td><td style="vertical-align:bottom;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-113" name="us-gaap:EarningsPerShareDiluted" contextref="FD2020Q1YTD" unitref="usdPerShare" decimals="2" scale="0" format="ixt:numdotdecimal" data-original-id="d57646671e1485-wk-Fact-F0B2A39BE95F51C2AF7842068DD11A52" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="false" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">4.99</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">$</span></div></td><td style="vertical-align:bottom;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-114" name="us-gaap:EarningsPerShareDiluted" contextref="FD2019Q1QTD" unitref="usdPerShare" decimals="2" scale="0" format="ixt:numdotdecimal" data-original-id="d57646671e1504-wk-Fact-A9D72943DC955B7B839F8F6A0F96DA4C" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="false" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">4.18</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td></tr><tr><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;height:18px;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="3" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;height:18px;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;height:18px;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="3" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;height:18px;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td></tr><tr><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">Shares used in computing earnings per share:</span></div></td><td colspan="3" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="3" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td></tr><tr><td style="vertical-align:bottom;background-color:#efefef;padding-left:28px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">Basic</span></div></td><td colspan="2" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-115" name="us-gaap:WeightedAverageNumberOfSharesOutstandingBasic" contextref="FD2020Q1YTD" unitref="shares" decimals="-3" scale="3" format="ixt:numdotdecimal" data-original-id="d57646671e1601-wk-Fact-B661469625D25E3284DDB6E26D54C3EA" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">4,415,040</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="2" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-116" name="us-gaap:WeightedAverageNumberOfSharesOutstandingBasic" contextref="FD2019Q1QTD" unitref="shares" decimals="-3" scale="3" format="ixt:numdotdecimal" data-original-id="d57646671e1620-wk-Fact-655F80FE67315A799C2C1979E97D8733" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">4,735,820</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td></tr><tr><td style="vertical-align:bottom;padding-left:28px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;">Diluted</span></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-117" name="us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding" contextref="FD2020Q1YTD" unitref="shares" decimals="-3" scale="3" format="ixt:numdotdecimal" data-original-id="d57646671e1640-wk-Fact-00CB47DE67DA5962A6593B9096C81216" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">4,454,604</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;">&nbsp;</span></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><span style="font-family:Helvetica,sans-serif;font-size:9pt;"><span><span><ix:nonfraction id="fact-identifier-118" name="us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding" contextref="FD2019Q1QTD" unitref="shares" decimals="-3" scale="3" format="ixt:numdotdecimal" data-original-id="d57646671e1659-wk-Fact-35A9990D13485EC3B06DBAA4377E7A97" continued-taxonomy="false" enabled-taxonomy="true" highlight-taxonomy="false" selected-taxonomy="false" hover-taxonomy="false" onclick="Taxonomies.clickEvent(event, this)" onkeyup="Taxonomies.clickEvent(event, this)" onmouseenter="Taxonomies.enterElement(event, this);" onmouseleave="Taxonomies.leaveElement(event, this);" tabindex="18" isamountsonly="true" istextonly="false" iscalculationsonly="true" isnegativesonly="false" isadditionalitemsonly="false" isstandardonly="true" iscustomonly="false">4,773,252</ix:nonfraction></span></span></span></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><span style="font-family:inherit;font-size:10pt;"><br></span></div></td></tr></tbody></table>'''
    soup = BeautifulSoup(response.text, 'html.parser')
    all_in_one_dict = {'Yearly': {},
                       'Quarterly': {}}

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
            date_formats = r"(((1[0-2]|0?[1-9])\/(3[01]|[12][0-9]|0?[1-9])\/(?:[0-9]{2})?[0-9]{2})|((Jan(uary)?|Feb(ruary)?|Mar(ch)?|Apr(il)?|May|Jun(e)?|Jul(y)?|Aug(ust)?|Sep(tember)?|Oct(ober)?|Nov(ember)?|Dec(ember)?)\s+\d{1,2},\s+\d{4}))"

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
                    for col in columns:
                        # Filing for June 30, 2019:
                        # Fiscal year 2019  September   December    March   June --> september and december are 2018

                        match = re.search(flexible_month_day_year_regex, col) or re.search(
                            month_slash_day_slash_year_regex, col)
                        if match:
                            for dts in ['%b %d %Y', '%m/%d/%y']:
                                try:
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

                    first_level = 'Quarterly' if (re.search(r'Quarter', table_title, re.IGNORECASE) or
                                                  re.search(r'Three|Quarter', ' '.join(columns), re.IGNORECASE)) \
                        else 'Yearly'

                    if 'Six' in first_level:
                        break

                    if len(columns) > 0 and format_match:
                        header_found = True
                        header_index = index
                        # first_bolded_index = next(i for i, v in enumerate(indented_list) if v[2])

                        for date in dates:
                            if date not in all_in_one_dict[first_level].keys():
                                all_in_one_dict[first_level][date] = {}
                            if table_title not in all_in_one_dict[first_level][date].keys():
                                all_in_one_dict[first_level][date][table_title] = {}

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
                            if current_category not in all_in_one_dict[first_level][dates[j]][table_title].keys():
                                all_in_one_dict[first_level][dates[j]][table_title][current_category] = float(
                                    re.sub('^$', '0', reg_row[i]))

                except:
                    traceback.print_exc()
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
                    # pattern_string = '^(?!.*{})'.format('Year' if filing_type == '10-Q' else 'Quarter') + pattern_string
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
    doc_links = get_filings_urls_first_layer(cik, '10-K')
    doc_links.extend(get_filings_urls_first_layer(cik, '10-Q'))
    filings_dictio = get_filings_urls_second_layer(doc_links)
    pprint(filings_dictio)
    sheet_names = [config.balance_sheet_name, config.income_statement_name, config.cash_flow_statement_name]
    missing_dates_links = []
    for sheet_name in sheet_names:
        existing_dates = excel.read_dates_from_csv(ticker, sheet_name)
        for x, y in filings_dictio['HTML Links']:
            formatted_date = datetime.strptime(x, '%Y-%m-%d')
            if formatted_date not in existing_dates and formatted_date not in [x for x, y in missing_dates_links]:
                missing_dates_links.append((formatted_date, y))

    missing_dates_links.sort(key=lambda tup: tup[0], reverse=True)
    for index, (filing_date, link) in enumerate(missing_dates_links):
        try:
            if index > 4:
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

    for sheet_period, sheet_dict in financials_dictio.items():

        for sheet_name in sheet_names:
            diction = {i.strftime('%Y-%m-%d'): {(j.split('_')[1], j.split('_')[-1] if j.split('_')[1] != j.split('_')[
                -1] else ' ') if 'Balance Sheet' not in sheet_name
                                                else (
                (j.split('_')[1], j.split('_')[2] if (len(j.split('_')) > 2) else ' ',
                 j.split('_')[-1] if j.split('_')[1] != j.split('_')[-1] else ''))
                                                : sheet_dict[i][j]
                                                for j in sheet_dict[i].keys() if j.split('_')[0] in sheet_name
                                                # sheet name
                                                } for i in sheet_dict.keys()}  # date

            df = pd.DataFrame.from_dict(diction)
            df = df.reindex(sorted(df.columns, reverse=True), axis=1)
            # if len(existing_dates_with_df) > 0:
            #     df = pd.concat([df, existing_dates_with_df[sheet_name][1]], axis=1).fillna(0)
            df.dropna(axis=0, how='all', inplace=True)
            df = df.loc[:, df.any()]

            path = '{}/{}.xlsx'.format(config.FINANCIAL_STATEMENTS_DIR_PATH, ticker)
            if not df.empty:
                # print(df.to_string())
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
        'https://www.sec.gov/ix?doc=/Archives/edgar/data/320193/000032019319000076/a10-qq320196292019.htm',
        datetime(2019, 6, 29)))


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
