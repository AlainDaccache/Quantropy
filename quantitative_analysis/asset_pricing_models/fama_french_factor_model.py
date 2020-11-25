class FamaFrenchFactorModel:

    def fama_french_3_factor_model(portfolio_returns, regression_period: int = 36, benchmark_returns='MKT',
                                   frequency='Monthly', date: datetime = None):
        '''
        Eugene Fama and Kenneth French identified two anomalies that can further explain stock returns:
        * lower value (in terms of Price-to-Book)
        * bigger size (in terms of market capitalization)
        They constructed portfolios being a cross of those two factors,
        :param portfolio_returns:
        :param regression_period:
        :param frequency:
        :param date:
        :return:
        '''
        return AssetPricingModel(FactorModelDataset.FAMA_FRENCH_DATASET, ['MKT-RF', 'SMB', 'HML'], frequency) \
            .regress_factor_loadings(portfolio_returns=portfolio_returns, benchmark_returns=benchmark_returns,
                                     date=date, regression_period=regression_period)

    def carhart_4_factor_model(portfolio_returns, regression_period: int = 36, benchmark_returns='MKT',
                               frequency='Monthly', date: datetime = None):
        return AssetPricingModel(FactorModelDataset.FAMA_FRENCH_DATASET, ['MKT-RF', 'SMB', 'HML', 'UMD'], frequency) \
            .regress_factor_loadings(portfolio_returns=portfolio_returns, benchmark_returns=benchmark_returns,
                                     date=date, regression_period=regression_period)

    def fama_french_5_factor_model(portfolio_returns, regression_period: int = 36, benchmark_returns='MKT',
                                   frequency='Monthly', date: datetime = None):
        return AssetPricingModel(FactorModelDataset.FAMA_FRENCH_DATASET, ['MKT-RF', 'SMB', 'HML', 'RMW', 'CMA'],
                                 frequency) \
            .regress_factor_loadings(portfolio_returns=portfolio_returns, benchmark_returns=benchmark_returns,
                                     date=date, regression_period=regression_period)