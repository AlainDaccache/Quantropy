import os
from datetime import datetime, timedelta
import pandas_datareader.data as web
import historical_data_collection.excel_helpers as excel
import ta
import config


def save_stock_prices(stock, start=datetime(1970, 1, 1), end=datetime.now()):
    df = web.DataReader(stock.replace('.', '-'), data_source='yahoo', start=start, end=end)
    df['Pct Change'] = df['Adj Close'].pct_change()
    df.index = df.index + timedelta(days=1) - timedelta(seconds=1)
    path = os.path.join(config.STOCK_PRICES_DIR_PATH, '{}.xlsx'.format(stock))
    excel.save_into_csv(path, df, overwrite_sheet=True)
    return df


def get_technical_indicators(stock):
    df = excel.read_df_from_csv(stock, config.technical_indicators_name)
    if df.empty:
        df = save_stock_prices(stock)
        df = ta.add_all_ta_features(
            df, open="Open", high="High", low="Low", close="Adj Close", volume="Volume", fillna=True)
        path = '{}/{}.xlsx'.format(config.FINANCIAL_STATEMENTS_DIR_PATH, stock)
        excel.save_into_csv(path, df, config.technical_indicators_name)
        return df
    else:
        return df

if __name__ == '__main__':
    save_stock_prices(stock='FB')