import pandas as pd
from simpledbf import Dbf5

test = pd.read_csv(r'C:\Users\engel\PycharmProjects\q_hackathon\src\data\SchulenNSW\master_dataset.csv', sep=",")

dbf = Dbf5(r'C:\Users\engel\PycharmProjects\q_hackathon\src\data\SchulenNRW\schulen.dbf')
dbf_as_df = dbf.to_dataframe()

print("hi")
