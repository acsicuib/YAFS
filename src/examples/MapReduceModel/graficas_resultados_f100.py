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
#TODO y-axys dimension  

#TODO Formatear numeros GRANDES
def autolabel(rects,hshift,scale=1.0,label=""):
    for rect in rects:
        h = rect.get_height()
        ax.text(rect.get_x()+rect.get_width()/2., 1.05*h+hshift,
                '%1.3f %s' % (int(h)/scale,label),
#                '%d'%int(h),
                ha='center', va='bottom', size=16)


def autolabel2(rects,hshift):
    for rect in rects:
        h = rect.get_height()
        ax.text(rect.get_x()+rect.get_width()/2., 1.05*h+hshift,
                '%2.f' % (int(h)),
#                '%d'%int(h),
                ha='center', va='bottom', size=16)


# pathResults = "resultsParte2.csv"
# pathResults = "resultsParte_f100.csv"



import argparse

parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument(
    '--work-dir',
    type=str,
    default="exp22/",
    help='Working directory')

parser.add_argument(
    '--simulations',
    type=int,
    default=5,
    help='Number of simulations')


args, pipeline_args = parser.parse_known_args()
pathExperimento = args.work_dir

nSimulations = args.simulations
pathResults = pathExperimento+"resultsParte_f100.csv"



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
        
            #rep      #rep.p     #single #cloud     #rnd     #rnd.p
colors = ["#F85A3E","#CBC544","#1A7AF8","#99194b","#3aa54b","#3a364b"]

N = 4 #bars: two series: s1 , s2
width = 0.2       # the width of the bars
# fn = range(20,220,20)
fn = range(100,301,20)

dr = pd.DataFrame()
dr["ffiles"]=[100]*11
dr["nnodes"]=fn
for metric in metrics:
    s1,s2,s3,s4 = {},{},{},{}
    s1b,s2b,s3b,s4b = {},{},{},{}
    ylabel = info_metrics[metric]
    
    print "METRICA %s --- %s" %(metric,ylabel)

    
#    for it in range(nSimulations):
    if True:
        it = 2
        #LOAD OF VALUES
        df = pd.read_csv(pathResults,sep=";",index_col=0,header=-1)
        df["t"],df["f"],df["n"] = df[2].str.split("-").str

#        s1[it] = df[df.t=="rep"].loc[metric][3] 
#        s2[it] = df[df.t=="sin"].loc[metric][3]
#        s3[it] = df[df.t=="cloud"].loc[metric][3]
#        s4[it] = df[df.t=="Fstrrep"].loc[metric][3]
        
        
        s1[it] = df[(df.t=="rep") & (df[1]==it)].loc[metric][3]
        s2[it] =  df[(df.t=="sin") & (df[1]==it)].loc[metric][3]
        s4[it] = df[(df.t=="Fstrrep") & (df[1]==it)].loc[metric][3]
        
        if metric == "totalLATrepclo":
            s1b[it] = df[(df.t=="rep")& (df[1]==it)].loc["totalLATrepcloSTD"][3]
            s2b[it] = df[(df.t=="sin")& (df[1]==it)].loc["totalLATrepcloSTD"][3]
            s4b[it] = df[(df.t=="Fstrrep")& (df[1]==it)].loc["totalLATrepcloSTD"][3]
       
        
    ss1,ss2,ss3,ss4 = defaultdict(list),defaultdict(list),defaultdict(list),defaultdict(list)
    ss1b,ss2b,ss3b,ss4b = defaultdict(list),defaultdict(list),defaultdict(list),defaultdict(list)
    s1m,s1std = np.array([]),np.array([])
    s2m,s2std = np.array([]),np.array([])
#    s3m,s3std = np.array([]),np.array([])
    s4m,s4std = np.array([]),np.array([])
#    s1m,s1std = np.array([]),np.array([])
#    s2m,s2std = np.array([]),np.array([])
#    s3m,s3std = np.array([]),np.array([])
#    s4m,s4std = np.array([]),np.array([])
    maxDD = -1;
    for value in range(len(fn)):

#        for it in range(nSimulations): 
        if True:
            it = 2        
            
            
            ss1[value].append(s1[it][value])
            ss2[value].append(s2[it][value]) 
#            ss3[value].append(s3[it][value]) 
            ss4[value].append(s4[it][value]) 
            if metric == "totalLATrepclo":
                ss1b[value].append(s1b[it][value])
                ss2b[value].append(s2b[it][value])
                ss4b[value].append(s4b[it][value])   

        s1m = np.append(s1m,np.array(ss1[value]).mean())
        s2m =np.append(s2m,np.array(ss2[value]).mean())
        s4m =np.append(s4m,np.array(ss4[value]).mean())

        if metric == "totalLATrepclo":
            #CASO A - usar STD de varias simulaciones
#            s1std = np.append(s1std,np.array(ss1b[value]).mean())
#            s2std = np.append(s2std,np.array(ss2b[value]).mean())
#            s4std = np.append(s4std,np.array(ss4b[value]).mean())
            
            #CASO B - usar la media de las medias 
            
            s1std = np.append(s1std,np.array(ss1[value]).std())
            s2std = np.append(s2std,np.array(ss2[value]).std())
            s4std = np.append(s4std,np.array(ss4[value]).std())
            
            
        else:
            s1std = np.append(s1std,np.array(ss1[value]).std())
            s2std = np.append(s2std,np.array(ss2[value]).std())
            s4std = np.append(s4std,np.array(ss4[value]).std())
            
            
    maxi =  max(s1std.max(),s2std.max(),s4std.max())  
    if maxi > maxDD:
       maxDD = maxi
            
    dr[metric]=s4m/s1m
    
    if len(ss1)!=len(ss2): print "ERROR! - Series with different sizes" #END?
    
    ind = np.arange(len(ss1))  # the x locations for the groups

    fig = plt.figure(figsize=(20, 5))
    ax = fig.add_subplot(111)
#    ax.yaxis.set_major_formatter(ScalarFormatter())
    separationBetweenMultiBars=1.15

    ticksvals = fn


#    s1std = 0
#    s2std = 0
#    s3std = 0
#    s4std = 0

    rects1 = ax.bar(ind, s1m,yerr=s1std, width=width, color="#F85A3E")

    if metric == "totalMSG" or metric == "totalMSGsrcrep" :
        rects13 = ax.bar(ind, s1m/3.0, width, color='#CBC544')
        

#    rects3 = ax.bar(ind+width*2, s3m,yerr=s3std, width=width, color=colors[3])   #cloud

    if metric == "totalMSG" or metric == "totalMSGsrcrep" :
        rects4 = ax.bar(ind+width, s4m,yerr=s4std, width=width, color=colors[4])  #rnd
        rects41 = ax.bar(ind+width, s4m/3.0, width, color=colors[5])                  

    else:
        rects4 = ax.bar(ind+width, s4m,yerr=s4std, width=width, color=colors[4])  #rnd

#    if metric == "totalMSG" or metric == "totalMSGsrcrep" :
    rects2 = ax.bar(ind+width*2, s2m,yerr=s2std, width=width, color="#1A7AF8") # single-file
#    else:
#        rects2 = ax.bar(ind+width*2, s2m,yerr=s2std, width=width, color="#1A7AF8") # single-file
                        
    maxDD = 0.0                  
    if maxDD ==0.0:
        ax.set_xlabel('# devices for the experiment',size=22)            
    else:                        
        ax.set_xlabel('# devices for the experiment (max. deviation:'+'{:e}'.format(float(maxDD))+')',size=22)            
                      

    ax.set_ylabel(ylabel,size=22)                
    
    ax.set_xticks(ind+(width*1.5))
    ax.set_xticklabels( ticksvals )
        
#    ax.legend( (rects1[0], rects2[0]), ('replica-aware', 'single-file'), fontsize=18,  ) #loc='lower right'
            
#    if metric == "totalMSG" or metric == "totalMSGsrcrep":
#        ax.legend( (rects1[0], rects13[0], rects2[0], rects3[0], rects4[0], rects41[0]), ('replica-aware', 'replica-aware (avg. per replica)','single-file','only-cloud','fogstore','fogstore (avg. per replica)'), fontsize=16, ncol=2   ) #loc='lower right'
#    elif metric == "totalLATrepclo":
##        ax.legend( (rects1[0], rects2[0]), ('replica-aware', 'single-file','cloud','random'), fontsize=18)
#        ax.legend( (rects1[0], rects2[0],rects3[0],rects4[0]), ('replica-aware', 'single-file','only-cloud-file','fogstore'),fontsize=16,  loc='lower right',ncol=6,framealpha=0.95)
##        ax.set_ylim(0,180)
#
#    else:
#        ax.legend( (rects1[0], rects2[0],rects3[0],rects4[0]), ('replica-aware', 'single-file','only-cloud','fogstore'),fontsize=16,  loc='upper left',ncol=6,framealpha=0.95)
#        
#    
                
    if metric == "totalMSG" or metric == "totalMSGsrcrep" :#or metric == "totalLATrepclo":
        ax.legend( (rects1[0], rects13[0],  rects4[0], rects41[0],rects2[0]), ('replica-aware', 'replica-aware (avg. per replica)','fogstore','fogstore (avg. per replica)','single-file'), fontsize=16, ncol=2   ) #loc='lower right'
#    elif :
#        ax.legend( (rects1[0], rects2[0]), ('replica-aware', 'single-file','cloud','random'), fontsize=18)
#        ax.legend( (rects1[0], rects4[0],rects2[0]), ('replica-aware', 'fogstore','single-file',),fontsize=16,  loc='lower right',ncol=6,framealpha=0.95)
#        ax.set_ylim(0,180)

    else:
        ax.legend( (rects1[0], rects4[0],rects2[0]), ('replica-aware', 'fogstore','single-file',),fontsize=16,  loc='upper left',ncol=6,framealpha=0.95)
        
    
    
    
    ax.grid()
            
    plt.savefig(pathExperimento+"/metric_%s-n.pdf"%metric)
    plt.show()
        
    
    
#####
# FIGURA: R.LAT.MAX, R.LAT.MIN, S.LAT.(MIN==MAX)
#####
# FIGURA: R.LAT.MAX, R.LAT.MIN, S.LAT.(MIN==MAX)

N = 6 #bars: two series: s1 , s2
width = 0.14       # the width of the bars
# fn = range(20,220,20)
fn = range(100,301,20)
ylabel = "latency (ms)"
s1,s2,s3,s4,s5,s6 = {},{},{},{},{},{}
s1b,s2b,s3b,s4b,s5b,s6b = {},{},{},{},{},{}

s1m, s1std = np.array([]), np.array([])
s2m, s2std = np.array([]), np.array([])
s3m, s3std = np.array([]), np.array([])
s4m, s4std = np.array([]), np.array([])
s5m, s5std = np.array([]), np.array([])
s6m, s6std = np.array([]), np.array([])
s1b,s2b,s3b,s4b,s5b,s6b = {},{},{},{},{},{}


for it in range(nSimulations):
    #LOAD OF VALUES
    df = pd.read_csv(pathResults,sep=";",index_col=0,header=-1)
    df["t"],df["f"],df["n"] = df[2].str.split("-").str

#    s1[it] = df[df.t=="rep"].loc[metric][3] 
#    s2[it] = df[df.t=="sin"].loc[metric][3]
#    s3[it] = df[df.t=="cloud"].loc[metric][3]
#    s4[it] = df[df.t=="Fstrrep"].loc[metric][3]

#    s1[it] = df[df.t=="rep"].loc["totalLATmin"][3]
#    s2[it] = df[df.t=="rep"].loc["totalLATmax"][3]
#    s3[it] = df[df.t=="sin"].loc["totalLATmin"][3]
#    s4[it] = df[df.t=="cloud"].loc["totalLATmin"][3] 
#    s5[it] = df[df.t=="Fstrrep"].loc["totalLATmin"][3]
#    s6[it] = df[df.t=="Fstrrep"].loc["totalLATmax"][3]
    
    
    s1[it] = df[(df.t=="rep") & (df[1]==it)].loc["totalLATmin"][3]
    s2[it] =  df[(df.t=="rep") & (df[1]==it)].loc["totalLATmax"][3]

    s1b[it] =  df[(df.t=="rep") & (df[1]==it)].loc["totalLATminSTD"][3]
    s2b[it] = df[(df.t=="rep") & (df[1]==it)].loc["totalLATmaxSTD"][3]

    s3[it] =  df[(df.t=="sin") & (df[1]==it)].loc["totalLATmin"][3]
    s3b[it] = df[(df.t=="sin") & (df[1]==it)].loc["totalLATminSTD"][3]

#    s4[it] = df[df.t=="cloud"].loc["totalLATmin"][3]

    s5[it] = df[(df.t=="Fstrrep") & (df[1]==it)].loc["totalLATmin"][3]
    s6[it] =  df[(df.t=="Fstrrep") & (df[1]==it)].loc["totalLATmax"][3]

    s5b[it] =  df[(df.t=="Fstrrep") & (df[1]==it)].loc["totalLATminSTD"][3]
    s6b[it] =  df[(df.t=="Fstrrep") & (df[1]==it)].loc["totalLATmaxSTD"][3]
    
    


ss1,ss2,ss3,ss4,ss5,ss5,ss6 = defaultdict(list),defaultdict(list),defaultdict(list),defaultdict(list),defaultdict(list),defaultdict(list),defaultdict(list)
ss1b,ss2b,ss3b,ss4b,ss5b,ss5b,ss6b = defaultdict(list),defaultdict(list),defaultdict(list),defaultdict(list),defaultdict(list),defaultdict(list),defaultdict(list)
s1m,s1std = np.array([]),np.array([])
s2m,s2std = np.array([]),np.array([])
s3m,s3std = np.array([]),np.array([])
s4m,s4std = np.array([]),np.array([])
s5m,s5std = np.array([]),np.array([])
s6m,s6std = np.array([]),np.array([])
maxDD = -1;


for value in range(len(fn)):
    print value
    for it in range(nSimulations):    
        print it
        ss1[value].append(s1[it][value])
        print ss1
        
        ss2[value].append(s2[it][value]) 
        ss3[value].append(s3[it][value]) 
#        ss4[value].append(s4[it][value])
        ss5[value].append(s5[it][value])
        ss6[value].append(s6[it][value])
        
        ss1b[value].append(s1b[it][value])
        ss1b[value].append(s1b[it][value])
        ss2b[value].append(s2b[it][value]) 
        ss3b[value].append(s3b[it][value]) 
#        ss4b[value].append(s4b[it][value])
        ss5b[value].append(s5b[it][value])
        ss6b[value].append(s6b[it][value])
        
    s1m = np.append(s1m,np.array(ss1[value]).mean())
    s2m = np.append(s2m,np.array(ss2[value]).mean())
    s3m = np.append(s3m,np.array(ss3[value]).mean())
    s5m = np.append(s5m,np.array(ss5[value]).mean())
    s6m = np.append(s6m,np.array(ss6[value]).mean())
    #CASO A

#    s1std = np.append(s1std,np.array(ss1b[value]).mean())
#    s2std = np.append(s2std,np.array(ss2b[value]).mean())
#    s3std = np.append(s3std,np.array(ss3b[value]).mean())
#    s5std = np.append(s5std,np.array(ss5b[value]).mean())
#    s6std = np.append(s6std,np.array(ss6b[value]).mean())

    #CASO B

    s1std = np.append(s1std,np.array(s1m[value]).std())
    s2std = np.append(s2std,np.array(s2m[value]).std())
    s3std = np.append(s3std,np.array(s3m[value]).std())
    s5std = np.append(s5std,np.array(s5m[value]).std())
    s6std = np.append(s6std,np.array(s6m[value]).std())
    
    maxi =  max(s1std.max(),s2std.max(),s3std.max(),s5std.max(),s6std.max())  
    if maxi > maxDD:
        maxDD = maxi
        
        
dr["latMin"]=s5m/s1m
dr["latMax"]=s6m/s2m

#    slatMAX = df[df.t=="sin"].loc["totalLATmax"][2]

if len(s1m)!=len(s2m): print "ERROR! - Series with different sizes" #END?
if len(s1m)!=len(s3m): print "ERROR! - Series with different sizes" #END?
if len(s1m)!=len(s4m): print "ERROR! - Series with different sizes" #END?
if len(s1m)!=len(s5m): print "ERROR! - Series with different sizes" #END?
if len(s1m)!=len(s6m): print "ERROR! - Series with different sizes" #END?

ind = np.arange(len(ss1))  # the x locations for the groups


#TODO MODIFICAR EN CUANTO HAYA MAS SIMULACIONES
# s1std = s1m/4.0
# s2std = s2m/4.0
# s3std = s3m/4.0
# s4std = s4m/4.0
# s5std = s5m/4.0
# s6std = s6m/4.0

separationBetweenMultiBars=1.15
ticksvals = fn

fig = plt.figure(figsize=(20, 5))
ax = fig.add_subplot(111)

rects1 = ax.bar(ind, s1m, yerr=s1std, width=width, color='#fdd5ce')
                
rects2 = ax.bar(ind+width, s2m, yerr=s2std, width=width, color='#F85A3E') #CB523A

#rects4 = ax.bar(ind+width*3, s4m, yerr=s4std, width=width, color=colors[3])
rects5 = ax.bar(ind+width*2, s5m, yerr=s5std, width=width, color='#b5e3bd')
rects6 = ax.bar(ind+width*3, s6m, yerr=s6std, width=width, color=colors[4])

rects3 = ax.bar(ind+width*4, s3m, yerr=s3std, width=width, color='#1A7AF8')
                
#ax.set_xlabel('# devices for the experiment',size=22)     
              
maxDD = 0                  
if maxDD ==0.0:
        ax.set_xlabel('# devices for the experiment',size=22)            
else:                        
        ax.set_xlabel('# devices for the experiment (max. deviation:'+'{:e}'.format(float(maxDD))+')',size=22)            
                      


ax.set_ylabel(ylabel,size=22)                

ax.set_xticks(ind+(width*1.5))
ax.set_xticklabels( ticksvals )
    
ax.legend( (rects1[0], rects2[0],rects5[0],rects6[0],rects3[0]), ('replica-aware min', 'replica-aware max','fogstore min','fogstore max','single-file'), fontsize=16,  loc='lower right',ncol=6,framealpha=0.95)
ax.grid()        
plt.savefig(pathExperimento+"metric_latminmax-n.pdf")
plt.show()

#N = 6 #bars: two series: s1 , s2
#width = 0.14       # the width of the bars
#fn = range(20,220,20)
#ylabel = "latency (ms)"
#
#s1= df[df.t=="rep"].loc["totalLATmin"][2]
#s2 = df[df.t=="rep"].loc["totalLATmax"][2]
#s3 = df[df.t=="sin"].loc["totalLATmin"][2]
#s4 = df[df.t=="cloud"].loc["totalLATmin"][2]
#s5 = df[df.t=="rep"].loc["totalLATmin"][2]
#s6 = df[df.t=="rep"].loc["totalLATmax"][2]
#
#
#s5s = df[df.t=="rep"].loc["totalLATminSTD"][2]
#s6s = df[df.t=="rep"].loc["totalLATmaxSTD"][2]
#
##    slatMAX = df[df.t=="sin"].loc["totalLATmax"][2]
#
#if len(s1)!=len(s2): print "ERROR! - Series with different sizes" #END?
#
#ind = np.arange(len(s1))  # the x locations for the groups
#
#fig = plt.figure(figsize=(20, 5))
#ax = fig.add_subplot(111)
#
#separationBetweenMultiBars=1.15
#
#ticksvals = fn
#rects1 = ax.bar(ind, s1, width, color='#fdd5ce')
#rects2 = ax.bar(ind+width, s2, width, color='#F85A3E') #CB523A
#rects3 = ax.bar(ind+width*2, s3, width, color='#1A7AF8')
#rects4 = ax.bar(ind+width*3, s4, width, color=colors[3])
#rects5 = ax.bar(ind+width*4, s5, width, color='#b5e3bd')
#rects6 = ax.bar(ind+width*5, s6, width, color=colors[4])
#
#
#ax.set_xlabel('# devices for the experiment',size=22)            
#ax.set_ylabel(ylabel,size=22)                
#
#ax.set_xticks(ind+width*2.5)
#ax.set_xticklabels( ticksvals )
#    
#ax.legend( (rects1[0], rects2[0],rects3[0],rects4[0],rects5[0],rects6[0]), ('replica-aware min', 'replica-aware max','single-file','cloud','random min','random max'), fontsize=18,  loc='upper right')
#ax.grid()
#       
#plt.savefig("figures/metric_latminmax-n.pdf")
#plt.show()
#
#
#  
dr.loc['mean'] = dr.mean()
dr.to_csv(pathExperimento+"aceleracion-f100.csv" ,float_format='%0.3f')    
with open(pathExperimento+"aceleracion-f100-latex.txt","w") as f:
    f.write(dr.to_latex(float_format='%0.3f'))