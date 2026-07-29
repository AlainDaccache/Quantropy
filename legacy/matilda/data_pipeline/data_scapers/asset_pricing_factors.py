import os
import pickle
import re
import urllib.request
import zipfile
from datetime import timedelta, datetime, date
import pandas as pd
from matilda import config


def resample_df(df: pd.DataFrame):
    # infer frequency
    test_0, test_1 = df.index[:2]  # take two consecutive elements
    delta = (test_1 - test_0).days  # timedelta object, get days
    if 1 <= delta <= 7:
        cur_freq = 'Daily'
    elif 7 <= delta <= 30.5:
        cur_freq = 'Weekly'
    elif 30.5 <= delta <= 30.5 * 4:
        cur_freq = 'Monthly'
    elif 30.5 * 4 <= delta <= 365.25:
        cur_freq = 'Quarterly'
    else:
        cur_freq = 'Yearly'

    output = {cur_freq: df}
    freqs = ['Daily', 'Weekly', 'Monthly', 'Quarterly', 'Yearly']
    for freq in freqs[freqs.index(cur_freq) + 1:]:
        df = df.resample(freq[0]).apply(lambda x: ((x + 1).cumprod() - 1).last("D"))
        df.index = df.index + timedelta(days=1) - timedelta(seconds=1)  # reindex to EOD
        output[freq] = df
    return output


def save_output_routine(factors_freq: dict, output_file_name: str):
    file_path = os.path.join(config.FACTORS_DIR_PATH, f'{output_file_name}.xlsx')
    writer = pd.ExcelWriter(file_path, engine='xlsxwriter')
    for freq, df in factors_freq.items():
        df.to_excel(writer, sheet_name=freq)
    writer.save()
    pickle_path = os.path.join(config.FACTORS_DIR_PATH, 'pickle', f'{output_file_name}.pkl')
    with open(pickle_path, 'wb') as handle:
        pickle.dump(factors_freq, handle, protocol=pickle.HIGHEST_PROTOCOL)


def scrape_factors(url: str, output_file_name: str, sep=",", skiprows=None,
                   from_date=None, to_date=None, columns_rename=None, apply_fn=None, index_col=0):
    if columns_rename is None:
        columns_rename = {'MKT': 'MKT-RF',
                          'Mkt-RF': 'MKT-RF'}

    format = url.split('.')[-1]
    if format == 'zip':
        urllib.request.urlretrieve(url, 'temp.zip')
        zip_file = zipfile.ZipFile('temp.zip', 'r')
        zip_file.extractall()
        file_name = zip_file.namelist()[0]
        zip_file.close()
        factors_df = pd.read_csv(file_name, skiprows=skiprows, sep=sep, index_col=index_col)
        os.remove(file_name)
        os.remove('temp.zip')
    else:
        factors_df = pd.read_csv(url, skiprows=skiprows, index_col=index_col, sep=sep)

    factors_df.dropna(how='all', inplace=True)  # drop rows where all entries are NaN

    for format in ['%Y%m%d', '%Y%m', '%Y']:  # convert index to datetime
        try:
            factors_df.index = pd.to_datetime(factors_df.index, format=format)
            break
        except:
            pass

    if apply_fn is not None:
        factors_df = factors_df.apply(apply_fn)  # apply function

    factors_df.rename(columns=columns_rename, inplace=True)  # rename columns
    factors_df.index = factors_df.index + timedelta(days=1) - timedelta(seconds=1)  # reindex to EOD

    if to_date is None:
        to_date = factors_df.index[-1]
    if from_date is None:
        from_date = factors_df.index[0]
    ff_factors = factors_df[(factors_df.index >= from_date) & (factors_df.index <= to_date)]  # slice dates

    resampled_ff_factors: dict = resample_df(df=ff_factors)  # resample frequencies
    save_output_routine(factors_freq=resampled_ff_factors, output_file_name=output_file_name)  # save output
    return resampled_ff_factors


def scrape_AQR_factors(output_file_name='AQR Factors'):
    url = 'https://images.aqr.com/-/media/AQR/Documents/Insights/Data-Sets/Quality-Minus-Junk-Factors-Daily.xlsx'
    path = os.path.join(config.FACTORS_DIR_PATH, "AQR Factors Data.xlsx")  # save it as this name
    urllib.request.urlretrieve(url, path)

    daily_df = pd.DataFrame()
    for sheet_name in ['QMJ Factors', 'MKT', 'SMB', 'HML Devil', 'UMD', 'RF']:
        temp = pd.read_excel(io=pd.ExcelFile(path), sheet_name=sheet_name, skiprows=18, index_col=0)
        temp.index = pd.to_datetime(temp.index)
        usa_series = pd.Series(temp['USA'] if sheet_name != 'RF' else temp['Risk Free Rate'], name=sheet_name)
        daily_df = daily_df.join(usa_series, how='outer') if not daily_df.empty else pd.DataFrame(usa_series)
    daily_df.dropna(how='all', inplace=True)
    os.remove(path)
    daily_df.rename(columns={'MKT': 'MKT-RF', 'QMJ Factors': 'QMJ', 'HML Devil': 'HML'}, inplace=True)
    resampled_df = resample_df(df=daily_df)
    save_output_routine(factors_freq=resampled_df, output_file_name=output_file_name)
    return resampled_df


if __name__ == '__main__':
    Fama_French_3 = scrape_factors(
        url='http://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_Factors_daily_CSV.zip',
        skiprows=4, apply_fn=lambda x: x / 100, output_file_name='Fama-French 3 Factors')

    # Carhart_Factor = scrape_factors(
    #     url='https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Momentum_Factor_daily_CSV.zip',
    #     skiprows=13, columns_rename={'Mom   ': 'UMD'}, output_file_name='Carhart Factor')
    #
    # Fama_French_5 = scrape_factors(
    #     url='https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_5_Factors_2x3_daily_CSV.zip',
    #     skiprows=3, output_file_name='Fama-French 5 Factors')
    #
    # Q_Factors = scrape_factors(url='http://global-q.org/uploads/1/2/2/6/122679606/q5_factors_daily_2019a.csv',
    #                            columns_rename={'R_F': 'RF', 'R_MKT': 'MKT-RF', 'R_ME': 'ME', 'R_IA': 'IA',
    #                                            'R_ROE': 'ROE', 'R_EG': 'EG'}, output_file_name='Q-Factors')

    # Pastor_Stambaugh_Factors = scrape_factors(url='http://finance.wharton.upenn.edu/~stambaug/liq_data_1962_2019.txt',
    #                                           columns_rename={'Agg Liq.': 'LIQ_AGG', 'Innov Liq (eq8)': 'LIQ_INNOV',
    #                                                           'Traded Liq (LIQ_V)': 'LIQ_V'},
    #                                           sep='\t|\t ', output_file_name='Pastor-Stambaugh Factors', skiprows=10)
    #
    # Stambaugh_Yuan_Factors = scrape_factors(url='http://finance.wharton.upenn.edu/~stambaug/M4d.csv',
    #                                         columns_rename={'MKTRF': 'MKT-RF'},
    #                                         output_file_name='Stambaugh-Yuan Factors')
    #
    # AQR_Factors = scrape_AQR_factors()
