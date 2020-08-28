import config
import historical_data_collection.excel_helpers as excel


def gross_national_product_price_index(date):
    return float(excel.read_entry_from_csv(config.MACRO_DATA_FILE_PATH, 'Yearly', 'GNP Price Index', date))


def cumulative_factors_helper(df, from_date, to_date):
    frm = excel.get_date_index(date=from_date, dates_values=df.index)
    to = excel.get_date_index(date=to_date, dates_values=df.index)
    sliced_df = df[to:] if frm == -1 else df[frm:to]
    cum_prod = (sliced_df + 1).cumprod() - 1
    return cum_prod[-1]


def risk_free_rate(date, freq: str = 'Yearly'):
    df = excel.read_df_from_csv(path='{}/{}.xlsx'.format(config.FACTORS_DIR_PATH, 'CAPM'), sheet_name=freq)['RF']
    date_index = excel.get_date_index(date, df.index)
    return df.iloc[date_index]


def risk_free_rates(from_date, to_date, freq: str = 'Yearly'):
    df = excel.read_df_from_csv(path='{}/{}.xlsx'.format(config.FACTORS_DIR_PATH, 'CAPM'), sheet_name=freq)['RF']
    frm = excel.get_date_index(date=from_date, dates_values=df.index)
    to = excel.get_date_index(date=to_date, dates_values=df.index)
    sliced_df = df[to:] if frm == -1 else df[frm:to]
    return sliced_df


def cumulative_risk_free_rate(from_date, to_date):
    df = excel.read_df_from_csv(path='{}/{}.xlsx'.format(config.FACTORS_DIR_PATH, 'CAPM'), sheet_name='Daily')['RF']
    return cumulative_factors_helper(df=df, from_date=from_date, to_date=to_date)


def market_premium(date, freq: str = 'Yearly'):
    df = excel.read_df_from_csv(path='{}/{}.xlsx'.format(config.FACTORS_DIR_PATH, 'CAPM'), sheet_name=freq)['Mkt-RF']
    date_index = excel.get_date_index(date, df.index)
    return df.iloc[date_index]


def cumulative_market_premium(from_date, to_date):
    df = excel.read_df_from_csv(path='{}/{}.xlsx'.format(config.FACTORS_DIR_PATH, 'CAPM'), sheet_name='Daily')['Mkt-RF']
    return cumulative_factors_helper(df=df, from_date=from_date, to_date=to_date)
