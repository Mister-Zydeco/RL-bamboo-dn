from tabula import read_pdf
import pandas as pd


(df, ) = read_pdf('./data/animals-heathrow.pdf', pages=3,
                  multiple_tables=False,
                  pandas_options={
                    'header': [0, 1], 'skipinitialspace': True,
                  }
)
ca = ['Consignments', 'Animals']
df = df.iloc[:, [0, 1, 2, 4, 5, 7, 8, 10, 11, 13]]
lev1 = ['TAXA'] + [x for x in range(2019, 2023) for _ in range(2)] + [2023]
lev2 = ['X'] + [ca[ix % 2] for ix in range(0, 8)] + ['X']
df.columns = pd.MultiIndex.from_arrays([lev1, lev2])
df23 = df.iloc[:, -1].str.split(expand=True).apply(pd.to_numeric)
df23.columns = pd.MultiIndex.from_arrays([[2023, 2023], ca])
taxa = df.iloc[:, 0].rename('TAXA')
df = pd.concat([df.iloc[:, 1:-1], df23], axis=1)
df = df.set_index(taxa)
print(df.index)

print(df.info())
print(df.iloc[:, :5].to_string())
print(df.iloc[:, 5:].to_string())
