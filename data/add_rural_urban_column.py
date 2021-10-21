import pandas as pd
from simpledbf import Dbf5

dbf = Dbf5(r'C:\Users\engel\PycharmProjects\q_hackathon\src\data\SchulenNRW\schulen.dbf')
df = dbf.to_dataframe()

df['Schulform'] = df['Schulform'].apply(lambda x: x.replace('Ã¶', 'ö'))
def get_size(row):
    return 0 if int(row['Schueler']) < 450 else 1
df['is_big'] = df.apply(lambda row: get_size(row), axis=1)
df = df.rename(columns={'Schulnumme': 'Schulnummer', 'Postleitza': 'Postleitzahl', 'Schueler': 'Schüler'})


plz_data = pd.read_csv(r'C:\Users\engel\PycharmProjects\q_hackathon\src\data\postal_codes_ger.csv', sep=",")
plz_data = plz_data[plz_data['state'] == 'Nordrhein-Westfalen']
plz_data = plz_data.drop(columns=['country_code', 'place', 'state',
                         'state_code', 'province', 'province_code',
                         'community_code', 'latitude', 'longitude'])
df["Postleitzahl"] = df["Postleitzahl"].astype(int)

df = df.rename(columns={'Postleitzahl':'zipcode'})

result_df = df.merge(plz_data, how='left', on="zipcode")
result_df = result_df[~result_df["community"].isna()]

result_df['is_rural'] = result_df["community"].apply(lambda x: 0 if "Stadt" in x or "Städte" in x else 1)

result_df = result_df.rename(columns={'Schulnummer': 'school_number', 'Schulform': 'school_type',
                        'Name': 'name', 'Kurzname': 'short_name', 'Adresse': 'address',
                        'Ort': 'location', 'Schüler': 'student', 'Rufnummer': 'tel',
                        'Email': 'email'})

result_df.to_csv("school_dataset.csv")

print("hi")

