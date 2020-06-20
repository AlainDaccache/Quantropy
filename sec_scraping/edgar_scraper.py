import collections
import re
import traceback
from pprint import pprint
import pandas as pd
import requests
import unicodedata
from bs4 import BeautifulSoup, NavigableString
import sec_scraping.regex_patterns as fin_reg
import sec_scraping.unit_tests as test

# TODO clean up data
# - \n should be replaced with ' '

# TODO try getting data from previous years from the same statements,
#  and skip the financial reports of those years to save time

# TODO currency and unit multiplier checking in table

# TODO fill 0's with NaNs and order dataframe properly

# TODO Review regexes of balance sheet, more testing
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


# TODO override table multiplier if in row label it's written 'thousands' etc.
# SHOULD START FROM ROW, THEN CATEGORY ALl THE WAY TO HEADER THEN TITLE
def find_table_unit(table):
    unit_dict = {'thousands': 1000, 'millions': 1000000, 'billions': 1000000000}
    for unit in unit_dict.keys():
        if unit in table.text: # TODO, unit might also be outside the table, above it (but below [and including] title)
            return unit_dict[unit]
    return unit_dict['millions'] # default


def find_table_currency(table):
    pass


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
    <div style="line-height:120%;padding-top:24px;text-align:justify;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;font-weight:bold;">Other Income/(Expense), Net</font></div>
    <div style="line-height:120%;text-align:justify;font-size:10pt;"><div style="padding-left:0px;text-indent:0px;line-height:normal;padding-top:10px;"><table cellpadding="0" cellspacing="0" style="font-family:Times New Roman;font-size:10pt;width:100%;border-collapse:collapse;text-align:left;"><tbody><tr><td colspan="18"></td></tr><tr><td style="width:40%;"></td><td style="width:1%;"></td><td style="width:10%;"></td><td style="width:1%;"></td><td style="width:1%;"></td><td style="width:9%;"></td><td style="width:1%;"></td><td style="width:1%;"></td><td style="width:1%;"></td><td style="width:10%;"></td><td style="width:1%;"></td><td style="width:1%;"></td><td style="width:9%;"></td><td style="width:1%;"></td><td style="width:1%;"></td><td style="width:1%;"></td><td style="width:10%;"></td><td style="width:1%;"></td></tr><tr><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="3" style="vertical-align:bottom;border-bottom:1px solid #000000;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:center;font-size:8pt;"><font style="font-family:Helvetica,sans-serif;font-size:8pt;font-weight:bold;">2017</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;border-bottom:1px solid #000000;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:center;font-size:8pt;"><font style="font-family:Helvetica,sans-serif;font-size:8pt;font-weight:bold;">Change</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="3" style="vertical-align:bottom;border-bottom:1px solid #000000;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:center;font-size:8pt;"><font style="font-family:Helvetica,sans-serif;font-size:8pt;font-weight:bold;">2016</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;border-bottom:1px solid #000000;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:center;font-size:8pt;"><font style="font-family:Helvetica,sans-serif;font-size:8pt;font-weight:bold;">Change</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="3" style="vertical-align:bottom;border-bottom:1px solid #000000;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:center;font-size:8pt;"><font style="font-family:Helvetica,sans-serif;font-size:8pt;font-weight:bold;">2015</font></div></td></tr><tr><td style="vertical-align:top;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">Interest and dividend income</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;border-top:1px solid #000000;"><div style="text-align:left;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">$</font></div></td><td style="vertical-align:bottom;padding-top:2px;padding-bottom:2px;border-top:1px solid #000000;"><div style="text-align:right;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">5,201</font></div></td><td style="vertical-align:bottom;border-top:1px solid #000000;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;border-top:1px solid #000000;"><div style="text-align:left;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">$</font></div></td><td style="vertical-align:bottom;padding-top:2px;padding-bottom:2px;border-top:1px solid #000000;"><div style="text-align:right;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">3,999</font></div></td><td style="vertical-align:bottom;border-top:1px solid #000000;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;border-top:1px solid #000000;"><div style="text-align:left;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">$</font></div></td><td style="vertical-align:bottom;padding-top:2px;padding-bottom:2px;border-top:1px solid #000000;"><div style="text-align:right;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">2,921</font></div></td><td style="vertical-align:bottom;border-top:1px solid #000000;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td></tr><tr><td style="vertical-align:top;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">Interest expense</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">(2,323</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-right:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">)</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">(1,456</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-right:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">)</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">(733</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-right:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">)</font></div></td></tr><tr><td style="vertical-align:top;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">Other expense, net</font></div></td><td colspan="2" style="vertical-align:bottom;border-bottom:1px solid #000000;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">(133</font></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;padding-right:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">)</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;border-bottom:1px solid #000000;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">(1,195</font></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;padding-right:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">)</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td colspan="2" style="vertical-align:bottom;border-bottom:1px solid #000000;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">(903</font></div></td><td style="vertical-align:bottom;border-bottom:1px solid #000000;padding-right:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">)</font></div></td></tr><tr><td style="vertical-align:top;background-color:#efefef;padding-left:28px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="text-align:left;padding-left:12px;text-indent:-12px;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">Total other income/(expense), net</font></div></td><td style="vertical-align:bottom;border-bottom:3px double #000000;padding-left:2px;padding-top:2px;padding-bottom:2px;background-color:#efefef;"><div style="text-align:left;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">$</font></div></td><td style="vertical-align:bottom;border-bottom:3px double #000000;background-color:#efefef;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">2,745</font></div></td><td style="vertical-align:bottom;border-bottom:3px double #000000;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">104</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-right:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">%</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;border-bottom:3px double #000000;padding-left:2px;padding-top:2px;padding-bottom:2px;background-color:#efefef;"><div style="text-align:left;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">$</font></div></td><td style="vertical-align:bottom;border-bottom:3px double #000000;background-color:#efefef;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">1,348</font></div></td><td style="vertical-align:bottom;border-bottom:3px double #000000;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">5</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-right:2px;padding-top:2px;padding-bottom:2px;"><div style="text-align:left;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">%</font></div></td><td style="vertical-align:bottom;background-color:#efefef;padding-left:2px;padding-top:2px;padding-bottom:2px;padding-right:2px;"><div style="overflow:hidden;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;">&nbsp;</font></div></td><td style="vertical-align:bottom;border-bottom:3px double #000000;padding-left:2px;padding-top:2px;padding-bottom:2px;background-color:#efefef;"><div style="text-align:left;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">$</font></div></td><td style="vertical-align:bottom;border-bottom:3px double #000000;background-color:#efefef;padding-top:2px;padding-bottom:2px;"><div style="text-align:right;font-size:9pt;"><font style="font-family:Helvetica,sans-serif;font-size:9pt;">1,285</font></div></td><td style="vertical-align:bottom;border-bottom:3px double #000000;background-color:#efefef;"><div style="text-align:left;font-size:10pt;"><font style="font-family:inherit;font-size:10pt;"><br></font></div></td></tr></tbody></table></div></div>
    '''
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
        try:
            table_title = unicodedata.normalize("NFKD",
                                                find_table_title(table)).strip().replace('\n', '')
        except:
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
                elif (len(row.find_all('th')) != 0 or is_bold(row)) and not header_found:
                    header_found = True
                    # lambda tag: tag.name=='table' and tag.has_attr('id') and tag['id']=="Table1"
                    # make sure that table has a date header
                    reg_row = list(filter(fin_reg.date_regex.search, reg_row))
                    # TODO need to save relevant header index (to compare year, find currency, unit around the row...)
                    # if the table does not have a date as its headers, we're not interested in it, so move on to the next table
                    if len(reg_row) == 0:
                        # look ahead one row, maybe date in next, as long as bold (check Goldman Sachs example)
                        try:
                            if is_bold(rows[index+1]):
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
                                if is_bold(row, alltext=True): # if current row is bold
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

                    indented_list.append((current_left_margin, reg_row[0], is_bold(row, alltext=True)))
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

def normalization_first_level(input_dict):
    pass


def normalization_second_level(input_dict):
    #                 for cat in normalized_category.split('_')[1:-1]:
    #                     category_regexed.append('(?=.*{})'.format(cat))
    #                 # last_cat = normalized_category.split('_')[-1]
    #                 pattern_string = r'(' + '|'.join(category_regexed) + r').*^' + pattern_string
    pass


def normalizatation_third_level(input_dict):
    pass


def normalize_tables(input_dict):
    # pprint(input_dict)
    master_dict = collections.OrderedDict()
    for normalized_category, pattern_string in flatten_dict(fin_reg.financial_entries_regex_dict).items():
        master_dict[normalized_category] = 0
            # float('Nan')
    for scraped_name, scraped_value in flatten_dict(input_dict).items():

        found_match = False

        for normalized_category, pattern_string in flatten_dict(fin_reg.financial_entries_regex_dict).items():
            relevant = False
            if ('Balance Sheet' in normalized_category.split('_')[0] and re.search(fin_reg.balance_sheet_regex, scraped_name, re.IGNORECASE))\
                    or ('Income Statement' in normalized_category.split('_')[0] and re.search(fin_reg.income_statement_regex, scraped_name, re.IGNORECASE))\
                    or ('Cash Flow Statement' in normalized_category.split('_')[0] and re.search(fin_reg.cash_flow_statement_regex, scraped_name, re.IGNORECASE)):

                pattern_string = '^' + pattern_string

                # first we want to give priority to the elements in the consolidated financial statements
                if re.search(pattern_string, scraped_name, re.IGNORECASE):
                    found_match = True

                # this takes care of having two entries for marketable securities, accounts receivables as in Goldman Sachs
                    # so if the entry is already in the master dict, then we add to it (as in we've found before same entry, so we add to it)
                    master_dict[normalized_category] += float(re.sub('[-—–]', '0', scraped_value))
                    # np.nan_to_num(0)
                    if 'Allowances for Doubtful Accounts' in normalized_category:
                        master_dict[normalized_category] = float(re.search(pattern_string, scraped_name, re.IGNORECASE).groups()[-1])

        if not found_match and (re.search(fin_reg.balance_sheet_regex, scraped_name, re.IGNORECASE)
                                or re.search(fin_reg.income_statement_regex, scraped_name, re.IGNORECASE)
                                or re.search(fin_reg.cash_flow_statement_regex, scraped_name, re.IGNORECASE)):
            print('No match for ' + scraped_name)

    if 'Balance Sheet_Assets_Current Assets_Accounts Receivable_Net Accounts Receivable' in master_dict.keys():
        if 'Balance Sheet_Assets_Current Assets_Accounts Receivable_Allowances for Doubtful Accounts' in master_dict.keys():
            master_dict['Balance Sheet_Assets_Current Assets_Accounts Receivable_Gross Accounts Receivable'] = \
                master_dict['Balance Sheet_Assets_Current Assets_Accounts Receivable_Net Accounts Receivable'] + \
                master_dict['Balance Sheet_Assets_Current Assets_Accounts Receivable_Allowances for Doubtful Accounts']

    balance_sheet = {i: master_dict[i] for i in master_dict.keys() if re.search(r'Balance Sheet', i)}
    income_statement = {i: master_dict[i] for i in master_dict.keys() if re.search(r'Income Statement', i)}
    cash_flow_statement = {i: master_dict[i] for i in master_dict.keys() if re.search(r'Cash Flow Statement', i)}
    return master_dict


def testing():
    url = 'https://www.sec.gov/Archives/edgar/data/320193/000032019317000070/a10-k20179302017.htm'
    # all_in_one_dict = scrape_html_tables_from_url(url)
    all_in_one_dict = test.aapl_dict
    # pprint(all_in_one_dict)
    hi = {}
    hi['199'] = normalize_tables(all_in_one_dict)
    pprint(hi)
    df = pd.DataFrame.from_dict(hi)
    # pprint(df[(df.T != 0).any()])
    df = df[(df.T != 0).any()]
    df = df.replace(0, {0: float('Nan')})
    print(df)
    # pprint(normalize_tables(all_in_one_dict))

if __name__ == '__main__':
    financials_dictio = {}
    filings_dictio = get_filings_urls_second_layer('AAPL', '10-K')
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

    df = pd.DataFrame.from_dict(balance_sheet_dict)
    df = df[(df.T != 0).any()]
    df = df.replace(0, {0: float('Nan')})
    print(df.to_string())

    # testing()

