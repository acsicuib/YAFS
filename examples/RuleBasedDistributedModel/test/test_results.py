import pandas as pd
import numpy as np

import json

pathCSV = "/Users/isaaclera/PycharmProjects/YAFS/src/examples/RuleBasedDistributedModel/exp1/results_20191009/Results_RTSG_150000_0.csv"
#pathCSVl = "/Users/isaaclera/PycharmProjects/YAFS/src/examples/RuleBasedDistributedModel/exp1/results_20191009/Results_RTSG_150000_0_link.csv"
#dfl = pd.read_csv(pathCSVl)  # include header

df = pd.read_csv(pathCSV)  # include header

#list_requests = df.groupby(['DES.src','TOPO.src'])['id'].apply(list)

#Solo un mensaje entre source  y modulo. Reducir esto!
df["response"]= df['time_out']- df['time_emit']

df2 = df.groupby(['DES.dst', 'TOPO.dst','TOPO.src', 'module']).agg({"response": ['mean', 'std', 'count'],
                "service":'mean'}).reset_index()
df2.columns = ["USER", "SRC", "DST", "module", "mean", "std", "transmissions","service"]
# Same users deployed in same node are grouped
df2 = df2.groupby(['SRC', 'DST', 'module']).agg(
    {"mean": np.mean, "std": np.mean, "transmissions": np.mean, "service":np.mean}).reset_index()
for i, row in df2.iterrows():
    service_node = int(row["SRC"])
    service_name = row["module"]
    user_node = int(row["DST"])
    print service_node,service_name,user_node,row[3:]

constraints =    
path = "/Users/isaaclera/PycharmProjects/YAFS/src/examples/RuleBasedDistributedModel/exp1/"
dataPopulation = json.load(open(path + 'usersDefinition.json'))
for element in dataPopulation["sources"]:
    print(element)
