from fredapi import Fred
from matilda import config
import pandas as pd

from matilda.data_pipeline.data_preparation_helpers import generate_df_from_series_list


def scrape_macro(series_id: dict):
    """

    :param series_id: dictionary of FRED ID (key) and Series name (value) pairs
    :return:
    """
    fred = Fred(api_key=config.FRED_API_KEY)
    return [
        pd.Series(data=fred.get_series(series_key).dropna(), name=series_value)
        for series_key, series_value in series_id.items()
    ]


if __name__ == '__main__':
    series_id = {
        # Gross Domestic Product
        'GDP': 'Gross Domestic Product (Nominal)',
        'GDPC1': 'Gross Domestic Product (Real)',  # this one is adjusted for inflation
        # Interest Rates
        'DGS10': 'Treasury Yield Curve (10Y)',  # constant maturity Treasury rates (CMT)
        'T10Y2Y': 'Treasury Yield Curve (10Y-2)',
        # Inflation
        'T10YIE': 'Inflation Rate (10Y Breakeven)',
        'CPIAUCSL': 'Consumer Price Index (CPI)',
        # Market Labor
        'UNRATE': 'Unemployment Rate',
        'PAYEMS': 'Non-Farm Payrolls (NFP)',  # All Employees, Total Nonfarm
        'INDPRO': 'Industrial Production',
        # Consumer Behavior
        'TOTALSA': 'Total Vehicle Sales',  # Retail sales
        'ECOMPCTSA': 'E-Commerce Retail Sales',  # Retail sales
        'EXHOSLUSM495S': 'Existing Home Sales'
    }
    series_list = scrape_macro(series_id)
    df = generate_df_from_series_list(series_list)
    print(df)
