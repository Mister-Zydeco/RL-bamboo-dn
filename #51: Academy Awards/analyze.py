import pandas as pd
import matplotlib.pyplot as plt
import pyarrow
import sys

df = pd.read_csv('./data/oscars.csv', dtype_backend='pyarrow', sep='\t')
columns = ['Year', 'CanonicalCategory', 'Film', 'FilmId', 'Name', 'Winner']
df = df.loc[:, columns].rename({'CanonicalCategory': 'Category'}, axis=1)
df['Winner'] = df['Winner'].apply(
    lambda x: True if  not pd.isna(x) else False
)
df['Year'] = pd.to_numeric(df['Year'].str.replace('../', '', regex=True))
remakes_df = (
    df.loc[:, ['FilmId', 'Film']].drop_duplicates()['Film'].value_counts()
)

print('Remakes')
print(remakes_df.head())
print(remakes_df[remakes_df > 1].shape)

print('\nNominations')
nominations = df['FilmId'].value_counts().head(10)
cols = ['Film', 'Year', 'Name']
nominations_df = df.query('FilmId in @nominations.index').loc[:, cols]
def shorten(x):
    return f'{x[:20]}...' if (not pd.isna(x)) and len(x) > 20 else x

nominations_df['Name'] = nominations_df['Name'].apply(shorten)
nominations_df['Film'] = nominations_df['Film'].apply(shorten)
print(nominations_df.to_string(index=False))

print('\nWinners')
winners = df.loc[df['Winner'], 'FilmId'].value_counts().head(10)
winners_df = df.query('FilmId in @winners.index').loc[:, cols]
winners_df['Name'] = winners_df['Name'].apply(shorten)
winners_df['Film'] = winners_df['Film'].apply(shorten)
print(winners_df.to_string(index=False))

cats = df['Category'].drop_duplicates()
print(f'cats are {cats.to_string(index=False)}')
actor_cats = cats[cats.str.contains('ACT')]
print(f'actor_cats are {actor_cats}')
actor_nominees = (
    df.query('(Category in @actor_cats)')['Name'].value_counts()
)
print('\nActor nominations')
print(actor_nominees.info())
print(actor_nominees.index)
winner_counts = (
    df.query('(Winner) & (Category in @actor_cats)')['Name'].value_counts()
)
print('\nActor winners')
print(winner_counts.head())

carrer_nominations_gb_actor = (
    df.query('Category in @actor_cats').loc[:, ['Year', 'Name']]
        .sort_values('Year').groupby('Name')
)    
earliest, latest = (
    career_nomination_by_actor.nth(X).set_index['Name'].rename({'Year': Y}, axis=1)
    for X, Y in zip([0, -1], ['Earliest', 'Latest'])
)                                                
multiply_nominated = pd.concat([earliest, latest], axis=1)
multiply_nominated['Span'] = multiply_nominated.apply(
    (lambda row: row['Latest'] - row['Earliest']), axis=1
)
print(multiply_nominated.sort_values('Span', ascending=False).head())

df.query('Winner').loc[:, ['Year', 'Category']].set_index('Year')
df.query('Winner').value_counts('Year', sort=False).reset_index().plot(
    x='Year', y='count'
)
plt.show()
print(f'Memory used by pyarrow df={df.memory_usage(deep=True).sum()}')
alt_df = pd.read_csv('./data/oscars.csv', sep='\t')
alt_df = (
    alt_df.loc[:, columns]
    .rename({'CanonicalCategory': 'Category'}, axis=1)
)
alt_df['Winner'] = alt_df['Winner'].apply(
    lambda x: True if  not pd.isna(x) else False
)
alt_df['Year'] = pd.to_numeric(alt_df['Year'].str.replace('../', '', regex=True))
print(f'Memory used by traditional alt_df={alt_df.memory_usage(deep=True).sum()}')


cols = ['Year', 'Category', 'Winner']
multiple = (
    df.query('Winner').loc[:, cols]
      .groupby(['Year', 'Category']).size().reset_index(name='counts')
)

substitutions = {
    'SCIENTIFIC (?:AND|OR) TECHNICAL AWARD': 'SATA',
    'Scientific and Engineering Award': 'SEA',
    'Technical Achievement Award': 'TAA', 'Academy Award of Merit': 'AAM',
    'SPECIAL ACHIEVEMENT AWARD': 'SAA',
    'JOHN A. BONNER MEDAL OF COMMENDATION': 'BONNER',
    'JEAN HERSHOLT HUMANITARIAN AWARD': 'HERSHOLT',
    'DOCUMENTARY': 'DOC', 'COMMENDATION': 'CMND', 'SHORT FILM \(Live Action\)': 'SHORT (LA)'
}
for source, target in substitutions.items():
    multiple['Category'] = multiple['Category'].str.replace(source, target, regex=True)
to_keep = multiple['counts'] > 1
multiple = multiple[to_keep]
print(multiple.to_string(index=False))