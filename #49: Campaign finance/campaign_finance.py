import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

url = ('https://www.fec.gov/campaign-finance-data/'
       'all-candidates-file-description/')
meta_dfs = pd.read_html(url)
colnames = meta_dfs[0].iloc[1:,0].rename('COLNAMES')
print(colnames)
print('----')

campaign_finance_df = pd.read_csv(
    './data/weball24.txt', header=None, sep='|',
    names=colnames.to_numpy())


fields = ['CAND_NAME', 'TTL_RECEIPTS', 'CAND_OFFICE_ST', 'PTY_CD']
by_total_receipts = (
    campaign_finance_df.loc[:, fields]
    .sort_values(by='TTL_RECEIPTS', ascending=False)
    .drop_duplicates().reset_index(drop=True).head(10)
)
print(by_total_receipts.to_string())
print('----')

fields = ['CAND_NAME', 'CAND_OFFICE_ST', 
          'PTY_CD', 'CAND_PTY_AFFILIATION', 'TTL_RECEIPTS']
st_vs_fed_df = (
    campaign_finance_df.loc[:, ['CAND_OFFICE_ST', 'TTL_RECEIPTS']]
)
st_vs_fed_df['STATE_OR_FED'] = 'STATE'
st_vs_fed_df.loc[
    st_vs_fed_df['CAND_OFFICE_ST'] == '00', 'STATE_OR_FED'] = 'FED'
#st_vs_fed_df = st_vs_fed_df.loc[st_vs_fed_df['TTL_RECEIPTS'] > 1.0e5, :]
box_labels = ['STATE', 'FED']
st_or_fed_receipts = [
    st_vs_fed_df.loc[
        st_vs_fed_df['STATE_OR_FED'] == x,
        'TTL_RECEIPTS'].to_numpy()
    for x in box_labels
]

fig, ax = plt.subplots()
ax.boxplot(st_or_fed_receipts, labels=box_labels)
plt.show(block=False) 
input('Hit ENTER to continue...')
print(
    st_vs_fed_df.groupby(by='CAND_OFFICE_ST')['TTL_RECEIPTS']
    .agg(func=['sum', 'mean', 'median']).to_string()
)
print('----')
fields = ['CAND_PTY_AFFILIATION', 'PTY_CD', 'TTL_RECEIPTS']
by_party_dfs = [
    campaign_finance_df.loc[:, [x, 'TTL_RECEIPTS']]
    .groupby(by=x).agg(func=['sum', 'mean', 'median'])
    for x in ['CAND_PTY_AFFILIATION', 'PTY_CD']
]
print(by_party_dfs[0].to_string())
print('----')
print(by_party_dfs[1].to_string())
print('----')

less_cash_df = campaign_finance_df.loc[
    campaign_finance_df['COH_BOP'] > campaign_finance_df['COH_COP'],
    :
]
print(f'{less_cash_df.shape[0]} candidates with less cash at end')
print('----')

fields = [
    'CAND_NAME', 'PTY_CD', 'CAND_OFFICE_ST', 'COH_BOP',
    'COH_COP', 'DEBTS_OWED_BY'
]
net_cash_df = campaign_finance_df.loc[:, fields]
net_cash_df['COH_NET'] = net_cash_df['COH_COP'] - net_cash_df['COH_BOP']
conditions = [net_cash_df['CAND_OFFICE_ST'] == '00']
choices = ['FED']
net_cash_df['STATE_OR_FED'] = np.select(
    conditions, choices, default='STATE'
)
net_cash_df = (
    net_cash_df
        .drop(columns=['CAND_OFFICE_ST', 'COH_BOP', 'COH_COP'])
        .drop_duplicates().reset_index(drop=True)
)
print(net_cash_df.sort_values('COH_NET').head(10).to_string(index=False))
print('----')

rd_df = (campaign_finance_df.loc[:, ['TTL_RECEIPTS', 'TTL_DISB']]
         .drop_duplicates())
print(rd_df.corr())

fig, ax = plt.subplots()
ax.scatter(rd_df['TTL_RECEIPTS'].to_numpy(),
           rd_df['TTL_DISB'].to_numpy())
ax.set_xlabel('Receipts')
ax.set_ylabel('Disbursements')

plt.show()
input('Hit ENTER to continue...')

