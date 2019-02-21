#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  5 12:02:41 2018

@author: isaaclera
"""

import numpy as np
#import matplotlib.pyplot as plt
import pandas as pd
#from pandas import Series, date_range
#import matplotlib.pyplot as plt
#import numpy as np
import json
#from scipy import stats
import collections
import networkx as nx
import warnings
import math
import argparse
warnings.simplefilter(action='ignore', category=FutureWarning)


def performResults(df,dfl,pathNetwork,f,exp,it):
    #T1+T2
    # Number of messages from sensors to replicas
    # Total de paquetes desde los sensores hasta las replicas (suma de las replicas). (acc. from sensors a replicas)
    #Sin identificar elementos.

#    print "Total number of perfomed transmissions : %i" %len(df)
    totalmessages = len(dfl)
    f.write("totalMSG;%i;%s;%i\n"%(it,exp,totalmessages))
    totalMessagesSRCREP = dfl["message"].str.contains("M.USER.APP").sum()
    
#    print "Total Message  between sources -> replicas: %i" %totalMessages
    f.write("totalMSGsrcrep;%i;%s;%i\n"%(it,exp,totalMessagesSRCREP))
    
#    print "Total messages between replicas -> cloud: %i" %(len(df)-totalMessages)
    f.write("totalMSGrepclo;%i;%s;%i\n"%(it,exp,totalmessages-totalMessagesSRCREP))
    
    #T3
    #Latency from replicas to the cloud (in this case is the totalResponse)!
    #Latency desde las replicas al cloud
    dtmp = df[df["module"].str.contains("CLOUD")]
    latency = (dtmp["time_out"]-dtmp["time_emit"]).mean()
    devlatency = (dtmp["time_out"] - dtmp["time_emit"]).std()
    f.write("totalLATrepclo;%i;%s;%f\n"%(it,exp,latency))
    f.write("totalLATrepcloSTD;%i;%s;%f\n"%(it,exp,devlatency))


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
    #MOT ELEGANT
     
    try:
        for app, src, dst, message in dtmp.index.to_series().values:
            if app!=previousAPP:
                if previousAPP>=0:
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
                     except AttributeError:
                        print "NO MAX"
                        value = 0
                     totalRmax.append(value)
                    
#                     print "APP: ",previousAPP
#                     print "\t\t MIN PATH Latency: ", totalRmin
                     valuemin = np.array(totalRmin).mean()
                     totalmin.append(valuemin)
#                     print "\t\t MAX PATH Latency: ", totalRmax
                     totalmax.append(np.array(totalRmax).mean())
                         
                previousAPP = app
#                minpath = PATH(src=0,dst=0,len=999999)
#                maxpath = PATH(src=0,dst=0,len=-1)
                previousSRC = -1
                
#                totalRmin = []
#                totalRmax = []
    
#            print "APP: ",previousAPP
            if src!=previousSRC:
#                print "CHANGE SRC"
                if previousSRC>=0:
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
                    except AttributeError:
                        print "NO MAX"
                        value = 0
                    totalRmax.append(value)
                    
          
                previousSRC = src  
                minpath = PATH(src=0,dst=0,len=999999)
                maxpath = PATH(src=0,dst=0,len=-1)
                         
                totalRmin = []
                totalRmax = []
                                   
    
#            print "\t SRC: ",src
            
            if previousSRC == dst:
                minpath = PATH(src=previousSRC,dst=dst,len=0)
            else:
                path = list(nx.shortest_path(G, source=previousSRC, target=dst))
#                print "\t\t - PATH",path
                if minpath.len>len(path):
                    minpath = PATH(src=previousSRC,dst=dst,len=len(path))
                if maxpath.len<len(path):
                    maxpath = PATH(src=previousSRC,dst=dst,len=len(path))
                     
        #end for           
        #LAST ELEMENT
        if previousAPP>=0:
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
             except AttributeError:
                 print "NO MAX"
                 value = 0
             totalRmax.append(value)
            
#             print "APP: ",previousAPP
#             print "\t\t MIN PATH Latency: ", totalRmin
             valuemin = np.array(totalRmin).mean()
             totalmin.append(valuemin)
#             print "\t\t MAX PATH Latency: ", totalRmax
             totalmax.append(np.array(totalRmax).mean())

#        print np.array(totalmin).mean()
#        print np.array(totalmax).mean()
        f.write("totalLATmin;%i;%s;%f\n"%(it,exp,np.array(totalmin).mean()))
        f.write("totalLATmax;%i;%s;%f\n"%(it,exp,np.array(totalmax).mean()))
        f.write("totalLATminSTD;%i;%s;%f\n"%(it,exp,np.array(totalmin).std()))
        f.write("totalLATmaxSTD;%i;%s;%f\n"%(it,exp,np.array(totalmax).std()))
    except:
        print "ERROR LAT MIN Y MAX:   " , exp




# pathExperimento = "files2/"
# duration = 100000
# nSimulations = 1



parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument(
    '--work-dir',
    type=str,
    default="",
    help='Working directory')

parser.add_argument(
    '--simulations',
    type=int,
    default=1,
    help='Number of simulations')

parser.add_argument(
    '--duration',
    type=int,
    default=100000,
    help='Simulation time')

args, pipeline_args = parser.parse_known_args()

nSimulations = args.simulations
pathExperimento = args.work_dir+""
duration = args.duration
fcsv = open(pathExperimento+"resultsParte_f100.csv","w")

for i in range(nSimulations):
    for n in xrange(100,301,20):
        exps = "rep-f100-n%i"%n
        print "\tRunning %s"%exps

        exp = "f100n%i"%n
        model = "Replica"
        pathNetwork = pathExperimento+"%s-network.json"%exp

        path =pathExperimento+"Results_%i_%s_%s_%s"%(i,exp,model,duration)
        df = pd.read_csv(path + ".csv")
        dfl = pd.read_csv(path + "_link.csv")
        performResults(df,dfl,pathNetwork,fcsv,exps,i)


        model = "Single"
        exps = "sin-f100-n%i"%n
        print "\tRunning %s"%exps
        path =pathExperimento+"Results_%i_%s_%s_%s"%(i,exp,model,duration)
        df = pd.read_csv(path + ".csv")
        dfl = pd.read_csv(path + "_link.csv")
        performResults(df,dfl,pathNetwork,fcsv,exps,i)

        # model = "Cloud"
        # exps = "cloud-f100-n%i" % n
        # print "\tRunning %s" % exps
        # path = pathExperimento + "Results_%i_%s_%s_%s" % (i,exp, model, duration)
        # df = pd.read_csv(path + ".csv")
        # dfl = pd.read_csv(path + "_link.csv")
        # performResults(df, dfl, pathNetwork, fcsv, exps,i)

        model = "FstrRep"
        exps = "Fstrrep-f100-n%i" % n
        print "\tRunning %s" % exps
        path = pathExperimento + "Results_%i_%s_%s_%s" % (i,exp, model, duration)
        df = pd.read_csv(path + ".csv")
        dfl = pd.read_csv(path + "_link.csv")
        performResults(df, dfl, pathNetwork, fcsv, exps,i)


#df["totalResponse"] = df.time_out - df.time_emit
#df["latency"]= df.time_reception - df.time_emit
fcsv.close()

