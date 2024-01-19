import glob
import pandas as pd
import pickle

with open('./states.csv') as fh:
    states_df = pd.read_csv(fh)
print(states_df.info())

dfs = []
for filename in glob.glob('data/*.csv'):
    state = filename[5:7]
    common_col = 'STTMINWG'
    with open(filename) as fh:
        df = pd.read_csv(fh, parse_dates=['DATE'])
        df['STATE'] = state
        df.rename(columns={f'{common_col}{state}': 'MIN_WAGE'},
                  inplace=True, copy=False)
    dfs.append(df)
nmw_df = pd.concat(dfs, ignore_index=True)
nmw_df = nmw_df.set_index(['STATE', 'DATE'])
with open('data/nmw.pickle', 'wb') as fh:
    pickle.dump(nmw_df, fh)
with open('data/states.pickle', 'wb') as fh:
    pickle.dump(states_df, fh)





