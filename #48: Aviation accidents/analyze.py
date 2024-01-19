import pandas as pd
import numpy as np
import glob
import pickle
import re
import matplotlib.pyplot as plt


with open('./data/df.pickle', 'rb') as fh:
    df = pickle.load(fh)

df = df.set_index('cm_mkey')
df['cm_eventDate'] = pd.to_datetime(df['cm_eventDate'])

df['does_not_have_vehicles'] = df['cm_vehicles'].isna()
def vehicle_counter(x):
    return pd.NA if x.does_not_have_vehicles else len(x.cm_vehicles)

def stdize(x):
    return x.replace('-', '').upper()

def vehicle_mmo(x, colkey):
    if x.does_not_have_vehicles:
        return np.nan
    else:
        return x.cm_vehicles[0].get(colkey, None)

df['n_vehicles'] = df.apply(vehicle_counter, axis=1)
print(df['n_vehicles'].value_counts())


mmo_cols = ['make', 'model', 'operatorName']
for key in mmo_cols:
    df[key] = df.apply(vehicle_mmo, colkey=key, axis=1).str.upper()

mm_cols = ['make', 'model']
for key in mm_cols:
    df[key] = df[key].str.replace('\W', '', regex=True)
mm_counts = df.loc[:, mm_cols].value_counts()
print(mm_counts.iloc[:10].to_string())



opyr_cols = ['cm_eventDate', 'operatorName']
trail_rx = re.compile(',? INC\.?$')
df_opyr = df.loc[:, opyr_cols]
df_opyr['operatorName'] = df_opyr['operatorName'].replace(trail_rx, '')
df_opyr['count'] = 1
mask_vals = ['', 'ON FILE', 'UNKNOWN',
             'NAME', 'NOT PROVIDED BY AUTHORITY',
             'REGISTRATION PENDING']
mask = df_opyr['operatorName'].isin(mask_vals)
df_opyr = df_opyr[~mask]

def gbopyr_func(ix):
    return (ix[0].year, ix[1])

df_opyr = df_opyr.dropna(how='any').set_index(
            opyr_cols).groupby(gbopyr_func).count()
df_opyr.index = pd.MultiIndex.from_tuples(
    df_opyr.index, name=['year', 'operatorName'])
df_opyr = df_opyr.reset_index().sort_values(
    ['year', 'count'], ascending=[True, False]).reset_index(drop=True)

print(f'df_opyr.columns={df_opyr.columns}')
gb_opyr = df_opyr.groupby('year')
dict_yrmax = gb_opyr['count'].nth(0).to_dict()
df_opyr['max_for_year'] = pd.Series(
    dict_yrmax[yr] for yr, group in gb_opyr
    for _ in range(group.shape[0]))
df_opyr = df_opyr.query('count == max_for_year')
print(df_opyr.drop('max_for_year', axis=1).to_string(index=False))

def gbinjyr_func(ix):
    return ix.year

inj_cols = ['cm_eventDate', 'cm_fatalInjuryCount',
               'cm_seriousInjuryCount', 'cm_minorInjuryCount']

inj_df = df.loc[:, inj_cols].resample('Y', origin='01/01/1998',
                                   on='cm_eventDate').sum()
inj_df.index = pd.Index(x.year for x in inj_df.index)

def col_shorten(x):
    return x.replace('cm_', '').replace('InjuryCount', '')
inj_df = inj_df.rename(columns=col_shorten)
print(inj_df.to_string())

colors_l = ['#22ff22', '#ffff22', '#ff2222']
labels_l = ['minor', 'serious', 'fatal']
yrs = np.array(range(1998, 2024))
fig, ax = plt.subplots(1)
ax.set_title('Injuries in U.S. Aviation 1998-2023')
q = inj_df.loc[yrs, labels_l].T.to_numpy()
print(q)
for line, color in zip(labels_l, colors_l):
    ax.plot(yrs, inj_df.loc[yrs, line].to_numpy(), label=line, color=color)
plt.savefig('plots.png')
plt.show(block=False)
input('Hit enter when ready to close...')
