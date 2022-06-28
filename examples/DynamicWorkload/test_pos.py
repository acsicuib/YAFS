import pandas as pd

df = pd.read_csv("pos_network.csv")

for r in df.iterrows():
    print r
    lat = r[1].height
    lng = r[1].width


