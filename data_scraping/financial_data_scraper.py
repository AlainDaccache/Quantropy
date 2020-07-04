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
import ta
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
    pattern_match = re.findall('(margin-left|padding-left):(\d+)', str(td))
    if len(pattern_match) > 0:
        return max([float(m[-1]) for m in pattern_match])

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
    table = '''
    <p style="text-align:center;margin-bottom:0pt;margin-top:4pt;text-indent:0%;font-weight:bold;font-size:10pt;font-family:Times New Roman;font-style:normal;text-transform:none;font-variant: normal;"><a name="Consolidated_Balance_Sheets"></a><a name="Consolidated_Balance_Sheets"></a>Consolidated Balance Sheets </p>
    <div>
<table border="0" cellspacing="0" cellpadding="0" align="center" style="border-collapse:collapse; width:100%;">
<tbody><tr>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:66.98%;">
<p style="text-align:center;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1.62%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;color:#000000;font-size:8pt;font-family:Times New Roman;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td colspan="2" valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:13.88%;">
<p style="text-align:center;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;color:#000000;font-size:8pt;font-family:Times New Roman;font-style:normal;text-transform:none;font-variant: normal;">December 31,</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;color:#000000;font-size:8pt;font-family:Times New Roman;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1.62%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;color:#000000;font-size:8pt;font-family:Times New Roman;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td colspan="2" valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:13.88%;">
<p style="text-align:center;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;color:#000000;font-size:8pt;font-family:Times New Roman;font-style:normal;text-transform:none;font-variant: normal;">December 31,</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;color:#000000;font-size:8pt;font-family:Times New Roman;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:66.98%;">
<p style="text-align:center;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;color:#000000;font-size:8pt;font-family:Times New Roman;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1.62%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;color:#000000;font-size:8pt;font-family:Times New Roman;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td colspan="2" valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:13.88%; border-bottom:solid 0.75pt #000000;">
<p style="text-align:center;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;color:#000000;font-size:8pt;font-family:Times New Roman;font-style:normal;text-transform:none;font-variant: normal;">2015</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;color:#000000;font-size:8pt;font-family:Times New Roman;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1.62%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;color:#000000;font-size:8pt;font-family:Times New Roman;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td colspan="2" valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:13.88%; border-bottom:solid 0.75pt #000000;">
<p style="text-align:center;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;color:#000000;font-size:8pt;font-family:Times New Roman;font-style:normal;text-transform:none;font-variant: normal;">2014</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;color:#000000;font-size:8pt;font-family:Times New Roman;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:66.98%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;color:#000000;font-family:Times New Roman;font-size:10pt;font-style:normal;text-transform:none;font-variant: normal;">Assets</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1.62%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%; border-top:solid 0.75pt #000000;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%; border-top:solid 0.75pt #000000;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1.62%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%; border-top:solid 0.75pt #000000;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%; border-top:solid 0.75pt #000000;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:66.98%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">Current assets</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1.62%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1.62%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:66.98%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:13.7pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">Cash and cash equivalents</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1.62%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">$</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">1,196,908</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1.62%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">$</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">1,905,713</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:66.98%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:13.7pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">Restricted cash and marketable securities</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1.62%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">22,628</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1.62%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">17,947</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:66.98%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:13.7pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">Accounts receivable</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1.62%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">168,965</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1.62%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">226,604</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:66.98%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:13.7pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">Inventory</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1.62%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">1,277,838</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1.62%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">953,675</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;width:66.98%; border-bottom:solid 0.75pt transparent;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:13.7pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">Prepaid expenses and other current assets</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;width:1.62%; border-bottom:solid 0.75pt transparent;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%; border-bottom:solid 0.75pt #000000;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%; border-bottom:solid 0.75pt #000000;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">125,229</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;width:1%; border-bottom:solid 0.75pt transparent;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;width:1.62%; border-bottom:solid 0.75pt transparent;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%; border-bottom:solid 0.75pt #000000;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%; border-bottom:solid 0.75pt #000000;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">76,134</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;width:1%; border-bottom:solid 0.75pt transparent;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;width:66.98%; border-bottom:solid 0.75pt transparent;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:27.35pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">Total current assets</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;width:1.62%; border-bottom:solid 0.75pt transparent;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%; border-top:solid 0.75pt #000000; border-bottom:solid 0.75pt #000000;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%; border-top:solid 0.75pt #000000; border-bottom:solid 0.75pt #000000;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">2,791,568</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;width:1%; border-bottom:solid 0.75pt transparent;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;width:1.62%; border-bottom:solid 0.75pt transparent;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%; border-top:solid 0.75pt #000000; border-bottom:solid 0.75pt #000000;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%; border-top:solid 0.75pt #000000; border-bottom:solid 0.75pt #000000;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">3,180,073</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;width:1%; border-bottom:solid 0.75pt transparent;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:66.98%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">Operating lease vehicles, net</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1.62%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%; border-top:solid 0.75pt #000000;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%; border-top:solid 0.75pt #000000;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">1,791,403</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1.62%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%; border-top:solid 0.75pt #000000;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%; border-top:solid 0.75pt #000000;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">766,744</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:66.98%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">Property, plant and equipment, net</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1.62%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">3,403,334</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1.62%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">1,829,267</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:66.98%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">Restricted cash</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1.62%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">31,522</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1.62%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">11,374</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;width:66.98%; border-bottom:solid 0.75pt transparent;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">Other assets</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;width:1.62%; border-bottom:solid 0.75pt transparent;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%; border-bottom:solid 0.75pt #000000;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%; border-bottom:solid 0.75pt #000000;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">74,633</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;width:1%; border-bottom:solid 0.75pt transparent;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;width:1.62%; border-bottom:solid 0.75pt transparent;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%; border-bottom:solid 0.75pt #000000;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%; border-bottom:solid 0.75pt #000000;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">43,209</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;width:1%; border-bottom:solid 0.75pt transparent;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;width:66.98%; border-bottom:double 2.5pt transparent;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:27.35pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">Total assets</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;width:1.62%; border-bottom:double 2.5pt transparent;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%; border-top:solid 0.75pt #000000; border-bottom:double 2.5pt #000000;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">$</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%; border-top:solid 0.75pt #000000; border-bottom:double 2.5pt #000000;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">8,092,460</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;width:1%; border-bottom:double 2.5pt transparent;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;width:1.62%; border-bottom:double 2.5pt transparent;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%; border-top:solid 0.75pt #000000; border-bottom:double 2.5pt #000000;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">$</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%; border-top:solid 0.75pt #000000; border-bottom:double 2.5pt #000000;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">5,830,667</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;width:1%; border-bottom:double 2.5pt transparent;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:66.98%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;font-weight:bold;color:#000000;font-family:Times New Roman;font-size:10pt;font-style:normal;text-transform:none;font-variant: normal;">Liabilities and Stockholders' Equity</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1.62%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%; border-top:double 2.5pt #000000;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%; border-top:double 2.5pt #000000;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1.62%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%; border-top:double 2.5pt #000000;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%; border-top:double 2.5pt #000000;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:66.98%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">Current liabilities</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1.62%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1.62%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:66.98%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:13.7pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">Accounts payable</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1.62%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">$</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">916,148</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1.62%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">$</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">777,946</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:66.98%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:13.7pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">Accrued liabilities</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1.62%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">422,798</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1.62%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">268,883</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:66.98%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:13.7pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">Deferred revenue</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1.62%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">423,961</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1.62%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">191,651</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:66.98%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:13.7pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">Resale value guarantees</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1.62%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">136,831</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1.62%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">—</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:66.98%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:13.7pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">Customer deposits</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1.62%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">283,370</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1.62%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">257,587</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;width:66.98%; border-bottom:solid 0.75pt transparent;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:13.7pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">Long-term debt and capital leases</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;width:1.62%; border-bottom:solid 0.75pt transparent;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%; border-bottom:solid 0.75pt #000000;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%; border-bottom:solid 0.75pt #000000;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">633,166</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;width:1%; border-bottom:solid 0.75pt transparent;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;width:1.62%; border-bottom:solid 0.75pt transparent;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%; border-bottom:solid 0.75pt #000000;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%; border-bottom:solid 0.75pt #000000;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">611,099</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;width:1%; border-bottom:solid 0.75pt transparent;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;width:66.98%; border-bottom:solid 0.75pt transparent;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:27.35pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">Total current liabilities</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;width:1.62%; border-bottom:solid 0.75pt transparent;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%; border-bottom:solid 0.75pt #000000;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%; border-bottom:solid 0.75pt #000000;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">2,816,274</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;width:1%; border-bottom:solid 0.75pt transparent;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;width:1.62%; border-bottom:solid 0.75pt transparent;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%; border-bottom:solid 0.75pt #000000;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%; border-bottom:solid 0.75pt #000000;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">2,107,166</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;width:1%; border-bottom:solid 0.75pt transparent;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:66.98%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1.62%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1.62%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:66.98%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">Deferred revenue</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1.62%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">446,105</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1.62%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">292,271</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:66.98%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">Long-term debt and capital leases</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1.62%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">2,040,375</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1.62%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">1,818,785</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:66.98%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">Resale value guarantee</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1.62%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">1,293,741</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1.62%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">487,879</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;width:66.98%; border-bottom:solid 0.75pt transparent;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">Other long-term liabilities</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;width:1.62%; border-bottom:solid 0.75pt transparent;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%; border-bottom:solid 0.75pt #000000;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%; border-bottom:solid 0.75pt #000000;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">364,976</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;width:1%; border-bottom:solid 0.75pt transparent;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;width:1.62%; border-bottom:solid 0.75pt transparent;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%; border-bottom:solid 0.75pt #000000;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%; border-bottom:solid 0.75pt #000000;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">154,660</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;width:1%; border-bottom:solid 0.75pt transparent;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;width:66.98%; border-bottom:solid 0.75pt transparent;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:27.35pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">Total liabilities</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;width:1.62%; border-bottom:solid 0.75pt transparent;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%; border-top:solid 0.75pt #000000; border-bottom:solid 0.75pt #000000;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%; border-top:solid 0.75pt #000000; border-bottom:solid 0.75pt #000000;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">6,961,471</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;width:1%; border-bottom:solid 0.75pt transparent;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;width:1.62%; border-bottom:solid 0.75pt transparent;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%; border-top:solid 0.75pt #000000; border-bottom:solid 0.75pt #000000;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%; border-top:solid 0.75pt #000000; border-bottom:solid 0.75pt #000000;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">4,860,761</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;width:1%; border-bottom:solid 0.75pt transparent;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:66.98%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1.62%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%; border-top:solid 0.75pt #000000;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%; border-top:solid 0.75pt #000000;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1.62%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%; border-top:solid 0.75pt #000000;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%; border-top:solid 0.75pt #000000;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:66.98%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">Convertible senior notes (Notes 8)</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1.62%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">42,045</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1.62%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">58,196</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:66.98%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">Stockholders' equity:</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1.62%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1.62%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:66.98%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:13.7pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">Preferred stock; $0.001 par value; 100,000 shares authorized; no shares</p>
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:13.7pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;&nbsp; issued and outstanding</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1.62%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">—</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1.62%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">—</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:66.98%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:13.7pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">Common stock; $0.001 par value; 2,000,000 shares authorized as of</p>
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:13.7pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;&nbsp; December 31, 2015 and 2014, respectively;&nbsp;&nbsp;131,425 and 125,688</p>
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:13.7pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;&nbsp; shares issued and outstanding as of December 31, 2015 and 2014, respectively</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1.62%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">131</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1.62%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">126</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:66.98%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:13.7pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">Additional paid-in capital</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1.62%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">3,414,692</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1.62%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">2,345,266</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:66.98%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:13.7pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">Accumulated other comprehensive loss</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1.62%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">(3,556</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">)</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1.62%;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">(22</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">)</p></td>
</tr>
<tr>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;width:66.98%; border-bottom:solid 0.75pt transparent;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:13.7pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">Accumulated deficit</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;width:1.62%; border-bottom:solid 0.75pt transparent;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%; border-bottom:solid 0.75pt #000000;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%; border-bottom:solid 0.75pt #000000;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">(2,322,323</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;width:1%; border-bottom:solid 0.75pt transparent;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">)</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;width:1.62%; border-bottom:solid 0.75pt transparent;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%; border-bottom:solid 0.75pt #000000;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%; border-bottom:solid 0.75pt #000000;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">(1,433,660</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;width:1%; border-bottom:solid 0.75pt transparent;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">)</p></td>
</tr>
<tr>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;width:66.98%; border-bottom:solid 0.75pt transparent;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:27.35pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">Total stockholders' equity</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;width:1.62%; border-bottom:solid 0.75pt transparent;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%; border-top:solid 0.75pt #000000; border-bottom:solid 0.75pt #000000;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%; border-top:solid 0.75pt #000000; border-bottom:solid 0.75pt #000000;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">1,088,944</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;width:1%; border-bottom:solid 0.75pt transparent;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;width:1.62%; border-bottom:solid 0.75pt transparent;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%; border-top:solid 0.75pt #000000; border-bottom:solid 0.75pt #000000;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%; border-top:solid 0.75pt #000000; border-bottom:solid 0.75pt #000000;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">911,710</p></td>
<td valign="bottom" bgcolor="#CFF0FC" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;width:1%; border-bottom:solid 0.75pt transparent;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
<tr>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;width:66.98%; border-bottom:double 2.5pt transparent;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:27.35pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">Total liabilities and stockholders' equity</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;width:1.62%; border-bottom:double 2.5pt transparent;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%; border-top:solid 0.75pt #000000; border-bottom:double 2.5pt #000000;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">$</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%; border-top:solid 0.75pt #000000; border-bottom:double 2.5pt #000000;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">8,092,460</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;width:1%; border-bottom:double 2.5pt transparent;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;width:1.62%; border-bottom:double 2.5pt transparent;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:1%; border-top:solid 0.75pt #000000; border-bottom:double 2.5pt #000000;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">$</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;padding-Bottom:0pt;width:12.88%; border-top:solid 0.75pt #000000; border-bottom:double 2.5pt #000000;white-space:nowrap;">
<p style="text-align:right;margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-family:Times New Roman;font-size:10pt;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">5,830,667</p></td>
<td valign="bottom" bgcolor="#FFFFFF" style="padding-left:0pt;padding-Right:0.75pt;padding-Top:0.75pt;width:1%; border-bottom:double 2.5pt transparent;white-space:nowrap;">
<p style="margin-bottom:0pt;margin-top:0pt;margin-left:0pt;;text-indent:0pt;;color:#000000;font-size:1pt;font-family:Times New Roman;font-weight:normal;font-style:normal;text-transform:none;font-variant: normal;">&nbsp;</p></td>
</tr>
</tbody></table></div>
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
                # if len(row.find_all(lambda tag: tag.has_attr('style') and ('border-bottom:solid' in tag['style']
                #                                                            or 'border-top:solid' in tag['style']))) > 0:
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
                    # if re.search(r'Total', reg_row[0], re.IGNORECASE):
                    #     indented_list.pop()
                    while len(indented_list) > 0 and \
                        re.search(r'^{}$'.format(reg_row[0].split('Total ')[-1]), # current entry
                                        indented_list[-1][1], # last category
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

            if not found_match:
                if re.search(fin_reg.balance_sheet_regex, scraped_name, re.IGNORECASE):
                    # if matches current asset, put there, if matches current liability, put there etc.
                    pass
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
    # if other or net (but not both) are empty, then all under net account receivable
    if math.isnan(input_dict['Balance Sheet_Assets_Current Assets_Accounts Receivable_Net Accounts Receivable']) and \
            not math.isnan(input_dict['Balance Sheet_Assets_Current Assets_Accounts Receivable_Other Receivables']):
        input_dict['Balance Sheet_Assets_Current Assets_Accounts Receivable_Net Accounts Receivable'] = \
            input_dict['Balance Sheet_Assets_Current Assets_Accounts Receivable_Other Receivables']


    input_dict['Balance Sheet_Assets_Current Assets_Accounts Receivable_Gross Accounts Receivable'] = \
        input_dict['Balance Sheet_Assets_Current_Accounts Receivable_Net Accounts Receivable'] + \
        input_dict['Balance Sheet_Assets_Current_Accounts Receivable_Allowances for Doubtful Accounts'] + \
        input_dict['Balance Sheet_Assets_Current_Accounts Receivable_Other Receivables']


def normalize_tables(input_dict, filing_type):
    master_dict = normalization_first_level(input_dict, filing_type)
    master_dict = normalization_second_level(input_dict, master_dict, filing_type)
    # master_dict = normalizatation_third_level(master_dict)

    # balance_sheet = {i: master_dict[i] for i in master_dict.keys() if re.search(r'Balance Sheet', i)}
    # income_statement = {i: master_dict[i] for i in master_dict.keys() if re.search(r'Income Statement', i)}
    # cash_flow_statement = {i: master_dict[i] for i in master_dict.keys() if re.search(r'Cash Flow Statement', i)}
    return master_dict


def testing():
    url = 'https://www.sec.gov/Archives/edgar/data/1318605/000119312513096241/d452995d10k.htm'
    all_in_one_dict = scrape_html_tables_from_url(url)
    pprint(all_in_one_dict)
    # all_in_one_dict = test.aapl_dict
    # pprint(all_in_one_dict)
    gs_dict = {}
    pprint(normalize_tables(all_in_one_dict, filing_type='10-K'))


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


def get_stock_prices(stock, start=datetime(1970, 1, 1), end=datetime.now()):
    df = excel.read_df_from_csv(stock, config.stock_prices_sheet_name)
    if df.empty:
        df = web.DataReader(stock.replace('.', '-'), data_source='yahoo', start=start, end=end)
        df['pct_change'] = df['Adj Close'].pct_change()
        excel.save_into_csv(stock, df, config.stock_prices_sheet_name)
        return df
    return df


def get_technical_indicators(stock):
    df = excel.read_df_from_csv(stock, config.technical_indicators_name)
    if df.empty:
        df = get_stock_prices(stock)
        df = ta.add_all_ta_features(
            df, open="Open", high="High", low="Low", close="Adj Close", volume="Volume", fillna=True)
        excel.save_into_csv(stock, df, config.technical_indicators_name)
        return df
    else:
        return df

if __name__ == '__main__':
    company_tickers = ['AAPL', 'GOOG', 'FB', 'AMZN', 'TSLA', 'NFLX',
                       'MS', 'JPM', 'WFC', 'C', 'BAC',
                       'KO', 'PG', 'JNJ', 'PEP', 'VZ', 'GS']
    for ticker in company_tickers[:4]:
        get_stock_prices(ticker)
        get_technical_indicators(ticker)
        # scrape_financial_statements(ticker, '10-K')

    # testing()
    # scrape_pdf()