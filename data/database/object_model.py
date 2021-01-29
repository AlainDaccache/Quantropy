from mongoengine import *


class Meta(Document):
    date_last_refreshed = DateTimeField()


class Company(Document):
    name = StringField(required=True)
    ticker = StringField(primary_key=True, required=True)
    cik = StringField(required=False, max_length=10, min_length=10)

    location = StringField()
    exchange = StringField()

    sic_sector = StringField(required=False)
    sic_industry = StringField(required=False)
    gics_sector = StringField(required=False)
    gics_industry_group = StringField(required=False)
    gics_industry = StringField(required=False)
    gics_sub_industry = StringField(required=False)
    company_url = StringField(required=False)
    description = StringField(required=False)
    employees = IntField(required=False)

    filings = ListField(ReferenceField('Filing'))


class CashAndShortTermInvestments(EmbeddedDocument):
    CashAndCashEquivalents = IntField()
    MarketableSecurities = IntField()
    CashAndShortTermInvestments = IntField()


class AccountsReceivable(EmbeddedDocument):
    AllowanceForDoubtfulAccounts = IntField()
    NetAccountsReceivable = IntField()
    VendorNontradeReceivables = IntField()


class PropertyPlantAndEquipment(EmbeddedDocument):
    GrossPropertyPlantAndEquipment = IntField()
    AccumulatedDepreciationAndAmortization = IntField()
    NetPropertyPlantAndEquipment = IntField()


class IntangibleAssets(EmbeddedDocument):
    Goodwill = IntField()
    NetIntangibleAssetsExcludingGoodwill = IntField()
    TotalIntangibleAssets = IntField()


class NonCurrentAssets(EmbeddedDocument):
    MarketableSecurities = IntField()
    RestrictedCash = IntField()
    PropertyPlantAndEquipment = EmbeddedDocumentField(PropertyPlantAndEquipment)
    OperatingLeaseRightOfUseAssets = IntField()
    DeferredTaxAssets = IntField()
    IntangibleAssets = EmbeddedDocumentField(IntangibleAssets)
    OtherNonCurrentAssets = IntField()
    TotalNonCurrentAssets = IntField()


class CurrentAssets(EmbeddedDocument):
    CashAndShortTermInvestments = EmbeddedDocumentField(CashAndShortTermInvestments)
    AccountsReceivable = EmbeddedDocumentField(AccountsReceivable)
    PrepaidExpense = IntField()
    InventoryNet = IntField()
    IncomeTaxesReceivable = IntField()
    AssetsHeldForSale = IntField()
    DeferredTaxAssets = IntField()
    OtherCurrentAssets = IntField()
    TotalCurrentAssets = IntField()


class Assets(EmbeddedDocument):
    CurrentAssets = EmbeddedDocumentField(CurrentAssets)
    NonCurrentAssets = EmbeddedDocumentField(NonCurrentAssets)
    TotalAssets = IntField()


class CurrentLiabilities(EmbeddedDocument):
    LongTermDebtCurrentMaturities = IntField()
    AccountsPayable = IntField()
    OtherAccountsPayable = IntField()
    OperatingLeaseLiability = IntField()
    EmployeeRelatedLiabilities = IntField()
    AccruedIncomeTaxes = IntField()
    AccruedLiabilities = IntField()
    DeferredRevenue = IntField()
    CommercialPaper = IntField()
    IncomeTaxesPayable = IntField()
    OtherCurrentLiabilities = IntField()
    TotalCurrentLiabilities = IntField()


class NonCurrentLiabilities(EmbeddedDocument):
    DeferredTaxLiabilities = IntField()
    LongTermDebtNoncurrentMaturities = IntField()
    OperatingLeaseLiability = IntField()
    DefinedBenefitPlanLiability = IntField()
    AccruedIncomeTaxes = IntField()
    DeferredRevenue = IntField()
    LongTermUnearnedRevenue = IntField()
    OtherLiabilitiesNoncurrent = IntField()
    TotalNonCurrentLiabilities = IntField()


class Liabilities(EmbeddedDocument):
    CurrentLiabilities = EmbeddedDocumentField(CurrentLiabilities)
    NonCurrentLiabilities = EmbeddedDocumentField(NonCurrentLiabilities)
    TotalLiabilities = IntField()


class CommonStockAndAdditionalPaidInCapital(EmbeddedDocument):
    CommonStockValueIssued = IntField()
    AdditionalPaidInCapital = IntField()
    CommonStocksIncludingAdditionalPaidInCapital = IntField()
    WeightedAverageNumberOfSharesOutstandingBasic = IntField()
    WeightedAverageNumberDilutedSharesOutstandingAdjustment = IntField()
    WeightedAverageNumberOfSharesOutstandingDiluted = IntField()


class ShareholdersEquity(EmbeddedDocument):
    PreferredStockValueIssued = IntField()
    CommonStockAndAdditionalPaidInCapital = EmbeddedDocumentField(CommonStockAndAdditionalPaidInCapital)
    TreasuryStockValue = IntField()
    RetainedEarningsAccumulatedDeficit = IntField()
    AccumulatedOtherComprehensiveIncomeLoss = IntField()
    DeferredStockCompensation = IntField()
    StockholdersEquityAttributableToParent = IntField()
    MinorityInterest = IntField()
    StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest = IntField()


class LiabilitiesAndShareholdersEquity(EmbeddedDocument):
    Liabilities = EmbeddedDocumentField(Liabilities)
    ShareholdersEquity = EmbeddedDocumentField(ShareholdersEquity)
    TotalLiabilitiesAndShareholdersEquity = IntField()


class BalanceSheet(EmbeddedDocument):
    filing = ReferenceField('Filing')
    Assets = EmbeddedDocumentField(Assets)
    LiabilitiesAndShareholdersEquity = EmbeddedDocumentField(LiabilitiesAndShareholdersEquity)


class Filing(Document):
    company = ReferenceField(Company)
    date = DateTimeField(required=True)
    period = StringField()  # Yearly, Quarterly
    BalanceSheet = EmbeddedDocumentField(BalanceSheet)
    # IncomeStatement = EmbeddedDocumentField(IncomeStatement)
    # CashFlowStatement = EmbeddedDocumentField(CashFlowStatement)


class DatePrice(EmbeddedDocument):
    date = DateTimeField()
    price = FloatField()


class AssetPrices(Document):
    company = ReferenceField(Company)
    open = ListField(EmbeddedDocumentField(DatePrice))
    high = ListField(EmbeddedDocumentField(DatePrice))
    low = ListField(EmbeddedDocumentField(DatePrice))
    close = ListField(EmbeddedDocumentField(DatePrice))
    adj_close = ListField(EmbeddedDocumentField(DatePrice))
    volume = ListField(EmbeddedDocumentField(DatePrice))


class RiskFactor(EmbeddedDocument):
    name = StringField()
    series = ListField(EmbeddedDocumentField(DatePrice))


class RiskFactorModel(Document):
    name = StringField()
    risk_factors = ListField(EmbeddedDocumentField(RiskFactor))
