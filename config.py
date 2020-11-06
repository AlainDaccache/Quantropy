import os
# project_dir_name = os.path.dirname(os.path.abspath("config.py"))
# financial_statements_folder_path = os.path.join(os.path.abspath(os.getcwd()).rsplit('company_analysis\\', 1)[0],
#                                                 'data_scraping',
#                                                 'financial_statements').replace('\\', '/')


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR_NAME = 'data'
DATA_DIR_PATH = os.path.join(ROOT_DIR, DATA_DIR_NAME)

MARKET_INDICES_DIR_NAME = 'historical_indices_constituents'
MARKET_INDICES_DIR_PATH = os.path.join(DATA_DIR_PATH, MARKET_INDICES_DIR_NAME)
MARKET_INDICES_TOTAL_US_STOCK_MARKET = os.path.join(MARKET_INDICES_DIR_PATH, 'iShares-Core-SP-Total-US-Stock-Market-ETF_fund.xlsx')


MARKET_EXCHANGES_DIR_NAME = 'historical_exchanges_constituents'
MARKET_EXCHANGES_DIR_PATH = os.path.join(DATA_DIR_PATH, MARKET_EXCHANGES_DIR_NAME)
FACTORS_DIR_NAME = 'factors_data'
FACTORS_DIR_PATH = os.path.join(DATA_DIR_PATH, FACTORS_DIR_NAME)

FINANCIAL_STATEMENTS_DIR_NAME = 'financial_statements'
FINANCIAL_STATEMENTS_DIR_PATH = os.path.join(DATA_DIR_PATH, FINANCIAL_STATEMENTS_DIR_NAME)

STOCK_PRICES_DIR_NAME = 'stock_prices'
STOCK_PRICES_DIR_PATH = os.path.join(DATA_DIR_PATH, STOCK_PRICES_DIR_NAME)

MACRO_DATA_FILE_NAME = 'Macro-Data.xlsx'
MACRO_DATA_FILE_PATH = os.path.join(DATA_DIR_PATH, MACRO_DATA_FILE_NAME)

COMPANY_META_DATA_FILE_NAME = 'Companies_Metadata.xlsx'
COMPANY_META_DATA_FILE_PATH = os.path.join(DATA_DIR_PATH, COMPANY_META_DATA_FILE_NAME)

stock_prices_sheet_name = 'Stock Prices'
balance_sheet_name = 'Balance Sheet'
income_statement_name = 'Income Statement'
cash_flow_statement_name = 'Cash Flow Statement'
technical_indicators_name = 'Technical Indicators'

yearly = 'Yearly'
quarterly = 'Quarterly'
six_months = '6 Months'
nine_months = '9 Months'
periods = [quarterly, six_months, nine_months, yearly]

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