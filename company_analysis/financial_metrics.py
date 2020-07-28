import os
from datetime import datetime, timedelta
import company_analysis.financial_statements_entries as fi
import data_scraping.excel_helpers as excel
import config


def market_price(stock, date=datetime.today(), lookback_period=timedelta(days=0)):
    path = os.path.join(config.STOCK_PRICES_DIR_PATH, '{}.xlsx'.format(stock))
    output = excel.read_entry_from_csv(path, config.stock_prices_sheet_name, 'Adj Close', date, lookback_period.days)
    print('Market Price for {} on the {} is: {}'.format(stock, date, output))
    return output


def gross_profit(stock, date=datetime.today(), lookback_period=timedelta(days=0), annual=True, ttm=False):
    return fi.net_sales(stock=stock, date=date, lookback_period=lookback_period, annual=annual,
                        ttm=ttm) - fi.cost_of_goods_services(stock=stock, date=date, lookback_period=lookback_period,
                                                             annual=annual, ttm=ttm)


def ebit(stock, date=datetime.today(), lookback_period=timedelta(days=0), annual=True, ttm=False):
    try:
        return fi.net_income(stock, date, lookback_period, annual, ttm) + fi.interest_expense(stock, date,
                                                                                              lookback_period, annual,
                                                                                              ttm) + fi.income_tax_expense(
            stock, date, lookback_period, annual, ttm)
    except:
        return fi.net_sales(stock, date, lookback_period, annual, ttm) - fi.cost_of_goods_services(stock, date,
                                                                                                   lookback_period,
                                                                                                   annual,
                                                                                                   ttm) - fi.total_operating_expenses(
            stock, date, lookback_period, annual, ttm) - fi.accumulated_depreciation_amortization(stock, date,
                                                                                                  lookback_period,
                                                                                                  annual, ttm)


def ebitda(stock, date=datetime.today(), lookback_period=timedelta(days=0), annual=True, ttm=False):
    output = ebit(stock, date, lookback_period, annual, ttm) + fi.accumulated_depreciation_amortization(stock, date,
                                                                                                        lookback_period,
                                                                                                        annual, ttm)
    print('EBITDA for {} on the {} is: {}'.format(stock, date, output))
    return output


def capital_expenditures(stock, date, lookback_period=timedelta(days=0), annual=True, ttm=False):
    ppe_delta = (fi.net_property_plant_equipment(stock=stock, date=date, lookback_period=lookback_period, annual=annual,
                                                 ttm=ttm)
                 - fi.net_property_plant_equipment(stock=stock, date=date, lookback_period=timedelta(days=365), annual=annual, ttm=ttm))
    return ppe_delta + fi.change_in_depreciation_and_amortization(stock=stock, date=date, lookback_period=lookback_period,
                                                                annual=annual, ttm=ttm)


def debt_service(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=True, ttm=True):
    return fi.interest_expense(stock=stock, date=date, lookback_period=lookback_period, annual=annual,
                               ttm=ttm)  # TODO Review


def net_credit_sales(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=True, ttm=True):
    return fi.net_sales(stock=stock, date=date, lookback_period=lookback_period, annual=annual,
                        ttm=ttm) - fi.net_accounts_receivable(stock=stock, date=date, lookback_period=lookback_period,
                                                              annual=annual, ttm=ttm)  # TODO Review


def working_capital(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=True, ttm=True):
    return fi.current_total_assets(stock=stock, date=date, lookback_period=lookback_period, annual=annual,
                                   ttm=ttm) - fi.current_total_liabilities(stock=stock, date=date,
                                                                           lookback_period=lookback_period,
                                                                           annual=annual, ttm=ttm)


def market_capitalization(stock, date=datetime.now(), lookback_period=timedelta(days=0), diluted_shares=True, annual=False, ttm=False):
    shares_outstanding = fi.total_shares_outstanding(stock=stock, date=date, lookback_period=lookback_period, annual=annual, ttm=ttm, diluted=diluted_shares)
    output = market_price(stock, date, lookback_period) * shares_outstanding
    print('Market Capitalization for {} on the {} is: {}'.format(stock, date, output))
    return output


def enterprise_value(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=True, ttm=False):
    output = market_capitalization(stock=stock, date=date, lookback_period=lookback_period, annual=annual, ttm=ttm) \
             + fi.total_liabilities(stock=stock, date=date, lookback_period=lookback_period, annual=annual, ttm=ttm) \
             - fi.cash_and_cash_equivalents(stock=stock, date=date, lookback_period=lookback_period, annual=annual,
                                            ttm=ttm)
    print('Enterprise Value for {} on the {} is: {}'.format(stock, date, output))
    return output


def gross_national_product_price_index(date):
    return float(excel.read_entry_from_csv(config.MACRO_DATA_FILE_PATH, 'Yearly', 'GNP Price Index', date))


def risk_free_rate(date, period):
    # period is 'Yearly', 'Monthly', 'Daily'
    return float(excel.read_entry_from_csv(path='{}/{}.xlsx'.format(config.FACTORS_DIR_PATH, 'Factors'),
                                           sheet_name=period, x= 'RF', y=date))


def get_stock_location(stock):
    return excel.read_entry_from_csv(config.COMPANY_META_DATA_FILE_PATH, 'Sheet1', 'Location', stock)


def get_stock_industry(stock):
    return excel.read_entry_from_csv(config.COMPANY_META_DATA_FILE_PATH, 'Sheet1', 'Industry', stock)


def get_stock_sector(stock):
    return excel.read_entry_from_csv(config.COMPANY_META_DATA_FILE_PATH, 'Sheet1', 'Sector', stock)


if __name__ == '__main__':
    print(gross_national_product_price_index(datetime(2018, 5, 3)))
    print(get_stock_industry('AAPL'))
    print(enterprise_value)
