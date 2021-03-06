import os
import urllib.request
import pandas as pd
from matilda import config
from matilda.database.data_preparation_helpers import read_df_from_csv, save_into_csv


def save_gnp_price_index():
    url = 'https://fred.stlouisfed.org/graph/fredgraph.csv?bgcolor=%23e1e9f0&chart_type=line&drp=0&fo=open%20sans&' \
          'graph_bgcolor=%23ffffff&height=450&mode=fred&recession_bars=on&txtcolor=%23444444&ts=12&tts=12&width=1168&nt' \
          '=0&thu=0&trc=0&show_legend=yes&show_axis_titles=yes&show_tooltip=yes&id=A001RG3A086NBEA&scale=left&cosd=1929' \
          '-01-01&coed=2019-01-01&line_color=%234572a7&link_values=false&line_style=solid&mark_type=none&mw=3&lw=2&ost=' \
          '-99999&oet=99999&mma=0&fml=a&fq=Annual&fam=avg&fgst=lin&fgsnd=2009-06-01&line_index=1&transformation=lin&vin' \
          'tage_date=2020-07-10&revision_date=2020-07-10&nd=1929-01-01'

    urllib.request.urlretrieve(url, 'temp.csv')
    df = pd.read_csv('temp.csv')
    df.columns = ['Date', 'GNP Price Index']
    df.set_index(df.columns[0], inplace=True)
    df.index = pd.to_datetime(df.index, format='%Y-%m-%d')
    # df.index = df.index - timedelta(days=1)

    with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
        print(df)

    existing_df = read_df_from_csv(config.MACRO_DATA_FILE_PATH, config.yearly_factors)
    final_df = existing_df.merge(df, how='outer', left_index=True, right_index=True)
    save_into_csv(config.MACRO_DATA_FILE_PATH, final_df, config.yearly_factors)
    os.remove('temp.csv')
