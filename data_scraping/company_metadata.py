import traceback
import pandas as pd
import pickle
import re
import requests
import unicodedata
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from time import sleep
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pprint import pprint
import numpy as np
import os
import config
import urllib


def save_gics():
    url = 'https://en.wikipedia.org/wiki/Global_Industry_Classification_Standard'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', class_='wikitable')

    headers = []
    for th in table.find_all('th', {'colspan': '2'}):
        headers.append(th.text.rstrip())

    gics_dict = {}
    for tr in table.find_all('tr'):
        for td in tr.find_all('td'):
            if re.search(r'^\d{2}$', td.text):  # two digits code is for sector
                gics_dict[(td.text.rstrip(), td.nextSibling.nextSibling.text.rstrip())] = {}
            elif re.search(r'^\d{4}$', td.text):  # four digits code is for industry group
                sector_number = td.text[:2]
                for key, value in gics_dict.items():
                    if key[0] == sector_number:
                        gics_dict[key][(td.text.rstrip(), td.nextSibling.nextSibling.text.rstrip())] = {}
            elif re.search(r'^\d{6}$', td.text):  # six digits code is for industry
                industry_group_number = td.text[:4]
                for key, value in gics_dict.items():
                    for kk, vv in value.items():
                        if kk[0] == industry_group_number:
                            gics_dict[key][kk][(td.text.rstrip(), td.nextSibling.nextSibling.text.rstrip())] = []
            elif re.search(r'^\d{8}$', td.text):  # eight digits code is for sub-industry
                industry_number = td.text[:6]
                for key, value in gics_dict.items():
                    for kk, vv in value.items():
                        for kkk, vvv in vv.items():
                            if kkk[0] == industry_number:
                                gics_dict[key][kk][kkk].append(
                                    (td.text.rstrip(), td.nextSibling.nextSibling.text.rstrip()))

    pprint(gics_dict)
    cleaned_gics_dict = {}
    for key, value in gics_dict.items():
        cleaned_gics_dict[key[1]] = {}
        for kk, vv in value.items():
            cleaned_gics_dict[key[1]][kk[1]] = {}
            for kkk, vvv in vv.items():
                cleaned_gics_dict[key[1]][kk[1]][kkk[1]] = []
                for v in vvv:
                    cleaned_gics_dict[key[1]][kk[1]][kkk[1]].append(v[1])
    pprint(cleaned_gics_dict)
    # df = pd.DataFrame.from_dict({(i, j, k): pd.Series(l)
    #                             for i in cleaned_gics_dict.keys()
    #                             for j in cleaned_gics_dict[i].keys()
    #                             for k, l in cleaned_gics_dict[i][j].items()},
    #                             orient='index')

    # df = pd.concat({k: pd.DataFrame(v).T for k, v in cleaned_gics_dict.items()}, axis=0)
    df = pd.DataFrame([(i, j, k, l)
                       for i in cleaned_gics_dict.keys()
                       for j in cleaned_gics_dict[i].keys()
                       for k in cleaned_gics_dict[i][j].keys()
                       for l in cleaned_gics_dict[i][j][k]])

    df.columns = headers
    df.set_index((df.columns[0]), inplace=True)

    # df.columns = headers
    # df = df.iloc[:,1]
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
        print(df)

    writer = pd.ExcelWriter(os.path.join(config.ROOT_DIR, config.DATA_DIR_NAME, 'Industry-Classification.xlsx'),
                            engine='xlsxwriter')
    df.to_excel(writer, sheet_name='GICS')

    writer.save()


def save_nasdaq():
    urls = ['ftp://ftp.nasdaqtrader.com/symboldirectory/nasdaqlisted.txt',
            'ftp://ftp.nasdaqtrader.com/symboldirectory/nasdaqtraded.txt']
    main_df = pd.DataFrame()
    for url in urls:
        path = os.path.join(config.ROOT_DIR, config.DATA_DIR_NAME, config.MARKET_TICKERS_DIR_NAME, 'NASDAQ_Listed.txt')
        urllib.request.urlretrieve(url, path)
        if main_df.empty:
            main_df = pd.read_csv(path, sep="|")[:-1]
        else:
            cur_df = pd.read_csv(path, sep="|")[:-1]
            main_df = pd.concat([main_df, cur_df], axis=0, ignore_index=True)
            main_df = main_df.drop_duplicates('Symbol').reset_index(drop=True)
            # main_df['feedback_id'].fillna(main_df['Symbol'])
            # main_df = main_df.drop_duplicates().reset_index(drop=True)
            # main_df.set_index(list(main_df)[0], inplace=True)
            main_df.set_index('Symbol', inplace=True)
            main_df = main_df[['Security Name', 'Financial Status', 'ETF']]
            main_df.sort_index(inplace=True)
    with open(os.path.join(config.ROOT_DIR, config.DATA_DIR_NAME, config.MARKET_TICKERS_DIR_NAME, "nasdaq_df.pickle"),
              "wb") as f:
        pickle.dump(main_df, f)
    os.remove(os.path.join(config.ROOT_DIR, config.DATA_DIR_NAME, config.MARKET_TICKERS_DIR_NAME, 'NASDAQ_Listed.txt'))
    print(main_df.head())
    return


def save_dow_jones_tickers():
    url = 'https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average'
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'lxml')
    table = soup.find('table', {'class': 'wikitable sortable'})
    tickers = []
    for row in table.findAll('tr')[1:]:
        ticker = unicodedata.normalize("NFKD", row.findAll('td')[2].text).split(': ')[-1]
        ticker = ticker.strip()
        tickers.append(ticker)

    with open(os.path.join(config.ROOT_DIR, config.DATA_DIR_NAME, config.MARKET_TICKERS_DIR_NAME,
                           "djia30_tickers.pickle"), "wb") as f:
        pickle.dump(tickers, f)

    return tickers


def save_sp500_tickers():
    url = 'http://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'lxml')
    table = soup.find('table', {'class': 'wikitable sortable'})
    tickers = []
    for row in table.findAll('tr')[1:]:
        ticker = row.findAll('td')[0].text
        ticker = ticker.strip()
        tickers.append(ticker)

    with open(
            os.path.join(config.ROOT_DIR, config.DATA_DIR_NAME, config.MARKET_TICKERS_DIR_NAME, "sp500_tickers.pickle"),
            "wb") as f:
        pickle.dump(tickers, f)

    return tickers


def save_russell_3000_tickers():
    url = "http://www.beatthemarketanalyzer.com/blog/wp-content/uploads/2016/10/Russell-3000-Stock-Tickers-List.xlsx"
    path = os.path.join(config.ROOT_DIR, config.DATA_DIR_NAME, config.MARKET_TICKERS_DIR_NAME,
                        'Russell-3000-Stock-Tickers-List.xlsx')
    urllib.request.urlretrieve(url, path)
    df = pd.read_excel(pd.ExcelFile(path), index_col=0, skiprows=3)
    print(df.to_string())
    tickers = list(df.index)
    with open(os.path.join(config.ROOT_DIR, config.DATA_DIR_NAME, config.MARKET_TICKERS_DIR_NAME,
                           "russell3000_tickers.pickle"), "wb") as f:
        pickle.dump(tickers, f)
    os.remove(path)


def get_company_meta():
    with open(os.path.join(config.ROOT_DIR, config.DATA_DIR_NAME, config.MARKET_TICKERS_DIR_NAME, "nasdaq_df.pickle"),
              "rb") as f:
        nasdaq_df = pickle.load(f)

    nasdaq_tickers = nasdaq_df.index
    driver = webdriver.Chrome(ChromeDriverManager().install())
    comp_list = []
    financial_status_codes = {'D': 'Deficient',
                              'E': 'Delinquent',
                              'Q': 'Bankrupt',
                              'N': 'Normal',
                              'G': 'Deficient and Bankrupt',
                              'H': 'Deficient and Delinquent',
                              'J': 'Delinquent and Bankrupt',
                              'K': 'Deficient, Delinquent, and Bankrupt'}

    sic_codes_division = {(1, 9 + 1): 'Agriculture, Forestry, and Fishing',
                          (10, 14 + 1): 'Mining',
                          (15, 17 + 1): 'Construction',
                          (20, 39 + 1): 'Manufacturing',
                          (40, 49 + 1): 'Transportation, Communications, Electric, Gas, And Sanitary Services',
                          (50, 51 + 1): 'Wholesale Trade',
                          (52, 59 + 1): 'Retail Trade',
                          (60, 67 + 1): 'Finance, Insurance, and Real Estate',
                          (70, 89 + 1): 'Services',
                          (90, 99 + 1): 'Public Administration'}

    with open(os.path.join(config.ROOT_DIR, config.DATA_DIR_NAME, "country_codes_dictio.pickle"),
              "rb") as f:
        country_codes = pickle.load(f)

    # for ticker in nasdaq_tickers[:200]:
    for ticker in nasdaq_tickers[:200]:

        security_name = nasdaq_df['Security Name'].loc[ticker].split('-')[0].strip()
        security_type = nasdaq_df['Security Name'].loc[ticker].split('-')[1].strip() \
            if len(nasdaq_df['Security Name'].loc[ticker].split('-')) > 1 else 'Exchange-Traded Fund'
        try:
            financial_status = financial_status_codes[nasdaq_df['Financial Status'].loc[ticker]]
        except:
            financial_status = np.nan
        industry, sector, cik, state_location = '', '', '', ''
        sic_code = 0

        try:
            for i in range(2):  # just try again if didn't work first time, might be advertisement showed up
                try:
                    button = driver.find_element_by_xpath("//a[@class='acsCloseButton acsAbandonButton ']")
                    button.click()
                    sleep(1)
                except:
                    pass
                if nasdaq_df['ETF'].loc[ticker] == 'Y':
                    driver.get('https://www.sec.gov/edgar/searchedgar/mutualsearch.html')
                    field = driver.find_element_by_xpath("//input[@id='gen_input']")
                    field.send_keys(ticker)  # TODO might split ticker from the '$' or '.' (classes)
                    sleep(1)
                    field.send_keys(Keys.ENTER)
                    sleep(1)
                    if 'No records matched your query' not in driver.page_source:
                        for t in driver.find_elements_by_xpath("//b[@class='blue']"):  # TODO
                            if t.text == ticker:
                                cik = driver.find_element_by_xpath('').text
                                security_type = driver.find_element_by_xpath('').text
                    break  # still should go to the 'finally' block

                base_url = 'https://www.sec.gov/cgi-bin/browse-edgar?CIK={}'.format(ticker)
                resp = requests.get(base_url).text

                if 'No matching Ticker Symbol' in resp or 'No records matched your query' in resp:
                    driver.get('https://www.sec.gov/edgar/searchedgar/companysearch.html')
                    # html = driver.page_source TODO for new 10-K forms maybe works?
                    input_box = driver.find_element_by_xpath("//input[@id='company']")
                    input_box.send_keys(ticker)
                    html = driver.page_source
                    # wait until the autofill box loads
                    WebDriverWait(driver, 10).until(EC.visibility_of_element_located(
                        (By.XPATH, "//tr[@class='smart-search-hint smart-search-selected-hint']")))
                    element = driver.find_element_by_xpath(
                        "//tr[@class='smart-search-hint smart-search-selected-hint']")
                    if not re.search(r'(\(|[^A-Z]){}([^A-Z]|\))'.format(ticker), element.text):
                        break
                    sleep(1)
                    input_box.send_keys(Keys.ENTER)
                    # wait until company page loads
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "seriesDiv")))
                    resp = requests.get(driver.current_url).text

                soup = BeautifulSoup(resp, 'html.parser')
                # name = soup.find('span', class_='companyName').text.split(' CIK')[0]
                cik = re.compile(r'.*CIK#: (\d{10}).*').findall(soup.text)[0]
                ident_info = soup.find('p', class_="identInfo")
                industry = ident_info.find('br').previousSibling.split('- ')[-1]
                sic_code = re.search(r'(\d{4})', ident_info.text).group()
                country_code = re.compile(r'.*State location: (..)').findall(soup.text)[0]
                for type, code_dict in country_codes.items():
                    if country_code in code_dict.keys():
                        state_location = type + '/' + code_dict[country_code]
                        break

                for key, value in sic_codes_division.items():
                    if int(sic_code[0]) == 0:
                        if int(sic_code[1]) in range(key[0], key[1]):
                            sector = value
                            break
                    elif int(sic_code[:2]) in range(key[0], key[1]):
                        sector = value
                        break

                break

            # except TimeoutException or ElementNotInteractableException:
        except:
            driver.get('https://www.sec.gov/edgar/searchedgar/companysearch.html')

        finally:
            comp_list.append([ticker,
                              security_name,
                              industry.title(),
                              sector.title(),
                              sic_code,
                              cik,
                              state_location,
                              security_type,
                              financial_status])

    comp_df = pd.DataFrame(comp_list,
                           columns=['Ticker', 'Company Name', 'Industry', 'Sector', 'SIC Code', 'CIK', 'Location', 'Security Type',
                                    'Financial Status'])
    comp_df = comp_df[comp_df['Security Type'] != 'Exchange-Traded Fund']  # remove ETFs for now
    comp_df.set_index('Ticker', inplace=True)

    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(comp_df.to_string())
    path = os.path.join(config.ROOT_DIR, config.DATA_DIR_NAME, 'Nasdaq-Companies.xlsx')
    comp_df.to_excel(path, engine='xlsxwriter')


def save_country_codes():
    dictio = {}
    url = 'https://www.sec.gov/edgar/searchedgar/edgarstatecodes.htm'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    for table in soup.find_all('table', {'cellpadding':'3'}):
        current_category = ''
        for tr in table.find_all('tr')[1:]:
            if len(tr.find_all('th')) > 0:
                current_category = unicodedata.normalize("NFKD", tr.text).replace('\n', '')
                if current_category == 'States':
                    current_category = 'United States'
                dictio[current_category] = {}
            else:
                code = unicodedata.normalize("NFKD", tr.find_all('td')[0].text).replace('\n', '')
                state = unicodedata.normalize("NFKD", tr.find_all('td')[1].text).replace('\n', '')
                dictio[current_category][code] = state
    with open(os.path.join(config.ROOT_DIR, config.DATA_DIR_NAME, "country_codes_dictio.pickle"),
              "wb") as f:
        pickle.dump(dictio, f)
    pprint(dictio)


if __name__ == '__main__':
    # save_gics()
    save_dow_jones_tickers()
    # save_sp500_tickers()
    # save_russell_3000_tickers()
    # save_nasdaq()
    # get_company_meta()
    # save_country_codes()
