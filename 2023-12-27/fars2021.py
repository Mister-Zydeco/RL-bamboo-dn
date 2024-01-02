import requests
import zipfile
import io
import pandas as pd
import re


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
person_fields.append('YEAR')
all_pedestrian_cases = all_person_cases.query('PER_TYP == 5')
all_sid_ped_cases = all_pedestrian_cases.query(
    '(INJ_SEV == 3) | (INJ_SEV == 4)'
)

pedestrian_pcts = []
case_id_fields = ['STATE', 'ST_CASE', 'YEAR']
all_person_cases = all_person_cases.set_index(case_id_fields).sort_index()
all_accident_cases = all_accident_cases.set_index(case_id_fields).sort_index()
all_ped_accident_cases = pd.merge(all_pedestrian_cases, all_accident_cases,
                                 on=case_id_fields)

lighting_conditions = all_ped_accident_cases['LGT_COND'].value_counts()
print(lighting_conditions.to_string())
