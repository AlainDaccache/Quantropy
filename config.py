import os

financial_statements_folder_path = os.path.join(os.path.abspath(os.getcwd()).rsplit('\\', 1)[0],
                                                'sec_scraping',
                                                'financial_statements').replace('\\', '/')

balance_sheet_name = 'Balance Sheets'
income_statement_name = 'Income Statements'
cash_flow_statement_name = 'Cash Flow Statements'

yearly = '10-K'
quarterly = '10-Q'