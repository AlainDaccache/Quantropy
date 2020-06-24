import collections
import os
import re
import traceback
from datetime import datetime
from pprint import pprint
import pandas as pd
import requests
import unicodedata
from bs4 import BeautifulSoup, NavigableString
import sec_scraping.regex_patterns as fin_reg
import sec_scraping.unit_tests as test
import config
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
    table = '''
    <div style="line-height:120%;padding-top:16px;text-align:center;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;font-weight:bold;">CONSOLIDATED BALANCE SHEETS</font></div>
    <div style="line-height:120%;text-align:justify;font-size:10pt;"><div style="padding-left:0px;text-indent:0px;line-height:normal;padding-top:10px;"><table cellpadding="0" cellspacing="0" style="font-family:Times New Roman;font-size:10pt;width:100%;border-collapse:collapse;text-align:left;"><tbody><tr><td colspan="8"></td></tr><tr><td style="width:71%;"></td><td style="width:1%;"></td><td style="width:12%;"></td><td style="width:1%;"></td><td style="width:1%;"></td><td style="width:1%;"></td><td style="width:12%;"></td><td style="width:1%;"></td></tr><tr><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="3" style="vertical-align:bottom;border-bottom:1px solid #000000;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:center;font-size:8pt;"><font style="font-family:Helvetica,sans-serif;font-size:8pt;font-weight:bold;">September&nbsp;29, <br>2018</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="3" style="vertical-align:bottom;border-bottom:1px solid #000000;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:center;font-size:8pt;"><font style="font-family:Helvetica,sans-serif;font-size:8pt;font-weight:bold;">September&nbsp;30, <br>2017</font></div></td></tr><tr><td colspan="8" style="vertical-align:top;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:center;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;font-weight:bold;">ASSETS:</font></div></td></tr><tr><td style="vertical-align:top;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">Current assets:</font></div></td><td colspan="3" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="3" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td></tr><tr><td style="vertical-align:top;padding-left:28px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">Cash and cash equivalents</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">$</font></div></td><td style="vertical-align:bottom;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">25,913</font></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">$</font></div></td><td style="vertical-align:bottom;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">20,289</font></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td></tr><tr><td style="vertical-align:top;background-color:#efefef;padding-left:28px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">Marketable securities</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">40,388</font></div></td><td style="vertical-align:bottom;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">53,892</font></div></td><td style="vertical-align:bottom;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td></tr><tr><td style="vertical-align:top;padding-left:28px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">Accounts receivable, net</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">23,186</font></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">17,874</font></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td></tr><tr><td style="vertical-align:top;background-color:#efefef;padding-left:28px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">Inventories</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">3,956</font></div></td><td style="vertical-align:bottom;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">4,855</font></div></td><td style="vertical-align:bottom;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td></tr><tr><td style="vertical-align:top;padding-left:28px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">Vendor non-trade receivables</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">25,809</font></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">17,799</font></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td></tr><tr><td style="vertical-align:top;background-color:#efefef;padding-left:28px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">Other current assets</font></div></td><td colspan="2" style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">12,087</font></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">13,936</font></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td></tr><tr><td style="vertical-align:top;padding-left:52px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">Total current assets</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">131,339</font></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">128,645</font></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td></tr><tr><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;height:18px;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="3" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;height:18px;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;height:18px;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="3" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;height:18px;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td></tr><tr><td style="vertical-align:top;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">Non-current assets:</font></div></td><td colspan="3" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="3" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td></tr><tr><td style="vertical-align:top;background-color:#efefef;padding-left:28px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">Marketable securities</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">170,799</font></div></td><td style="vertical-align:bottom;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">194,714</font></div></td><td style="vertical-align:bottom;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td></tr><tr><td style="vertical-align:top;padding-left:28px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">Property, plant and equipment, net</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">41,304</font></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">33,783</font></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td></tr><tr><td style="vertical-align:top;background-color:#efefef;padding-left:28px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">Other non-current assets</font></div></td><td colspan="2" style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">22,283</font></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">18,177</font></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td></tr><tr><td style="vertical-align:top;padding-left:52px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">Total non-current assets</font></div></td><td colspan="2" style="vertical-align:bottom;border-bottom:1px solid #000000;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">234,386</font></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;border-bottom:1px solid #000000;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">246,674</font></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td></tr><tr><td style="vertical-align:top;background-color:#efefef;padding-left:76px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">Total assets</font></div></td><td style="vertical-align:bottom;border-bottom:3px double #000000;padding-left:2px;padding-top:2px;padding-bottom:2px;background-color:#efefef;"><div style="text-align:left;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">$</font></div></td><td style="vertical-align:bottom;border-bottom:3px double #000000;background-color:#efefef;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">365,725</font></div></td><td style="vertical-align:bottom;border-bottom:3px double #000000;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;border-bottom:3px double #000000;padding-left:2px;padding-top:2px;padding-bottom:2px;background-color:#efefef;"><div style="text-align:left;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">$</font></div></td><td style="vertical-align:bottom;border-bottom:3px double #000000;background-color:#efefef;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">375,319</font></div></td><td style="vertical-align:bottom;border-bottom:3px double #000000;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td></tr><tr><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;height:18px;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="3" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;height:18px;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;height:18px;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="3" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;height:18px;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td></tr><tr><td colspan="8" style="vertical-align:top;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:center;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;font-weight:bold;">LIABILITIES AND SHAREHOLDERS’ EQUITY:</font></div></td></tr><tr><td style="vertical-align:top;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">Current liabilities:</font></div></td><td colspan="3" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="3" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td></tr><tr><td style="vertical-align:top;background-color:#efefef;padding-left:28px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">Accounts payable</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;background-color:#efefef;"><div style="text-align:left;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">$</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">55,888</font></div></td><td style="vertical-align:bottom;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;background-color:#efefef;"><div style="text-align:left;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">$</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">44,242</font></div></td><td style="vertical-align:bottom;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td></tr><tr><td style="vertical-align:top;padding-left:28px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">Other current liabilities</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">32,687</font></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">30,551</font></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td></tr><tr><td style="vertical-align:top;background-color:#efefef;padding-left:28px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">Deferred revenue</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">7,543</font></div></td><td style="vertical-align:bottom;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">7,548</font></div></td><td style="vertical-align:bottom;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td></tr><tr><td style="vertical-align:top;padding-left:28px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">Commercial paper</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">11,964</font></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">11,977</font></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td></tr><tr><td style="vertical-align:top;background-color:#efefef;padding-left:28px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">Term debt</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">8,784</font></div></td><td style="vertical-align:bottom;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">6,496</font></div></td><td style="vertical-align:bottom;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td></tr><tr><td style="vertical-align:top;padding-left:52px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">Total current liabilities</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;border-top:1px solid #000000;"><div style="text-align:right;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">116,866</font></div></td><td style="vertical-align:bottom;border-top:1px solid #000000;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;border-top:1px solid #000000;"><div style="text-align:right;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">100,814</font></div></td><td style="vertical-align:bottom;border-top:1px solid #000000;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td></tr><tr><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;height:18px;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="3" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;height:18px;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;height:18px;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="3" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;height:18px;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td></tr><tr><td style="vertical-align:top;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">Non-current liabilities:</font></div></td><td colspan="3" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="3" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td></tr><tr><td style="vertical-align:top;background-color:#efefef;padding-left:28px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">Deferred revenue</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">2,797</font></div></td><td style="vertical-align:bottom;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">2,836</font></div></td><td style="vertical-align:bottom;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td></tr><tr><td style="vertical-align:top;padding-left:28px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">Term debt</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">93,735</font></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">97,207</font></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td></tr><tr><td style="vertical-align:top;background-color:#efefef;padding-left:28px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">Other non-current liabilities</font></div></td><td colspan="2" style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">45,180</font></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">40,415</font></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td></tr><tr><td style="vertical-align:top;padding-left:52px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">Total non-current liabilities</font></div></td><td colspan="2" style="vertical-align:bottom;border-bottom:1px solid #000000;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">141,712</font></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;border-bottom:1px solid #000000;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">140,458</font></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td></tr><tr><td style="vertical-align:top;background-color:#efefef;padding-left:76px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">Total liabilities</font></div></td><td colspan="2" style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">258,578</font></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">241,272</font></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td></tr><tr><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;height:18px;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="3" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;height:18px;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;height:18px;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="3" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;height:18px;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td></tr><tr><td style="vertical-align:top;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">Commitments and contingencies</font></div></td><td colspan="3" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;"><br></font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="3" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;"><br></font></div></td></tr><tr><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;height:18px;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="3" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;height:18px;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;height:18px;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="3" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;height:18px;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td></tr><tr><td style="vertical-align:top;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">Shareholders’ equity:</font></div></td><td colspan="3" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="3" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td></tr><tr><td style="vertical-align:top;padding-left:28px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="padding-left:12px;text-indent:-12px;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">Common stock and additional paid-in capital, $0.00001 par value: 12,600,000 shares authorized; 4,754,986 and 5,126,201 shares issued and outstanding, respectively</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">40,201</font></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">35,867</font></div></td><td style="vertical-align:bottom;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td></tr><tr><td style="vertical-align:top;background-color:#efefef;padding-left:28px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">Retained earnings</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">70,400</font></div></td><td style="vertical-align:bottom;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">98,330</font></div></td><td style="vertical-align:bottom;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td></tr><tr><td style="vertical-align:top;padding-left:28px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">Accumulated other comprehensive income/(loss)</font></div></td><td colspan="2" style="vertical-align:bottom;border-bottom:1px solid #000000;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">(3,454</font></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;padding-right:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">)</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;border-bottom:1px solid #000000;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">(150</font></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;padding-right:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">)</font></div></td></tr><tr><td style="vertical-align:top;background-color:#efefef;padding-left:52px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">Total shareholders’ equity</font></div></td><td colspan="2" style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">107,147</font></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;border-top:1px solid #000000;"><div style="text-align:right;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">134,047</font></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;background-color:#efefef;border-top:1px solid #000000;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td></tr><tr><td style="vertical-align:top;padding-left:76px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">Total liabilities and shareholders’ equity</font></div></td><td style="vertical-align:bottom;border-bottom:3px double #000000;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">$</font></div></td><td style="vertical-align:bottom;border-bottom:3px double #000000;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">365,725</font></div></td><td style="vertical-align:bottom;border-bottom:3px double #000000;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:right;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;"><br></font></div></td><td style="vertical-align:bottom;border-bottom:3px double #000000;padding-left:2px;padding-top:2px;padding-bottom:2px;border-top:1px solid #000000;"><div style="text-align:left;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">$</font></div></td><td style="vertical-align:bottom;border-bottom:3px double #000000;padding-top:2px;padding-bottom:2px;border-top:1px solid #000000;"><div style="text-align:right;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">375,319</font></div></td><td style="vertical-align:bottom;border-bottom:3px double #000000;border-top:1px solid #000000;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td></tr></tbody></table></div></div>
    '''
    soup = BeautifulSoup(table, 'html.parser')
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
        master_dict['Balance Sheet_Assets_Current Assets_Accounts Receivable_Allowances for Doubtful Accounts'] + \
        master_dict['Balance Sheet_Assets_Current Assets_Accounts Receivable_Other Receivables']


    # balance_sheet = {i: master_dict[i] for i in master_dict.keys() if re.search(r'Balance Sheet', i)}
    # income_statement = {i: master_dict[i] for i in master_dict.keys() if re.search(r'Income Statement', i)}
    # cash_flow_statement = {i: master_dict[i] for i in master_dict.keys() if re.search(r'Cash Flow Statement', i)}
    return master_dict


def testing():
    url = 'https://www.sec.gov/Archives/edgar/data/1326801/000132680119000009/fb-12312018x10k.htm'
    all_in_one_dict = scrape_html_tables_from_url(url)
    # pprint(all_in_one_dict)
    # all_in_one_dict = test.aapl_dict
    pprint(all_in_one_dict)
    gs_dict = {'CONSOLIDATED STATEMENTS OF INCOME': {'Costs and expenses_Cost of revenue': 3789.0,
                                                    'Costs and expenses_General and administrative': 1731.0,
                                                    'Costs and expenses_Income before provision for income taxes': 12518.0,
                                                    'Costs and expenses_Income from operations': 12427.0,
                                                    'Costs and expenses_Interest and other income/(expense), net': 91.0,
                                                    'Costs and expenses_Less Net income attributable to participating securities': 29.0,
                                                    'Costs and expenses_Marketing and sales': 3772.0,
                                                    'Costs and expenses_Net income': 10217.0,
                                                    'Costs and expenses_Net income attributable to Class A and Class B common stockholders': 10188.0,
                                                    'Costs and expenses_Provision for income taxes': 2301.0,
                                                    'Costs and expenses_Research and development': 5919.0,
                                                    'Costs and expenses_Total costs and expenses': 15211.0,
                                                    'Earnings per share attributable to Class A and Class B common stockholders_Basic': 356.0,
                                                    'Earnings per share attributable to Class A and Class B common stockholders_Diluted': 349.0,
                                                    'Revenue': 27638.0,
                                                    'Share-based compensation expense included in costs and expenses_Cost of revenue': 113.0,
                                                    'Share-based compensation expense included in costs and expenses_General and administrative': 243.0,
                                                    'Share-based compensation expense included in costs and expenses_Marketing and sales': 368.0,
                                                    'Share-based compensation expense included in costs and expenses_Research and development': 2494.0,
                                                    'Share-based compensation expense included in costs and expenses_Total share-based compensation expense': 3218.0,
                                                    'Weighted average shares used to compute earnings per share attributable to Class A and Class B common stockholders_Basic': 2863.0,
                                                    'Weighted average shares used to compute earnings per share attributable to Class A and Class B common stockholders_Diluted': 2925.0}}
    # pprint(normalize_tables(gs_dict))


def save_into_excel(ticker, filing_type, balance_sheet_dict, income_statement_dict, cash_flow_statement_dict):
    if not os.path.exists(config.financial_statements_folder_path):
        os.makedirs(config.financial_statements_folder_path)

    financial_statements_file_path = "{}/{}.xlsx".format(config.financial_statements_folder_path, ticker)
    writer = pd.ExcelWriter(financial_statements_file_path, engine='xlsxwriter')

    for sheet_name, dict in zip(['{} {}'.format(config.balance_sheet_name, filing_type),
                                 '{} {}'.format(config.income_statement_name, filing_type),
                                 '{} {}'.format(config.cash_flow_statement_name, filing_type)],
                                [balance_sheet_dict, income_statement_dict, cash_flow_statement_dict]):
        with open(financial_statements_file_path, "w") as csv:
            df = pd.DataFrame.from_dict(dict)
            df = df[(df.T != 0).any()]
            df.to_excel(writer, sheet_name=sheet_name)

    writer.save()
    writer.close()


def existing_dates_in_csv(ticker):
    path = "{}/{}.xlsx".format(config.financial_statements_folder_path, ticker)
    if not os.path.exists(path):
        return []

    with open(path, "r") as csv:
        xls = pd.ExcelFile(path)
        df = pd.read_excel(xls, '{} {}'.format(config.balance_sheet_name, config.yearly), index_col=0)
        dates = [datetime.strptime(x, '%Y-%m-%d') for x in df.columns]
        return dates


if __name__ == '__main__':
    # company_tickers = ['AAPL', 'GOOG', 'FB', 'AMZN', 'TSLA', 'NFLX',
    #                    'GS', 'MS', 'JPM', 'WFC', 'C', 'BAC',
    #                    'KO', 'PG', 'JNJ', 'DIS', 'PEP', 'VZ']
    # ticker = 'AAPL'
    # filing_type = '10-K'
    # financials_dictio = {}
    # cik = get_company_cik(ticker)
    # doc_links = get_filings_urls_first_layer(cik, filing_type)
    # filings_dictio = get_filings_urls_second_layer(filing_type, doc_links)
    # pprint(filings_dictio)
    # existing_dates = existing_dates_in_csv(ticker)
    # missing_dates_links = [(x, y) for x, y in filings_dictio['HTML Links']
    #          if datetime.strptime(x, '%Y-%m-%d') not in existing_dates]
    # for filing_date, link in missing_dates_links:
    #         try:
    #             print(filing_date, link)
    #             financials_dictio[filing_date] = normalize_tables(scrape_tables_from_url(link))
    #         except Exception:
    #             traceback.print_exc()
    #
    # financials_dictio = {k: v for k, v in financials_dictio.items() if v is not None}
    # balance_sheet_dict, income_statement_dict, cash_flow_statement_dict = {}, {}, {}
    # for dictio, regex in zip([balance_sheet_dict, income_statement_dict, cash_flow_statement_dict],
    #                        [fin_reg.balance_sheet_regex, fin_reg.income_statement_regex, fin_reg.cash_flow_statement_regex]):
    #     for key, value in financials_dictio.items():
    #         dictio[key] = {}
    #         for kk, vv in value.items():
    #             if re.search(regex, kk, re.IGNORECASE):
    #                 dictio[key][kk.split('_')[-1]] = vv
    #
    # save_into_excel(ticker, filing_type, balance_sheet_dict, income_statement_dict, cash_flow_statement_dict)
    testing()
