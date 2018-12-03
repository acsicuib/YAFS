#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  5 12:02:41 2018

@author: isaaclera
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pandas import Series, date_range
import matplotlib.pyplot as plt
import numpy as np
import json
from scipy import stats
import collections
import networkx as nx

time = 10000
path ="exp1/Results__%i"%time

#T1+T2
# Number of messages from sensors to replicas
# Total de paquetes desde los sensores hasta las replicas (suma de las replicas). (acc. from sensors a replicas) 
#Sin identificar elementos.


df = pd.read_csv(path + ".csv")
dfl = pd.read_csv(path + "_link.csv")

print "Total number of perfomed transmissions : %i" %len(df)

#Group by app, src, and id
print "Total n.messages between sources -> replicas by app"
dtmp = df[df["module.src"]=="None"].groupby(['app','TOPO.src'])['id'].apply(list)
print "\tApplication\tMessages "
totalMessages = 0
for app,values in enumerate(dtmp):
    print "\t%i\t%i" %(app,len(values))
    totalMessages+=len(values)

print "Total Message  between sources -> replicas: %i" %totalMessages

print "Total messages between replicas -> cloud: %i" %(len(df)-totalMessages)

#T3
#Latency from replicas to the cloud
#Latency desde las replicas al cloud

#desde df- identificar id que van al cloud
#desde dfl - coger mensajes[ids] and borrar aquellos from M.USER.APP.
dtmp = df[df["module.src"]!="None"].groupby(['app','TOPO.src'])['id'].apply(list)
print "Total n.messages between replicas -> cloud by app:"
print "\tApplication\tMessages "
totalMessages = 0
for app,values in enumerate(dtmp):
    print "\t%i\t%i" %(app,len(values))
    totalMessages+=len(values)
#OJO-Si desglosar latency por app...deberia de estar aqui, lo siguiente:
    
#TOTAL    
idMessagesToCloud = df[df["module.src"]!="None"]["id"].values
#Selecting only transmissions between replicas and cloud 
dftmp = dfl[dfl["id"].isin(idMessagesToCloud)]
dftmp = dftmp[dftmp['message'].str.contains("M.CLOUD")]
grm = dftmp.groupby(["id"]).agg({"latency":np.sum})
print "Total avg. latency (replicas->cloud): %f" %grm.mean().latency

#T4
#Latencia desde el sensor - con la replica(modulo) más cercana | más lejana (H)
print "Computing latency sources -> replica (MIN and MAX Path) each app"
PATH = collections.namedtuple('PATH', 'src dst len')
#LOADING NETWORK 
data = json.load(open('exp1/networkDefinition.json'))
G = nx.Graph()
for edge in data["link"]:
    G.add_edge(edge["s"], edge["d"])
    
    
dtmp = df[df["module.src"]=="None"].groupby(['app','TOPO.src','TOPO.dst','message'])['id'].apply(list)
dmsg = dfl[dfl["message"].str.contains("M.USER.APP")]
for app in dtmp.index.levels[0].values:
    print "app ",app
    minpath = PATH(src=0,dst=0,len=999999)
    maxpath = PATH(src=0,dst=0,len=-1)
    for src in dtmp[app].index.levels[0].values:
#        print "\tsrc ",src
        for dst in dtmp[app][src].index.levels[0].values:
#            print "\t\tdst ",dst
            path = list(nx.shortest_path(G, source=src, target=dst))
#            print "\t\t",path
            if minpath.len>len(path):
                minpath = PATH(src=src,dst=dst,len=len(path))
            if maxpath.len<len(path):
                maxpath = PATH(src=src,dst=dst,len=len(path))
    print "\t",minpath
    print "\t",maxpath  
    
    #MinPATH
    idMin = dtmp[app][minpath.src][minpath.dst].values[0]
    print "\t\t MIN PATH Latency: ", dmsg[dmsg["id"].isin(idMin)].groupby(['id']).agg({"latency":np.sum}).mean().values[0] #Include cloud?

    idMax = dtmp[app][maxpath.src][maxpath.dst].values[0]
    print "\t\t MAX PATH Latency: ", dmsg[dmsg["id"].isin(idMax)].groupby(['id']).agg({"latency":np.sum}).mean().values[0]
    
    