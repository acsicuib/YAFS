#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jan  9 11:03:53 2019

@author: isaaclera
"""

import collections
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pickle
from scipy import stats
import matplotlib.patheffects as pe
import os
import networkx as nx
import json

def set_box_color(bp, color):
    plt.setp(bp['boxes'], color=color)
    plt.setp(bp['whiskers'], color=color)
    plt.setp(bp['caps'], color=color)
    plt.setp(bp['medians'], color=color)
    
# =============================================================================
# Boxplot matriz of each app - gtw/user
# =============================================================================

def drawBoxPlot_Both_USER_ax(app,dr,drILP,ax):
     data_a=dr[dr.app==app].r.values
     data_b=drILP[drILP.app==app].r.values
     ticks = list(np.sort(dr[dr.app==app].user.unique()))
     bpl = ax.boxplot(data_a, positions=np.array(xrange(len(data_a)))*2.0-0.4, sym='', widths=0.55,
                      whiskerprops = dict(linewidth=2),
                     boxprops = dict(linewidth=2),
                      capprops = dict(linewidth=2),
                     medianprops = dict(linewidth=2))
     bpI = ax.boxplot(data_b, positions=np.array(xrange(len(data_b)))*2.0+0.4, sym='', widths=0.55,
                         whiskerprops = dict(linewidth=2),
                     boxprops = dict(linewidth=2),
                      capprops = dict(linewidth=2),
                     medianprops = dict(linewidth=2))
     set_box_color(bpl, '#a6bddb')
     set_box_color(bpI, '#e34a33')
     ax.get_xaxis().set_ticks(xrange(0, len(ticks) * 2, 2))
     ax.set_xticklabels(ticks)
     ax.set_title("App:%i"%app)
     ax.set_xlim(-2, len(ticks)*2)
     ax.plot([], c='#a6bddb', label="Electre III",linewidth=3)
     ax.plot([], c='#e34a33', label="Weighted aveg.",linewidth=3)


            
def drawRequestOnTimeline(ticks,messagesbyTime,i=0):
    
    fig, ax = plt.subplots(figsize=(8.0,4.0))
    ax.plot(ticks, messagesbyTime, '-',color='#756bb1',alpha=1.,linewidth=2)
    
    z = np.polyfit(ticks, messagesbyTime, 10)
    p = np.poly1d(z)
    
    ax1 = ax.plot(ticks,p(ticks),":",color='#c1bcdc',linewidth=6,label="Total num. of requests",path_effects=[pe.Stroke(linewidth=8, foreground='purple'), pe.Normal()])
    ax.set_xlabel("Simulation number: %i"%i, fontsize=12)
    ax.set_ylabel("QoS satisfaction \n (num. of requests)", fontsize=12)
    ax.tick_params(labelsize=10)
    #ax.set_xlim(-20,2020)
    #ax.set_ylim(0,120)
    #plt.legend([ax1,ax2,ax3],['Total num. of requests','Partition','ILP'],loc="upper right",fontsize=18)
    plt.legend(loc="lower left",fontsize=12)
    plt.tight_layout()
    #plt.savefig('TimeSerie_Requests-%i.pdf'%i, format='pdf', dpi=600)


def getRbyApp(df,dtmp):
    dr = pd.DataFrame(
        columns=['app', 'user', 'avg', 'std', 'm', 'r', 'invalid', 'over','totalmsg'])  # m - numero de mensajes enviados
    times = []
    ixloc = 0
    for g in dtmp.keys():
        ids = dtmp[g]
        responses = []
        messages = []
        over = 0
        # Firstly, it computes the mode in all the app,user transmissions
        for i in ids:
            messages.append(df[df.id == i].shape[0])  # number of messages send by the user

        # Requests with a inferior number of messages are filtered
        msg = np.array(messages)
        # mode = stats.mode(msg).mode[0]
        mode = stats.mode(msg)[0][0]

        # Secondly, if each transmission has the same mode then the time is storaged
        invalid = 0
        for i in ids:
            dm = df[df.id == i]
            if mode == dm.shape[0]:
                r = dm['time_out'].max() - dm['time_emit'].min()
                responses.append(r)
                times.append(dm['time_emit'].min())
            else:
                invalid += 1

        resp = np.array(responses)

        avg = resp.mean()
        dsv = resp.std()
        totalmsg = len(resp)
        dr.loc[ixloc] = [g[0], g[1], avg, dsv, mode, resp, invalid, over,totalmsg]
        ixloc += 1
        print g, "\t", len(dtmp[g]), "\t", invalid, "\t", over

    return dr, times

# =============================================================================
# =============================================================================
# #  GLOBAL VARIABLES
# =============================================================================
# =============================================================================
simulationTime=10000
data = "20190111"
pathEXP = "exp1/"
pathSimple = "exp1/results_%s/"%data
simulations = 1
idCloud = 153






### Latency
#ONLY ONE TIME
if not os.path.exists(pathSimple+"dr_%s_%i.pkl"%("MCDA",0)):
    for case in ["MCDA","WA"]:
        sR = pd.Series()
        for it in range(simulations):
            fCSV = "Results_%s_%i_%i.csv"%(case,simulationTime,it)
            
            df = pd.read_csv(pathSimple+fCSV)
            dtmp = df[df["module.src"]=="None"].groupby(['app','TOPO.src'])['id'].apply(list)
            dr,timeC = getRbyApp(df,dtmp)
            
            dC = pd.DataFrame(index=np.array(timeC).astype('datetime64[s]'))
            dC["QTY"]=np.ones(len(timeC))
            dC = dC.resample('10s').agg(dict(QTY='sum'))
            messagesbyTime = dC.QTY.values
            
            dr.to_pickle(pathSimple+"dr_%s_%i.pkl"%(case,it))
            np.save(pathSimple+"messagesbyTime_%s_%i.npy"%(case,it),messagesbyTime)
              
for i in range(simulations):
    if i!=5:
     print "Boxing plot: %i" %i
     dr = pd.read_pickle(pathSimple+"dr_%s_%i.pkl"%("MCDA",i))
     drILP = pd.read_pickle(pathSimple+"dr_%s_%i.pkl"%("WA",i))

     fig, axlist = plt.subplots(nrows=2, ncols=5, figsize=(14, 10))
     for idx,ax in enumerate(axlist.flatten()):
         drawBoxPlot_Both_USER_ax(idx,dr,drILP,ax)

     fig.subplots_adjust(top=0.9, left=0.1, right=0.9, bottom=0.12)
     fig.subplots_adjust(hspace=0.4,wspace=0.35)
     axlist.flatten()[-2].legend(loc='upper center', bbox_to_anchor=(-0.85, -0.33), ncol=4,fontsize=16 )

     axlist[1][2].set_xlabel('IoT devices (Gateways id.) - Simulation: %i'%i,fontsize=20)
     axlist[0][0].set_ylabel('Response time (ms)',fontsize=20)
     axlist[0][0].yaxis.set_label_coords(-0.4, 0)
     ax.tick_params(labelsize=12)
     plt.savefig('BoxPlot_ResponseAppUser_%i.pdf'%i, format='pdf', dpi=600)
#     plt.show()
      

     
# =============================================================================
# Distribucion de servicios y network visualization
# =============================================================================
def distributionServices(case):
    path =  pathSimple+"/tmp_%s/" %(case)
#    fname = "file_alloc_entities_%s_%i_%i.pkl"% (case, simulationTime, it)
    #La distribución de servicios en los nodos
    fname2="file_alloc_entities_%s_%i_%i.pkl"% (case, simulationTime, it)
    f = open(path+fname2,"r")
    cs2 = pickle.load(f)
    dep = {}
    for k in cs2:
        dep[str(k)]=len(cs2[k])
        
    df = pd.DataFrame().from_dict(dep, orient='index')   
    df = df[df[0] != 0]
    df = df.sort_values(by=[0],ascending=False)
    print "%s Total servicios desplegados: %i"%(case,df[0].sum())


    fig, ax = plt.subplots(figsize=(8.0,4.0))
    ax.set_xlabel("Nodes", fontsize=14)
    ax.set_ylabel("Num. of deployed services", fontsize=14)
    ax.bar(range(len(df)),df[0].values)
    plt.xticks(range(len(df)), df.index.values)
    ax.set_title("Distribution of nodes using %s approach"%case)
    #plt.legend(loc="lower left",fontsize=14)
    plt.tight_layout()
    #plt.savefig('frec_of_services.pdf', format='pdf', dpi=600)
    return dep
    
dep_MCDA = distributionServices("MCDA")
dep_WA = distributionServices("WA")
   
   


## discovering source entities
sources_MCDA,sources_WA = {},{}
sources2_MCDA,sources2_WA = {},{}
case= "MCDA"
dr = pd.read_pickle(pathSimple+"dr_%s_%i.pkl"%(case,0))
nodeSources = dr.user.values
for k in range(200):
    sources_MCDA[str(k)]=k in nodeSources
    if k in nodeSources:
        sources2_MCDA[str(k)] = 10.0
    else:
        sources2_MCDA[str(k)] = 0.0     
case=  "WA"
dr = pd.read_pickle(pathSimple+"dr_%s_%i.pkl"%(case,0))
nodeSources = dr.user.values
for k in range(200):
    sources_WA[str(k)]=k in nodeSources
    if k in nodeSources:
        sources2_WA[str(k)] = 10.0
    else:
        sources2_WA[str(k)] = 0.0 
    
#Ok
G = nx.read_gexf(pathEXP+"network.gexf")
nx.set_node_attributes(G, values=dep_MCDA, name='deploys_MCDA')
nx.set_node_attributes(G, values=dep_WA, name='deploys_WA')
nx.set_node_attributes(G, values=sources_MCDA, name='sources_MCDA')
nx.set_node_attributes(G, values=sources2_MCDA, name='sourcesValue_MCDA')
nx.set_node_attributes(G, values=sources_WA, name='sources_WA')
nx.set_node_attributes(G, values=sources2_WA, name='sourcesValue_WA')
nx.write_gexf(G,pathSimple+"netwok-WA-MCDA.gexf")    




# =============================================================================
# Calculo Average Distance
# =============================================================================

G = nx.read_gexf(pathEXP+"network.gexf")
def compute_distance(k):
    return nx.shortest_path_length(G,str(k[0]),str(k[1]))
    
cache_distance_MCDA ={}
case = "MCDA"
it =0 

fCSV = "Results_%s_%i_%i.csv"%(case,simulationTime,it)
df = pd.read_csv(pathSimple+fCSV)
for row in df[["TOPO.src","TOPO.dst"]].iterrows():
    k = (row[1][0],row[1][1])
    if not k in cache_distance_MCDA.keys():
        cache_distance_MCDA[k] = compute_distance(k)

cache_distance_WA ={}
case = "WA"

fCSV = "Results_%s_%i_%i.csv"%(case,simulationTime,it)
df = pd.read_csv(pathSimple+fCSV)
for row in df[["TOPO.src","TOPO.dst"]].iterrows():
    k = (row[1][0],row[1][1])
    if not k in cache_distance_WA.keys():
        cache_distance_WA[k] = compute_distance(k)
           
 
x = cache_distance_MCDA.values() 
counter=collections.Counter(x)
print(counter)
y = cache_distance_WA.values() 
counterWA=collections.Counter(y)
print(counterWA)

#unificacion datos

data_a, data_b = {},{}
for k in range(8):
    data_a[k] = counter[k]
    data_b[k] = counterWA[k]
    
data_a = data_a.values()
data_b = data_b.values()
ticks = range(8)
N = len(ticks)
ind = np.array(ticks)
width = 0.45
        
fig, ax = plt.subplots(figsize=(8.0,4.0))
ax.get_xaxis().set_ticks(xrange(0, len(ticks) * 2, 2))
r = ax.bar(ind, data_a, width, color='r')
r2 = ax.bar(ind+width, data_b, width, color='y')
ax.set_xticks(ind+ width/2)
ax.set_xticklabels(ticks)
#ax.set_title("App")
ax.set_xlim(-width, len(ticks))
ax.plot([], c='#a6bddb', label="Electre III",linewidth=3)
ax.plot([], c='#e34a33', label="WA",linewidth=3)
ax.set_xlabel("Hop count among services", fontsize=18)
ax.set_ylabel("Quantity", fontsize=18)
plt.legend([r,r2],['Electre III','WA'],loc="upper right",fontsize=14)
plt.tight_layout()



# =============================================================================
# Calculo POWER
# =============================================================================

#Getting power values from network
dataNetwork = json.load(open(pathEXP + 'networkDefinition.json'))
powers = {}
for node in dataNetwork["entity"]:
    powers[node["id"]]=(node["POWERmin"]+node["POWERmax"])/2.0

#distribution of services in the experiment
#dep_MCDA = distributionServices("MCDA")
#dep_WA = distributionServices("WA")

valuesPower_MCDA,valuesPower_WA = [],[]

for k in dep_MCDA.keys():
    if k!=idcloud: 
        if dep_MCDA[k]>=1:
            valuesPower_MCDA.append(powers[int(k)])

for k in dep_WA.keys():
    if k!=idcloud:
        if dep_WA[k]>=1:
            valuesPower_WA.append(powers[int(k)])

data_a = [valuesPower_MCDA]
data_b = [valuesPower_WA]
ticks = [1,2]
fig, ax = plt.subplots(figsize=(5.0,4.0))
bpl = ax.boxplot(data_a, positions=[1], sym='', widths=0.5,
              whiskerprops = dict(linewidth=2),
             boxprops = dict(linewidth=2),
              capprops = dict(linewidth=2),
             medianprops = dict(linewidth=2))
bpI = ax.boxplot(data_b, positions=[2], sym='', widths=0.5,
                 whiskerprops = dict(linewidth=2),
             boxprops = dict(linewidth=2),
              capprops = dict(linewidth=2),
             medianprops = dict(linewidth=2))

set_box_color(bpl, '#a6bddb')
set_box_color(bpI, '#e34a33')
ax.get_xaxis().set_ticks([1,2])
ax.set_xticklabels(["Electre III","WA"])
#ax.set_title("App:%i"%app)
ax.set_xlim(0.55,2.55)
#ax.set_xlabel("Hop count among services", fontsize=18)
ax.set_ylabel("Watts", fontsize=12)
plt.tight_layout()
  

# =============================================================================
# THE PRICE
# =============================================================================
priceMCDA = 0
for k in dep_MCDA.keys():
    if dep_MCDA[k]>0:
        if int(k)<100:
            priceMCDA+=1
            
priceWA = 0
for k in dep_WA.keys():
    if dep_WA[k]>0:
        if int(k)<100:
            priceWA+=1

print "The cost in Electre is: %i"%priceMCDA
print "The cost in WA is: %i"%priceWA

# =============================================================================
# Penalización por uso de ese nodo en APP
# =============================================================================
cases =["MCDA","WA"]

for case in cases:
    fCSV = "Results_%s_%i_%i.csv"%(case,simulationTime,it)
    df = pd.read_csv(pathSimple+fCSV)
    gb = df.groupby(['app', 'TOPO.dst'])
    counts = gb.size().to_frame(name='counts')
    app = counts.index.get_level_values("app").values
    topo = counts.index.get_level_values("TOPO.dst").values
#    print len(app) == len(topo)
    
    pena = 0
    for i in range(len(app)):
        if app[i]%2 != topo[i]%2:
            pena +=1
            
    print "Penalización por caso: %s = %i" %(case,pena)

    