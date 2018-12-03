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
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


def performResults(df,dfl,pathNetwork,f,exp):
    #T1+T2
    # Number of messages from sensors to replicas
    # Total de paquetes desde los sensores hasta las replicas (suma de las replicas). (acc. from sensors a replicas)
    #Sin identificar elementos.

    print "Total number of perfomed transmissions : %i" %len(df)
    f.write("totalMSG;%s;%i\n"%(exp,len(df)))

    #Group by app, src, and id
    print "Total n.messages between sources -> replicas by app"
    dtmp = df[df["module.src"]=="None"].groupby(['app','TOPO.src'])['id'].apply(list)
    #print "\tApplication\tMessages "
    totalMessages = 0
    for app,values in enumerate(dtmp):
      # print "\t%i\t%i" %(app,len(values))
       totalMessages+=len(values)

    print "Total Message  between sources -> replicas: %i" %totalMessages
    f.write("totalMSGsrcrep;%s;%i\n"%(exp,totalMessages))
    
    print "Total messages between replicas -> cloud: %i" %(len(df)-totalMessages)
    f.write("totalMSGrepclo;%s;%i\n"%(exp,len(df)-totalMessages))
    
    #T3
    #Latency from replicas to the cloud
    #Latency desde las replicas al cloud

    #desde df- identificar id que van al cloud
    #desde dfl - coger mensajes[ids] and borrar aquellos from M.USER.APP.
    dtmp = df[df["module.src"]!="None"].groupby(['app','TOPO.src'])['id'].apply(list)
    print "Total n.messages between replicas -> cloud by app:"
#    print "\tApplication\tMessages "
#    totalMessages = 0
#    for app,values in enumerate(dtmp):
#        print "\t%i\t%i" %(app,len(values))
#        totalMessages+=len(values)
    #OJO-Si desglosar latency por app...deberia de estar aqui, lo siguiente:

    #TOTAL
    idMessagesToCloud = df[df["module.src"]!="None"]["id"].values
    #Selecting only transmissions between replicas and cloud
    dftmp = dfl[dfl["id"].isin(idMessagesToCloud)]
    dftmp = dftmp[dftmp['message'].str.contains("M.CLOUD")]
    grm = dftmp.groupby(["id"]).agg({"latency":np.sum})
    print "Total avg. latency (replicas->cloud): %f" %grm.mean().latency
    f.write("totalLATrepclo;%s;%f\n"%(exp,grm.mean().latency))

    #T4
    #Latencia desde el sensor - con la replica(modulo) más cercana | más lejana (H)
    print "Computing latency sources -> replica (MIN and MAX Path) each app"
    PATH = collections.namedtuple('PATH', 'src dst len')
    #LOADING NETWORK
    data = json.load(open(pathNetwork))
    G = nx.Graph()
    for edge in data["link"]:
        G.add_edge(edge["s"], edge["d"])
        
#    print G.nodes


    dtmp = df[df["module.src"]=="None"].groupby(['app','TOPO.src','TOPO.dst','message'])['id'].apply(list)
    dmsg = dfl[dfl["message"].str.contains("M.USER.APP")]
#    dtmp.index = dtmp.index.to_series()
    previousAPP=-1
    previousSRC = -1  
    minpath,maxpath = PATH(src=0,dst=0,len=999999),PATH(src=0,dst=0,len=-1)
    totalmin,totalRmin,totalmax,totalRmax = [],[],[],[]

    for ii in dtmp.index.to_series():
#        print ii
        if ii[0]!=previousAPP:
            if previousAPP>=0:
                 #MinPATH
#                 if minpath.len == 0:
#                     print "\t\t MIN PATH Latency: ",0
#                 else:
                 #LAST SRC
                 idMin = dtmp[previousAPP][minpath.src][minpath.dst].values[0]
                 value = dmsg[dmsg["id"].isin(idMin)].groupby(['id']).agg({"latency":np.sum}).mean().values[0] #Include cloud?
                 totalRmin.append(value)
                 idMax = dtmp[previousAPP][maxpath.src][maxpath.dst].values[0]
                 value = dmsg[dmsg["id"].isin(idMax)].groupby(['id']).agg({"latency":np.sum}).mean().values[0] 
                 totalRmax.append(value)
                
                 print "APP: ",previousAPP
                 print "\t\t MIN PATH Latency: ", totalRmin
                 totalmin.append(np.array(totalRmin).mean())
                 print "\t\t MAX PATH Latency: ", totalRmax
                 totalmax.append(np.array(totalRmax).mean())
                 
            previousAPP = ii[0]
            minpath = PATH(src=0,dst=0,len=999999)
            maxpath = PATH(src=0,dst=0,len=-1)
            previousSRC = -1
            
            totalRmin = []
            totalRmax = []

#        print "APP ",previousAPP
        if ii[1]!=previousSRC:
            if previousSRC>=0:
                idMin = dtmp[previousAPP][minpath.src][minpath.dst].values[0]
                value = dmsg[dmsg["id"].isin(idMin)].groupby(['id']).agg({"latency":np.sum}).mean().values[0] #Include cloud?
                totalRmin.append(value)
                idMax = dtmp[previousAPP][maxpath.src][maxpath.dst].values[0]
                value = dmsg[dmsg["id"].isin(idMax)].groupby(['id']).agg({"latency":np.sum}).mean().values[0] 
                totalRmax.append(value)
                previousSRC = ii[1]
            else:
                previousSRC = ii[1]
                
#        print "SRC ",previousSRC
        
        dst = ii[2]
#        print "DST ",dst    

        if previousSRC == dst:
            minpath = PATH(src=previousSRC,dst=dst,len=0)
        else:
            path = list(nx.shortest_path(G, source=previousSRC, target=dst))
#            print "\t\t",path
            if minpath.len>len(path):
                minpath = PATH(src=previousSRC,dst=dst,len=len(path))
            if maxpath.len<len(path):
                maxpath = PATH(src=previousSRC,dst=dst,len=len(path))
                        
    print np.array(totalmin).mean()
    print np.array(totalmax).mean()
    f.write("totalLATmin;%s;%f\n"%(exp,np.array(totalmin).mean()))
    f.write("totalLATmax;%s;%f\n"%(exp,np.array(totalmax).mean()))
#    for app in dtmp.index.levels[0].values:
#        print "app ",app
#        minpath = PATH(src=0,dst=0,len=999999)
#        maxpath = PATH(src=0,dst=0,len=-1)
#        for src in dtmp[app].index.levels[0].values:
#            print "\tsrc ",src
#            for dst in dtmp[app][src].index.levels[0].values:
#                print "\t\tdst ",dst
#                if src == dst:
#                    minpath = PATH(src=src,dst=dst,len=0)
#                else:
#                    path = list(nx.shortest_path(G, source=src, target=dst))
#                    print "\t\t",path
#                    if minpath.len>len(path):
#                        minpath = PATH(src=src,dst=dst,len=len(path))
#                    if maxpath.len<len(path):
#                        maxpath = PATH(src=src,dst=dst,len=len(path))
#            break
#        break
#    
#        print "\t",minpath
#        print "\t",maxpath
#
#        #MinPATH
#        idMin = dtmp[app][minpath.src][minpath.dst].values[0]
#        print "\t\t MIN PATH Latency: ", dmsg[dmsg["id"].isin(idMin)].groupby(['id']).agg({"latency":np.sum}).mean().values[0] #Include cloud?
#
#        idMax = dtmp[app][maxpath.src][maxpath.dst].values[0]
#        print "\t\t MAX PATH Latency: ", dmsg[dmsg["id"].isin(idMax)].groupby(['id']).agg({"latency":np.sum}).mean().values[0]
#



fcsv = open("results.csv","a") 
pathExperimento = "files/"
time = 10000000

exp = "f5n50"
model = "Replica"
models = "rep"
exps = "%s-f5-n50"%(models)
pathNetwork = pathExperimento+"%s-network.json"%exp
path =pathExperimento+"Results_%s_%s_%s"%(exp,model,time)
df = pd.read_csv(path + ".csv")
dfl = pd.read_csv(path + "_link.csv")
print " REPLICA "*5
performResults(df,dfl,pathNetwork,fcsv,exps)

model = "Single"
print " \n\nSINGLE "*5
models = "sin"
exps = "%s-f5-n50"%(models)
path =pathExperimento+"Results_%s_%s_%s"%(exp,model,time)
df = pd.read_csv(path + ".csv")
dfl = pd.read_csv(path + "_link.csv")
performResults(df,dfl,pathNetwork,fcsv,exps)

fcsv.close()
