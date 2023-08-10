import time
import myConfig
import experimentConfiguration
import random
import matplotlib.pyplot as plt


# Initialization and set up
randomPlacement = True
popularityPlacement = False
heuristicPlacement = False
firstPlacement = False

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
    file = open('data\\mechanisms_exec_time.csv', 'a+')
    file.write('%s, random, %s\n' % (conf.myConfiguration, str(ftime)))
# Popularity placement of the applications
if popularityPlacement:
    random.seed(15612357)
    stime = time.time()
    exp_conf.popularityPlacement()
    ftime = time.time() - stime
    file = open('data\\mechanisms_exec_time.csv', 'a+')
    file.write('%s, popularity, %s\n' % (conf.myConfiguration, str(ftime)))
    file.close()
# Heuristic placement of the applications
if heuristicPlacement:
    random.seed(15612357)
    stime = time.time()
    exp_conf.heuristicPlacement()
    ftime = time.time() - stime
    file = open('data\\mechanisms_exec_time.csv', 'a+')
    file.write('%s, heuristic, %s\n' % (conf.myConfiguration, str(ftime)))
    file.close()
# First placement of the applications
if firstPlacement:
    random.seed(15612357)
    stime = time.time()
    exp_conf.firstPlacement()
    ftime = time.time() - stime
    file = open('data\\mechanisms_exec_time.csv','a+')
    file.write('%s, first, %s\n' % (conf.myConfiguration, str(ftime)))
    file.close()
