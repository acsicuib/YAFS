#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  5 12:02:41 2018

@author: isaaclera
"""

import numpy as np
import matplotlib.pyplot as plt
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


def performResults(df,dfl,pathNetwork,f,exp,it,idcloud):
    #T1+T2
    # Number of messages from sensors to replicas
    # Total de paquetes desde los sensores hasta las replicas (suma de las replicas). (acc. from sensors a replicas)
    #Sin identificar elementos.


    totalmessages = len(dfl)
    # print "Total number of perfomed transmissions : %i" %totalmessages
    f.write("totalMSG;%i;%s;%i\n"%(it,exp,totalmessages))
    totalMessagesSRCREP = dfl["message"].str.contains("M.USER.APP").sum()
    
    # print "Total Message  between sources -> replicas: %i" %totalMessagesSRCREP
    f.write("totalMSGsrcrep;%i;%s;%i\n"%(it,exp,totalMessagesSRCREP))
    
#    print "Total messages between replicas -> cloud: %i" %(len(df)-totalMessages)
    f.write("totalMSGrepclo;%i;%s;%i\n"%(it,exp,totalmessages-totalMessagesSRCREP))
    
    #T3
    #Latency from replicas to the cloud (in this case is the totalResponse)!
    #Latency desde las replicas al cloud
    # dtmp = df[df["module"].str.contains("CLOUD")]
    # lat = dtmp["time_out"] - dtmp["time_emit"]
    # # print lat.head()
    # # print "MAX %d" %lat.max()
    # # print "MIN %d" %lat.min()
    # latency = lat.mean()
    # latencySTD = lat.std()


    dt2 = df[df["TOPO.dst"] == idcloud][["app", "TOPO.src", "time_reception", "time_emit"]]
    dt2["latency"] = dt2["time_reception"] - dt2["time_emit"]

    appCloud, appCloudst = {}, {}
    for app in np.unique(dt2["app"]):
        dt3 = dt2[dt2.app == app]
        appCloud[app] = (dt3["latency"]).mean()
        appCloudst[app] = (dt3["time_reception"] - dt3["time_emit"]).std()

    lat = np.array(appCloud.values()).mean()
    devlatency = np.array(appCloudst.values()).mean()
    f.write("totalLATrepclo;%i;%s;%f\n" % (it, exp, lat))
    f.write("totalLATrepcloSTD;%i;%s;%f\n" % (it, exp, devlatency))

    # print "totalLATrepclo;%s;%f\n"%(exp,latency)
    # print "totalLATrepcloSTD;%s;%f\n"%(exp,latencySTD)


    # exit()

    #
    # f.write("totalLATrepclo;%i;%s;%f\n"%(it,exp,latency))
    # f.write("totalLATrepcloSTD;%i;%s;%f\n"%(it,exp,latencySTD))


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

    dtmp = df[df["module.src"] == "None"].groupby(['app', 'TOPO.src', 'TOPO.dst', 'message'])['id'].apply(list)
    dmsg = dfl[dfl["message"].str.contains("M.USER.APP")]

    try:
        minmaxPATHs = {}
        mindst, maxdst = 0, 0
        previousAPP = -1
        previousSRC = -1
        minpath, maxpath = PATH(src=0, dst=0, len=999999), PATH(src=0, dst=0, len=-1)
        for app, src, dst, message in dtmp.index.to_series().values:
            if previousSRC > 0:
                if src != previousSRC:
                    minmaxPATHs[(previousAPP, previousSRC)] = {"min": minpath.dst, "max": maxpath.dst}
                    #                print "MIN ",minpath, mindst
                    #                print "MAX ",maxpath, maxdst
                    minpath, maxpath = PATH(src=0, dst=0, len=999999), PATH(src=0, dst=0, len=-1)
                    previousAPP = app
                    previousSRC = src
            else:
                previousAPP = app
                previousSRC = src
                #        print app, src, dst, message
            path = list(nx.shortest_path(G, source=src, target=dst))
            if minpath.len > len(path):
                minpath = PATH(src=src, dst=dst, len=len(path))
                mindst = dst
            if maxpath.len < len(path):
                maxpath = PATH(src=src, dst=dst, len=len(path))
                maxdst = dst

        totalRmin, totalRmax = [], []
        for app, src in minmaxPATHs:
            dstmin = minmaxPATHs[(app, src)]["min"]
            dstmax = minmaxPATHs[(app, src)]["max"]

            idMin = dtmp[app][src][dstmin].values[0]
            valueMin = dmsg[dmsg["id"].isin(idMin)].groupby(['id']).agg({"latency": np.sum}).mean().values[
                0]  # Include cloud?
            if math.isnan(valueMin): valueMin = 0
            totalRmin.append(valueMin)

            idMax = dtmp[app][src][dstmax].values[0]
            valueMax = dmsg[dmsg["id"].isin(idMax)].groupby(['id']).agg({"latency": np.sum}).mean().values[0]
            if math.isnan(valueMax):
                print "NO MAXIMO"
                valueMax = 0
            totalRmax.append(valueMax)

        # print "MIN"
        # print np.array(totalRmin).mean()
        # print np.array(totalRmin).std()
        # print "MAX"
        # print np.array(totalRmax).mean()
        # print np.array(totalRmax).std()
        f.write("totalLATmin;%i;%s;%f\n" % (it, exp, np.array(totalRmin).mean()))
        f.write("totalLATmax;%i;%s;%f\n" % (it, exp, np.array(totalRmax).mean()))
        f.write("totalLATminSTD;%i;%s;%f\n" % (it, exp, np.array(totalRmin).std()))
        f.write("totalLATmaxSTD;%i;%s;%f\n" % (it, exp, np.array(totalRmax).std()))

    #    dtmp.index = dtmp.index.to_series()



    #     previousAPP=-1
#     previousSRC = -1
#     minpath,maxpath = PATH(src=0,dst=0,len=999999),PATH(src=0,dst=0,len=-1)
#     totalmin,totalRmin,totalmax,totalRmax = [],[],[],[]
#     #MOT ELEGANT
# #    previousPATH = {}
#     try:
#         for app, src, dst, message in dtmp.index.to_series().values:
#             if app!=previousAPP:
#                 if previousAPP>=0:
#                      # print "MIN PATH: ",minpath
#                      # print "MAX PATH: ",maxpath
#                      idMin = dtmp[previousAPP][minpath.src][minpath.dst].values[0]
#                      value = dmsg[dmsg["id"].isin(idMin)].groupby(['id']).agg({"latency":np.sum}).mean().values[0] #Include cloud?
#                      if math.isnan(value): value=0
#                      totalRmin.append(value)
#                      try:
#                          idMax = dtmp[previousAPP][maxpath.src][maxpath.dst].values[0]
#                          value = dmsg[dmsg["id"].isin(idMax)].groupby(['id']).agg({"latency":np.sum}).mean().values[0]
#                      except IndexError:
#                          print "NO MAX"
#                          value = 0
#                      totalRmax.append(value)
#
#                      # print "APP: ",previousAPP
#                      # print "\t\t MIN PATH Latency: ", totalRmin
#                      valuemin = np.array(totalRmin).mean()
#                      totalmin.append(valuemin)
#                      # print "\t\t MAX PATH Latency: ", totalRmax
#                      totalmax.append(np.array(totalRmax).mean())
#
#                 previousAPP = app
# #                minpath = PATH(src=0,dst=0,len=999999)
# #                maxpath = PATH(src=0,dst=0,len=-1)
#                 previousSRC = -1
#
# #                totalRmin = []
# #                totalRmax = []
#
#             # print "APP: ",previousAPP
#             if src!=previousSRC:
# #                print "CHANGE SRC"
#                 if previousSRC>=0:
#                     idMin = dtmp[previousAPP][minpath.src][minpath.dst].values[0]
#                     value = dmsg[dmsg["id"].isin(idMin)].groupby(['id']).agg({"latency":np.sum}).mean().values[0] #Include cloud?
#                     if math.isnan(value): value=0
#                     totalRmin.append(value)
#                     try:
#                         idMax = dtmp[previousAPP][maxpath.src][maxpath.dst].values[0]
#                         value = dmsg[dmsg["id"].isin(idMax)].groupby(['id']).agg({"latency":np.sum}).mean().values[0]
#                     except IndexError:
#                          print "NO MAX"
#                          value = 0
#                     totalRmax.append(value)
#
#                 previousSRC = src
#
#                 minpath = PATH(src=0,dst=0,len=999999)
#                 maxpath = PATH(src=0,dst=0,len=-1)
#
#                 totalRmin = []
#                 totalRmax = []
#
#
#             # print "\t SRC: ",src
#
#
#             path = list(nx.shortest_path(G, source=previousSRC, target=dst))
#
#             if previousSRC == dst:
#                 minpath = PATH(src=previousSRC,dst=dst,len=0)
#             else:
#                 if minpath.len>len(path):
#                     minpath = PATH(src=previousSRC,dst=dst,len=len(path))
#             if maxpath.len<len(path):
#                 maxpath = PATH(src=previousSRC,dst=dst,len=len(path))
#
#         #end for
#
#
#
#         #LAST ELEMENT
#         if previousAPP>=0:
#              # print "MIN PATH: ",minpath
#              # print "MAX PATH: ",maxpath
#
#              idMin = dtmp[previousAPP][minpath.src][minpath.dst].values[0]
#              value = dmsg[dmsg["id"].isin(idMin)].groupby(['id']).agg({"latency":np.sum}).mean().values[0] #Include cloud?
#              if math.isnan(value): value=0
#              totalRmin.append(value)
#              try:
#                  idMax = dtmp[previousAPP][maxpath.src][maxpath.dst].values[0]
#                  value = dmsg[dmsg["id"].isin(idMax)].groupby(['id']).agg({"latency":np.sum}).mean().values[0]
#              except IndexError:
#                  print "NO MAX"
#                  value = 0
#              totalRmax.append(value)
#
#              # print "APP: ",previousAPP
#              # print "\t\t MIN PATH Latency: ", totalRmin
#              # print "\t\t MAX PATH Latency: ", totalRmax
#              valuemin = np.array(totalRmin).mean()
#              totalmin.append(valuemin)
#              totalmax.append(np.array(totalRmax).mean())
#
#         # print "MIN "
#         # print np.array(totalmin).mean()
#         # print np.array(totalmin).std()
#         # print "Max"
#         # print np.array(totalmax).mean()
#         # print np.array(totalmax).std()
#
#         f.write("totalLATmin;%i;%s;%f\n"%(it,exp,np.array(totalmin).mean()))
#         f.write("totalLATmax;%i;%s;%f\n"%(it,exp,np.array(totalmax).mean()))
#         f.write("totalLATminSTD;%i;%s;%f\n"%(it,exp,np.array(totalmin).std()))
#         f.write("totalLATmaxSTD;%i;%s;%f\n"%(it,exp,np.array(totalmax).std()))
    except:
        print "ERROR LAT MIN Y MAX:   "




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

fcsv = open(pathExperimento+"resultsParte_n200.csv","w")


for i in range(nSimulations):
    for f in xrange(100,201,10):
        exps = "rep-f%i-n200"%f
        print "\tRunning %s"%exps
        exp = "f%in200"%f
        model = "Replica"
        pathNetwork = pathExperimento + "%s-network.json" % exp

        path =pathExperimento+"Results_%i_%s_%s_%s"%(i,exp,model,duration)
        df = pd.read_csv(path + ".csv")
        dfl = pd.read_csv(path + "_link.csv")
        performResults(df,dfl,pathNetwork,fcsv,exps,i,200)


        model = "Single"
        exps = "sin-f%i-n200"%f
        print "\tRunning %s"%exps
        path =pathExperimento+"Results_%i_%s_%s_%s"%(i,exp,model,duration)
        df = pd.read_csv(path + ".csv")
        dfl = pd.read_csv(path + "_link.csv")
        performResults(df,dfl,pathNetwork,fcsv,exps,i,200)
        #
        # model = "Cloud"
        # exps = "cloud-f%i-n200" % f
        # print "\tRunning %s" % exps
        # path = pathExperimento + "Results_%i_%s_%s_%s" % (i,exp, model, duration)
        # df = pd.read_csv(path + ".csv")
        # dfl = pd.read_csv(path + "_link.csv")
        # performResults(df, dfl, pathNetwork, fcsv, exps,i)

        model = "FstrRep"
        exps = "Fstrrep-f%i-n200" % f
        print "\tRunning %s" % exps
        path = pathExperimento + "Results_%i_%s_%s_%s" % (i,exp, model, duration)
        df = pd.read_csv(path + ".csv")
        dfl = pd.read_csv(path + "_link.csv")
        performResults(df, dfl, pathNetwork, fcsv, exps,i,200)

fcsv.close()
