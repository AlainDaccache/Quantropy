import enum

from mongoengine import *

# TODO https://mlab.com/

connect('matilda')


class Company(Document):
    name = StringField(required=True)
    ticker = StringField(required=True)
    cik = StringField(primary_key=True, required=False, max_length=10, min_length=10)
    sic_sector = StringField(required=False)
    sic_industry = StringField(required=False)
    gics_sector = StringField(required=False)
    gics_industry_group = StringField(required=False)
    gics_industry = StringField(required=False)
    gics_sub_industry = StringField(required=False)
    company_url = StringField(required=False)
    description = StringField(required=False)
    employees = IntField(required=False)


class AssetPricesEntry(Document):
    Open = FloatField(required=True)
    High = FloatField(required=True)
    Low = FloatField(required=True)
    Close = FloatField(required=True)
    AdjClose = FloatField(required=True)
    Volume = FloatField(required=True)


class AssetPrices(Document):
    company = ReferenceField(Company, required=True)
    date_time = DateTimeField(required=True)
    frequency = StringField(required=True)
    asset_prices = ListField(ReferenceField(AssetPricesEntry))


class FinancialStatementEntry(Document):
    entry_name = StringField(required=True)
    entry_value = FloatField(required=True)
    entry_multiplier = StringField(required=True)


class FinancialStatement(Document):
    statement_name = StringField(required=True)
    company = ReferenceField(Company, required=True)
    filing_date = DateField(required=True)
    filing_period = StringField(required=True)
    financial_statement_entries = ListField(ReferenceField(FinancialStatementEntry))


class FinancialStatementNames(enum.Enum):
    Balance_Sheet = 'Balance Sheet'
    Income_Statement = 'Income Statement'
    Cash_Flow_Statement = 'Cash Flow Statement'


class FinancialStatementPeriod(enum.Enum):
    FY = 'FY'
    Q1 = 'Q1'
    Q2 = 'Q2'
    Q3 = 'Q3'
    Q4 = 'Q4'


if __name__ == '__main__':
    apple = Company(name='Apple', ticker='AAPL')
    facebook = Company(name='Facebook', ticker='FB')
    for company in Company.objects:
        print(company.ticker)
