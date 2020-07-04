import os
# project_dir_name = os.path.dirname(os.path.abspath("config.py"))
# financial_statements_folder_path = os.path.join(os.path.abspath(os.getcwd()).rsplit('company_analysis\\', 1)[0],
#                                                 'data_scraping',
#                                                 'financial_statements').replace('\\', '/')

financial_statements_folder_path = 'C:\\Users\\15148\\IdeaProjects\\Seeking_Order_In_Chaos\\data_scraping\\financial_statements'.replace('\\', '/')
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





