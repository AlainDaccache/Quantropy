import os
import re
import urllib.request
import zipfile
from datetime import timedelta
import pandas as pd
import config
from data.data_preparation_helpers import save_into_csv


def resample_daily_df(daily_df, path):
    for freq in ['Weekly', 'Monthly', 'Quarterly', 'Yearly']:
        df = daily_df.resample(freq[0]).apply(lambda x: ((x + 1).cumprod() - 1).last("D"))
        df.index = df.index + timedelta(days=1) - timedelta(seconds=1)  # reindex to EOD
        save_into_csv(filename=path, df=df, sheet_name=freq)


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
    daily_df.index = daily_df.index + timedelta(days=1) - timedelta(seconds=1)  # reindex to EOD
    daily_df.rename(columns={'MKT': 'MKT-RF', 'QMJ Factors': 'QMJ', 'HML Devil': 'HML'}, inplace=True)
    os.remove(path)
    daily_df.to_excel(path, sheet_name='Daily')
    resample_daily_df(daily_df=daily_df, path=path)
    daily_df.to_pickle(os.path.join(config.FACTORS_DIR_PATH, 'pickle', "AQR Factors Data.pkl"))


def scrape_Fama_French_factors():
    factors_urls = [
        ('Fama-French 3 Factors Data',
         'http://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_Factors_daily_CSV.zip'),

        ('Carhart 4 Factors Data',
         'https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Momentum_Factor_daily_CSV.zip'),

        ('Fama-French 5 Factors Data',
         'https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_5_Factors_2x3_daily_CSV.zip')]
    for idx, url in enumerate(factors_urls):
        urllib.request.urlretrieve(url[1], 'fama_french.zip')
        zip_file = zipfile.ZipFile('fama_french.zip', 'r')
        zip_file.extractall()
        zip_file.close()
        file_name = next(file for file in os.listdir('.') if re.search('F-F', file))
        skiprows = 4 if idx == 0 else 13 if idx == 1 else 3 if idx == 2 else Exception
        ff_factors = pd.read_csv(file_name, skiprows=skiprows, index_col=0)
        ff_factors.dropna(how='all', inplace=True)
        ff_factors.index = pd.to_datetime(ff_factors.index, format='%Y%m%d')
        ff_factors = ff_factors.apply(lambda x: x / 100)  # original is in percent
        ff_factors.rename(columns={'Mkt-RF': 'MKT-RF'}, inplace=True)
        ff_factors.index = ff_factors.index + timedelta(days=1) - timedelta(seconds=1)  # reindex to EOD
        if idx == 1:  # carhart
            ff_factors.rename(columns={'Mom   ': 'UMD'}, inplace=True)
            three_factors = pd.read_pickle(
                os.path.join(config.FACTORS_DIR_PATH, 'pickle', '{}.pkl'.format(factors_urls[0][0])))
            ff_factors = three_factors.join(ff_factors, how='inner')
        os.remove(file_name)
        os.remove('fama_french.zip')

        excel_path = os.path.join(config.FACTORS_DIR_PATH, '{}.xlsx'.format(url[0]))
        ff_factors.to_excel(excel_path, sheet_name='Daily')
        resample_daily_df(daily_df=ff_factors, path=excel_path)
        pickle_path = os.path.join(config.FACTORS_DIR_PATH, 'pickle', '{}.pkl'.format(url[0]))
        ff_factors.to_pickle(pickle_path)


def scrape_Q_factors():
    pass


if __name__ == '__main__':
    # scrape_AQR_factors()
    scrape_Fama_French_factors()
