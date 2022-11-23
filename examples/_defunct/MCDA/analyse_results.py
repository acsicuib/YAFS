#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 20 10:26:38 2018

@author: isaaclera
"""
import collections
import numpy as np
import matplotlib.pyplot as plt
import pickle

case = "MCDA"
stop_time=10000
it = 0

path = "exp1/tmp_server/"
fname = "file_assignments_%s_%i_%i.pkl"% (case, stop_time, it)


#control services 
#cs = {(62, u'14_79'): ([62, 6, 2, 155], [15]), (62, u'14_77'): ([62, 6, 2, 155], [13]), (951, u'14_76'): ([951, 847, 363, 390, 14, 21], [10]), (884, u'14_76'): ([884, 871, 395, 6, 62], [9]), (62, u'14_80'): ([62, 6, 2, 155], [12]), (62, u'14_78'): ([62, 6, 2, 155], [14])}

with open(path+fname,"r") as f:
    cs = pickle.load(f)
    
    
    c = []
    for k in cs:
        c.append(len(cs[k][0]))
    
    a = np.array(c)
    plt.hist(a, bins=10)  # arguments are passed to np.histogram
    plt.title("Histogram with 'auto' bins")
    plt.show()

#Cual es la topología del último nodo?
fname2="file_alloc_entities_%s_%i_%i.pkl"% (case, stop_time, it)
f = open(path+fname2,"r")
cs2 = pickle.load(f)
dep = {}
for k in cs2:
    dep[k]=len(cs2[k])
    
l = np.sort(dep.values())
l[-1]=0
plt.plot(l[l>0])
l[l>0]

## La latencia media de cada usuario
## El power de cada nodo
## La utilización de cada nodo
## 