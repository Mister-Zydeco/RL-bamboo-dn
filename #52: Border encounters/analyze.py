import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv(
    './data/nationwide-encounters-fy21-fy24-dec-aor.csv'
)
df['Fiscal Year'] = df['Fiscal Year'].str.replace(' .*', '', regex=True)

df['date'] = df.apply(
    lambda x: pd.to_datetime(f'{x["Fiscal Year"]}-{x["Month (abbv)"]}'),
    axis=1
)
df = df.set_index('date')
print(df.columns)
encounters_per_month = df.loc[:,'Encounter Count'].groupby(df.index).sum()
print(encounters_per_month)
encounters_per_month.plot()
