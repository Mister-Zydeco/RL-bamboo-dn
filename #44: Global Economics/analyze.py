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
plt.rcParams['figure.titlesize'] = 'x-small'

def axes_new_pos(ax):
    pos = ax.get_position()
    width, height = 0.8 * (pos.x1 - pos.x0), pos.y1 - pos.y0
    return [pos.x0, pos.y0, width, height]

def make_intl_title(st):
    return f'{st}:\nU.S., Great Britain,\nGermany, and France'

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

def get_ticks(yrs2):
    major, minor = [], []
    for ix, x in enumerate(yrs2):
        ar =  major if x[-1] in list('05') else minor
        ar.append(ix)
    return major, minor


un_df = dfs['unemployment']
countries = ["USA", "FRA", "DEU", "GBR"]
qstring = '(FREQUENCY == "A") & (LOCATION == "USA") & (SUBJECT == "TOT")'
    
fig = plt.figure(layout='constrained', figsize=(8.5, 10))
gs = fig.add_gridspec(4, 2, hspace=0.8, wspace=0.6)
us_unemp_ax = fig.add_subplot(gs[0, 0]) 
int_unemp_ax = fig.add_subplot(gs[0, 1]) 
cpi_ax = fig.add_subplot(gs[1, 0]) 
cpiq_ax = fig.add_subplot(gs[1, 1])
gdp_unemp_22_ax = fig.add_subplot(gs[2:3, :])


df = un_df.reset_index(drop=True).query(qstring).loc[:, ['TIME', 'Value']]
df = df.sort_values('TIME')
df['TIME'] = pd.to_numeric(df['TIME']).apply(lambda x: f'{x % 100:02d}')
sns.lineplot(data=df, x='TIME', y='Value', ax=us_unemp_ax)
major, minor = get_ticks(df['TIME'].values)
us_unemp_ax.set_xticks(major)
us_unemp_ax.set_xticks(minor, minor=True)
us_unemp_ax.set(xlabel='Year', ylabel='% US unemp.')
us_unemp_ax.set_title('U.S. annual unemployment')
print('us_unemp')

qstring2 = (
    '(FREQUENCY == "A") & (LOCATION in @countries) & (SUBJECT == "TOT")'
)
fs = ['FREQUENCY', 'SUBJECT']
cols = ['TIME', 'LOCATION', 'Value']
int_df = un_df.query(qstring2).loc[:, cols]
int_df = int_df.query('"1995" <= TIME <= "2022"').sort_values(by=['TIME'])


int_df['TIME'] = (
    pd.to_numeric(int_df['TIME']).apply(lambda x: f'{x % 100:02d}')
)
int_df = int_df.rename({'LOCATION': 'Country'}, axis=1)
sns.lineplot(
    data=int_df, x='TIME', y='Value', hue='Country', ax=int_unemp_ax
)
tickvals = int_df['TIME'].drop_duplicates().values
major, minor = get_ticks(tickvals)
ticklabels = [tickvals[x][-2:] for x in major]

int_unemp_ax.set_xticks(major, labels=ticklabels)
int_unemp_ax.set_xticks(minor, minor=True)
int_unemp_ax.set(
    xlabel='Year', ylabel='% unemp.',
    position=axes_new_pos(int_unemp_ax),
    title=make_intl_title('Annual unemployment')
)
int_unemp_ax.legend(loc='upper left', bbox_to_anchor=(1.05, 1.2))
print('int_unemp')

qstring3 = f'{qstring2} & (MEASURE == "AGRWTH")'
cpi_df = (
    dfs['cpi'].query(qstring3).loc[:, cols].set_index(['TIME', 'LOCATION'])
    .groupby(level='LOCATION').pct_change().unstack('LOCATION')
)
cpi_df.columns = cpi_df.columns.droplevel().rename(None)
cpi_df = cpi_df.loc['1995':'2022', :].reset_index()
cpi_df['TIME'] = (
    pd.to_numeric(cpi_df['TIME']).apply(lambda x: f'{x % 100:02d}')
)
melted_cpi_df = pd.melt(cpi_df, id_vars=['TIME'], var_name='Country')
sns.lineplot(
    x='TIME', y='value', hue='Country',
    data=melted_cpi_df, ax=cpi_ax
)
tickvals = melted_cpi_df['TIME'].drop_duplicates().values
major, minor = get_ticks(tickvals)
ticklabels = [tickvals[x][-2:] for x in major]
cpi_ax.set_xticks(major, labels=ticklabels)
cpi_ax.xaxis.set_ticks(minor, minor=True)
cpi_ax.set(
    xlabel='Year', ylabel='CPI Delta.', position=axes_new_pos(cpi_ax),
    title=make_intl_title('Annual CPI Delta')
)
cpi_ax.legend(loc='upper left', bbox_to_anchor=(1.05, 1.2))
print('cpi')

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
sns.lineplot(
    x='TIME', y='value', hue='Country',
    data=melted_cpiq_df, ax=cpiq_ax
)
tickvals = [
    x for x in cpiq_df['TIME'].values
    if x - int(x) < 0.1 and int(x) % 10 in [0, 5]
]
minortickvals = [
    x for x in cpiq_df['TIME'].values
    if x - int(x) < 0.1 and int(x) % 10 not in [0, 5]
]
ticklabels = [f'{int(x) % 10:02d}' for x in tickvals]
cpiq_ax.set_xticks(tickvals, labels=ticklabels)
cpiq_ax.set_xticks(minortickvals, minor=True)
cpiq_ax.set(
    xlabel='Quarter', ylabel='CPI Delta',
    position=axes_new_pos(cpiq_ax),
    title=make_intl_title('Quarterly CPI delta')
)
cpiq_ax.legend(loc='upper left', bbox_to_anchor=(1.05, 1.2))
print('cpiq')

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
gdp_unemp_22_ax.set(
    title='Unemployment vs. per capita GDP, 2022',
    xlabel='Per capita GDP (1000s of USD)', ylabel='% unemp.',
    position=axes_new_pos(gdp_unemp_22_ax)
)
print('gdp_unemp_22')

plt.savefig('plots.png')
plt.show()
