import os
import re
import urllib.request
import zipfile
from datetime import timedelta
import numpy as np
import pandas as pd
import historical_data_collection.data_preparation_helpers as excel
import config


def resample_daily_df(daily_df, path):
    for freq in ['Weekly', 'Monthly', 'Quarterly', 'Yearly']:
        df = daily_df.resample(freq[0]).apply(lambda x: ((x + 1).cumprod() - 1).last("D"))
        df.index = df.index + timedelta(days=1) - timedelta(seconds=1)  # reindex to EOD
        excel.save_into_csv(filename=path, df=df, sheet_name=freq)
        daily_df.to_pickle(path + '.pkl')


def scrape_AQR_factors():
    url = 'https://images.aqr.com/-/media/AQR/Documents/Insights/Data-Sets/Quality-Minus-Junk-Factors-Daily.xlsx'
    path = os.path.join(config.FACTORS_DIR_PATH, "AQR Factors Data.xlsx")  # save it as this name
    urllib.request.urlretrieve(url, path)

    daily_df = pd.DataFrame()
    for sheet_name in ['QMJ Factors', 'MKT', 'SMB', 'HML Devil', 'UMD', 'RF']:
        temp = pd.read_excel(io=pd.ExcelFile(path), sheet_name=sheet_name, skiprows=18, index_col=0)
        temp.index = pd.to_datetime(temp.index)
        usa_series = pd.Series(temp['USA'] if sheet_name != 'RF' else temp['Risk Free Rate'], name=sheet_name)
        daily_df = daily_df.join(usa_series, how='outer') if not daily_df.empty else pd.DataFrame(usa_series)

    daily_df.rename(columns={'MKT': 'MKT-RF', 'QMJ Factors': 'QMJ', 'HML Devil': 'HML'}, inplace=True)
    os.remove(path)
    daily_df.to_excel(path, sheet_name='Daily')
    resample_daily_df(daily_df=daily_df, path=path)


def scrape_Fama_French_factors():
    daily_df = pd.DataFrame()
    for idx, url in \
            enumerate([
                # 3 Factors
                'http://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_Factors_daily_CSV.zip',
                # 5 Factors
                'https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_5_Factors_2x3_daily_CSV.zip',
                # Momentum
                'https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Momentum_Factor_daily_CSV.zip']):
        urllib.request.urlretrieve(url, 'fama_french.zip')
        zip_file = zipfile.ZipFile('fama_french.zip', 'r')
        zip_file.extractall()
        zip_file.close()
        file_name = next(file for file in os.listdir('.') if re.search('F-F', file))
        ff_factors = pd.read_csv(file_name, skiprows=3 if idx == 0 else 13, index_col=0)
        ff_factors = ff_factors[:-1] if idx == 1 else ff_factors
        ff_factors.index = pd.to_datetime(ff_factors.index, format='%Y%m%d')
        ff_factors = ff_factors.apply(lambda x: x / 100)  # original is in percent
        daily_df = ff_factors if daily_df.empty else daily_df.join(ff_factors, how='outer')
        os.remove(file_name)
        os.remove('fama_french.zip')

    path = os.path.join(config.FACTORS_DIR_PATH, 'Fama-French Factors Data')
    daily_df.rename(columns={'Mom   ': 'UMD', 'Mkt-RF': 'MKT-RF'}, inplace=True)
    daily_df.index = daily_df.index + timedelta(days=1) - timedelta(seconds=1)  # reindex to EOD
    daily_df.to_excel(path + '.xlsx', sheet_name='Daily')
    daily_df.to_pickle(path + '.pkl')
    resample_daily_df(daily_df=daily_df, path=path)


def scrape_Q_factors():
    pass


if __name__ == '__main__':
    # scrape_AQR_factors()
    scrape_Fama_French_factors()
