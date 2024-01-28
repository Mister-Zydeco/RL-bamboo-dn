import pandas as pd
import numpy as np
import requests
import os
import pickle
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
print('Completed imports...')

plt.rcParams['font.size'] = 8
plt.rcParams['legend.loc'] = 'right'
prefix = 'https://stats.oecd.org/sdmx-json/data/DP_LIVE'
suffix = (
    '.../OECD?contentType=csv&detail=code'
    '&separator=comma&csv-lang=en'
)
urls = [prefix + x + suffix for x in ['/.GDP', '/.HUR', '/.CPI']]
names = ['gdp', 'unemployment', 'cpi']

def read_func(url):
    try:
        return pd.read_csv(url)
    except Exception:
        print(f'Failed at {url}')

if not all(os.path.isfile(f'./data/{x}.pickle') for x in names):
    dfs = {
        name: read_func(url)
        for name, url in zip(names, urls)
    }
    for name, df in dfs.items():
        with open(f'./data/{name}.pickle', 'wb') as fh:
            pickle.dump(df, fh)
    print('Completed file reading...')
else:
    dfs = {}
    for name in names:
        with open(f'./data/{name}.pickle', 'rb') as fh:
            dfs[name] = pickle.load(fh)
    print('Completed unpickling...')


un_df = dfs['unemployment']
countries = ["USA", "FRA", "DEU", "GBR"]
qstring = '(FREQUENCY == "A") & (LOCATION == "USA") & (SUBJECT == "TOT")'
    
fig = plt.figure(layout='constrained')
gs = fig.add_gridspec(19, 8)
us_unemp_ax = fig.add_subplot(gs[0:2, 1:6]) 
int_unemp_ax = fig.add_subplot(gs[4:6, 1:6]) 
cpi_ax = fig.add_subplot(gs[8:10, 1:6]) 
cpiq_ax = fig.add_subplot(gs[11:13, 1:6])
gdp_unemp_22_ax = fig.add_subplot(gs[15:18, 1:6])


df = un_df.reset_index(drop=True).query(qstring).loc[:, ['TIME', 'Value']]
df = df.sort_values('TIME')
df['TIME'] = pd.to_numeric(df['TIME']).apply(lambda x: f'{x % 100:02d}')
sns.lineplot(data=df, x='TIME', y='Value', ax=us_unemp_ax)
us_unemp_ax.xaxis.set_ticks(
    [x for x in df['TIME'].values if x[-1] in list('05')]
)
us_unemp_ax.set(xlabel='Year', ylabel='% US unemp.')
us_unemp_ax.set_title('U.S. annual unemployment')

qstring2 = (
    '(FREQUENCY == "A") & (LOCATION in @countries) & (SUBJECT == "TOT")'
)
cols = ['TIME', 'LOCATION', 'Value']
int_df = un_df.reset_index(drop=True).query(qstring2).loc[:, cols]

int_df = int_df.sort_values('TIME')
int_df['TIME'] = (
    pd.to_numeric(int_df['TIME']).apply(lambda x: f'{x % 100:02d}')
)
int_df = int_df.rename({'LOCATION': 'Country'}, axis=1)
sns.lineplot(
    data=int_df, x='TIME', y='Value', hue='Country', ax=int_unemp_ax
)
int_unemp_ax.xaxis.set_ticks(
    [x for x in int_df['TIME'].values if x[-1] in list('05')]
)
int_unemp_ax.set(xlabel='Year', ylabel='% unemp.')
int_unemp_ax.set_title(
    'Annual unemployment:\n'
    'U.S., Great Britain,\n'
    'Germany, and France'
)
int_unemp_ax.set(xlabel='Year', ylabel='% unemp.')

qstring3 = f'{qstring2} &(MEASURE == "AGRWTH")'
cpi_df = (
    dfs['cpi'].query(qstring3).loc[:, cols].set_index(['TIME', 'LOCATION'])
    .groupby(level='LOCATION').pct_change().unstack('LOCATION')
)
cpi_df.columns = cpi_df.columns.droplevel().rename(None)
cpi_df = cpi_df.loc['1995':'2022', :].reset_index()
melted_cpi_df = pd.melt(cpi_df, id_vars=['TIME'], var_name='Country')
sns.lineplot(
    x='TIME', y='value', hue='Country',
    data=melted_cpi_df, ax=cpi_ax
)
cpi_ax.xaxis.set_ticks([x for x in cpi_df['TIME'].values
                    if x[-1] in list('05')])
cpi_ax.set(xlabel='Year', ylabel='CPI Delta')
cpi_ax.set_title(
    'Annual CPI delta:\n'
    'U.S., Great Britain,\n'
    'Germany, and France'
)

qstring4 = (
    '(FREQUENCY == "Q") & (LOCATION in @countries)'
    ' & (SUBJECT == "TOT") & (MEASURE == "AGRWTH")'
)
cpiq_df = (
    dfs['cpi'].query(qstring4).loc[:, cols].set_index(['TIME', 'LOCATION'])
    .groupby(level='LOCATION').pct_change().unstack('LOCATION')
)
cpiq_df.columns = cpiq_df.columns.droplevel().rename(None)
cpiq_df = cpiq_df.loc['1995-Q1':'2023-Q3', :].reset_index()

def conv(x):
    yr, qtr = (int(piece) for piece in x.split('-Q'))
    return yr + (qtr - 1)/4

cpiq_df['TIME'] = cpiq_df['TIME'].apply(conv)
melted_cpiq_df = pd.melt(
    cpiq_df, id_vars=['TIME'], var_name='Country'
)
xtick_values = [
    x for x in cpiq_df['TIME'].values
    if x - int(x) < 0.1 and int(x) % 5 == 0
]
xtick_labels = [f'{int(x) % 100:02d}' for x in xtick_values]
cpiq_ax.set_xticks(xtick_values, labels=xtick_labels)
cpiq_ax.set(xlabel='Quarter', ylabel='CPI Delta')
sns.lineplot(
    x='TIME', y='value', hue='Country',
    data=melted_cpiq_df, ax=cpiq_ax
)
cpiq_ax.set_title(
    'Quarterly CPI delta:\n'
    'U.S., Great Britain,\n'
    'Germany, and France'
)

gdp22_df = (
    dfs['gdp']
    .query('(TIME == 2022) & (MEASURE == "USD_CAP")')
    .loc[:, ['LOCATION', 'Value']]
    .rename({'LOCATION': 'Country'}, axis=1)
    .set_index('Country', drop=True)
)
    
unemp22_df = (
    un_df.query('(TIME == "2022") & (SUBJECT == "TOT")')
    .loc[:, ['LOCATION', 'Value']]
    .rename({'LOCATION': 'Country'}, axis=1)
    .set_index('Country', drop=True)
)

gdp_unemp_22_df = pd.DataFrame.from_dict({
    'GDP': gdp22_df['Value'] / 1000,
    'Unemployment': unemp22_df['Value']
})

print(gdp_unemp_22_df.sort_values(by='GDP', ascending=False).head())
print(gdp_unemp_22_df.corr())
sns.scatterplot(
    data=gdp_unemp_22_df, x='GDP', y='Unemployment',
    ax=gdp_unemp_22_ax, hue='Country', legend=False
)
gdp_unemp_22_ax.set_title(
    'Unemployment vs.\n'
    'per capita GDP, 2022'
)
gdp_unemp_22_ax.set_xlabel(
    'Per capita GDP (1000s of USD)'
)

plt.savefig('plots.png')
plt.show()
