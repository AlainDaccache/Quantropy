from datetime import datetime, timedelta
from pprint import pprint

import company_analysis.financial_statements_entries as financials
import company_analysis.financial_metrics as metrics
import company_analysis.accounting_ratios as ratios
import numpy as np

'''
Default Prediction Models
'''


def piotroski_f_score(stock, date=datetime.now(), annual=True, ttm=False, diluted_shares=True):
    boolean_list = {}

    # Return on Assets (1 point if it is positive in the current year, 0 otherwise)
    boolean_list['Return on Assets'] = ratios.return_on_assets(stock, date, annual, ttm) > 0

    # Operating Cash Flow (1 point if it is positive in the current year, 0 otherwise)
    boolean_list['Operating Cash Flow'] = financials.cash_flow_operating_activities(stock, date, annual, ttm) > 0

    # Change in Return of Assets (ROA) (1 point if ROA is higher in the current year compared to the previous one, 0 otherwise)
    boolean_list['Change in Return of Assets'] = ratios.return_on_assets(stock, date, annual, ttm) \
                                                 > ratios.return_on_assets(stock, date-timedelta(days=365), annual, ttm)

    # Accruals (1 point if Operating Cash Flow/Total Assets is higher than ROA in the current year, 0 otherwise)
    boolean_list['Accruals'] = financials.cash_flow_operating_activities(stock, date, annual, ttm) / \
                               financials.total_assets(stock, date, annual, ttm) \
                               > ratios.return_on_assets(stock, date, annual, ttm)

    # Change in Leverage (long-term) ratio (1 point if the ratio is lower this year compared to the previous one, 0 otherwise)
    boolean_list['Change in Leverage Ratio'] = ratios.debt_to_capital(stock, date, annual, ttm, long_term=True) \
                                               > ratios.debt_to_capital(stock, date-timedelta(days=365), annual, ttm, long_term=True)

    # Change in Current ratio (1 point if it is higher in the current year compared to the previous one, 0 otherwise)
    boolean_list['Change in Current Ratio'] = ratios.current_ratio(stock, date, annual, ttm) \
                                              > ratios.current_ratio(stock, date-timedelta(days=365), annual, ttm)

    # Change in the number of shares (1 point if no new shares were issued during the last year)
    boolean_list['Change in Number of Shares'] = financials.total_shares_outstanding(stock, date, diluted_shares, annual, ttm) <= \
                                                 financials.total_shares_outstanding(stock, date - timedelta(days=365), diluted_shares, annual, ttm)

    # Change in Gross Margin (1 point if it is higher in the current year compared to the previous one, 0 otherwise)
    boolean_list['Gross Margin'] = ratios.gross_margin(stock, date, annual, ttm) \
                                   > ratios.gross_margin(stock, date-timedelta(days=365), annual, ttm)

    # Change in Asset Turnover ratio (1 point if it is higher in the current year compared to the previous one, 0 otherwise)
    boolean_list['Asset Turnover Ratio'] = ratios.asset_turnover_ratio(stock, date, annual, ttm) \
                                           > ratios.asset_turnover_ratio(stock, date-timedelta(days=365), annual, ttm)

    return boolean_list


def altman_z_score(stock, date=datetime.now()):
    A = metrics.working_capital(stock, date) / financials.total_assets(stock, date)
    B = financials.retained_earnings(stock, date) / financials.total_assets(stock, date)
    C = metrics.ebit(stock, date) / financials.total_assets(stock, date)
    D = metrics.market_capitalization(stock, date) / financials.total_liabilities(stock, date)
    E = financials.net_sales(stock, date) / financials.total_assets(stock, date)
    return 1.2*A + 1.4*B + 3.3*C + 0.6*D + 1.0*E


def stock_x_industry(stock):
    pass


def altman_z_score_plus(stock, date=datetime.now()):
    A = metrics.working_capital(stock, date) / financials.total_assets(stock, date)
    B = financials.retained_earnings(stock, date) / financials.total_assets(stock, date)
    C = metrics.ebit(stock, date) / financials.total_assets(stock, date)
    D = financials.total_shareholders_equity(stock, date) / financials.total_liabilities(stock, date)
    if ('Manufacturing' not in stock_x_industry(stock)) and ('Manufacturers' not in stock_x_industry(stock)):
        return 6.56*A + 3.26*B + 6.72*C + 1.05*D
    elif 'Emerging Markets Integrated' in stock_x_industry(stock):
        return 3.25 + 6.56*A + 3.26*B + 6.72*C + 1.05*D
    else:
        return altman_z_score(stock, date)


def gross_national_product_price_index_level(date):
    pass


def ohlson_o_score(stock, date=datetime.now()):
    TA = financials.total_assets(stock, date)
    GNP = gross_national_product_price_index_level(date)
    TL = financials.total_liabilities(stock, date)
    WC = metrics.working_capital(stock, date)
    CL = financials.current_total_liabilities(stock, date)
    CA = financials.current_total_assets(stock, date)
    X = 1 if TL > TA else 0
    NI = financials.net_income(stock, date)
    NI_prev = financials.net_income(stock, date - timedelta(days=365))
    FFO = financials.cash_flow_operating_activities(stock, date) # TODO should do 'funds from operations' instead
    Y = 1 if (NI < 0 and NI_prev < 0) else 0
    return -1.32 - 0.407 * np.log(TA/GNP) + 6.03 * (TL/TA) - 1.43 * (WC/TA) + 0.0757 * (CL/CA) - 1.72 * X \
           - 2.37 * (NI/TA) - 1.83 * (FFO/TL) + 0.285 * Y - 0.521 * ((NI - NI_prev) / (abs(NI) + abs(NI_prev)))


'''
Earnings Manipulation Models
'''

if __name__ == '__main__':
    dict = piotroski_f_score('AAPL')
    pprint(dict)
    print(sum(v for k, v in dict.items()))
