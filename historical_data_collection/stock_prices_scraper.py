import os
from datetime import datetime, timedelta
import pandas_datareader.data as web
import typing
import pandas as pd
import historical_data_collection.data_preparation_helpers as excel
import ta
import config
import macroeconomic_analysis.macroeconomic_analysis as macro


def save_stock_prices(stock, start=datetime(1970, 1, 1), end=datetime.now()):
    if isinstance(stock, config.MarketIndices):
        stock = macro.companies_in_index(market_index=stock, date=end)
    if isinstance(stock, typing.List):
        stock = [stk.replace('.', '-') for stk in stock]
    else:
        stock = stock.replace('.', '-')
    for stk in list(stock):
        df: pd.DataFrame = web.DataReader(stk, data_source='yahoo', start=start, end=end)
        df.index = df.index + timedelta(days=1) - timedelta(seconds=1)  # TODO think about EOD?
        # path = os.path.join(config.STOCK_PRICES_DIR_PATH, '{}.xlsx'.format(stk))
        # excel.save_into_csv(path, df, overwrite_sheet=True)
        path = os.path.join(config.STOCK_PRICES_DIR_PATH, '{}.pkl'.format(stk))
        df.to_pickle(path=path)


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
    # save_stock_prices(stock=config.MarketIndices.DOW_JONES)
    save_stock_prices(stock=['^DJI'])

