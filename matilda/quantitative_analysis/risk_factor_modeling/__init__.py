"""
This module contains the theory behind, and implementation of asset pricing models, which will allow you,
in plain terms, to identify (and capitalize on) the drivers of the stock market's returns. We will start by
analyzing common factor models developed in academia (i.e. CAPM, Fama-French, Carhart...) and
used in the industry (AQR, MSCI, MorningStar, BlackRock).
We will then going about researching factors to define your own asset pricing models.

Such models are typically used to
    1. *Explain* stock market returns (in regression terms), and determine the degree of out-performance of your portfolio.
    2. Evaluate the risk factor exposures, to filter or optimize your portfolio.
    3. Compute the expected rate of return, in equity and option valuation models

.. moduleauthor:: Alain Daccache <alain.daccache@mail.mcgill.ca>

"""

from .asset_pricing_model import AssetPricingModel, CustomAssetPricingModel, CapitalAssetPricingModel, \
    FamaFrench_ThreeFactorModel, FamaFrench_FiveFactorModel, Carhart_FourFactorModel, Factor, FactorModelDataset, \
    AQR_FactorModel, Q_FactorModel

if __name__ == '__main__':
    pass
    # portfolio = Portfolio(assets=['AAPL'])
    #
    # capm = CapitalAssetPricingModel(frequency='Monthly').regress_factor_loadings(portfolio=portfolio,
    #                                                                              rolling=False,
    #                                                                              regression_window=36)
    # fama_french_3 = FamaFrench_ThreeFactorModel(frequency='Monthly').regress_factor_loadings(portfolio=portfolio,
    #                                                                                          rolling=False,
    #                                                                                          regression_window=36)
    # fama_french_5 = FamaFrench_FiveFactorModel(frequency='Monthly').regress_factor_loadings(portfolio=portfolio,
    #                                                                                         rolling=False,
    #                                                                                         regression_window=36)
    #
    # capm.markowitz_efficient_frontier(portfolio=Portfolio(assets=MarketIndices.DOW_JONES))
    # capm.security_market_line(portfolio=Portfolio(assets=MarketIndices.DOW_JONES), date=datetime.now(),
    #                           regression_window=5 * 12)
    #
    # # Setting for yahoo finance: monthly returns for past 5 years, using S&P 500 as benchmark
    # capital_asset_pricing_model(portfolio_returns='AAPL', regression_window=12 * 5, frequency='Monthly',
    #                             benchmark_returns='^GSPC')
    #
    #
    # class SMB(Factor):
    #     def __init__(self):
    #         super().__init__(factors_names=['Market Cap'])
    #
    #     def factor_formula(self, stock, date):
    #         return [metrics.market_capitalization(stock=stock, date=date)]
    #
    #
    # class Quality(Factor):
    #     def __init__(self, weights=None, factors_names=None):
    #
    #         if factors_names is None:
    #             factors_names = ['ROA', 'ROE']
    #         if weights is None:
    #             weights = [0.5, 0.5]
    #         super().__init__(weights=weights, factors_names=factors_names)
    #
    #     def factor_formula(self, stock, date):
    #         return [ratios.return_on_assets(stock=stock, date=date, period='FY'),
    #                 ratios.return_on_equity(stock=stock, date=date, period='FY')]
    #
    #
    # class MultiValue(Factor):
    #     def __init__(self, weights=None, factors_names=None):
    #
    #         if factors_names is None:
    #             factors_names = ['P/E', 'P/B']
    #         if weights is None:
    #             weights = [0.5, 0.5]
    #         super().__init__(weights=weights, factors_names=factors_names)
    #
    #     def factor_formula(self, stock, date):
    #         return [ratios.price_to_earnings(stock=stock, date=date, period='FY'),
    #                 ratios.price_to_book_value(stock=stock, date=date, period='FY')]
    #
    #
    # tickers = macro.companies_in_index(config.MarketIndices.DOW_JONES)[:10]
    # asset_pricing = CustomAssetPricingModel(factors=[SMB(), Quality(), MultiValue()], securities_universe=tickers,
    #                                         start_date=datetime(2019, 9, 1), end_date=datetime(2020, 3, 5),
    #                                         rebalancing_frequency=RebalancingFrequency.QUARTERLY
    #                                         )
    # pipeline_df = asset_pricing.compute_raw_factors()
    # print('Raw computed factors are\n', pipeline_df)
    #
    # # pipeline_df = asset_pricing.normalize_factors(pipeline_df=pipeline_df, winsorize_bounds=(0.20, 0.80),
    # #                                               method='min-max')
    # # print('Normalized factors are\n', pipeline_df)
    #
    # pipeline_df = asset_pricing.factor_weighted_sum(pipeline_df)
    # print('Weighted summed factors are\n', pipeline_df)
    #
    # asset_pricing.portfolio_cross_section(pipeline_df)
