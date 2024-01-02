import requests
import zipfile
import io
import pandas as pd
import re
import pickle


person_dfs, accident_dfs = [], []
person_fields = ['STATE', 'ST_CASE', 'PER_TYP', 'INJ_SEV']
accident_fields = ['YEAR', 'STATE', 'ST_CASE', 'LGT_COND']
for year in range(2010, 2022):
    filename = f'FARS{year}NationalCSV.zip'
    directory = f'FARS/{year}/National'
    url = f'https://static.nhtsa.gov/nhtsa/downloads/{directory}/{filename}'
    response = requests.get(url)
    zipf = zipfile.ZipFile(io.BytesIO(response.content))
    namelist = zipf.namelist()
    personfilename, accidentfilename = None, None
    for filename in namelist:
        if re.search('person.csv', filename, re.IGNORECASE):
            personfilename = filename
        if re.search('accident.csv', filename, re.IGNORECASE):
            accidentfilename = filename
    with zipf.open(personfilename) as pfh:
        #person_df_annual = pd.read_csv(pfh, encoding_errors='ignore')
        person_df_annual = pd.read_csv(pfh, encoding='latin-1')
        person_df_annual = person_df_annual[person_fields]
    with zipf.open(accidentfilename) as afh:
        #accident_df_annual = pd.read_csv(afh, encoding_errors='ignore')
        accident_df_annual = pd.read_csv(afh, encoding='latin-1')
        accident_df_annual = accident_df_annual[accident_fields]
    person_df_annual.insert(0, 'YEAR', year)
    person_dfs.append(person_df_annual)
    accident_dfs.append(accident_df_annual)
    print(f'Finished {year}')
    
all_person_cases = pd.concat(person_dfs, ignore_index=True)
all_accident_cases = pd.concat(accident_dfs, ignore_index=True)
DATADIR = '.'
with open(f'{DATADIR}/person.pickle', 'wb') as pers_fh:
    pickle.dump(all_person_cases, pers_fh)
with open(f'{DATADIR}/accident.pickle', 'wb') as accident_fh:
    pickle.dump(all_accident_cases, accident_fh)
