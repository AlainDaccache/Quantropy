import os
import re
import urllib.request
import zipfile
from datetime import timedelta
import numpy as np
import pandas as pd
import historical_data_collection.excel_helpers as excel
import config


def save_factors_data(url, factor, period, skiprows):
    if len(url) == 0:  # that's for CAPM
        ff3 = pd.read_excel('{}/{}.xlsx'.format(config.FACTORS_DIR_PATH, 'Fama-French 3 Factor'),
                            sheet_name=period, index_col=0)
        capm = ff3[['Mkt-RF', 'RF']]
        excel.save_into_csv('{}/{}.xlsx'.format(config.FACTORS_DIR_PATH, factor), capm, sheet_name=period)
        return

    urllib.request.urlretrieve(url, 'fama_french.zip')
    zip_file = zipfile.ZipFile('fama_french.zip', 'r')
    zip_file.extractall()
    zip_file.close()

    file_name = next(file for file in os.listdir('.') if re.search('F-F', file))
    ff_factors = pd.read_csv(file_name, skiprows=skiprows, index_col=0)
    # We want to find out the row with NULL value. We will skip these rows
    ff_row = np.array(ff_factors.isnull().any(1)).nonzero()[0].tolist()
    ff_row = np.insert(ff_row, 0, 0, axis=0)

    # TODO waw hahaa worst hardcode
    temp_ff_row = ff_row
    for idx, val in enumerate(temp_ff_row):
        if abs(val - ff_row[idx - 1]) <= 1:
            ff_row = np.delete(ff_row, idx - 1)
            break

    first_pass = True
    formats = {'Daily': {'Format': '%Y%m%d',
                         'Offset': timedelta(days=1) - timedelta(seconds=1)},
               'Weekly': {'Format': '%Y%m%d',
                          'Offset': timedelta(days=1) - timedelta(seconds=1)},
               'Monthly': {'Format': '%Y%m',
                           'Offset': pd.offsets.MonthEnd()},
               'Yearly': {'Format': '%Y',
                          'Offset': pd.offsets.YearEnd()}}
    for idx, nrow in enumerate(ff_row[1:]):

        # Read the csv file again with skipped rows
        skiprows = skiprows + 3 if not first_pass else skiprows
        ff_factors = pd.read_csv(file_name,
                                 skiprows=ff_row[idx] + skiprows,
                                 nrows=nrow - ff_row[idx],
                                 index_col=0)

        ff_factors.index = [str(x).strip() for x in ff_factors.index.to_list()]
        cur_period = period.split('/')[0] if first_pass else period.split('/')[-1]
        format = formats[cur_period]['Format']

        try:
            ff_factors.index = pd.to_datetime(ff_factors.index, format=format)
        except:  # TODO hard fix, because of the 'copyright' row at bottom, filter later
            ff_factors = ff_factors[:-1]
            ff_factors.index = pd.to_datetime(ff_factors.index, format=format)

        if re.search('Monthly|Yearly', period, re.IGNORECASE):
            ff_factors.index = ff_factors.index + timedelta(days=1) - timedelta(seconds=1)

        ff_factors.index = ff_factors.index + formats[cur_period]['Offset']
        ff_factors = ff_factors.apply(lambda x: x / 100)
        path = os.path.join(config.FACTORS_DIR_PATH, '{}.xlsx'.format(factor))

        for col in ff_factors.columns:
            ff_factors.rename(columns={col: col.strip()}, inplace=True)

        if 'Carhart' in factor:
            ff3 = pd.read_excel('{}/{}.xlsx'.format(config.FACTORS_DIR_PATH, 'Fama-French 3 Factor'),
                                sheet_name=cur_period, index_col=0)
            ff_factors.rename(columns={'Mom': 'MOM'}, inplace=True)
            ff_factors = pd.merge(ff3, ff_factors, left_index=True, right_index=True)

        excel.save_into_csv(filename=path, df=ff_factors, sheet_name=cur_period, overwrite_sheet=True)
        first_pass = False

    os.remove(file_name)
    os.remove('fama_french.zip')

    return ff_factors


three_factors_url_daily = 'https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_Factors_daily_CSV.zip'
three_factors_url_weekly = 'https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_Factors_weekly_CSV.zip'
three_factors_url_monthly_yearly = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_Factors_CSV.zip"
five_factors_url_daily = 'https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_5_Factors_2x3_daily_CSV.zip'
five_factors_url_weekly = ''
five_factors_url_monthly_yearly = 'https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_5_Factors_2x3_CSV.zip'
momentum_factor_url_daily = 'https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Momentum_Factor_daily_CSV.zip'
momentum_factor_url_monthly_yearly = 'https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Momentum_Factor_CSV.zip'
carhart_four_factor_url_monthly = 'https://breakingdownfinance.com/wp-content/uploads/2019/07/Carhart-4-factor-data.xlsx'

factors_inputs = [
    (three_factors_url_daily, 'Fama-French 3 Factor', 'Daily', 3),
    (three_factors_url_weekly, 'Fama-French 3 Factor', 'Weekly', 3),
    (three_factors_url_monthly_yearly, 'Fama-French 3 Factor', 'Monthly/Yearly', 3),
    (five_factors_url_daily, 'Fama-French 5 Factor', 'Daily', 3),
    (five_factors_url_monthly_yearly, 'Fama-French 5 Factor', 'Monthly/Yearly', 3),
    (momentum_factor_url_daily, 'Carhart 4 Factor', 'Daily', 13),
    (momentum_factor_url_monthly_yearly, 'Carhart 4 Factor', 'Monthly/Yearly', 13),
    ('', 'CAPM', 'Daily', 0), ('', 'CAPM', 'Weekly', 0),
    ('', 'CAPM', 'Monthly', 0), ('', 'CAPM', 'Yearly', 0)
]

