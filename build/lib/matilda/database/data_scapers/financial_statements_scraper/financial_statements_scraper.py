import collections
import os
import re
import traceback
from datetime import datetime
import pandas as pd
from pprint import pprint
from matilda import config
import io
import json
from zope.interface import Interface
from matilda.data_infrastructure.data_preparation_helpers import save_pretty_excel, read_dates_from_csv


class FinancialStatementsParserInterface(Interface):
    regex_patterns: dict

    def load_data_source(self, ticker: str) -> dict:
        """
        Load in the file links

        :param ticker:
        :return: dictionary of format: frequency ('Quarterly' or 'Yearly')
                                        -> financial statement ('Balance Sheet', 'Income Statement', 'Cash Flow Statement')
                                        -> date (datetime)
                                        -> link
        """
        pass

    def scrape_tables(self, url: str, filing_date: datetime, filing_type: str) -> dict:
        """Extract tables from the currently loaded file."""
        pass

    def normalize_tables(self, regex_patterns, filing_date, input_dict, visited_data_names) -> (dict, dict):
        """Standardize tables to match across years and companies"""
        pass


date_regex = re.compile(r'^(0[1-9]|1[012])[- /.](0[1-9]|[12][0-9]|3[01])[- /.](19|20)\d\d$'  # match mm/dd/yyyy
                        r'|'
                        r'^(0[1-9]|[12][0-9]|3[01])[- /.](0[1-9]|1[012])[- /.](19|20)\d\d$'  # match dd-mm-yyyy
                        r'|'
                        r'^([^\s]+) (\d{2}),? ?(\d{4})$'  # match Month D, Yr (i.e. February 17, 2009 or February 17,2009)
                        r'|'
                        r'^\d{4}$'  # match year (i.e. 2011)
                        r'|'
                        'Fiscal\d{4}'
                        r'|'
                        r'^Change$'
                        r'|'
                        r'(\b\d{1,2}\D{0,3})?\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|(Nov|Dec)(?:ember)?)\D?(\d{1,2}\D?)?\D?((19[7-9]\d|20\d{2})|\d{2})')


# make sure delta between bigger and smaller is 3 months i.e. 3 and 6, 6 and 9, 9 and 12
def quarterlize_statements(smaller_period_df, bigger_period_df, existing_quarters):
    global closest_smaller_period_index
    df_output = pd.DataFrame()
    for bigger_period_index, bigger_period_date in enumerate(bigger_period_df.columns):
        if bigger_period_date not in existing_quarters:
            try:
                closest_smaller_period_index = next(
                    index for (index, item) in enumerate(smaller_period_df.columns) if item < bigger_period_date)
            except:
                traceback.print_exc()
            # print(closest_smaller_period_index)
            df_output[bigger_period_date] = bigger_period_df[bigger_period_date] \
                                            - smaller_period_df.iloc[:, closest_smaller_period_index]
    # print(smaller_period_df.to_string())
    return df_output


def scrape_financial_statements(scraper_interface_implementation, ticker: str, how_many_years: int = 2,
                                how_many_quarters: int = 8):
    # if not FinancialStatementsParserInterface.implementedBy(scraper_interface_implementation):
    #     raise Exception

    global quarterly_df
    path = '{}/{}.xlsx'.format(config.FINANCIAL_STATEMENTS_DIR_PATH, ticker)
    log_folder_path = os.path.join(config.DATA_DIR_PATH, 'logs')
    if not os.path.exists(log_folder_path):
        os.mkdir(log_folder_path)
    company_log_path = os.path.join(log_folder_path, ticker)
    if not os.path.exists(company_log_path):
        os.mkdir(company_log_path)

    dictio_period_year_table = {}
    filing_dictio = scraper_interface_implementation().load_data_source(ticker=ticker)

    for filing_type, statement_date_link in filing_dictio.items():
        for statement, dates_and_links in statement_date_link.items():

            # find missing dates from excel (this way we don't rescrape those that are there)
            missing_dates_links = []
            existing_dates = read_dates_from_csv(path, '{} {}'.format(statement, filing_type))

            for date, link in dates_and_links:
                formatted_date = datetime.strptime(date, '%Y-%m-%d')
                if formatted_date not in existing_dates and formatted_date not in [x for x, y in missing_dates_links]:
                    missing_dates_links.append((formatted_date, statement, link))
            missing_dates_links.sort(key=lambda tup: tup[0], reverse=True)

            for index, (filing_date, filing_statement, link) in enumerate(missing_dates_links):
                try:
                    if (index > how_many_years - 1 and filing_type == 'Yearly') \
                            or (index > how_many_quarters - 1 and filing_type == 'Quarterly'):
                        break
                    print(filing_date, link)

                    output = scraper_interface_implementation().scrape_tables(url=link, filing_date=filing_date,
                                                                              filing_type=filing_type)

                    pprint(output)
                    for sheet_period, sheet_dict in output.items():
                        if sheet_period not in dictio_period_year_table.keys():
                            dictio_period_year_table[sheet_period] = {}
                        for year, title_dict in sheet_dict.items():
                            # if we don't have the year in our dictio that collects everything, just add all and go to next year of the output
                            if year not in dictio_period_year_table[sheet_period].keys():
                                dictio_period_year_table[sheet_period][year] = title_dict
                                continue

                            #  else, we have a year, so we add up those two dicts together
                            for title, last_layer in title_dict.items():  # title / key:float
                                if title not in dictio_period_year_table[sheet_period][year].keys():
                                    dictio_period_year_table[sheet_period][year][title] = last_layer

                                else:
                                    dictio_period_year_table[sheet_period][year][title].update(last_layer)

                except Exception:
                    traceback.print_exc()

            # if same links across statements, break from loop, so you go to next filing type


    with io.open(os.path.join(company_log_path, 'scraped_dictio.txt'), "w", encoding="utf-8") as f:
        f.write(json.dumps(str(dictio_period_year_table)))

    financials_dictio = {}

    for sheet_period, sheet_dict in dictio_period_year_table.items():
        visited_data_names = {}
        if sheet_period not in financials_dictio.keys():
            financials_dictio[sheet_period] = {}
        for year, title_dict in sheet_dict.items():
            if year not in financials_dictio[sheet_period].keys():
                financials_dictio[sheet_period][year] = {}
            visited_data_names, financials_dictio[sheet_period][year] = \
                scraper_interface_implementation().normalize_tables(
                    regex_patterns=scraper_interface_implementation().regex_patterns, filing_date=year,
                    input_dict=title_dict, visited_data_names=visited_data_names)

        # log = open(os.path.join(company_log_path, '{}_normalized_dictio.txt'.format(sheet_period)), "w")
        # print(visited_data_names, file=log)
        save_pretty_excel(path=path, financials_dictio=financials_dictio)

# if __name__ == '__main__':
#     tickers = excel.get_stock_universe('DJIA')
#     for ticker in ['AAPL', 'FB']:
#         scrape_financial_statements(scraper_interface_implementation=html_scraper.HtmlParser,
#                                     ticker=ticker, how_many_years=3, how_many_quarters=0)
