import pandas as pd
import pickle

with open('data/states.pickle', 'rb') as fh:
    states_df = pickle.load(fh)
states_series = states_df['Abbreviation']
print(states_series.to_string())

with open('data/nmw.pickle', 'rb') as fh:
    nmw_df = pickle.load(fh)


nmw_df = nmw_df.set_index(['STATE', 'DATE'])
    
present_states = nmw_df.index.unique('STATE').values
absent_states = states_df[~states_df['Abbreviation'].isin(present_states)]
print(absent_states.to_string())


nmw_gb = nmw_df.groupby(level=0, as_index=False)
earliest_reports = nmw_gb.nth(0).sort_index(
    level='DATE', ascending=False)
print(earliest_reports.info())
print(earliest_reports.to_string())

nmw2324_df = nmw_gb.nth[-2:].unstack().iloc[:, 0:2].T.reset_index(
    drop=True).T.sort_values('STATE').dropna(how='any')
nmw2324_df.columns = ['2023', '2024']
nmw2324_df['DIFF'] = nmw2324_df['2024'] - nmw2324_df['2023']
nmw2324_df = nmw2324_df[nmw2324_df['DIFF'] > 0]
nmw2324_df['% DIFF'] = 100 * nmw2324_df['DIFF'] / nmw2324_df['2023']
print(nmw2324_df.sort_values(by='DIFF', ascending=False).head())
print(nmw2324_df.sort_values(by='% DIFF', ascending=False).head())



print(nmw_df.columns)
nmw_dfr = nmw_df.reset_index()
print(nmw_dfr.head())

nmw_dfr['YEAR'] = nmw_dfr['DATE'].dt.year
nmw_dfr['DECADE'] = (nmw_dfr['YEAR'] - nmw_dfr['YEAR'].mod(10)).mod(100)
decade_av = nmw_dfr.groupby(by='DECADE')['MIN_WAGE'].mean()
print(decade_av.to_string())
xs = [60, 70, 80, 90, 0, 10, 20]
xlabels = [f'{x:02d}' for x in xs]
ys = decade_av.values
print(ys)
