import requests
import zipfile
import io

DATADIR = './data'
for year in range(2010, 2022):
    filename = f'FARS{year}NationalCSV.zip'
    directory = f'FARS/{year}/National'
    url = f'https://static.nhtsa.gov/nhtsa/downloads/{directory}/{filename}'
    response = requests.get(url)
    bytestream = io.BytesIO(response.content)
    with open(f'{DATADIR}/{filename}', 'wb') as wfh:
        wfh.write(bytestream.getvalue())
    print(f'Finished getting {filename}...')
