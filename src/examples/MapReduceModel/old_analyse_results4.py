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
import math
warnings.simplefilter(action='ignore', category=FutureWarning)


def performResults(df,dfl,pathNetwork,f,exp):
    #T1+T2
    # Number of messages from sensors to replicas
    # Total de paquetes desde los sensores hasta las replicas (suma de las replicas). (acc. from sensors a replicas)
    #Sin identificar elementos.

#    print "Total number of perfomed transmissions : %i" %len(df)
    totalmessages = len(dfl)
    f.write("totalMSG;%s;%i\n"%(exp,totalmessages))

    #Group by app, src, and id
#    print "Total n.messages between sources -> replicas by app"
#    dtmp = df[df["module.src"]=="None"].groupby(['app','TOPO.src'])['id'].apply(list)
    #print "\tApplication\tMessages "
       
#    totalMessages = 0
#    for app,values in enumerate(dtmp):
#       print "\t%i\t%i" %(app,len(values))
#       for messageID in values:
#           totalMessages+=len(dfl[dfl.id==messageID][dfl["message"].str.contains("M.USER.APP")])
# Is the same=>
    totalMessagesSRCREP = dfl["message"].str.contains("M.USER.APP").sum()
    
#    print "Total Message  between sources -> replicas: %i" %totalMessages
    f.write("totalMSGsrcrep;%s;%i\n"%(exp,totalMessagesSRCREP))
    
#    print "Total messages between replicas -> cloud: %i" %(len(df)-totalMessages)
    f.write("totalMSGrepclo;%s;%i\n"%(exp,totalmessages-totalMessagesSRCREP))
    
    #T3
    #Latency from replicas to the cloud
    #Latency desde las replicas al cloud

    #desde df- identificar id que van al cloud
    #desde dfl - coger mensajes[ids] and borrar aquellos from M.USER.APP.
    dtmp = df[df["module.src"]!="None"].groupby(['app','TOPO.src'])['id'].apply(list)
#    print "Total n.messages between replicas -> cloud by app:"
#    print "\tApplication\tMessages "
#    totalMessages = 0
#    for app,values in enumerate(dtmp):
#        print "\t%i\t%i" %(app,len(values))
#        totalMessages+=len(values)
    #OJO-Si desglosar latency por app...deberia de estar aqui, lo siguiente:

    #TOTAL
    dfl["message"].str.contains("M.USER.APP")
    
    
    idMessagesToCloud = df[df["module.src"]!="None"]["id"].values
    #Selecting only transmissions between replicas and cloud
    dftmp = dfl[dfl["id"].isin(idMessagesToCloud)]
    dftmp = dftmp[dftmp['message'].str.contains("M.CLOUD")]
    
    grm = dftmp.groupby(["id"]).agg({"latency":np.sum})
#    print "Total avg. latency (replicas->cloud): %f" %grm.mean().latency
    f.write("totalLATrepclo;%s;%f\n"%(exp,grm.mean().latency))

    #T4
    #Latencia desde el sensor - con la replica(modulo) más cercana | más lejana (H)
#    print "Computing latency sources -> replica (MIN and MAX Path) each app"
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
    try:
        for ii in dtmp.index.to_series():
#            print ii
            if ii[0]!=previousAPP:
                if previousAPP>=0:
#                     print "CHANGE APP"
                     #MinPATH
    #                 if minpath.len == 0:
    #                     print "\t\t MIN PATH Latency: ",0
    #                 else:
                     #LAST SRC
                     idMin = dtmp[previousAPP][minpath.src][minpath.dst].values[0]
                     value = dmsg[dmsg["id"].isin(idMin)].groupby(['id']).agg({"latency":np.sum}).mean().values[0] #Include cloud?
                     if math.isnan(value): value=0
                     totalRmin.append(value)
                     try:
                         idMax = dtmp[previousAPP][maxpath.src][maxpath.dst].values[0]
                         value = dmsg[dmsg["id"].isin(idMax)].groupby(['id']).agg({"latency":np.sum}).mean().values[0] 
                     except IndexError:
                         print "NO MAX"
                         value = 0
                     totalRmax.append(value)
                    
#                     print "APP: ",previousAPP
#                     print "\t\t MIN PATH Latency: ", totalRmin
                     valuemin = np.array(totalRmin).mean()
                     totalmin.append(valuemin)
#                     print "\t\t MAX PATH Latency: ", totalRmax
                     totalmax.append(np.array(totalRmax).mean())
                     
                previousAPP = ii[0]
                minpath = PATH(src=0,dst=0,len=999999)
                maxpath = PATH(src=0,dst=0,len=-1)
                previousSRC = -1
                
                totalRmin = []
                totalRmax = []
    
#            print "APP ",previousAPP
            if ii[1]!=previousSRC:
#                print "CHANGE SRC"
                if previousSRC>=0:
                    idMin = dtmp[previousAPP][minpath.src][minpath.dst].values[0]
                    value = dmsg[dmsg["id"].isin(idMin)].groupby(['id']).agg({"latency":np.sum}).mean().values[0] #Include cloud?
                    if math.isnan(value): value=0
                    totalRmin.append(value)
                    idMax = dtmp[previousAPP][maxpath.src][maxpath.dst].values[0]
                    value = dmsg[dmsg["id"].isin(idMax)].groupby(['id']).agg({"latency":np.sum}).mean().values[0] 
                    totalRmax.append(value)
                    previousSRC = ii[1]
                else:
                    previousSRC = ii[1]
                    
#            print "SRC ",previousSRC
            
            dst = ii[2]
#            print "DST ",dst    
    
            if previousSRC == dst:
                minpath = PATH(src=previousSRC,dst=dst,len=0)
            else:
                path = list(nx.shortest_path(G, source=previousSRC, target=dst))
#                print "\t\t",path
                if minpath.len>len(path):
                    minpath = PATH(src=previousSRC,dst=dst,len=len(path))
                if maxpath.len<len(path):
                    maxpath = PATH(src=previousSRC,dst=dst,len=len(path))
                            
    #    print np.array(totalmin).mean()
    #    print np.array(totalmax).mean()
        f.write("totalLATmin;%s;%f\n"%(exp,np.array(totalmin).mean()))
        f.write("totalLATmax;%s;%f\n"%(exp,np.array(totalmax).mean()))
    except:
        print "ERROR LAT MIN Y MAX:   " , exp
        
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



fcsv = open("files/resultsParte1.csv","w") 
pathExperimento = "files/"
duration = 10000000
for f in xrange(5,10,5):
#for f in xrange(5,105,5):
#for f in xrange(45,50,5):
    exps = "rep-f%i-n50"%f
    print "\tRunning %s"%exps

    exp = "f%in50"%f
    model = "Replica"
    pathNetwork = pathExperimento+"%s-network.json"%exp
    


    path =pathExperimento+"Results_%s_%s_%s"%(exp,model,duration)
    df = pd.read_csv(path + ".csv")
    dfl = pd.read_csv(path + "_link.csv")
    performResults(df,dfl,pathNetwork,fcsv,exps)


    model = "Single"
    exps = "sin-f%i-n50"%f
    print "\tRunning %s"%exps
    path =pathExperimento+"Results_%s_%s_%s"%(exp,model,duration)
    df = pd.read_csv(path + ".csv")
    dfl = pd.read_csv(path + "_link.csv")
    performResults(df,dfl,pathNetwork,fcsv,exps)


fcsv.close()
