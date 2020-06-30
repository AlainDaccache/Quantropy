import pandas as pd
import ta

# Load datas
df = pd.read_csv('ta/tests/data/datas.csv', sep=',')

# Clean NaN values
df = ta.utils.dropna(df)

# Add ta features filling NaN values
df = ta.add_all_ta_features(
    df, open="Open", high="High", low="Low", close="Close", volume="Volume_BTC", fillna=True)
