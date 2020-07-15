import os
# project_dir_name = os.path.dirname(os.path.abspath("config.py"))
# financial_statements_folder_path = os.path.join(os.path.abspath(os.getcwd()).rsplit('company_analysis\\', 1)[0],
#                                                 'data_scraping',
#                                                 'financial_statements').replace('\\', '/')


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR_NAME = 'data'
DATA_DIR_PATH = os.path.join(ROOT_DIR, DATA_DIR_NAME)

MARKET_TICKERS_DIR_NAME = 'market_tickers'
MARKET_TICKERS_DIR_PATH = os.path.join(DATA_DIR_PATH, MARKET_TICKERS_DIR_NAME)

FACTORS_DIR_NAME = 'factors_data'
FACTORS_DIR_PATH = os.path.join(DATA_DIR_PATH, FACTORS_DIR_NAME)

FINANCIAL_STATEMENTS_DIR_NAME = 'financial_statements'
FINANCIAL_STATEMENTS_DIR_PATH = os.path.join(DATA_DIR_PATH, FINANCIAL_STATEMENTS_DIR_NAME)

MACRO_DATA_FILE_NAME = 'Macro-Data.xlsx'
MACRO_DATA_FILE_PATH = os.path.join(DATA_DIR_PATH, MACRO_DATA_FILE_NAME)

COMPANY_META_DATA_FILE_NAME = 'US-Stock-Symbols.xlsx'
COMPANY_META_DATA_FILE_PATH = os.path.join(DATA_DIR_PATH, COMPANY_META_DATA_FILE_NAME)

stock_prices_sheet_name = 'Stock Prices'
balance_sheet_name = 'Balance Sheets'
income_statement_name = 'Income Statements'
cash_flow_statement_name = 'Cash Flow Statements'
technical_indicators_name = 'Technical Indicators'

yearly = '10-K'
quarterly = '10-Q'

balance_sheet_quarterly = '{} {}'.format(balance_sheet_name, quarterly)
balance_sheet_yearly = '{} {}'.format(balance_sheet_name, yearly)

income_statement_quarterly = '{} {}'.format(income_statement_name, quarterly)
income_statement_yearly = '{} {}'.format(income_statement_name, yearly)

cash_flow_statement_quarterly = '{} {}'.format(cash_flow_statement_name, quarterly)
cash_flow_statement_yearly = '{} {}'.format(cash_flow_statement_name, yearly)

yearly_statements = [balance_sheet_yearly, income_statement_yearly, cash_flow_statement_yearly]
quarterly_statements = [balance_sheet_quarterly, income_statement_quarterly, cash_flow_statement_quarterly]

all_financial_statements = yearly_statements + quarterly_statements

monthly_factors = 'Monthly'
yearly_factors = 'Yearly'
