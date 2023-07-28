import os
import time
import myConfig
import experimentConfiguration
import random
import winsound
import matplotlib.pyplot as plt

# Getting the working directory
wpath = os.path.dirname(__file__)

# Initialization and set up
randomPlacement = False
popularityPlacement = False
firstPlacement = False
heuristicPlacement = False
evoPlacement = True

random.seed(15612357)
conf = myConfig.myConfig()  # Setting up configuration preferences
random.seed(15612357)
exp_conf = experimentConfiguration.experimentConfiguration(conf)  # Creating a default config environments
random.seed(15612357)
exp_conf.loadConfiguration(conf.myConfiguration)

# Random network topology
random.seed(15612357)
exp_conf.networkGeneration()
# Random applications
random.seed(15612357)
exp_conf.appGeneration()
# Random users' requests
random.seed(15612357)
exp_conf.userGeneration()
# Building Request X Application matrix
random.seed(15612357)
exp_conf.requestsMapping()
# Random placement of the applications
if randomPlacement:
    random.seed(15612357)
    stime = time.time()
    exp_conf.randomPlacement()
    ftime = time.time() - stime
    file = open(wpath + '/conf/mechanisms_exec_time.csv', 'a+')
    file.write('%s, random, %s\n' % (conf.myConfiguration, str(ftime)))
# Popularity placement of the applications
if popularityPlacement:
    random.seed(15612357)
    stime = time.time()
    exp_conf.popularityPlacement()
    ftime = time.time() - stime
    file = open(wpath + '/conf/mechanisms_exec_time.csv', 'a+')
    file.write('%s, popularity, %s\n' % (conf.myConfiguration, str(ftime)))
    file.close()
# Heuristic placement of the applications
if heuristicPlacement:
    random.seed(15612357)
    stime = time.time()
    exp_conf.heuristicPlacement()
    ftime = time.time() - stime
    file = open(wpath + '/conf/mechanisms_exec_time.csv', 'a+')
    file.write('%s, heuristic, %s\n' % (conf.myConfiguration, str(ftime)))
    file.close()
# First placement of the applications
if firstPlacement:
    random.seed(15612357)
    stime = time.time()
    exp_conf.firstPlacement()
    ftime = time.time() - stime
    file = open(wpath + '/conf/mechanisms_exec_time.csv', 'a+')
    file.write('%s, first, %s\n' % (conf.myConfiguration, str(ftime)))
    file.close()
# Evolutionary placement of the applications
if evoPlacement:
    random.seed(15612357)
    stime = time.time()
    exp_conf.evoPlacement()
    ftime = time.time() - stime
    file = open(wpath + '/conf/mechanisms_exec_time.csv', 'a+')
    file.write('%s, ea, %s\n' % (conf.myConfiguration, str(ftime)))
    file.close()

winsound.Beep(2500, 2000)