import os
import config

if __name__ == '__main__':
    if not os.path.exists(config.DATA_DIR_PATH): os.mkdir(config.DATA_DIR_PATH)
    if not os.path.exists(config.MARKET_TICKERS_DIR_PATH): os.mkdir(config.MARKET_TICKERS_DIR_PATH)
    if not os.path.exists(config.FINANCIAL_STATEMENTS_DIR_PATH): os.mkdir(config.FINANCIAL_STATEMENTS_DIR_PATH)
    if not os.path.exists(config.FACTORS_DIR_PATH): os.mkdir(config.FACTORS_DIR_PATH)
    if not os.path.exists(os.path.join(config.DATA_DIR_PATH, 'stock_prices')): os.mkdir(
        os.path.join(config.DATA_DIR_PATH, 'stock_prices'))
    if not os.path.exists(config.MARKET_EXCHANGES_DIR_PATH): os.mkdir(config.MARKET_EXCHANGES_DIR_PATH)
