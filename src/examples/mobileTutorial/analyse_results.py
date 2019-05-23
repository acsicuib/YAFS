import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import json
import collections
import networkx as nx
import warnings
import math
import argparse

warnings.simplefilter(action='ignore', category=FutureWarning)


nSimulations = 1
pathExperimento = "exp/results_20190326/"
number_simulation_steps = 100
time_in_each_step = 1000
cases = ["one"]

# f = open(pathExperimento+"resultsParte_n200.csv","w")

# TODO fors cases and nSimulations
df = pd.read_csv(pathExperimento+"Results_one_0.csv")
df_link = pd.read_csv(pathExperimento+"Results_one_0_link.csv")


# Instruction to be package in a function
totalmessages = len(df_link)
# print "Total number of perfomed transmissions : %i" %totalmessages
#f.write("totalMSG;%i;%s;%i\n"%(it,exp,totalmessages))
totalMessagesSRCREP = df_link["message"].str.contains("M.USER.APP").sum()

#In this case the communication with the app is direct (Module.src = None ->> TOPO.dst)
df["latency"]= df["time_reception"] - df["time_emit"]

df["date"]=df.time_in.astype('datetime64[s]')
df.index = df.date


users = np.unique(df["TOPO.src"])

for user in users:
    #getting the id-messages used by this user
   ids = df_link[df_link["src"]==user].id
   
   #Alternative A
   # getting the idx_df which has the maximun ctime (the last message)
   # idxs = df_link[df_link.id.isin(ids)].groupby("id")["ctime"].transform(max) == df_link[df_link.id.isin(ids)]['ctime']
   # getting the dst in these case
   ##df_link[idxs]

   #alernative B (best)
   dfuser = df_link[df_link.id.isin(ids)].sort_values('ctime', ascending=False).drop_duplicates(['id'])
   dfuser = dfuser.sort_values("id",ascending=True)
   np.unique(dfuser["dst"])

latency_by_user={}

fig = plt.figure()
ax1 = fig.add_subplot(111)

for user in [636798]:
    print user
    dfap1 = df[df["TOPO.src"]==user]
    
    ids = df_link[df_link["src"]==user].id

    assert len(dfap1.id.values )==len(ids.values)
            
    dfuser = df_link[df_link.id.isin(ids)].sort_values('ctime', ascending=False).drop_duplicates(['id'])
    dfuser = dfuser.sort_values("id",ascending=True)    
    
    dfap1.join(dfuser[["dst"]])
    
    dfap1["dstC"]=dfuser["dst"].values
    
    ticks = range(len(dfap1.index))
    latency_by_user[user] = dfap1["latency"].resample('100s').agg(dict(latency='mean'))
    timeLatency = dfap1.latency.values
    ax1.plot(ticks, timeLatency, '-')
    ax1.set_xlabel("Simulation time", fontsize=16)
    ax1.set_ylabel("Latency time", fontsize=16)
