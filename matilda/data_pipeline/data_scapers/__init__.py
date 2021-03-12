import os
from matilda import config

if not os.path.exists(config.DATA_DIR_PATH):
    os.mkdir(config.DATA_DIR_PATH)

if not os.path.exists(config.STOCK_PRICES_DIR_PATH):
    os.mkdir(config.STOCK_PRICES_DIR_PATH)

if not os.path.exists(config.FINANCIAL_STATEMENTS_DIR_PATH):
    os.mkdir(config.FINANCIAL_STATEMENTS_DIR_PATH)

if not os.path.exists(config.FACTORS_DIR_PATH):
    os.mkdir(config.FACTORS_DIR_PATH)

if not os.path.exists(os.path.join(config.FACTORS_DIR_PATH, 'pickle')):
    os.mkdir(os.path.join(config.FACTORS_DIR_PATH, 'pickle'))

if not os.path.exists(config.MARKET_DATA_DIR_PATH):
    os.mkdir(config.MARKET_DATA_DIR_PATH)

if not os.path.exists(config.MARKET_EXCHANGES_DIR_PATH):
    os.mkdir(config.MARKET_EXCHANGES_DIR_PATH)

if not os.path.exists(config.MARKET_INDICES_DIR_PATH):
    os.mkdir(config.MARKET_INDICES_DIR_PATH)
