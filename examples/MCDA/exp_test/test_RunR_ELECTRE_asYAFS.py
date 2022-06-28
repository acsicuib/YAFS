# -*- coding: utf-8 -*-

from subprocess import Popen, PIPE
import os
import logging
import time
import numpy as np
import operator

np.random.seed(1)

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%I:%M:%S', level=logging.DEBUG)

def sort_table(table, col=0):
    return sorted(table, key=operator.itemgetter(col))

#see https://docs.python.org/3/library/subprocess.html#module-subprocess
def runMCDAR(pathRScript,pathWD,fileName,criteriaWeights,IndifferenceThresholds,
             PreferenceThresholds,VetoThresholds,minmaxcriteria):
    cmd = ["Rscript",pathRScript+"rscripts/ELECTREv1.R",pathWD,fileName,criteriaWeights,IndifferenceThresholds,
             PreferenceThresholds,VetoThresholds,minmaxcriteria]
    proc = Popen(cmd, stdout=PIPE)
    stdout = proc.communicate()[0]
    print stdout
    return  '{}'.format(stdout)
        
#Init 
#print os.getcwd()
pathTMP = "tmp/"
path = os.getcwd() +"/" 

dname = path+"tmp/20181127/"



#Run process 
logging.info("Running R-script")
criteriaWeights =  "4,1,2,3,1"
IndifferenceThresholds = "1.00000,99.93333,174.00000,820.00000,0.00000"
PreferenceThresholds =   "4.0,358.8,557.0,4220.0,20.0"
VetoThreshold  =  "4.0,446.0,626.6,8324.0,20.0"
criteriaMinMax = "min,min,min,min,max"

output= runMCDAR(path,dname,"data_0",criteriaWeights,IndifferenceThresholds,
             PreferenceThresholds,VetoThreshold,criteriaMinMax)

#Transform output
#logging.info("Transforming data")
print output
#if not "RESULT_OK" in output:
#    print "ERROR"
#text = "Final.Ranking.Matrix.alternative"
#process = output[output.index(text)+len(text):].split()
#ranking = [int(process[i]) for i in range(1,len(process),2)]
#best_node = ranking[0]
#output = output.replace("\"","")
#weights = output.split()[nprojects:]
#table = zip(range(nprojects),weights)
#table = sort_table(table, 1)
#
##Best project
#choice = table[0][0]
#print choice
##        


## Normalizacion de la matri
#data[:,4] = np.abs(data[:,4] - data[:,4].max())
#
#criteriaWeights= np.array([int(x) for x in criteriaWeights.split(",")])
#col_sums = data.sum(axis=0)
#new_matrix = np.true_divide(data,col_sums)
#
#choice = []
#for r in range(len(data)):
#    choice.append(np.average(new_matrix[r], weights=criteriaWeights))
#    
#print choice 
#print "Best choice: "
#print np.array(choice).argsort()
#
#    
#
#



