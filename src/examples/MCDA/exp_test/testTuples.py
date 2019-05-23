#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 12 15:40:05 2018

@author: isaaclera
"""
from collections import namedtuple
import operator
import itertools
import pandas as pd


NodeDES = namedtuple('NodeDES', ['node', 'des','path'])
l = list()
l.append(NodeDES(node=0,path=[1,2,3],des=0))
l.append(NodeDES(node=1,path=[4,5,6],des=1))
l.append(NodeDES(node=2,path=[7,8,9],des=2))

s = set()
for nodedes in l:
   for n in  nodedes.path:
       s.add((n,nodedes.des))
       
list2d = list(map(operator.attrgetter('path'), l))
merged = list(itertools.chain(*list2d))
print merged

df = pd.DataFrame(columns=["hopcount"])
df["hopcount"]=[1,2,3,4]
df["tt"]=[3,5,6,7]
df.labels=["",""]
print df.columns

df.to_csv("tmp.txt",index=False,index_label=False)
!cat tmp.txt


percentileHopCount = 20
values = (np.array(x)%2)
lp3 = [str(int(np.percentile(values, p))) for p in range(percentileHopCount, 100, percentileHopCount)]



from collections import defaultdict
dic = defaultdict(list)



df = pd.read_csv("hola.csv")
