import pandas as pd
import pickle
import matplotlib.pyplot as plt
import numpy as np


DATADIR = '.'
person_fields = ['YEAR', 'STATE', 'ST_CASE', 'PER_TYP', 'INJ_SEV']
accident_fields = ['YEAR', 'STATE', 'ST_CASE', 'LGT_COND']
with open(f'{DATADIR}/person.pickle', 'rb') as person_fh:
    all_person_cases = pickle.load(person_fh)
with open(f'{DATADIR}/accident.pickle', 'rb') as accident_fh:
    all_accident_cases = pickle.load(accident_fh)

case_id_fields = ['STATE', 'ST_CASE', 'YEAR']

all_pedestrian_cases = all_person_cases.query('PER_TYP == 5')


all_ped_accident_cases = pd.merge(all_pedestrian_cases, all_accident_cases,
                                 on=case_id_fields)
years = list(range(2012, 2022))

def count_unique(df, fields):
    return df.drop_duplicates(fields).shape[0]

total_ped_accidents = count_unique(all_pedestrian_cases, case_id_fields)
all_sid_ped_cases = all_pedestrian_cases.query(
    '(INJ_SEV == 3) | (INJ_SEV == 4)'
)
total_sid_ped_accidents = count_unique(all_sid_ped_cases, case_id_fields)

pct_sid_ped_accidents = pd.DataFrame({
    'PED_ACCIDENTS': [total_ped_accidents],
    'SID_PED_ACCIDENTS': [total_sid_ped_accidents],
    'PERCENT_SID': [100 * total_sid_ped_accidents / total_ped_accidents]
})
print(pct_sid_ped_accidents.to_string(index=False))

total_accident_counts_by_year = [
    count_unique(all_person_cases.query('YEAR == @yr'), case_id_fields)
    for yr in years
                
]
pedestrian_accident_counts_by_year = [
    count_unique(all_pedestrian_cases.query('YEAR == @yr'), case_id_fields)
    for yr in years
]
ped_freq_df = pd.DataFrame({
    'YEAR': years,
    'TOTAL_ACCIDENTS': total_accident_counts_by_year,
    'PED_ACCIDENTS': pedestrian_accident_counts_by_year,
})
ped_freq_df['PCT_PED_ACCIDENTS'] = (
    100.0 * ped_freq_df['PED_ACCIDENTS'] / ped_freq_df['TOTAL_ACCIDENTS']
)

print(ped_freq_df.to_string(index=False))

years_st = [str(yr) for yr in range(2012, 2022)]
accident_counts = {
    'Accidents with pedestrians': ped_freq_df['PED_ACCIDENTS'].to_numpy(),
    'All accidents': ped_freq_df['TOTAL_ACCIDENTS'].to_numpy()
}
width, bottom = 0.3, np.zeros(12)
fig, (ax1, ax2, ax3) = plt.subplots(3, figsize=(11,12))

for acc_type, acc_count in accident_counts.items():
    p = ax1.bar(years_st, acc_count, label=acc_type, bottom=bottom)
    bottom += acc_count

ax1.set_title('Pedestrian-involved accidents 2012-2021')
ax1.legend(loc='upper left')

ax2.set_title((
    'Precentage pedestrian involvement\n'
    'in accidents by year')
)
ax2.plot(years_st, ped_freq_df['PCT_PED_ACCIDENTS'].to_numpy())


lighting_codes = pd.DataFrame({
    'LGT_COND': list(range(1,10)),
    'LGT_COND_DESC': [
        'Daylight', 'Dark -- Not Lighted', 'Dark -- Lighted',
        'Dawn', 'Dusk', 'Dark -- Unknown Lighting', 'Other',
        'Not Reported', 'Reported as Unknown'
    ]
})


lighting_conditions = all_ped_accident_cases['LGT_COND'].value_counts()
lighting_conditions = lighting_conditions.rename_axis('LGT_COND')
lighting_conditions = lighting_conditions.reset_index(name='COUNT')
lighting_conditions = pd.merge(lighting_conditions, lighting_codes,
                               on='LGT_COND')
print(lighting_conditions.to_string(index=False))

pie = ax3.pie(
    lighting_conditions['COUNT'].to_numpy(),
    autopct=lambda v: f'{v:.1f}%' if v > 15 else None
)

ax3.axis('equal')
ax3.set_title(
    ('Breakdown of lighting conditions\n'
    'pedestrian-involved accidents 2012-2021'),
    loc='left'
)


n_lighting_conditions = lighting_conditions['COUNT'].sum()

def one_place_if_lt_15pct(v):
    x = 100.0 * v/n_lighting_conditions
    return f' ({x:.1f}%)' if x <= 15.0 else ''

lighting_conditions_aug = (
    lighting_conditions['LGT_COND_DESC'] +
    lighting_conditions['COUNT'].apply(one_place_if_lt_15pct)
)
ax3.legend(pie[0], lighting_conditions_aug.to_numpy(),
           loc='center left')
#ax3.legend(pie[0], lighting_conditions['LGT_COND_DESC'].to_numpy(),
#           loc='center left')

plt.subplots_adjust(left=0.08, right=0.92, top=0.92, bottom=0.3,
                    wspace=0.2, hspace=0.5)
plt.savefig('plots.png')
plt.show(block=False)
input('Hit enter when ready to close...')
