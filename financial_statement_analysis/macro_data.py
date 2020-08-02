from datetime import datetime, timedelta

import config
import data_scraping.excel_helpers as excel


def gross_national_product_price_index(date):
    return float(excel.read_entry_from_csv(config.MACRO_DATA_FILE_PATH, 'Yearly', 'GNP Price Index', date))

def cumulative_factors_helper(df, from_date, to_date):
    frm = excel.get_date_index(date=from_date, dates_values=df.index)
    to = excel.get_date_index(date=to_date, dates_values=df.index)
    sliced_df = df[to:] if frm == -1 else df[frm:to]
    cum_prod = (sliced_df + 1).cumprod() - 1
    return cum_prod[-1]


def cumulative_risk_free_rate(from_date, to_date):
    df = excel.read_df_from_csv(path='{}/{}.xlsx'.format(config.FACTORS_DIR_PATH, 'CAPM'), sheet_name='Daily')['RF']
    return cumulative_factors_helper(df=df, from_date=from_date, to_date=to_date)


def cumulative_market_premium(from_date, to_date):
    df = excel.read_df_from_csv(path='{}/{}.xlsx'.format(config.FACTORS_DIR_PATH, 'CAPM'), sheet_name='Daily')['Mkt-RF']
    return cumulative_factors_helper(df=df, from_date=from_date, to_date=to_date)
