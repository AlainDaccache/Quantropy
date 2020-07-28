import pandas_datareader.data as web
import pandas as pd
import statsmodels.formula.api as sm # module for stats models
from statsmodels.iolib.summary2 import summary_col
import matplotlib.pyplot as plt
import numpy as np
import data_scraping.excel_helpers as excel
# https://alphaarchitect.com/2011/08/01/how-to-use-the-fama-french-model/
# https://www.sciencedirect.com/topics/economics-econometrics-and-finance/capm
# https://hackernoon.com/using-capital-asset-pricing-model-capm-versus-black-scholes-model-to-value-stocks-a-how-to-guide-r53032tc
# http://content.moneyinstructor.com/948/capm.html
import config

'''
The capital asset pricing model calculates the fair value of stocks and compares them to the market value to determine
whether the stock should be bought or not. If the fair value is more than the market value, the stock should be bought, and otherwise.

The fair value is calculated by discounting the future cash flows of the stock using the discount rate. This discount
rate is calculated by calculating the beta, which in short form gives an indication of the correlation between the
returns on the stock with that of the market.

'''

def capm(portfolio_returns, benchmark='^GSPC'):
    df_factors = excel.read_df_from_csv(path='{}/{}.xlsx'.format(config.FACTORS_DIR_PATH, 'CAPM'))
    df_factors.rename(columns={'Mkt-RF': 'MKT'}, inplace=True)
    df_factors['MKT'] = df_factors['MKT']/100
    portfolio_returns.rename('Returns', inplace=True)
    df_stock_factor = pd.merge(portfolio_returns[-1260:],df_factors,left_index=True,right_index=True) # Merging the stock and factor returns dataframes together
    df_stock_factor['XsRet'] = df_stock_factor['Returns'] - df_stock_factor['RF'] # Calculating excess returns
    CAPM = sm.ols(formula='XsRet ~ MKT', data=df_stock_factor).fit(cov_type='HAC',cov_kwds={'maxlags':1})
    # plt.plot(df_stock_factor['XsRet'], df_stock_factor['MKT'], 'r.')
    # params[0] is const coef (y-axis intersection), and params[1] is AAPL coeff (correlation coefficient)
    plt.scatter(df_stock_factor['MKT'], df_stock_factor['XsRet'])
    plt.plot(df_stock_factor['MKT'], CAPM.params[0] + CAPM.params[1] * df_stock_factor['MKT'], 'b', lw=2)
    plt.grid(True)
    plt.axis('tight')
    plt.xlabel('Beta')
    plt.ylabel('Return')
    plt.show()
    print(CAPM.params)
    return CAPM


def fama_french_3_factor_model(portfolio_returns, benchmark='^GSPC', rf=0.02):
    df_factors = web.DataReader('F-F_Research_Data_5_Factors_2x3_daily', 'famafrench')[0]
    df_factors.rename(columns={'Mkt-RF': 'MKT'}, inplace=True)
    df_factors['MKT'] = df_factors['MKT']/100
    df_factors['SMB'] = df_factors['SMB']/100
    df_factors['HML'] = df_factors['HML']/100
    portfolio_returns.rename('Returns', inplace=True)
    df_stock_factor = pd.merge(portfolio_returns,df_factors,left_index=True,right_index=True) # Merging the stock and factor returns dataframes together
    df_stock_factor['XsRet'] = df_stock_factor['Returns'] - df_stock_factor['RF'] # Calculating excess returns
    FF3 = sm.ols( formula = 'XsRet ~ MKT + SMB + HML', data=df_stock_factor).fit(cov_type='HAC',cov_kwds={'maxlags':1})

    # plt.scatter(df_stock_factor['MKT'], df_stock_factor['XsRet'])
    # plt.plot(df_stock_factor['MKT'], FF3.params[0]
    #          + FF3.params[1] * df_stock_factor['MKT']
    #          + FF3.params[2] * df_stock_factor['SMB']
    #          + FF3.params[3] * df_stock_factor['HML'], 'b', lw=2)
    # plt.grid(True)
    # plt.axis('tight')
    # plt.xlabel('Beta')
    # plt.ylabel('Return')
    # plt.show()
    print(FF3.params)

    return FF3

def carhart_4_factor_model():
    pass


def fama_french_5_factor_model(portfolio_returns):
    # Reading in factor data
    df_factors = web.DataReader('F-F_Research_Data_5_Factors_2x3_daily', 'famafrench')[0]
    df_factors.rename(columns={'Mkt-RF': 'MKT'}, inplace=True)
    df_factors['MKT'] = df_factors['MKT']/100
    df_factors['SMB'] = df_factors['SMB']/100
    df_factors['HML'] = df_factors['HML']/100
    df_factors['RMW'] = df_factors['RMW']/100
    df_factors['CMA'] = df_factors['CMA']/100
    portfolio_returns.rename('Returns', inplace=True)
    df_stock_factor = pd.merge(portfolio_returns,df_factors,left_index=True,right_index=True) # Merging the stock and factor returns dataframes together
    df_stock_factor['XsRet'] = df_stock_factor['Returns'] - df_stock_factor['RF'] # Calculating excess returns

    FF5 = sm.ols( formula = 'XsRet ~ MKT + SMB + HML + RMW + CMA', data=df_stock_factor).fit(cov_type='HAC',cov_kwds={'maxlags':1})
    return FF5

def factor_dataframe(portfolio_returns):

    capm_stats = capm(portfolio_returns)
    ff3_stats = fama_french_3_factor_model(portfolio_returns)
    ff5_stats = fama_french_5_factor_model(portfolio_returns)

    # DataFrame with coefficients and t-stats
    results_df = pd.DataFrame({'CAPMcoeff':capm_stats.params,'CAPMtstat':capm_stats.tvalues,
                               'FF3coeff':ff3_stats.params, 'FF3tstat':ff3_stats.tvalues,
                               'FF5coeff':ff5_stats.params, 'FF5tstat':ff5_stats.tvalues},
                              index = ['Intercept', 'MKT', 'SMB', 'HML', 'RMW', 'CMA'])

    dfoutput = summary_col([capm_stats,ff3_stats, ff5_stats],stars=True,float_format='%0.4f',
                           model_names=['CAPM','FF3','FF5'],
                           info_dict={'N':lambda x: "{0:d}".format(int(x.nobs)),
                                      'Adjusted R2':lambda x: "{:.4f}".format(x.rsquared_adj)},
                           regressor_order = ['Intercept', 'MKT', 'SMB', 'HML', 'RMW', 'CMA'])
    print(dfoutput)
    return results_df

portfolio_returns = web.DataReader('AAPL',data_source='yahoo')['Adj Close'].pct_change()
factor_dataframe(portfolio_returns)


def fung_hsieh_7_factor_model():
    pass

def fung_hsieh_8_factor_model():
    pass

