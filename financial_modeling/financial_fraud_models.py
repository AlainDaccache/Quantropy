import math
from datetime import datetime, timedelta
import financial_statement_analysis.accounting_ratios as ratios
import financial_statement_analysis.financial_statements_entries as fi


def beneish_m_score(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=True, ttm=True,
                    describe=False):
    current_net_accounts_receivable = fi.net_accounts_receivable(stock=stock, date=date,
                                                                 lookback_period=lookback_period, annual=annual,
                                                                 ttm=ttm)
    current_net_sales = fi.net_sales(stock=stock, date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)
    current_receivables_to_sales = current_net_accounts_receivable / current_net_sales

    previous_net_accounts_receivable = fi.net_accounts_receivable(stock=stock,
                                                                  date=date - timedelta(days=365 if annual else 90),
                                                                  lookback_period=lookback_period, annual=annual,
                                                                  ttm=ttm)
    previous_net_sales = fi.net_sales(stock=stock, date=date - timedelta(days=365 if annual else 90),
                                      lookback_period=lookback_period, annual=annual, ttm=ttm)
    previous_receivables_to_sales = previous_net_accounts_receivable / previous_net_sales

    DSRI = current_receivables_to_sales / previous_receivables_to_sales

    previous_gross_profit_margin = ratios.gross_profit_margin(stock=stock, date=date - timedelta(days=365 if annual else 90),
                                                              lookback_period=lookback_period, annual=annual, ttm=ttm)
    current_gross_profit_margin = ratios.gross_profit_margin(stock=stock, date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)

    GMI = previous_gross_profit_margin / current_gross_profit_margin

    current_asset_quality = 1 - (
            fi.current_total_assets(stock=stock, date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)
            + fi.net_property_plant_equipment(stock=stock, date=date, lookback_period=lookback_period,
                                              annual=annual, ttm=ttm)
            + fi.current_marketable_securities(stock=stock, date=date, lookback_period=lookback_period,
                                               annual=annual, ttm=ttm))
    previous_asset_quality = 1 - (
            fi.current_total_assets(stock=stock, date=date - timedelta(days=365 if annual else 90),
                                    lookback_period=lookback_period, annual=annual, ttm=ttm)
            + fi.net_property_plant_equipment(stock=stock, date=date - timedelta(days=365 if annual else 90),
                                              lookback_period=lookback_period, annual=annual, ttm=ttm)
            + fi.current_marketable_securities(stock=stock, date=date - timedelta(days=365 if annual else 90),
                                               lookback_period=lookback_period, annual=annual, ttm=ttm))
    AQI = current_asset_quality / previous_asset_quality

    SGI = fi.net_sales(stock=stock, date=date, lookback_period=lookback_period, annual=annual, ttm=ttm) \
          / fi.net_sales(stock=stock, date=date - timedelta(days=365 if annual else 90),
                         lookback_period=lookback_period, annual=annual, ttm=ttm)

    current_depreciation = fi.accumulated_depreciation_amortization(stock=stock, date=date,
                                                                    lookback_period=lookback_period, annual=annual,
                                                                    ttm=ttm) \
                           / (fi.net_property_plant_equipment(stock=stock, date=date, lookback_period=lookback_period,
                                                              annual=annual, ttm=ttm)
                              + fi.accumulated_depreciation_amortization(stock=stock, date=date,
                                                                         lookback_period=lookback_period, annual=annual,
                                                                         ttm=ttm))
    previous_depreciation = fi.accumulated_depreciation_amortization(stock=stock,
                                                                     date=date - timedelta(days=365 if annual else 90),
                                                                     lookback_period=lookback_period, annual=annual,
                                                                     ttm=ttm) \
                            / (fi.net_property_plant_equipment(stock=stock,
                                                               date=date - timedelta(days=365 if annual else 90),
                                                               lookback_period=lookback_period, annual=annual, ttm=ttm)
                               + fi.accumulated_depreciation_amortization(stock=stock, date=date - timedelta(
                days=365 if annual else 90), lookback_period=lookback_period, annual=annual, ttm=ttm))

    DEPI = previous_depreciation / current_depreciation

    SGAI = (fi.selling_general_administrative(stock=stock, date=date, lookback_period=lookback_period, annual=annual,
                                              ttm=ttm)
            / fi.net_sales(stock=stock, date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)) \
           / (fi.selling_general_administrative(stock=stock, date=date - timedelta(days=365 if annual else 90),
                                                lookback_period=lookback_period, annual=annual, ttm=ttm)
              / fi.net_sales(stock=stock, date=date - timedelta(days=365 if annual else 90),
                             lookback_period=lookback_period, annual=annual, ttm=ttm))

    previous_leverage = (fi.current_total_liabilities(stock=stock, date=date - timedelta(days=365 if annual else 90),
                                                      lookback_period=lookback_period, annual=annual, ttm=ttm) +
                         fi.total_long_term_debt(stock=stock, date=date - timedelta(days=365 if annual else 90),
                                                 lookback_period=lookback_period, annual=annual, ttm=ttm)) \
                        / fi.total_assets(stock=stock, date=date - timedelta(days=365 if annual else 90),
                                          lookback_period=lookback_period, annual=annual, ttm=ttm)
    current_leverage = (fi.current_total_liabilities(stock=stock, date=date, lookback_period=lookback_period,
                                                     annual=annual, ttm=ttm)
                        + fi.total_long_term_debt(stock=stock, date=date, lookback_period=lookback_period,
                                                  annual=annual, ttm=ttm)) \
                       / fi.total_assets(stock=stock, date=date, lookback_period=lookback_period, annual=annual,
                                         ttm=ttm)
    LVGI = current_leverage / previous_leverage

    TATA = (fi.operating_income(stock=stock, date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)
            - fi.cash_flow_operating_activities(stock=stock, date=date, lookback_period=lookback_period, annual=annual,
                                                ttm=ttm)) \
           / fi.total_assets(stock=stock, date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)

    if not describe:
        return -4.84 + 0.92 * DSRI + 0.528 * GMI + 0.404 * AQI + 0.892 * SGI + 0.115 * DEPI - 0.172 * SGAI + 4.679 * TATA - 0.327 * LVGI
    else:
        return {'Inputs': {

        }}


score = beneish_m_score('AAPL', annual=True, ttm=False)
print(score)


def montier_c_score(stock, date):
    pass
