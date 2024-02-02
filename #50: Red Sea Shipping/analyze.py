import pandas as pd
from collections import defaultdict
from glob import glob
import matplotlib.pyplot as plt

dfs = {}
for fname in glob('./data/*.csv'):
    name = fname[7:10]
    renamer = {
        f'Number of {x} Ships': f'{name}-{x}'
        for x in ['Cargo', 'Tanker']
    }
    df = pd.read_csv(fname, index_col='DateTime', parse_dates=True)
    dfs[name] = df.loc[:, renamer.keys()].rename(columns=renamer)


def col_renamer(st):
    dic = {
        'bab': 'Bab el Mandeb', 'cap': 'Cape of Good Hope',
        'sue': 'Suez Canal'
    }
    return dic[st[:3]]

fig, (ax1, ax2) = plt.subplots(2, 1, layout='constrained')
fig.get_layout_engine().set(h_pad=0.25, w_pad=0.25)
big_df = pd.concat(dfs.values(), axis=1)
tanker_cols = ['bab-Tanker', 'cap-Tanker', 'sue-Tanker']
cargo_cols = ['bab-Cargo', 'cap-Cargo', 'sue-Cargo']
cargo_monthly_df = (
    big_df.loc[:, cargo_cols].rename(columns=col_renamer)
    .resample('M').mean()
)
cargo_monthly_df.plot(
    title='Mean daily cargo traffic by month', ax=ax1
)
ax1.legend(loc='upper left', bbox_to_anchor=(1.05, -0.5))
start, end = pd.to_datetime('2023-09-01'), pd.to_datetime('2024-01-21')
tanker_weekly_df = (
    big_df.loc[start:end, tanker_cols].rename(columns=col_renamer)
    .resample('W').mean()
)
tanker_weekly_df.plot(
    legend=False, title='Mean weekly tanker traffic by month', ax=ax2
)
print(f'Minimum Suez cargo day={big_df["sue-Cargo"].idxmin()}')
print(f'Minimum Suez tanker week={big_df["sue-Tanker"].idxmin()}')

start, end = pd.to_datetime('2021-03-15'), pd.to_datetime('2021-04-01')
three_day_suez_df = (
    big_df.loc[start:end, ['sue-Cargo', 'sue-Tanker']]
    .rolling(3).agg(['min', 'max'])
)
print('Rolling three-day traffic totals:')
print('Extrema from 2021-03-15 through 2021-04-01')
print(three_day_suez_df.to_string())
quarterlies_df = (
    big_df.resample('Q').mean().loc[:pd.to_datetime('2023-12-31'), :]
)
print(quarterlies_df.to_string())
quarterly_deltas_df = quarterlies_df.pct_change()
print(quarterly_deltas_df.to_string())


def augmented_idxmm(df, min_or_max):
    vals = []
    idxmm_s = df.idxmin() if min_or_max == 'min' else df.idxmax()

    for colname, ix in zip(idxmm_s.index, idxmm_s.values):
        vals.append(df.loc[ix, colname])
    return pd.DataFrame.from_dict({'index': idxmm_s, 'value': vals})
    
print('MINS')
qmin = augmented_idxmm(quarterly_deltas_df, 'min')
print(qmin)
print('MAXES')
qmax = augmented_idxmm(quarterly_deltas_df, 'max')
print(qmax)

plt.savefig('plots.png')
plt.show()
