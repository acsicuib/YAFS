#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 19 11:44:17 2018

@author: isaaclera
"""
import matplotlib
matplotlib.use('agg')
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from collections import defaultdict
from matplotlib.ticker import ScalarFormatter


def autolabel(rects,hshift,scale=1.0,label=""):
    for rect in rects:
        h = rect.get_height()
        ax.text(rect.get_x()+rect.get_width()/2., 1.05*h+hshift,
                '%1.0f %s' % (int(h)/scale,label),
#                '%d'%int(h),
                ha='center', va='bottom', size=16)


def autolabel2(rects,hshift):
    for rect in rects:
        h = rect.get_height()
        ax.text(rect.get_x()+rect.get_width()/2., 1.05*h+hshift,
                '%2.f' % (int(h)),
#                '%d'%int(h),
                ha='center', va='bottom', size=16)


def autolabel3(rects,hshift,scale=1.0,label=""):
    for rect in rects:
        h = rect.get_height()
        ax.text(rect.get_x()+rect.get_width()/2., 1.05*h+hshift,
                '%1.2f %s' % (int(h)/scale,label),
#                '%d'%int(h),
                ha='center', va='bottom', size=16)



##GETTING SERIES (ALL VARIABLES) FOR DEBUG
#Note that values are ordered by inserts in csv files (good)
#rtmsg= df[df.t=="rep"].loc["totalMSG"][2] 
#stmsg= df[df.t=="sin"].loc["totalMSG"][2]
#
#rtmsgSRCREP = df[df.t=="rep"].loc["totalMSGsrcrep"][2]
#stmsgSRCREP = df[df.t=="sin"].loc["totalMSGsrcrep"][2]
#
#rtmsgREPCLO = df[df.t=="rep"].loc["totalMSGrepclo"][2]
#stmsgREPCLO = df[df.t=="sin"].loc["totalMSGrepclo"][2]
#
#rlatMIN= df[df.t=="rep"].loc["totalLATmin"][2]
#rlatMAX = df[df.t=="rep"].loc["totalLATmax"][2]
#
#slatMIN = df[df.t=="sin"].loc["totalLATmin"][2]
#slatMAX = df[df.t=="sin"].loc["totalLATmax"][2]
####


#metrics = ["totalMSG","totalMSGsrcrep","totalMSGrepclo","totalLATrepclo"]
metrics = ["totalMSG","totalMSGsrcrep","totalMSGrepclo","totalLATrepclo","totalLATmin","totalLATmax"]
metrics = ["totalMSGsrcrep","totalMSGrepclo","totalLATrepclo"]#,"totalMSGsrcrep","totalMSGrepclo","totalLATrepclo","totalLATmin","totalLATmax"]

#tuple: yLabel, 
info_metrics = {"totalMSG":("# transmitted packets (NO)"), 
           "totalMSGsrcrep":("# transmitted packets"),
           "totalMSGrepclo":("# transmitted packets"),
           "totalLATrepclo":("latency (ms)"),
           "totalLATmin":("Latency min. (ms)"), #TEST
           "totalLATmax":("Latency max. (ms)"),     #TEST  
        }

# pathResults = "resultsParte_n50.csv"

import argparse

parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument(
    '--work-dir',
    type=str,
    default="",
    help='Working directory')

args, pipeline_args = parser.parse_known_args()
pathExperimento = args.work_dir
pathResults = pathExperimento+"resultsParte_n50.csv"


#rep      #rep.p     #single #cloud     #rnd     #rnd.p
colors = ["#F85A3E","#CBC544","#1A7AF8","#99194b","#3aa54b","#3a364b"]
N = 4 #bars: two series: s1 , s2
width = 0.2       # the width of the bars
fs = range(10,110,10)
nSimulations = 1

for metric in metrics:
    s1,s2,s3,s4 = {},{},{},{}
    ylabel = info_metrics[metric]
    
    print "METRICA %s --- %s" %(metric,ylabel)
    
    for it in range(nSimulations):
        #LOAD OF VALUES
        df = pd.read_csv(pathResults,sep=";",index_col=0,header=-1)
        df["t"],df["f"],df["n"] = df[2].str.split("-").str

        s1[it] = df[df.t=="rep"].loc[metric][3] 
        s2[it] = df[df.t=="sin"].loc[metric][3]
        s3[it] = df[df.t=="cloud"].loc[metric][3]
        s4[it] = df[df.t=="Fstrrep"].loc[metric][3]
    
    ss1,ss2,ss3,ss4 = defaultdict(list),defaultdict(list),defaultdict(list),defaultdict(list)
    s1m,s1std = np.array([]),np.array([])
    s2m,s2std = np.array([]),np.array([])
    s3m,s3std = np.array([]),np.array([])
    s4m,s4std = np.array([]),np.array([])
    for value in range(len(fs)):
        for it in range(nSimulations):    
            ss1[value].append(s1[it][value])
            ss2[value].append(s2[it][value]) 
            ss3[value].append(s3[it][value]) 
            ss4[value].append(s4[it][value]) 
            
        s1m = np.append(s1m,np.array(ss1[value]).mean())
        s1std = np.append(s1std,np.array(ss1[value]).std())
        
        s2m =np.append(s2m,np.array(ss2[value]).mean())
        s2std = np.append(s2std,np.array(ss2[value]).std())

        s3m =np.append(s3m,np.array(ss3[value]).mean())
        s3std = np.append(s3std,np.array(ss3[value]).std())

        s4m =np.append(s4m,np.array(ss4[value]).mean())
        s4std = np.append(s4std,np.array(ss4[value]).std())

#
#        s2m.append(np.array(ss2[value]).mean())
#        s2std.append(np.array(ss2[value]).std())
#        s3m.append(np.array(ss2[value]).mean())
#        s3std.append(np.array(ss2[value]).std())
#        s4m.append(np.array(ss4[value]).mean())
#        s4std.append(np.array(ss4[value]).std())

            
    if len(s1m)!=len(s2m): print "ERROR! - Series with different sizes" #END?
    
    ind = np.arange(len(s1m))  # the x locations for the groups

    fig = plt.figure(figsize=(20, 5))
    ax = fig.add_subplot(111)

    separationBetweenMultiBars=1.15

    ticksvals = fs

    #TODO MODIFICAR EN CUANTO HAYA MAS SIMULACIONES
    
    s1std = s1m/4.0
    s2std = s2m/4.0
    s3std = s3m/4.0
    s4std = s4m/4.0

    rects1 = ax.bar(ind, s1m,yerr=s1std, width=width, color=colors[0])

    if metric == "totalMSG" or metric == "totalMSGsrcrep" :
        rects13 = ax.bar(ind, s1m/3.0, width, color=colors[1])
                         
    rects2 = ax.bar(ind+width, s2m,yerr=s2std, width=width, color=colors[2])
    rects3 = ax.bar(ind+width*2, s3m,yerr=s3std, width=width, color=colors[3])   #cloud
    rects4 = ax.bar(ind+width*3, s4m,yerr=s4std, width=width, color=colors[4])  #rnd

    if metric == "totalMSG" or metric == "totalMSGsrcrep" :
        rects41 = ax.bar(ind+width*3, s4m/3.0, width, color=colors[5])#rnd
                         
    ax.set_xlabel('# files for the experiment',size=22)            
    ax.set_ylabel(ylabel,size=22)                
    
    ax.set_xticks(ind+(width*1.5))
    ax.set_xticklabels( ticksvals )
        
    if metric == "totalMSG" or metric == "totalMSGsrcrep":
        ax.legend( (rects1[0], rects13[0], rects2[0],rects3[0],rects4[0],rects41[0]),('replica-aware', 'replica-aware (avg. per replica)','single-file','only-cloud','fogstore','fogstore (avg. per replica)'), fontsize=16, ncol=2 ) #loc='lower right'
    elif metric == "totalLATrepclo":
        ax.legend( (rects1[0], rects2[0],rects3[0],rects4[0]), ('replica-aware', 'single-file','only-cloud','fogstore'),fontsize=16,  loc='upper left',ncol=6,framealpha=0.95)
    else:
        ax.legend( (rects1[0], rects2[0],rects3[0],rects4[0]), ('replica-aware', 'single-file','only-cloud','fogstore'), fontsize=16,  loc='upper left',ncol=6,framealpha=0.95)
            
    scale =1.0
    label =""
    ax.grid()
#    if metric == "totalMSG" or metric == "totalMSGsrcrep":
#        scale =1.0 
#        autolabel(rects1,0,scale,label)
#        autolabel(rects2,0,scale,label)
#
#    if metric == "totalMSGrepclo":
#        scale = 1.0
#        autolabel(rects1,0,scale,label)
#        autolabel(rects2,0,scale,label)
#        ax.set_ylim(0,50000)
  
#    if metric == "totalLATrepclo":
#        scale = 1.0
#        autolabel3(rects1,0,scale,label)
#        autolabel3(rects2,0,scale,label)
#        

            
    plt.savefig(pathExperimento+"metric_%s-f.pdf"%metric)
    plt.show()
        
    
    
#####
# FIGURA: R.LAT.MAX, R.LAT.MIN, S.LAT.(MIN==MAX)

N = 6 #bars: two series: s1 , s2
width = 0.14       # the width of the bars
fs = range(10,110,10)
ylabel = "latency (ms)"
s1,s2,s3,s4,s5,s6 = {},{},{},{},{},{}


for it in range(nSimulations):
    #LOAD OF VALUES
    df = pd.read_csv(pathResults,sep=";",index_col=0,header=-1)
    df["t"],df["f"],df["n"] = df[2].str.split("-").str

#    s1[it] = df[df.t=="rep"].loc[metric][3] 
#    s2[it] = df[df.t=="sin"].loc[metric][3]
#    s3[it] = df[df.t=="cloud"].loc[metric][3]
#    s4[it] = df[df.t=="Fstrrep"].loc[metric][3]

    s1[it] = df[df.t=="rep"].loc["totalLATmin"][3]
    s2[it] = df[df.t=="rep"].loc["totalLATmax"][3]
    s3[it] = df[df.t=="sin"].loc["totalLATmin"][3]
    s4[it] = df[df.t=="cloud"].loc["totalLATmin"][3]
    s5[it] = df[df.t=="Fstrrep"].loc["totalLATmin"][3]
    s6[it] = df[df.t=="Fstrrep"].loc["totalLATmax"][3]


    ss1,ss2,ss3,ss4,ss5,ss5,ss6 = defaultdict(list),defaultdict(list),defaultdict(list),defaultdict(list),defaultdict(list),defaultdict(list),defaultdict(list)
    s1m,s1std = np.array([]),np.array([])
    s2m,s2std = np.array([]),np.array([])
    s3m,s3std = np.array([]),np.array([])
    s4m,s4std = np.array([]),np.array([])
    s5m,s5std = np.array([]),np.array([])
    s6m,s6std = np.array([]),np.array([])
    for value in range(len(fs)):
        for it in range(nSimulations):    
            ss1[value].append(s1[it][value])
            ss2[value].append(s2[it][value]) 
            ss3[value].append(s3[it][value]) 
            ss4[value].append(s4[it][value])
            ss5[value].append(s5[it][value])
            ss6[value].append(s6[it][value])
            
        s1m = np.append(s1m,np.array(ss1[value]).mean())
        s1std = np.append(s1std,np.array(ss1[value]).std())
        
        s2m =np.append(s2m,np.array(ss2[value]).mean())
        s2std = np.append(s2std,np.array(ss2[value]).std())
    
        s3m =np.append(s3m,np.array(ss3[value]).mean())
        s3std = np.append(s3std,np.array(ss3[value]).std())
    
        s4m =np.append(s4m,np.array(ss4[value]).mean())
        s4std = np.append(s4std,np.array(ss4[value]).std())
        
        s5m =np.append(s5m,np.array(ss5[value]).mean())
        s5std = np.append(s5std,np.array(ss5[value]).std())
        
        s6m =np.append(s6m,np.array(ss6[value]).mean())
        s6std = np.append(s6std,np.array(ss6[value]).std())


#    slatMAX = df[df.t=="sin"].loc["totalLATmax"][2]

if len(ss1)!=len(ss2): print "ERROR! - Series with different sizes" #END?

ind = np.arange(len(ss1))  # the x locations for the groups


#TODO MODIFICAR EN CUANTO HAYA MAS SIMULACIONES
s1std = s1m/4.0
s2std = s2m/4.0
s3std = s3m/4.0
s4std = s4m/4.0
s5std = s5m/4.0
s6std = s6m/4.0

fig = plt.figure(figsize=(20, 5))
ax = fig.add_subplot(111)

separationBetweenMultiBars=1.15

ticksvals = fs




rects1 = ax.bar(ind, s1m, yerr=s1std, width=width, color='#fdd5ce')
rects2 = ax.bar(ind+width, s2m, yerr=s2std, width=width, color='#F85A3E') #CB523A
rects3 = ax.bar(ind+width*2, s3m, yerr=s3std, width=width, color='#1A7AF8')
rects4 = ax.bar(ind+width*3, s4m, yerr=s4std, width=width, color=colors[3])
rects5 = ax.bar(ind+width*4, s5m, yerr=s5std, width=width, color='#b5e3bd')
rects6 = ax.bar(ind+width*5, s6m, yerr=s6std, width=width, color=colors[4])
                
ax.set_xlabel('# files for the experiment',size=22)            
ax.set_ylabel(ylabel,size=22)                

ax.set_xticks(ind+(width*1.5))
ax.set_xticklabels( ticksvals )
    
ax.legend( (rects1[0], rects2[0],rects3[0],rects4[0],rects5[0],rects6[0]), ('replica-aware min', 'replica-aware max','single-file','only-cloud','fogstore min','fogstore max'), fontsize=16,  loc='lower right',ncol=6,framealpha=0.95)

#plt.legend(flip(handles, 2), flip(labels, 2), loc=9, ncol=2)
ax.grid()

        
plt.savefig(pathExperimento+"metric_latminmax-f.pdf")
plt.show()

#
#
#### TEST?
##N = 2 #bars: two series: s1 , s2
##width = 0.2       # the width of the bars
##fs = range(10,110,10)
##ylabel = "MIN Y MAX DE SINGLEFILE"
##
##s1 = df[df.t=="sin"].loc["totalLATmin"][2]
##s2 = df[df.t=="sin"].loc["totalLATmax"][2]
##
###    s1 = df[df.t=="rep"].loc[metric][2] 
###    s2 = df[df.t=="sin"].loc[metric][2]
##
##if len(s1)!=len(s2): print "ERROR! - Series with different sizes" #END?
##
##ind = np.arange(len(s1))  # the x locations for the groups
##
##fig = plt.figure(figsize=(20, 5))
##ax = fig.add_subplot(111)
###    ax.yaxis.set_major_formatter(ScalarFormatter())
##separationBetweenMultiBars=1.15
##
##ticksvals = fs
##rects1 = ax.bar(ind, s1, width, color='#F85A3E')
##rects2 = ax.bar(ind+width*separationBetweenMultiBars, s2, width, color='#1A7AF8')
## 
##ax.set_xlabel('# files',size=22)            
##ax.set_ylabel(ylabel,size=22)                
##
##ax.set_xticks(ind+width)
##ax.set_xticklabels( ticksvals )
##    
##ax.legend( (rects1[0], rects2[0]), ('single-min', 'single-max'), fontsize=18,  ) #loc='lower right'
##        
###plt.savefig("figures/metric_%s.pdf"%metric)
##plt.show()
##        
#    