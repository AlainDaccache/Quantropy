import os
# project_dir_name = os.path.dirname(os.path.abspath("config.py"))
# financial_statements_folder_path = os.path.join(os.path.abspath(os.getcwd()).rsplit('company_analysis\\', 1)[0],
#                                                 'data_scraping',
#                                                 'financial_statements').replace('\\', '/')
from enum import Enum
from functools import partial

yearly = 'Yearly'
quarterly = 'Quarterly'
six_months = '6 Months'
nine_months = '9 Months'
periods = [quarterly, six_months, nine_months, yearly]

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR_PATH = os.path.join(ROOT_DIR, 'data')

MARKET_DATA_DIR_PATH = os.path.join(DATA_DIR_PATH, 'market_data')

MARKET_INDICES_DIR_PATH = os.path.join(MARKET_DATA_DIR_PATH, 'historical_indices_constituents')
TOTAL_MARKET_PATH = os.path.join(MARKET_DATA_DIR_PATH, 'US-Stock-Market.pkl')
MARKET_EXCHANGES_DIR_PATH = os.path.join(MARKET_DATA_DIR_PATH, 'historical_exchanges_constituents')

FACTORS_DIR_PATH = os.path.join(DATA_DIR_PATH, 'factors_data')

FINANCIAL_STATEMENTS_DIR_PATH = os.path.join(DATA_DIR_PATH, 'financial_statements')
FINANCIAL_STATEMENTS_DIR_PATH_EXCEL = os.path.join(FINANCIAL_STATEMENTS_DIR_PATH, 'excel')
FINANCIAL_STATEMENTS_DIR_PATH_PICKLE = os.path.join(FINANCIAL_STATEMENTS_DIR_PATH, 'pickle')
FINANCIAL_STATEMENTS_DIR_PATH_PICKLE_UNFLATTENED = os.path.join(FINANCIAL_STATEMENTS_DIR_PATH, 'unflattened_pickle')
FINANCIAL_STATEMENTS_DIR_PATH_PICKLE_QUARTERLY = os.path.join(FINANCIAL_STATEMENTS_DIR_PATH_PICKLE, quarterly)
FINANCIAL_STATEMENTS_DIR_PATH_PICKLE_YEARLY = os.path.join(FINANCIAL_STATEMENTS_DIR_PATH_PICKLE, yearly)

STOCK_PRICES_DIR_NAME = 'stock_prices'
STOCK_PRICES_DIR_PATH = os.path.join(DATA_DIR_PATH, STOCK_PRICES_DIR_NAME)

MACRO_DATA_FILE_NAME = 'Macro-Data.xlsx'
MACRO_DATA_FILE_PATH = os.path.join(DATA_DIR_PATH, MACRO_DATA_FILE_NAME)

stock_prices_sheet_name = 'Stock Prices'
balance_sheet_name = 'Balance Sheet'
income_statement_name = 'Income Statement'
cash_flow_statement_name = 'Cash Flow Statement'
technical_indicators_name = 'Technical Indicators'

balance_sheet_quarterly = '{} ({})'.format(balance_sheet_name, quarterly)
balance_sheet_yearly = '{} ({})'.format(balance_sheet_name, yearly)

income_statement_quarterly = '{} ({})'.format(income_statement_name, quarterly)
income_statement_yearly = '{} ({})'.format(income_statement_name, yearly)
income_statements = ['{} ({})'.format(income_statement_name, period) for period in periods]

cash_flow_statement_quarterly = '{} ({})'.format(cash_flow_statement_name, quarterly)
cash_flow_statement_yearly = '{} ({})'.format(cash_flow_statement_name, yearly)
cash_flow_statements = ['{} ({})'.format(cash_flow_statement_name, period) for period in periods]

yearly_statements = [balance_sheet_yearly, income_statement_yearly, cash_flow_statement_yearly]
quarterly_statements = [balance_sheet_quarterly, income_statement_quarterly, cash_flow_statement_quarterly]

all_financial_statements = yearly_statements + quarterly_statements

monthly_factors = 'Monthly'
yearly_factors = 'Yearly'

ROW_SPACE_BETWEEN_DFS = 3


# Some enumerations...

class Period(Enum):
    YEARLY = 252
    MONTHLY = 21

class Regions(Enum):
    USA = 'United States'


class Exchanges(Enum):
    NASDAQ = 'NASDAQ'
    AMEX = 'AMEX'
    NYSE = 'NYSE'


class MarketIndices(Enum):
    DOW_JONES = 'Dow-Jones'
    SP_500 = 'S&P-500'
    RUSSELL_3000 = 'Russell-3000'


class SIC_Sectors(Enum):
    AGRICULTURE_FORESTRY_FISHING = 'Agriculture, Forestry, and Fishing'
    MINING = 'Mining'
    CONSTRUCTION = 'Construction'
    MANUFACTURING = 'Manufacturing'
    TRANSPORTATION_COMMUNICATIONS_ELECTRIC_GAS_SANITARY_SERVICES = 'Transportation, Communications, Electric, Gas, And Sanitary Services'
    WHOLESALE_TRADE = 'Wholesale Trade'
    RETAIL_TRADE = 'Retail Trade'
    FINANCE_INSURANCE_REAL_ESTATE = 'Finance, Insurance, and Real Estate'
    SERVICES = 'Services'
    PUBLIC_ADMINISTRATION = 'Public Administration'


class GICS_Sectors(Enum):
    ENERGY = 'Energy'
    MATERIALS = 'Materials'
    INDUSTRIALS = 'Industrials'
    CONSUMER_DISCRETIONARY = 'Consumer Discretionary'
    CONSUMER_STAPLES = 'Consumer Staples'
    HEALTHCARE = 'Health Care'
    FINANCIALS = 'Financials'
    INFORMATION_TECHNOLOGY = 'Information Technology'
    TELECOMMUNICATION_SERVICES = 'Telecommunication Services'
    UTILITIES = 'Utilities'
    REAL_ESTATE = 'Real Estate'


class SIC_Industries(Enum):
    pass

class GICS_Industries(Enum):
    pass


class PriceAction(Enum):
    OPEN = 'Open'
    HIGH = 'High'
    LOW = 'Low'
    CLOSE = 'Close'
    ADJ_CLOSE = 'Adj Close'
    VOLUME = 'Volume'


class TimeFrame(Enum):
    ONE_MINUTE = '1m'
    FIVE_MINUTES = '5m'
    FIFTEEN_MINUTES = '15m'
    THIRTY_MINUTES = '30m'
    ONE_HOUR = '1h'
    FOUR_HOUR = '4h'
    DAILY = '1D'
    WEEKLY = 'W'
    YEARLY = 'Y'


class RebalancingFrequency(Enum):
    MONTHLY = 30.5
    QUARTERLY = 3 * 30.5
    SEMIANNUALLY = 6 * 30.5
    ANNUALLY = 365.25
