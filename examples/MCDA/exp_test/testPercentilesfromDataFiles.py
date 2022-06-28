#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 20 15:37:54 2018

@author: isaaclera
"""

import pandas as pd
import numpy as np
from sklearn import preprocessing

df = pd.read_csv("data/data2.csv")

## Normalizar
x = df.values #returns a numpy array
min_max_scaler = preprocessing.MinMaxScaler()
x_scaled = min_max_scaler.fit_transform(x)
df = pd.DataFrame(x_scaled)

### Invertir attr. max 
df[1]=1-df[1]
## weighted average
wa=df.sum(axis=1)*[0.2,0.2,0.1,0.4]
print "BEST NODE: ",wa.idxmin()

l = np.array([4.,1.,2.,3.,1.])
l = 1/l 
l = l/l.sum()

wm_formula = (df['1']*df['10']).sum()/df['10'].sum()
 
# using numpy average() method
wm_numpy = np.average(df['a'], weights=df['b'])


lp = [str(int(np.percentile(df["hopcount"],p))) for p in [2,10,60,80]]
lp2 = [str(int(np.percentile(df["latency"],p))) for p in [2,20,60,80]]
lp3 = [str(int(np.percentile(df["power"],p))) for p in [5,40,60,80]]
lp4 = [str(int(np.percentile(df["deploymentPenalty"],p))) for p in [5,20,60,80]]
lp5 = [str(int(np.percentile(df["utilization"],p))) for p in [5,20,60,80]]
clp = np.vstack((lp,lp2,lp3,lp4,lp5))

print lp
print lp2
print lp3
print lp4
print lp5
print "-"*30
categoriesLowerProfiles = ",".join(str(x) for x in clp.flatten())
print categoriesLowerProfiles

c = [29, 35, 93, 128, 193, 219, 248, 268, 309, 312, 314, 325, 348, 364, 387, 477, 493, 515, 543, 629, 667, 796]

idCloud = 629

df["utilization"].ix[35]=10
df["utilization"].ix[219]=30
t = df["utilization"][c][df.utilization<20].sort_values(ascending=False)
if idCloud in C:
    return idCloud
best_node = t.index[0]
