import pandas as pd
import numpy as np
import glob
import pickle

columns = [
    'cm_mkey', 'cm_eventDate', 'cm_vehicles', 'cm_fatalInjuryCount',
    'cm_seriousInjuryCount', 'cm_minorInjuryCount'
]
df = pd.concat(pd.read_json(jfile).loc[:, columns]
               for jfile in glob.glob('./data/cases*.json'))
with open('./data/df.pickle','wb') as fh:
    pickle.dump(df, fh)
