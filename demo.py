from datetime import datetime
from functools import partial
from pprint import pprint

from fundamental_analysis.equity_valuation_models.equity_valuation_models import valuation_wrapper, \
    absolute_valuation_two_stage_model
from fundamental_analysis.financial_statements_entries import net_income
from portfolio_management.Portfolio import Portfolio
from portfolio_management.portfolio_optimization import EquallyWeightedPortfolio
from portfolio_management.portfolio_simulator import Strategy
from portfolio_management.stock_screener import StockScreener
import config
import fundamental_analysis.accounting_ratios as ratios
import fundamental_analysis.supporting_metrics as me
import pandas as pd
from quantitative_analysis.risk_factor_modeling import FamaFrench_ThreeFactorModel
from quantitative_analysis.risk_factor_modeling.asset_pricing_model import FactorModels

pprint(me.market_price(stock='BA',
                       date=[datetime.now(), datetime(2019, 1, 1)]))

pprint(net_income(stock=['AMGN', 'AXP'],
                  date=datetime.now(),
                  period='FY'))

pprint(ratios.price_to_book_ratio(stock=['BA', 'AXP', 'AAPL'],
                                  date=[datetime.now(), datetime(2019, 9, 1)],
                                  tangible_book_value=True,
                                  period='FY'))

pprint(valuation_wrapper(model_type=partial(absolute_valuation_two_stage_model),
                         model_metric=me.dividend_per_share,
                         stock='AAPL',
                         period='FY'))

ff3 = FamaFrench_ThreeFactorModel(frequency='Monthly', to_date=datetime.today())
reg = ff3.regress_factor_loadings(portfolio=Portfolio(assets=['MSFT']))
pprint(reg.params)

stock_screener = StockScreener(securities_universe=config.MarketIndices.DOW_JONES)
stock_screener.filter_by_comparison_to_number(partial(ratios.price_to_earnings, period='FY'), '>', 5)
stock_screener.filter_by_sector(sector=config.GICS_Sectors.INFORMATION_TECHNOLOGY)
stock_screener.run()

# TODO percentile_against_macro

lower_bounds = pd.Series(data=[40], index=['Alpha'])
upper_bounds = pd.Series(data=[80], index=['MKT'])
stock_screener.filter_by_exposure_from_factor_model(factor_model=FactorModels.CAPM,
                                                    lower_bounds=lower_bounds, upper_bounds=upper_bounds)
stock_screener.run(date=datetime(2018, 1, 1))
print(stock_screener.stocks)


class Alainps(Strategy):
    def is_time_to_reschedule(self, current_date, last_rebalancing_day):
        return (current_date - last_rebalancing_day).days > config.RebalancingFrequency.Quarterly.value


strategy = Alainps(starting_date=datetime(2019, 1, 1), ending_date=datetime(2020, 12, 1),
                   starting_capital=50000, stock_screener=stock_screener, max_stocks_count_in_portfolio=12,
                   net_exposure=(100, 0), portfolio_allocation=EquallyWeightedPortfolio)

strategy.historical_simulation()
