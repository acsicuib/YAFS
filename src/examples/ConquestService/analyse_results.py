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
import time
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
     bpl = ax.boxplot(data_a, positions=np.array(range(len(data_a)))*2.0-0.4, sym='', widths=0.55,
                      whiskerprops = dict(linewidth=2),
                     boxprops = dict(linewidth=2),
                      capprops = dict(linewidth=2),
                     medianprops = dict(linewidth=2))
     bpI = ax.boxplot(data_b, positions=np.array(range(len(data_b)))*2.0+0.4, sym='', widths=0.55,
                         whiskerprops = dict(linewidth=2),
                     boxprops = dict(linewidth=2),
                      capprops = dict(linewidth=2),
                     medianprops = dict(linewidth=2))
     set_box_color(bpl, '#a6bddb')
     set_box_color(bpI, '#e34a33')
     ax.get_xaxis().set_ticks(range(0, len(ticks) * 2, 2))
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
        columns=['app', 'user', 'r', 'time'])  # m - numero de mensajes enviados

    ixloc = 0
    for g in dtmp.keys():
        ids = dtmp[g]
        responses = []
        times = []
#        messages = []

        # Firstly, it computes the mode in all the app,user transmissions
#        for i in ids:
#            messages.append(df[df.id == i].shape[0])  # number of messages send by the user
#
#        # Requests with a inferior number of messages are filtered
#        msg = np.array(messages)
#        # mode = stats.mode(msg).mode[0]
#        mode = stats.mode(msg)[0][0]
        mode = 1
        print("-----"*10)
        for i in ids:
            dm = df[df.id == i]
            print(dm)
            if mode == dm.shape[0]:
                r = dm['time_out'].max() - dm['time_emit'].min()
                responses.append(r)
                print(r)
                times.append(dm['time_emit'].min())

        resp = np.array(responses)

        dr.loc[ixloc] = [g[0], g[1],resp, times]
        ixloc += 1

    return dr

def prepare_results(pathSimple):
    ### Latency
    #ONLY ONE TIME
   # if not os.path.exists(pathSimple+"dr_%s_%i.pkl"%("CQ",0)):
        for case in ["CQ"]:
            for it in range(nsimulations):
                fCSV = "Results_%s_%i_%i.csv"%(case,simulationTime,it)
                
                df = pd.read_csv(pathSimple+fCSV)
                dtmp = df[df["module.src"]=="None"].groupby(['app','TOPO.src'])['id'].apply(list)
                print(dtmp)
                dr= getRbyApp(df,dtmp)
                
#                dC = pd.DataFrame(index=np.array(timeC).astype('datetime64[s]'))
#                dC["QTY"]=np.ones(len(timeC))
#                dC = dC.resample('10s').agg(dict(QTY='sum'))
#                messagesbyTime = dC.QTY.values
                
                dr.to_pickle(pathSimple+"dr_%s_%i.pkl"%(case,it))
#                np.save(pathSimple+"messagesbyTime_%s_%i.npy"%(case,it),messagesbyTime)

            
                
# =============================================================================
# =============================================================================
# #  GLOBAL VARIABLES
# =============================================================================
# =============================================================================
timeSimulation=1000000

pathEXP = "exp1/"
nsimulations = 1
#datestamp = time.strftime('%Y%m%d')
datestamp = "20190131"
pathSimple = pathEXP+"results_"+datestamp+"/"
case ="CQ"

resampleSize = 1000
tickGeneration =  range(int(timeSimulation/resampleSize / 2.),timeSimulation/resampleSize,int(timeSimulation/resampleSize / 2.0 /10.0))
    
drs = {}
color_sequence = ['#1f77b4', '#aec7e8', '#ff7f0e', '#ffbb78', '#2ca02c',
                  '#98df8a', '#d62728', '#ff9896', '#9467bd', '#c5b0d5',
                  '#8c564b', '#c49c94', '#e377c2', '#f7b6d2', '#7f7f7f',
                  '#c7c7c7', '#bcbd22', '#dbdb8d', '#17becf', '#9edae5']
                  
for it in range(nsimulations):
    fCSV = "Results_%s_%i_%i.csv"%(case,timeSimulation,it)    
    df = pd.read_csv(pathSimple+fCSV)
    dtmp = df[df["module.src"]=="None"].groupby(['app','TOPO.src'])['id'].apply(list)
   
    drs = {}
    ticks = 0
    maxValue= 0 
    for g in dtmp.keys():
        print(g)
        ids = dtmp[g]


        t = []
        intime = []
        for i in ids:
            dm = df[df.id == i]
            t.append(dm['time_reception'].max()- dm['time_emit'].min())
            intime.append(dm['time_emit'].min())

        dr = pd.DataFrame() 
        dr["time"] = t
        dr.index = np.array(intime).astype('datetime64[s]')
        dr = dr.resample('1000s').agg(dict(time='mean'))   
        maxValue=max(maxValue,dr.time.max())
        ticks = range(len(dr.time.values))
        drs[(g[0],g[1])] = dr.time.values
        print("-"*40)


    fig, ax = plt.subplots(figsize=(12.0,4.0))
    for i,k in enumerate(drs):
        ax.plot(ticks, drs[k],'-',alpha=1.,linewidth=2,label="S%i on '%i'"%(k[0],k[1]), color=color_sequence[i])       

    plt.text(tickGeneration[0]-110, maxValue-20, "Generation:", fontsize=12, color=color_sequence[-1])
    for i,xc in enumerate(tickGeneration):
        plt.axvline(x=xc,color=color_sequence[-1])
        xsep=15
        if i+1>=10: xsep+=10
        plt.text(xc-xsep, maxValue-20, i+1, fontsize=14, color=color_sequence[-1])
        
    ax.set_xlabel("Simulation Time ( simulation number %i)"%it, fontsize=12)
    ax.set_ylabel("Latency", fontsize=12)
    ax.tick_params(labelsize=10)
    ax.set_xlim(0,len(ticks))
    #ax.set_ylim(0,120)
    leg = ax.legend();
    #plt.legend([ax1,ax2,ax3],['Total num. of requests','Partition','ILP'],loc="upper right",fontsize=18)
    plt.legend(loc="upper left",fontsize=12)
    plt.tight_layout()

    #SUMMARIZATION TABLE   (an to latex) 
    listG = ["case","base (msg)","base (mean)","base (std)"]
    for i,xc in enumerate(tickGeneration):
        listG.append("G%i (msg)"%(i+1))
        listG.append("G%i (mean)"%(i+1))
        listG.append("G%i (std)"%(i+1))
          
    dlat = pd.DataFrame(columns=listG)
    ixloc = 0    
    for i,k in enumerate(drs):

        ds = pd.DataFrame() 
        ds["time"] = drs[k]
        msg,mean,std = [],[],[]

        inter = [0]+tickGeneration+[resampleSize]
        
        for gen in range(len(inter)-1):
#            print inter[gen],inter[gen+1]
            msg.append(len(ds.time[inter[gen]:inter[gen+1]]))
            mean.append(ds.time[inter[gen]:inter[gen+1]].mean())
            std.append(ds.time[inter[gen]:inter[gen+1]].std())
        
        row = ["S%i on '%i'"%(k[0],k[1])]
        for i in range((len(listG)-1)/3):
            row.append(msg[i])
            row.append(mean[i])
            row.append(std[i])
           
        dlat.loc[ixloc] = row
        ixloc +=1
#    print dlat.columns
#    print len(dlat.columns)
    print("MAIN METRICS")
    print(dlat.iloc[:,[0,2,5,32]])
    print("-"*30)
    
    with open(pathSimple+'mytable_%i.tex'%it,'w') as tf:
       tf.write(dlat.to_latex(index=False))
       
 