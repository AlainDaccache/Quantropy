from datetime import datetime, timedelta
import fundamental_analysis.accounting_ratios as ratios
import fundamental_analysis.financial_statements_entries as fi


def beneish_m_score(stock: str, date: datetime = datetime.now(), lookback_period: timedelta = timedelta(days=0),
                    period: str = 'TTM', describe=False):
    current_net_accounts_receivable = fi.net_accounts_receivable(stock=stock, date=date,
                                                                 lookback_period=lookback_period, period=period)
    current_net_sales = fi.net_sales(stock=stock, date=date, lookback_period=lookback_period, period=period)
    current_receivables_to_sales = current_net_accounts_receivable / current_net_sales

    previous_net_accounts_receivable = fi.net_accounts_receivable(stock=stock,
                                                                  date=date - timedelta(
                                                                      days=365 if period == 'FY' else 90),
                                                                  lookback_period=lookback_period, period=period)
    previous_net_sales = fi.net_sales(stock=stock, date=date - timedelta(days=365 if period == 'FY' else 90),
                                      lookback_period=lookback_period, period=period)
    previous_receivables_to_sales = previous_net_accounts_receivable / previous_net_sales

    DSRI = current_receivables_to_sales / previous_receivables_to_sales

    previous_gross_profit_margin = ratios.gross_profit_margin(stock=stock,
                                                              date=date - timedelta(days=365 if period == 'FY' else 90),
                                                              lookback_period=lookback_period, period=period)
    current_gross_profit_margin = ratios.gross_profit_margin(stock=stock, date=date, lookback_period=lookback_period,
                                                             period=period)

    GMI = previous_gross_profit_margin / current_gross_profit_margin

    current_asset_quality = 1 - (
            fi.current_total_assets(stock=stock, date=date, lookback_period=lookback_period, period=period)
            + fi.net_property_plant_equipment(stock=stock, date=date, lookback_period=lookback_period,
                                              period=period)
            + fi.current_marketable_securities(stock=stock, date=date, lookback_period=lookback_period,
                                               period=period))
    previous_asset_quality = 1 - (
            fi.current_total_assets(stock=stock, date=date - timedelta(days=365 if period == 'FY' else 90),
                                    lookback_period=lookback_period, period=period)
            + fi.net_property_plant_equipment(stock=stock, date=date - timedelta(days=365 if period == 'FY' else 90),
                                              lookback_period=lookback_period, period=period)
            + fi.current_marketable_securities(stock=stock, date=date - timedelta(days=365 if period == 'FY' else 90),
                                               lookback_period=lookback_period, period=period))
    AQI = current_asset_quality / previous_asset_quality

    SGI = fi.net_sales(stock=stock, date=date, lookback_period=lookback_period, period=period) \
          / fi.net_sales(stock=stock, date=date - timedelta(days=365 if period == 'FY' else 90),
                         lookback_period=lookback_period, period=period)

    current_depreciation = fi.accumulated_depreciation_amortization(stock=stock, date=date,
                                                                    lookback_period=lookback_period, period=period) \
                           / (fi.net_property_plant_equipment(stock=stock, date=date, lookback_period=lookback_period,
                                                              period=period)
                              + fi.accumulated_depreciation_amortization(stock=stock, date=date,
                                                                         lookback_period=lookback_period,
                                                                         period=period))
    previous_depreciation = fi.accumulated_depreciation_amortization(stock=stock,
                                                                     date=date - timedelta(
                                                                         days=365 if period == 'FY' else 90),
                                                                     lookback_period=lookback_period, period=period) \
                            / (fi.net_property_plant_equipment(stock=stock,
                                                               date=date - timedelta(
                                                                   days=365 if period == 'FY' else 90),
                                                               lookback_period=lookback_period, period=period)
                               + fi.accumulated_depreciation_amortization(stock=stock, date=date - timedelta(
                days=365 if period == 'FY' else 90), lookback_period=lookback_period, period=period))

    DEPI = previous_depreciation / current_depreciation

    SGAI = (fi.selling_general_administrative(stock=stock, date=date, lookback_period=lookback_period, period=period)
            / fi.net_sales(stock=stock, date=date, lookback_period=lookback_period, period=period)) \
           / (fi.selling_general_administrative(stock=stock, date=date - timedelta(days=365 if period == 'FY' else 90),
                                                lookback_period=lookback_period, period=period)
              / fi.net_sales(stock=stock, date=date - timedelta(days=365 if period == 'FY' else 90),
                             lookback_period=lookback_period, period=period))

    previous_leverage = (fi.current_total_liabilities(stock=stock,
                                                      date=date - timedelta(days=365 if period == 'FY' else 90),
                                                      lookback_period=lookback_period, period=period) +
                         fi.total_long_term_debt(stock=stock, date=date - timedelta(days=365 if period == 'FY' else 90),
                                                 lookback_period=lookback_period, period=period)) \
                        / fi.total_assets(stock=stock, date=date - timedelta(days=365 if period == 'FY' else 90),
                                          lookback_period=lookback_period, period=period)
    current_leverage = (fi.current_total_liabilities(stock=stock, date=date, lookback_period=lookback_period,
                                                     period=period)
                        + fi.total_long_term_debt(stock=stock, date=date, lookback_period=lookback_period,
                                                  period=period)) \
                       / fi.total_assets(stock=stock, date=date, lookback_period=lookback_period, period=period)
    LVGI = current_leverage / previous_leverage

    TATA = (fi.operating_income(stock=stock, date=date, lookback_period=lookback_period, period=period)
            - fi.cash_flow_operating_activities(stock=stock, date=date, lookback_period=lookback_period, period=period)) \
           / fi.total_assets(stock=stock, date=date, lookback_period=lookback_period, period=period)

    if not describe:
        return -4.84 + 0.92 * DSRI + 0.528 * GMI + 0.404 * AQI + 0.892 * SGI + 0.115 * DEPI - 0.172 * SGAI + 4.679 * TATA - 0.327 * LVGI
    else:
        return {'Inputs': {

        }}


if __name__ == '__main__':
    score = beneish_m_score(stock='AAPL', period='FY')
    print(score)
