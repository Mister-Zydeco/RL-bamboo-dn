import requests
import io
import pandas as pd
import pickle

df = pd.read_csv('./states.csv')
print(df.to_string())
print(type(df['Abbreviation']))
state_abbrevs = df['Abbreviation'].tolist()
base_url = 'https://fred.stlouisfed.org/graph/fredgraph.csv?id=STTMINWG'

dfs = []
for state in state_abbrevs:
    response = requests.get(f'{base_url}{state}')
    if response.status_code != requests.codes.ok:
        print(f'Apparently no minimum wage data for {state}...')
    else:
        with open(f'data/{state}.csv', 'w') as fh:
            fh.write(response.text)

