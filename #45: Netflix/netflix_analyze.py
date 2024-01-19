import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_excel('./data/Netflix.xslx', skiprows=5,
                   parse_dates=['Release Date']).drop(
                      labels=['Unnamed: 0'], axis=1)
df_any_missing = df.isna().any()
print(df_any_missing.to_string())

df = df.query('`Release Date`.notna()')
df['Release Year'] = df['Release Date'].dt.year
df['Release Month'] = df['Release Date'].map('{:%b}'.format)
print(df.columns)
print('-----')
print(df['Release Year'].value_counts().to_frame('Releases per year')
        .sort_index())
print('-----')
print(df['Release Month'].value_counts()
        .to_frame('Releases by month').sort_index())
print('-----')
print('Unit of Mean Time Viewed is 10,000 hours')
df_mean_watched = df.groupby('Release Year')['Hours Viewed'].mean()
df_mean_watched = ((df_mean_watched.to_frame('Mean Time Viewed') / 10000)
                   .head(20))

print(df_mean_watched.to_string(formatters={\
    'Mean Time Viewed': '{:.2f}'.format}))

df_mean_watched = df_mean_watched.sort_index()
fig, ax = plt.subplots()
ax.plot(df_mean_watched.index.to_numpy(),
       df_mean_watched['Mean Time Viewed'].to_numpy())
ax.set_title('Mean Viewer-hours per show by year\n'
             'Units are 10,000 viewer-hours')
plt.savefig('plots.png')
plt.show(block=False)
input('Hit enter when ready to close...')
print('---')
print('First shows streamed by Netflix')
print(df[['Release Date', 'Title']].sort_values('Release Date').head())
print('----')

print('Total Time Viewed is across all seasons\n'
      'and is given in units of 10,000 hours')
df['Title sans season'] = df.Title.str.replace(
    ': Season .*', '', regex=True)
df_gb_title_ss = df.groupby('Title sans season')['Hours Viewed']
df_total_all_seasons = (
    (df_gb_title_ss.sum() / 10000).sort_values(ascending=False)
    .to_frame('Total Time Viewed')
)
print(df_total_all_seasons.head(6).to_string(
    formatters={'Total Time Viewed': '{:.2f}'.format}))
