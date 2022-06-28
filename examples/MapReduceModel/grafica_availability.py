#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 19 11:44:17 2018

@author: isaaclera
"""
import matplotlib
matplotlib.use('agg')


import csv

def autolabel2(rects,hshift,a,b):
    i = 0
    for rect in rects:
        h = rect.get_height()
        ax.text(rect.get_x()+rect.get_width()/2., 1.05*h+hshift, '%.0f'%float(float(a[i])*100.00/float(b[i]))+"%",ha='center', va='bottom', size=12)
        i = i + 1
        
        
def autolabel(rects,hshift):
    for rect in rects:
        h = rect.get_height()
        ax.text(rect.get_x()+rect.get_width()/2., 1.05*h+hshift, '%d'%int(h),
                ha='center', va='bottom', size=14)

        
# folder_='jsonmodelNew'

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


filename_ = pathExperimento+"results.csv"

#rep      #rep.p     #single #cloud     #rnd     #rnd.p
colors = ["#F85A3E","#CBC544","#1A7AF8","#99194b","#3aa54b","#3a364b"]
          
for variableSizeOf in ['-n','-f']:
    for metric_ in ['availabilitySensorWrites','availabilityCloudReads']:

        #variableSizeOf='-n'
        #variableSizeOf='-f'
        
        #metric_ = 'availabilitySensorWrites'
        #metric_ = 'availabilityCloudReads'
        singleValue = {}
        replicaValue= {}
        cloudValue= {}
        rndValue= {}
        

        
#        if variableSizeOf=='-f':
#            filename_  = './jsonmodel/results1bueno.csv'
#         
#        if variableSizeOf=='-n':
#            filename_  = './jsonmodel/results2bueno.csv'
#         filename_  = './'+folder_+'/results.csv'

        fn = range(100,201,10)
        nn = range(100,301,20)

        with open(filename_) as File:  
            reader = csv.reader(File,delimiter=';')
            for row in reader:
#                print row
                if row[0]==metric_: 
                    serie_,files_,nodes_ = row[1].split("-")
                    if serie_=='Replica':
                        if variableSizeOf=='-f':
                            if int(files_[1:]) in fn:
                                replicaValue[int(files_[1:])]=int(row[2])
                        if variableSizeOf=='-n':
                            if int(nodes_[1:]) in nn:
                                replicaValue[int(nodes_[1:])]=int(row[2])
                    if serie_=='Single':
                        if variableSizeOf=='-f':
                            if int(files_[1:]) in fn:
                                singleValue[int(files_[1:])]=int(row[2])
                        if variableSizeOf=='-n':
                            if int(nodes_[1:]) in nn:
                                singleValue[int(nodes_[1:])]=int(row[2])
                    if serie_=='Cloud':
                        if variableSizeOf=='-f':
                            if int(files_[1:]) in fn:
                                cloudValue[int(files_[1:])]=int(row[2])
                        if variableSizeOf=='-n':
                            if int(nodes_[1:]) in nn:
                                cloudValue[int(nodes_[1:])]=int(row[2])
                    if serie_=='FstrRep':
                        if variableSizeOf=='-f':
                            if int(files_[1:]) in fn:
                                rndValue[int(files_[1:])]=int(row[2])
                        if variableSizeOf=='-n':
                            if int(nodes_[1:]) in nn:
                                rndValue[int(nodes_[1:])]=int(row[2])

        
        singleList = sorted(singleValue.items(), key=lambda x: x[0], reverse=False)
        replicaList = sorted(replicaValue.items(), key=lambda x: x[0], reverse=False)
        rndList = sorted(rndValue.items(), key=lambda x: x[0], reverse=False)
        cloudList = sorted(cloudValue.items(), key=lambda x: x[0], reverse=False)
        
        
        yvals=list()
        zvals,cvals=list(),list()
        kvals=list()
        rvals=list()
        ticksvals=list()
        for i in replicaList:
            yvals.append(i[1])
            ticksvals.append(i[0])
            if variableSizeOf=='-f':
                kvals.append(i[0])
            if variableSizeOf=='-n':
                kvals.append(int(files_[1:]))
        for i in singleList:
            zvals.append(i[1])
        for i in cloudList:
            cvals.append(i[1])
        for i in rndList:
            rvals.append(i[1])
                
        
        import numpy as np
        import matplotlib.pyplot as plt
        
        N = 3
        ind = np.arange(len(kvals))  # the x locations for the groups
        width = 0.12       # the width of the bars
        
        fig = plt.figure(figsize=(20, 5))
        ax = fig.add_subplot(111)
        
        separationBetweenMultiBars=1.15
        
        #yvals = [4, 9, 2]
        rects1 = ax.bar(ind, yvals, width, color='#F85A3E') #replica
        #zvals = [1,2,3]
        rects2 = ax.bar(ind+width*separationBetweenMultiBars, zvals, width, color='#1A7AF8') #single
        #kvals = [11,12,13]
                     
        rects3 = ax.bar(ind+width*2*separationBetweenMultiBars, cvals, width, color=colors[3]) #cloud
        rects4 = ax.bar(ind+width*3*separationBetweenMultiBars, rvals, width, color=colors[4]) #rnd
        rects5 = ax.bar(ind+width*4*separationBetweenMultiBars, kvals, width, color='#CBC544')#total

        
        if metric_ == 'availabilityCloudReads':
            ax.set_ylim([0,129])
        if metric_ == 'availabilitySensorWrites':
            ax.set_ylim([0,119])
        if metric_ == 'availabilityCloudReads':
            ax.set_ylabel('# available files for reading',size=22)
        if metric_ == 'availabilitySensorWrites':
            ax.set_ylabel('# available files for writing',size=22)
        
        if variableSizeOf=='-f':
            ax.set_xlabel('# files for the experiment',size=22)
        if variableSizeOf=='-n':
            ax.set_xlabel('# devices for the experiment',size=22)            
        
        ax.set_xticks(ind+width*2.30)
        #ax.set_xticklabels( ('2011-Jan-4', '2011-Jan-5', '2011-Jan-6') )
        ax.set_xticklabels( ticksvals )
        
        if metric_ == 'availabilityCloudReads' and variableSizeOf=='-n':        
            ax.legend( (rects1[0], rects2[0], rects3[0], rects4[0], rects5[0]), ('replica-aware', 'single-file','only-cloud-file','fogstore', 'total number of files'), fontsize=18, loc='lower right' )
        else:
            ax.legend( (rects1[0], rects2[0], rects3[0], rects4[0], rects5[0]), ('replica-aware', 'single-file','only-cloud-file','fogstore', 'total number of files'), fontsize=18, loc='upper left'  )
        
        
        ax.grid()


        if metric_ == 'availabilityCloudReads':
            autolabel2(rects1,0,yvals,kvals)
            autolabel2(rects2,0,zvals,kvals)
#            autolabel2(rects3,0,cvals,kvals)
            autolabel2(rects4,0,rvals,kvals)
            autolabel(rects5,0)
        if metric_ == 'availabilitySensorWrites':
            autolabel2(rects1,0,yvals,kvals)
            autolabel2(rects2,0,zvals,kvals)
#            autolabel2(rects3,0,cvals,kvals)
            autolabel2(rects4,0,rvals,kvals)
            autolabel(rects5,0)
        
        plt.savefig(pathExperimento+metric_+variableSizeOf+".pdf")
        plt.show()
