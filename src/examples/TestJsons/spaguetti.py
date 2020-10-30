#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue May 22 15:58:58 2018

@author: carlos
"""

import networkx as nx
import itertools
from networkx.algorithms import community
import random
import operator
import json
import time




#****************************************************************************************************

#INICIALIZACIONES Y CONFIGURACIONES

#****************************************************************************************************
random.seed(8)
verbose_log = False
ILPoptimization= True
generatePlots = True
graphicTerminal =True


#myConfiguration_ = 'isaac1'
#myConfiguration_='experimentalInicial'
myConfiguration_ = 'newage2'
#myConfiguration_='tinny2'


if myConfiguration_=='tinny':
    TOTALNUMBEROFAPPS = 1
    CLOUDCAPACITY = 9999999999999999
    CLOUDSPEED = 9999
    CLOUDBW = 999
    CLOUDPR = 99
    PERCENTATGEOFGATEWAYS = 0.2
    func_PROPAGATIONTIME = "random.randint(10,10)"
    func_BANDWITDH = "random.randint(100,100)"
    func_SERVICEINSTR = "random.randint(100,100)"
    func_SERVICEMESSAGESIZE = "random.randint(500,500)"
    func_NETWORKGENERATION = "nx.barbell_graph(5, 1)" #algorithm for the generation of the network topology
    func_NODERESOURECES = "random.randint(1,1)" #random distribution for the resources of the fog devices
    func_NODESPEED = "random.randint(100,1000)" #random distribution for the speed of the fog devices
    func_APPGENERATION = "nx.gn_graph(random.randint(2,3))" #algorithm for the generation of the random applications
    func_REQUESTPROB="random.random()/4" #Popularidad de la app. threshold que determina la probabilidad de que un dispositivo tenga asociado peticiones a una app. tle threshold es para cada ap
    func_REQUESTPROB="1.0" #Popularidad de la app. threshold que determina la probabilidad de que un dispositivo tenga asociado peticiones a una app. tle threshold es para cada ap
    func_SERVICERESOURCES = "10"
    func_APPDEADLINE="(random.random()*4)"
    func_USERREQRAT="random.random()"



if myConfiguration_=='tinny2':
    TOTALNUMBEROFAPPS = 4
    CLOUDCAPACITY = 9999999999999999
    CLOUDSPEED = 9999
    CLOUDBW = 999
    CLOUDPR = 99
    PERCENTATGEOFGATEWAYS = 1.0
    func_PROPAGATIONTIME = "random.randint(10,10)"
    func_BANDWITDH = "random.randint(100,100)"
    func_SERVICEINSTR = "random.randint(100,100)"
    func_SERVICEMESSAGESIZE = "random.randint(500,500)"
    func_NETWORKGENERATION = "nx.barbell_graph(5, 1)" #algorithm for the generation of the network topology
    func_NODERESOURECES = "random.randint(1,10)" #random distribution for the resources of the fog devices
    func_NODESPEED = "random.randint(100,1000)" #random distribution for the speed of the fog devices
    func_APPGENERATION = "nx.gn_graph(random.randint(2,10))" #algorithm for the generation of the random applications
    func_REQUESTPROB="random.random()/4" #Popularidad de la app. threshold que determina la probabilidad de que un dispositivo tenga asociado peticiones a una app. tle threshold es para cada ap
    func_REQUESTPROB="1.0" #Popularidad de la app. threshold que determina la probabilidad de que un dispositivo tenga asociado peticiones a una app. tle threshold es para cada ap
    func_SERVICERESOURCES = "1"
    func_APPDEADLINE="(random.random()*4)"
    func_USERREQRAT="random.random()"



if myConfiguration_=='experimentalInicial':
    TOTALNUMBEROFAPPS = 4
    CLOUDCAPACITY = 9999999999999999
    CLOUDSPEED = 9999
    CLOUDBW = 999
    CLOUDPR = 99
    PERCENTATGEOFGATEWAYS = 1.0
    func_PROPAGATIONTIME = "random.randint(10,10)"
    func_BANDWITDH = "random.randint(100,100)"
    func_SERVICEINSTR = "random.randint(100,100)"
    func_SERVICEMESSAGESIZE = "random.randint(500,500)"
    func_NETWORKGENERATION = "nx.barbell_graph(5, 1)" #algorithm for the generation of the network topology
    func_NODERESOURECES = "random.randint(1,10)" #random distribution for the resources of the fog devices
    func_NODESPEED = "random.randint(100,1000)" #random distribution for the speed of the fog devices
    func_APPGENERATION = "nx.gn_graph(random.randint(2,10))" #algorithm for the generation of the random applications
    func_REQUESTPROB="random.random()/4" #Popularidad de la app. threshold que determina la probabilidad de que un dispositivo tenga asociado peticiones a una app. tle threshold es para cada ap
    func_REQUESTPROB="1.0" #Popularidad de la app. threshold que determina la probabilidad de que un dispositivo tenga asociado peticiones a una app. tle threshold es para cada ap
    func_SERVICERESOURCES = "random.random()"
    func_APPDEADLINE="(random.random()*4)"
    func_USERREQRAT="random.random()"



if myConfiguration_ == 'isaac1':

    #CLOUD
    CLOUDCAPACITY = 9999999999999999  #MB RAM
    CLOUDSPEED = 10000 #INSTR x MS
    CLOUDBW = 125000 # BYTES / MS --> 1000 Mbits/s
    CLOUDPR = 1 # MS


    #NETWORK
    PERCENTATGEOFGATEWAYS = 0.25
    func_PROPAGATIONTIME = "random.randint(5,5)" #MS
    func_BANDWITDH = "random.randint(75000,75000)" # BYTES / MS
    func_NETWORKGENERATION = "nx.barabasi_albert_graph(n=100, m=2)" #algorithm for the generation of the network topology
    func_NODERESOURECES = "random.randint(500,1500)" #MB RAM #random distribution for the resources of the fog devices
    func_NODESPEED = "random.randint(100,1000)" #INTS / MS #random distribution for the speed of the fog devices



    #APP and SERVICES
    TOTALNUMBEROFAPPS = 5
    func_APPGENERATION = "nx.gn_graph(random.randint(2,10))" #algorithm for the generation of the random applications
    func_SERVICEINSTR = "random.randint(20000,60000)" #INSTR --> teniedno en cuenta nodespped esto nos da entre 200 y 600 MS
    func_SERVICEMESSAGESIZE = "random.randint(1500000,4500000)" #BYTES y teniendo en cuenta net bandwidth nos da entre 20 y 60 MS
    func_SERVICERESOURCES = "random.randint(250,750)" #MB de ram que consume el servicio, teniendo en cuenta noderesources y appgeneration tenemos que nos caben aprox 1 app por nodo o unos 10 servicios
    func_APPDEADLINE="random.randint(2600,6600)" #MS


    #USERS and IoT DEVICES
    func_REQUESTPROB="random.random()/4" #Popularidad de la app. threshold que determina la probabilidad de que un dispositivo tenga asociado peticiones a una app. tle threshold es para cada ap
    func_USERREQRAT="random.randint(200,1000)"  #MS



if myConfiguration_ == 'newage':

    #CLOUD
    CLOUDCAPACITY = 9999999999999999  #MB RAM
    CLOUDSPEED = 10000 #INSTR x MS
    CLOUDBW = 125000 # BYTES / MS --> 1000 Mbits/s
    CLOUDPR = 1 # MS


    #NETWORK
    PERCENTATGEOFGATEWAYS = 0.25
    func_PROPAGATIONTIME = "random.randint(5,5)" #MS
    func_BANDWITDH = "random.randint(75000,75000)" # BYTES / MS
    func_NETWORKGENERATION = "nx.barabasi_albert_graph(n=100, m=2)" #algorithm for the generation of the network topology
    func_NODERESOURECES = "random.randint(5,15)" #MB RAM #random distribution for the resources of the fog devices
    func_NODESPEED = "random.randint(100,1000)" #INTS / MS #random distribution for the speed of the fog devices



    #APP and SERVICES
    TOTALNUMBEROFAPPS = 40
    func_APPGENERATION = "nx.gn_graph(random.randint(2,10))" #algorithm for the generation of the random applications
    func_SERVICEINSTR = "random.randint(20000,60000)" #INSTR --> teniedno en cuenta nodespped esto nos da entre 200 y 600 MS
    func_SERVICEMESSAGESIZE = "random.randint(1500000,4500000)" #BYTES y teniendo en cuenta net bandwidth nos da entre 20 y 60 MS
    func_SERVICERESOURCES = "random.randint(2,7)" #MB de ram que consume el servicio, teniendo en cuenta noderesources y appgeneration tenemos que nos caben aprox 1 app por nodo o unos 10 servicios
    func_APPDEADLINE="random.randint(2600,6600)" #MS


    #USERS and IoT DEVICES
    func_REQUESTPROB="random.random()/4" #Popularidad de la app. threshold que determina la probabilidad de que un dispositivo tenga asociado peticiones a una app. tle threshold es para cada ap
    func_USERREQRAT="random.randint(200,1000)"  #MS




if myConfiguration_ == 'newagepequenyoqueresuelveenpocotiempo':

    #CLOUD
    CLOUDCAPACITY = 9999999999999999  #MB RAM
    CLOUDSPEED = 10000 #INSTR x MS
    CLOUDBW = 125000 # BYTES / MS --> 1000 Mbits/s
    CLOUDPR = 1 # MS


    #NETWORK
    PERCENTATGEOFGATEWAYS = 0.25
    func_PROPAGATIONTIME = "random.randint(5,5)" #MS
    func_BANDWITDH = "random.randint(75000,75000)" # BYTES / MS
    func_NETWORKGENERATION = "nx.barabasi_albert_graph(n=50, m=2)" #algorithm for the generation of the network topology
    func_NODERESOURECES = "random.randint(5,15)" #MB RAM #random distribution for the resources of the fog devices
    func_NODESPEED = "random.randint(100,1000)" #INTS / MS #random distribution for the speed of the fog devices



    #APP and SERVICES
    TOTALNUMBEROFAPPS = 40
    func_APPGENERATION = "nx.gn_graph(random.randint(2,10))" #algorithm for the generation of the random applications
    func_SERVICEINSTR = "random.randint(20000,60000)" #INSTR --> teniedno en cuenta nodespped esto nos da entre 200 y 600 MS
    func_SERVICEMESSAGESIZE = "random.randint(1500000,4500000)" #BYTES y teniendo en cuenta net bandwidth nos da entre 20 y 60 MS
    func_SERVICERESOURCES = "random.randint(2,7)" #MB de ram que consume el servicio, teniendo en cuenta noderesources y appgeneration tenemos que nos caben aprox 1 app por nodo o unos 10 servicios
    func_APPDEADLINE="random.randint(2600,6600)" #MS


    #USERS and IoT DEVICES
    func_REQUESTPROB="random.random()/20" #Popularidad de la app. threshold que determina la probabilidad de que un dispositivo tenga asociado peticiones a una app. tle threshold es para cada ap
    func_USERREQRAT="random.randint(200,1000)"  #MS




if myConfiguration_ == 'newage2':

    #CLOUD
    CLOUDCAPACITY = 9999999999999999  #MB RAM
    CLOUDSPEED = 10000 #INSTR x MS
    CLOUDBW = 125000 # BYTES / MS --> 1000 Mbits/s
    CLOUDPR = 1 # MS


    #NETWORK
    PERCENTATGEOFGATEWAYS = 0.25
    func_PROPAGATIONTIME = "random.randint(5,5)" #MS
    func_BANDWITDH = "random.randint(75000,75000)" # BYTES / MS
    func_NETWORKGENERATION = "nx.barabasi_albert_graph(n=50, m=2)" #algorithm for the generation of the network topology
    func_NODERESOURECES = "random.randint(2,8)" #MB RAM #random distribution for the resources of the fog devices
    func_NODESPEED = "random.randint(100,1000)" #INTS / MS #random distribution for the speed of the fog devices



    #APP and SERVICES
    TOTALNUMBEROFAPPS = 10
    func_APPGENERATION = "nx.gn_graph(random.randint(2,6))" #algorithm for the generation of the random applications
    func_SERVICEINSTR = "random.randint(20000,60000)" #INSTR --> teniedno en cuenta nodespped esto nos da entre 200 y 600 MS
    func_SERVICEMESSAGESIZE = "random.randint(1500000,4500000)" #BYTES y teniendo en cuenta net bandwidth nos da entre 20 y 60 MS
    func_SERVICERESOURCES = "random.randint(2,5)" #MB de ram que consume el servicio, teniendo en cuenta noderesources y appgeneration tenemos que nos caben aprox 1 app por nodo o unos 10 servicios
    func_APPDEADLINE="random.randint(2600,6600)" #MS


    #USERS and IoT DEVICES
    func_REQUESTPROB="random.random()/6" #Popularidad de la app. threshold que determina la probabilidad de que un dispositivo tenga asociado peticiones a una app. tle threshold es para cada ap
    func_USERREQRAT="random.randint(200,1000)"  #MS


if myConfiguration_ == 'newage3':

    #CLOUD
    CLOUDCAPACITY = 9999999999999999  #MB RAM
    CLOUDSPEED = 1000 #INSTR x MS
    CLOUDBW = 125000 # BYTES / MS --> 1000 Mbits/s
    CLOUDPR = 10 # MS


    #NETWORK
    PERCENTATGEOFGATEWAYS = 0.2
    func_PROPAGATIONTIME = "random.randint(4,8)" #MS
    func_BANDWITDH = "random.randint(37500,62500)" # BYTES / MS enlaces de entre 300 Mbits /sec y 500 Mbits /seg
    func_NETWORKGENERATION = "nx.barabasi_albert_graph(n=50, m=2)" #algorithm for the generation of the network topology
    func_NODERESOURECES = "random.randint(2,10)" #MB RAM #random distribution for the resources of the fog devices
    func_NODESPEED = "random.randint(500,1000)" #INTS / MS #random distribution for the speed of the fog devices



    #APP and SERVICES
    TOTALNUMBEROFAPPS = 10
    func_APPGENERATION = "nx.gn_graph(random.randint(2,8))" #algorithm for the generation of the random applications
    func_SERVICEINSTR = "random.randint(400000,600000)" #INSTR --> teniedno en cuenta nodespped esto nos da entre 200 y 600 MS
    func_SERVICEMESSAGESIZE = "random.randint(1500000,4500000)" #BYTES y teniendo en cuenta net bandwidth nos da entre 20 y 60 MS
    func_SERVICERESOURCES = "random.randint(2,5)" #MB de ram que consume el servicio, teniendo en cuenta noderesources y appgeneration tenemos que nos caben aprox 1 app por nodo o unos 10 servicios
    func_APPDEADLINE="random.randint(20000,50000)" #MS


    #USERS and IoT DEVICES
    func_REQUESTPROB="random.random()/10" #Popularidad de la app. threshold que determina la probabilidad de que un dispositivo tenga asociado peticiones a una app. tle threshold es para cada ap
    func_USERREQRAT="random.randint(200,1000)"  #MS













#****************************************************************************************************

#ESCRITURA DE ESTADISTICAS PARA PLOTS

#****************************************************************************************************

#(deadline,shortestdistance):occurrences
statisticsDistanceDeadlineILP = {}

#(service,deadline):occurrences
statisticsServiceInstancesILP = {}

#distance:numberOfuserThatRequest
statisticsDistancesRequestILP = {}

#nodeid:numberOfuserThatRequest
statisticsNodesRequestILP = {}


#(nodeid,serviceId):ocurrences
statisticsNodesServicesILP = {}

def writeStatisticsAllocationILP(clientId,servId,devId):

    if not devId==cloudId:
        appId=int(mapService2App[servId])


        dist_ = nx.shortest_path_length(G,source=clientId,target=devId,weight="weight")

        mykey_=dist_
        if mykey_ in statisticsDistancesRequestILP:
            statisticsDistancesRequestILP[mykey_]= statisticsDistancesRequestILP[mykey_]+1
        else:
            statisticsDistancesRequestILP[mykey_]=1

        mykey_=devId
        if mykey_ in statisticsNodesRequestILP:
            statisticsNodesRequestILP[mykey_]= statisticsNodesRequestILP[mykey_]+1
        else:
            statisticsNodesRequestILP[mykey_]=1

        mykey_=(devId,servId)
        if mykey_ in statisticsNodesServicesILP:
            statisticsNodesServicesILP[mykey_]= statisticsNodesServicesILP[mykey_]+1
        else:
            statisticsNodesServicesILP[mykey_]=1


        mykey_=(appsDeadlines[appId],dist_)
        if mykey_ in statisticsDistanceDeadlineILP:
            statisticsDistanceDeadlineILP[mykey_]= statisticsDistanceDeadlineILP[mykey_]+1
        else:
            statisticsDistanceDeadlineILP[mykey_]=1

        mykey_=(servId,appsDeadlines[appId])
        if mykey_ in statisticsServiceInstancesILP:
            statisticsServiceInstancesILP[mykey_]=statisticsServiceInstancesILP[mykey_]+1
        else:
            statisticsServiceInstancesILP[mykey_]=1


#deviceId: total usage resources
nodeBussyResourcesILP={}

def writeStatisticsDevicesILP(servId,devId):



    #
    if not devId==cloudId:
        mykey_=devId
        if mykey_ in nodeBussyResourcesILP:
            nodeBussyResourcesILP[mykey_]=nodeBussyResourcesILP[mykey_]+float(myServicesResources[servId])
        else:
            nodeBussyResourcesILP[mykey_]=float(myServicesResources[servId])


#(centrality,resources):occurrences
statisticsCentralityResourcesILP = {}

def normalizeStatisticsDevicesILP():

    for i in nodeBussyResourcesILP.items():
        devId = i[0]
        mypercentageResources_ = float(nodeBussyResourcesILP[devId])/float(nodeResources[devId])
        mycentralityValues_ = centralityValuesNoOrdered[devId]
        mykey_=(mycentralityValues_,mypercentageResources_)
        if mykey_ in statisticsCentralityResourcesILP:
            statisticsCentralityResourcesILP[mykey_]=statisticsCentralityResourcesILP[mykey_]+1
        else:
            statisticsCentralityResourcesILP[mykey_]=1



#(deadline,shortestdistance):occurrences
statisticsDistanceDeadline = {}

#(service,deadline):occurrences
statisticsServiceInstances = {}


#distance:numberOfuserThatRequest
statisticsDistancesRequest = {}

#nodeid:numberOfuserThatRequest
statisticsNodesRequest = {}

#(nodeid,serviceId):ocurrences
statisticsNodesServices = {}

def writeStatisticsAllocation(tempServiceAlloc,clientId,appId):

#    for talloc_ in tempServiceAlloc.items():
#        dist_ = nx.shortest_path_length(G,source=clientId,target=talloc_[1],weight="weight")
#        mykey_=(clientId,appId,dist_)
#        if mykey_ in statisticsDistanceDeadline:
#            statisticsDistanceDeadline[mykey_]= statisticsDistanceDeadline[mykey_]+1
#        else:
#            statisticsDistanceDeadline[mykey_]=1
    for talloc_ in tempServiceAlloc.items():

        dist_ = nx.shortest_path_length(G,source=clientId,target=talloc_[1],weight="weight")

        mykey_=dist_
        if mykey_ in statisticsDistancesRequest:
            statisticsDistancesRequest[mykey_]= statisticsDistancesRequest[mykey_]+1
        else:
            statisticsDistancesRequest[mykey_]=1

        mykey_=talloc_[1]
        if mykey_ in statisticsNodesRequest:
            statisticsNodesRequest[mykey_]= statisticsNodesRequest[mykey_]+1
        else:
            statisticsNodesRequest[mykey_]=1

        mykey_=(talloc_[1],talloc_[0])
        if mykey_ in statisticsNodesServices:
            statisticsNodesServices[mykey_]= statisticsNodesServices[mykey_]+1
        else:
            statisticsNodesServices[mykey_]=1


        mykey_=(appsDeadlines[appId],dist_)
        if mykey_ in statisticsDistanceDeadline:
            statisticsDistanceDeadline[mykey_]= statisticsDistanceDeadline[mykey_]+1
        else:
            statisticsDistanceDeadline[mykey_]=1

        mykey_=(talloc_[0],appsDeadlines[appId])
        if mykey_ in statisticsServiceInstances:
            statisticsServiceInstances[mykey_]=statisticsServiceInstances[mykey_]+1
        else:
            statisticsServiceInstances[mykey_]=1

#(centrality,resources):occurrences
statisticsCentralityResources = {}


def writeStatisticsDevices(service2DevicePlacementMatrix):


    for devId in G.nodes:
        mypercentageResources_ = float(nodeBussyResources[devId])/float(nodeResources[devId])
        mycentralityValues_ = centralityValuesNoOrdered[devId]
        mykey_=(mycentralityValues_,mypercentageResources_)
        if mykey_ in statisticsCentralityResources:
            statisticsCentralityResources[mykey_]=statisticsCentralityResources[mykey_]+1
        else:
            statisticsCentralityResources[mykey_]=1




def networkDelay(i):

    processTime=0.0
    #processTime = mips_ / float(devices[devId]['IPT']) # tiempo de ejecutar todos los servicios de la app
    netTime = networkdistances[(i[0][0],i[1])]    #tiempo de red entre cliente y dispositivo
    return processTime + netTime


#****************************************************************************************************

#FUNCIONES PARA LA PARTE DE TRANSITIVE CLOSURE

#****************************************************************************************************



def normalizeSmallerSetsInSameLevel(transitivesClosures):


    for n in transitivesClosures:
        tmpList = list(transitivesClosures[n])
        for i in range(0,len(tmpList)):
            for j in range(i+1,len(tmpList)):
                if (tmpList[i] & tmpList[j])==tmpList[i]:
                    transitivesClosures[n].remove(tmpList[i])



def createSetFromSetOfSets(setofsets):

    finalset = set()
    for i in setofsets:
        finalset = finalset | set(i)

    return finalset


def normalizeIncludePrevious(transitivesClosures):


    previous = transitivesClosures[0]

    for n in transitivesClosures:
        if verbose_log:
            print "level"
            print n
        toInclude = set()
        for i in transitivesClosures[n]:
            current =  createSetFromSetOfSets(transitivesClosures[n])
            for j in previous:
                if len(j & current)==0:
                    if verbose_log:
                        print "individual"
                        print j
                    toInclude.add(j)
        if verbose_log:
            print "final"
            print toInclude
        transitivesClosures[n] = transitivesClosures[n] | toInclude
        previous = transitivesClosures[n]





def getTransitiveClosures(source, app_, transitivesClosures,cycles_, level):

#    if level > 10:
#        import sys
#        sys.exit("Error message")

    if verbose_log:
        print source
#    raw_input()
    neighbords_=list(app_.neighbors(source))
    if not level in transitivesClosures:
        transitivesClosures[level] = set()

    descendantsOfNeighbords = set()
    for i in neighbords_:
        descendantsOfNeighbords = descendantsOfNeighbords | set(nx.descendants(app_,i))



#
#    tmp = set()
#    tmp.add(source)
#    transitivesClosures[level].add(frozenset(tmp))


    tmp=set(nx.descendants(app_,source))
    tmp.add(source)
    tmp = frozenset(tmp)
#    print "tmp"
#    print tmp
#    print "cycles_"
#    print cycles_
#    print "transtivesClosures"
#    print transitivesClosures
#    print "level"
#    print level
    if not tmp in transitivesClosures[level]:
        if verbose_log:
            print tmp
        transitivesClosures[level].add(tmp)
        if not tmp in cycles_:



            if len(neighbords_)>0:
                if not (level+1) in transitivesClosures:
                    transitivesClosures[level+1] = set()



                tmp = set()
                tmp.add(source)
                transitivesClosures[level+1].add(frozenset(tmp))


            for n in neighbords_:

               # if not n in descendantsOfNeighbords:

                getTransitiveClosures(n,app_,transitivesClosures,cycles_,level+1)
    #            tmp=set(nx.descendants(app_,n))
    #            tmp.add(n)
    #            tmp = frozenset(tmp)
    #            transitivesClosures[1].add(tmp)




def transitiveClosureCalculation(source,app_):


    transitivesClosures = {}


    cycles_ = set()

    for i in nx.simple_cycles(app_):
        if verbose_log:
            print i
        tmp = frozenset(i)
        if verbose_log:
            print tmp
        cycles_.add(tmp)


    getTransitiveClosures(source,app_,transitivesClosures,cycles_,0)

    normalizeSmallerSetsInSameLevel(transitivesClosures)

    normalizeIncludePrevious(transitivesClosures)

    return transitivesClosures






#****************************************************************************************************

#END PARA LA PARTE DE TRANSITIVE CLOSURE

#****************************************************************************************************




#TODO ++++++++++++++++++++++++++++++++++++++
#TODO ++++++++++++++++++++++++++++++++++++++
#TODO ++++++++++++++++++++++++++++++++++++++
#TODO ++++++++++++++++++++++++++++++++++++++
#TODO ++++++++++++++++++++++++++++++++++++++
#TODO ++++++++++++++++++++++++++++++++++++++
#TODO ++++++++++++++++++++++++++++++++++++++
def devicesFirstFitDescendingOrder(community,clientId,appId):

    mips_ = float(appsTotalMIPS[appId])
    nodeFitness = {}

    for devId in community:
        if verbose_log:
            print "fitness for device "+str(devId)+ " from client "+str(clientId)
        processTime = mips_ / float(devices[devId]['IPT']) # tiempo de ejecutar todos los servicios de la app
        if verbose_log:
            print processTime
        netTime = nx.shortest_path_length(G,source=clientId,target=devId,weight="weight")    #tiempo de red entre cliente y dispositivo
        if verbose_log:
            print netTime
        nodeFitness[devId] = processTime + netTime


    sorted_ = sorted(nodeFitness.items(), key=operator.itemgetter(1))

    sortedList = list()

    for i in sorted_:
        sortedList.append(i[0])

    return sortedList

#    a= list(community)
#    random.shuffle(a)
#    return a


def weightNetwork(appdId):
    size = float(appsSourceMessage[appId]['bytes'])
    for e in G.edges:
        G[e[0]][e[1]]['weight']=float(G[e[0]][e[1]]['PR'])+ (size/float(G[e[0]][e[1]]['BW']))


def placeSubAppInCommunity(appId, subAppCommunity, orderedDevices):

    servicesToPlace = list(subAppCommunity)
#    s2p_Resources = list()
#    for i in servicesToPlace:
#        s2p_Resources.append(appsResources[appId][i])
#
#    totalResourcesAppNeeds = sum(s2p_Resources)

    availableResourcesNodes = {}
    availableSpeedNodes = {}

    for devId in orderedDevices:
        availableResourcesNodes[devId]=nodeResources[devId]-nodeBussyResources[devId]
        availableSpeedNodes[devId]=nodeSpeed[devId]



    for devId in orderedDevices:
        if verbose_log:
            print "            Testing service set "+str(subAppCommunity)+" of app "+str(appId)+" in device "+str(devId)
        neededResources = 0.0
        for servId in servicesToPlace:
            if service2DevicePlacementMatrix[servId][devId]!=1:
                neededResources = neededResources + appsResources[appId][servId]
        if availableResourcesNodes[devId] < neededResources:
            if verbose_log:
                print "            Performed allocation of service set "+str(subAppCommunity)+" of app "+str(appId)+" in device "+str(devId)
            return True,devId
        else:
            if verbose_log:
                print "            Not allocatted due to not enough resources in device"


    return False,-1


#****************************************************************************************************

#Placement de sengundo nivel (services to devices) que usa las communities

#****************************************************************************************************

def placeAppInCommunityOLD(appId, clientId, candidateCommunity):

    servicesToPlace = set()
    servicePlacement = {}
    for i in apps[appId].nodes:
        servicesToPlace.add(i)
        servicePlacement[i]= False


    orderedDevices=devicesFirstFitDescendingOrder(candidateCommunity,clientId,appId) #El orden de preferencia de los dispositivos es igual para todos los subapps communities

    for appCommu in appsCommunities[appId]:

        if appCommu[0] == appCommu[0] & servicesToPlace:  #la comunidad de app que pillo ahora, tiene todos sus servicios pendientes de allocar? comunidad = comunidad INTERSCCION PENDIENTES
            if verbose_log:
                print "        Testing service set "+str(appCommu)+" of app "+str(appId)+" in community "+str(candidateCommunity)

            allocat_, devId = placeSubAppInCommunity(appId,appCommu[0],orderedDevices)
            if allocat_:

                for servId in appCommu[0]:
#TODO aqui estoy haciendo el placement de todos los servicios en el application community
#por lo que podria provocar que estuviera sobreescribiendo el placement de un mismo servicio
#ya emplazado y lo acabaria emplazando en un peor lugar en cuanto al community, pero
# ?mejor? en cuanto a que hay mas servicios juntos ?lo dejo ? o miro antes si ya esta emplzado
# con un if? del estilo if not servicePlacement.has_key(servId):
                    if servicePlacement[i]== False:
                        servicePlacement[servId]=devId

                servicesToPlace = servicesToPlace - appCommu[0]
                if verbose_log:
                    print "        Allocated. Remaining services "+str(servicesToPlace)
                if len(servicesToPlace)==0:
                    return True,servicePlacement
            else:
                if verbose_log:
                    print "        Not allocated"


    return False,servicePlacement


#****************************************************************************************************

#Placement de sengundo nivel (services to devices) que usa las transitive closures
#recorre primero los devices, y va metiendo todos los posibles closures
#para los siguientes devices, solo intenta colocar closures con servicios no colocados anteriormente

#****************************************************************************************************


def placeAppInCommunity(appId, clientId, candidateCommunity):

    servicesToPlace = set()
    for i in apps[appId].nodes:
        servicesToPlace.add(i)

    orderedDevices=devicesFirstFitDescendingOrder(candidateCommunity,clientId,appId) #El orden de preferencia de los dispositivos es igual para todos los subapps communities

    availableResourcesNodes = {}
    availableSpeedNodes = {}

    tempServiceAlloc = {}
    for servId in apps[appId].nodes:
        tempServiceAlloc[servId]= None

    for devId in orderedDevices:
        availableResourcesNodes[devId]=nodeResources[devId]-nodeBussyResources[devId]
        availableSpeedNodes[devId]=nodeSpeed[devId]



        for appCommu in appsCommunities[appId].items():

            listOfTransitiveClosures = appCommu[1]



            for serviceSet in listOfTransitiveClosures:


                if len(serviceSet & servicesToPlace)>0:  #si la interseccion es NO vacia, es que aun no hemos colocado ninguna transitive closure superior que incluya cualquiera de esos servicios

                    requiredResources = 0.0
                    for service in serviceSet:
                        requiredResources = requiredResources + appsResources[appId][service]
                    if availableResourcesNodes[devId]>requiredResources:
                        servicesToPlace = servicesToPlace - serviceSet
                        if verbose_log:
                            print "        Temp-allocation of services "+str(serviceSet)+" in device "+str(devId)
                        for service in serviceSet:
                            tempServiceAlloc[service]= devId
                        availableResourcesNodes[devId] = availableResourcesNodes[devId] - requiredResources

                        if len(servicesToPlace)==0:
                            writeStatisticsAllocation(tempServiceAlloc,clientId,appId)
                            return True,tempServiceAlloc

    if verbose_log:
        print "        Rejected the temporal allocations"
        print "        Application not allocated in community"
    myemptydict = {}
    return False, myemptydict







#****************************************************************************************************

#Placement de sengundo nivel (services to devices) que usa las transitive closures
#pero en este caso, considera primero las transitives closures, y si no se colocan todas las de un nivel
# se empieza otra vez con las siguientes, *desperdiciando* posibles allocations the closures mas grandes
# es decir, primero recorre closures y en el inner for los devices

#****************************************************************************************************


def placeAppInCommunity2(appId, clientId, candidateCommunity):




    orderedDevices=devicesFirstFitDescendingOrder(candidateCommunity,clientId,appId) #El orden de preferencia de los dispositivos es igual para todos los subapps communities

    for appCommu in appsCommunities[appId].items():

        listOfTransitiveClosures = appCommu[1]

        availableResourcesNodes = {}
        availableSpeedNodes = {}

        tempServiceAlloc = {}
        for nodeId in apps[appId].nodes:
            tempServiceAlloc[nodeId]= None

        for devId in orderedDevices:
            availableResourcesNodes[devId]=nodeResources[devId]-nodeBussyResources[devId]
            availableSpeedNodes[devId]=nodeSpeed[devId]


        for serviceSet in listOfTransitiveClosures:
            requiredResources = 0.0
            for service in serviceSet:
                requiredResources = requiredResources + appsResources[appId][service]
            for devId in orderedDevices:
                if availableResourcesNodes[devId]>requiredResources:
                    if verbose_log:
                        print "        Temp-allocation of services "+str(serviceSet)+" in device "+str(devId)
                    for service in serviceSet:
                        tempServiceAlloc[service]= devId
                    availableResourcesNodes[devId] = availableResourcesNodes[devId] - requiredResources
                    break
            else: #este else solo se ejecuta si el for devId... llega a su fin, sin haber encontrado un device con espacio suficiente, es decir si NO ha salido por el break
                if verbose_log:
                    print "        Rejected the current allocation"
                break
        else: #este else solo se ejecuta cuando acabamos el bucle for serviceSet in... por haber llegado al final y no haber hecho un break por no tener sitio para algun set of services, es decir, si han allocated todos los conjuntos de servicios
            if verbose_log:
                print "        Finally we allocate the transitive closure level "+ str(listOfTransitiveClosures)
            if verbose_log:
                print "        and the allocation is defined as "+ str(tempServiceAlloc)
            return True,tempServiceAlloc

    myemptydict = {}
    return False, myemptydict









def communityCalculation(GRAPH,reverseOrd):

    communities_generator = community.girvan_newman(GRAPH)

    allCommunities = set()
    communityLevel = {}
    allCommunities.add(frozenset(GRAPH.nodes))
    communityLevel[frozenset(GRAPH.nodes)]=0
    i = 1
    for communities in itertools.islice(communities_generator, GRAPH.number_of_nodes()):
        if verbose_log:
            print(tuple(sorted(c) for c in communities))
        for c in communities:
            allCommunities.add(frozenset(c))
            communityLevel[frozenset(c)]=i
        i=i+1

    sorted_ = sorted(communityLevel.items(), key=operator.itemgetter(1), reverse=reverseOrd)

    return sorted_






#****************************************************************************************************

#GENERACION DEL MODELO

#****************************************************************************************************


#****************************************************************************************************
#Generacion de la topologia de red
#****************************************************************************************************
t = time.time()

#TOPOLOGY GENERATION


G = eval(func_NETWORKGENERATION)
#G = nx.barbell_graph(5, 1)
if graphicTerminal:
    nx.draw(G)



devices = list()

nodeResources = {}
nodeFreeResources = {}
nodeSpeed = {}
for i in G.nodes:
    nodeResources[i]=eval(func_NODERESOURECES)
    nodeSpeed[i]=eval(func_NODESPEED)

for e in G.edges:
    G[e[0]][e[1]]['PR']=eval(func_PROPAGATIONTIME)
    G[e[0]][e[1]]['BW']=eval(func_BANDWITDH)


#JSON EXPORT

netJson={}


for i in G.nodes:
    myNode ={}
    myNode['id']=i
    myNode['RAM']=nodeResources[i]
    myNode['IPT']=nodeSpeed[i]
    devices.append(myNode)




myEdges = list()
for e in G.edges:
    myLink={}
    myLink['s']=e[0]
    myLink['d']=e[1]
    myLink['PR']=G[e[0]][e[1]]['PR']
    myLink['BW']=G[e[0]][e[1]]['BW']

    myEdges.append(myLink)


#TODO, debería de estar con weight='weight' ??????


centralityValuesNoOrdered = nx.betweenness_centrality(G,weight="weight")
centralityValues=sorted(centralityValuesNoOrdered.items(), key=operator.itemgetter(1), reverse=True)

gatewaysDevices = set()
cloudgatewaysDevices = set()

highestCentrality = centralityValues[0][1]

for device in centralityValues:
    if device[1]==highestCentrality:
        cloudgatewaysDevices.add(device[0])



initialIndx = int((1-PERCENTATGEOFGATEWAYS)*len(G.nodes))  #Indice del final para los X tanto por ciento nodos

for idDev in range(initialIndx,len(G.nodes)):
    gatewaysDevices.add(centralityValues[idDev][0])



cloudId = len(G.nodes)
myNode ={}
myNode['id']=cloudId
myNode['RAM']=CLOUDCAPACITY
myNode['IPT']=CLOUDSPEED
devices.append(myNode)


for cloudGtw in cloudgatewaysDevices:
    myLink={}
    myLink['s']=cloudGtw
    myLink['d']=cloudId
    myLink['PR']=CLOUDPR
    myLink['BW']=CLOUDBW

    myEdges.append(myLink)


netJson['entity']=devices
netJson['link']=myEdges


file = open("networkDefinition.json","w")
file.write(json.dumps(netJson))
file.close()


#****************************************************************************************************
#Calculo de las communities
#****************************************************************************************************

#communities_generator = community.girvan_newman(G)
#
#allCommunities = set()
#communityLevel = {}
#i = 0
#for communities in itertools.islice(communities_generator, G.number_of_nodes()):
#    print(tuple(sorted(c) for c in communities))
#    for c in communities:
#        allCommunities.add(frozenset(c))
#        communityLevel[frozenset(c)]=i
#    i=i+1
#
#sortedCommunities = sorted(communityLevel.items(), key=operator.itemgetter(1), reverse=True)


sortedCommunities=communityCalculation(G, reverseOrd=True)



#communitiesResources = {}


#****************************************************************************************************
#Generacion de las aplicaciones
#****************************************************************************************************

numberOfServices=0
theServices_=list()
apps = list()
appsDeadlines = {}
appsResources = list()
appsSourceService = list()
appsSourceMessage = list()
appsTotalMIPS = list()
mapService2App = list()
mapServiceId2ServiceName = list()
appsCommunities = list()

appJson = list()
servicesResources = {}


for i in range(0,TOTALNUMBEROFAPPS):
    myApp = {}
#    APP = nx.lollipop_graph(3,1)
    APP = eval(func_APPGENERATION)
#    nx.is_directed_acyclic_graph(APP)

    mylabels = {}

    for n in range(0,len(APP.nodes)):
        mylabels[n]=str(n)

    if graphicTerminal:
        nx.draw(APP,labels=mylabels)


    edgeList_=list()

    for m in APP.edges:
        edgeList_.append(m)
    for m in edgeList_:
        APP.remove_edge(m[0],m[1])
        APP.add_edge(m[1],m[0])


    if graphicTerminal:
        nx.draw(APP,labels=mylabels)





    mapping=dict(zip(APP.nodes(),range(numberOfServices,numberOfServices+len(APP.nodes))))
    APP=nx.relabel_nodes(APP,mapping)

    #appsCommunities.append(communityCalculation(APP, reverseOrd=False))

    numberOfServices = numberOfServices + len(APP.nodes)
    apps.append(APP)
    for j in APP.nodes:
        servicesResources[j]=eval(func_SERVICERESOURCES)
    appsResources.append(servicesResources)

    topologicorder_ = list(nx.topological_sort(APP))
    source = topologicorder_[0]
#    source = -1
#    for j in nx.topological_sort(APP):
#        source=j


    appsCommunities.append(transitiveClosureCalculation(source,APP))
    transitiveClosureCalculation(source,APP)

    appsSourceService.append(source)


    appsDeadlines[i]=eval(func_APPDEADLINE)
    myApp['id']=i
    myApp['name']=str(i)
    myApp['deadline']=appsDeadlines[i]

    myApp['module']=list()

    edgeNumber=0
    myApp['message']=list()

    myApp['transmission']=list()

    totalMIPS = 0

    for n in APP.nodes:
        mapService2App.append(str(i))
        mapServiceId2ServiceName.append(str(i)+'_'+str(n))
        myNode={}
        myNode['id']=n
        myNode['name']=str(i)+'_'+str(n)
        myNode['RAM']=servicesResources[n]
        myNode['type']='MODULE'
        if source==n:
            myEdge={}
            myEdge['id']=edgeNumber
            edgeNumber = edgeNumber +1
            myEdge['name']="M.USER.APP."+str(i)
            myEdge['s']= "None"
            myEdge['d']=str(i)+'_'+str(n)
            myEdge['instructions']=eval(func_SERVICEINSTR)
            totalMIPS = totalMIPS + myEdge['instructions']
            myEdge['bytes']=eval(func_SERVICEMESSAGESIZE)
            myApp['message'].append(myEdge)
            appsSourceMessage.append(myEdge)
            if verbose_log:
                print "AÑADO MENSAGE SOURCE"
            for o in APP.edges:
                if o[0]==source:
                    myTransmission = {}
                    myTransmission['module']=str(i)+'_'+str(source)
                    myTransmission['message_in']="M.USER.APP."+str(i)
                    myTransmission['message_out']=str(i)+'_('+str(o[0])+"-"+str(o[1])+")"
                    myApp['transmission'].append(myTransmission)
#            myNode['type']='SOURCE'
#        else:
#            myNode['type']='MODULE'
        myApp['module'].append(myNode)


    for n in APP.edges:
        myEdge={}
        myEdge['id']=edgeNumber
        edgeNumber = edgeNumber +1
        myEdge['name']=str(i)+'_('+str(n[0])+"-"+str(n[1])+")"
        myEdge['s']=str(i)+'_'+str(n[0])
        myEdge['d']=str(i)+'_'+str(n[1])
        myEdge['instructions']=eval(func_SERVICEINSTR)
        totalMIPS = totalMIPS + myEdge['instructions']
        myEdge['bytes']=eval(func_SERVICEMESSAGESIZE)
        myApp['message'].append(myEdge)
        destNode = n[1]
        for o in APP.edges:
            if o[0]==destNode:
                myTransmission = {}
                myTransmission['module']=str(i)+'_'+str(n[1])
                myTransmission['message_in']=str(i)+'_('+str(n[0])+"-"+str(n[1])+")"
                myTransmission['message_out']=str(i)+'_('+str(o[0])+"-"+str(o[1])+")"
                myApp['transmission'].append(myTransmission)


    for n in APP.nodes:
        outgoingEdges = False
        for m in APP.edges:
            if m[0]==n:
                outgoingEdges = True
                break
        if not outgoingEdges:
            for m in APP.edges:
                if m[1]==n:
                    myTransmission = {}
                    myTransmission['module']=str(i)+'_'+str(n)
                    myTransmission['message_in']=str(i)+'_('+str(m[0])+"-"+str(m[1])+")"
                    myApp['transmission'].append(myTransmission)


    appsTotalMIPS.append(totalMIPS)




    #TODO decidir si quiero el grafo dirigido o no dirigido
#    for idx in range(0,len(apps)):
#        apps[idx] = apps[idx].to_undirected()
#
#


    appJson.append(myApp)


file = open("appDefinition.json","w")
file.write(json.dumps(appJson))
file.close()



#****************************************************************************************************
#Generacion de los IoT devices (users) que requestean cada aplciacion
#****************************************************************************************************

userJson ={}


myUsers=list()

appsRequests = list()
for i in range(0,TOTALNUMBEROFAPPS):
    userRequestList = set()
    probOfRequested = eval(func_REQUESTPROB)
    atLeastOneAllocated = False
    for j in gatewaysDevices:
        if random.random()<probOfRequested:
            myOneUser={}
            myOneUser['app']=str(i)
            myOneUser['message']="M.USER.APP."+str(i)
            myOneUser['id_resource']=j
            myOneUser['lambda']=eval(func_USERREQRAT)
            userRequestList.add(j)
            myUsers.append(myOneUser)
            atLeastOneAllocated = True
    if not atLeastOneAllocated:
        j=random.randint(0,len(gatewaysDevices)-1)
        myOneUser={}
        myOneUser['app']=str(i)
        myOneUser['message']="M.USER.APP."+str(i)
        myOneUser['id_resource']=j
        myOneUser['lambda']=eval(func_USERREQRAT)
        userRequestList.add(j)
        myUsers.append(myOneUser)
    appsRequests.append(userRequestList)

userJson['sources']=myUsers

file = open("usersDefinition.json","w")
file.write(json.dumps(userJson))
file.close()


#****************************************************************************************************

#FIN GENERACION MODELO

#****************************************************************************************************



#****************************************************************************************************

#INICIO OPTIMIZATION

#****************************************************************************************************


service2DevicePlacementMatrix = [[0 for j in xrange(len(G.nodes))] for i in xrange(numberOfServices)]

community2AppPlacementDict = {}
for myCommunity in sortedCommunities:
    community2AppPlacementDict[myCommunity[0]]=set()

nodeBussyResources = {}
for i in G.nodes:
    nodeBussyResources[i]=0.0


#****************************************************************************************************
#****************************************************************************************************
#****************************************************************************************************
#****************************************************************************************************
#TODO BOOOOORRRAAAARRRRRRRRR
#for i in xrange(numberOfServices):
#    for j in xrange(len(G.nodes)):
#        if random.random()<0.1:
#            service2DevicePlacementMatrix[i][j]=1
#****************************************************************************************************
#****************************************************************************************************
#****************************************************************************************************
#****************************************************************************************************



sortedAppsDeadlines = sorted(appsDeadlines.items(), key=operator.itemgetter(1))

print "Starting placement policy....."

for appToAllocate in sortedAppsDeadlines:
    appId=appToAllocate[0]
    weightNetwork(appId)
    nodesWithClients = appsRequests[appId]
    for clientId in nodesWithClients:
        if verbose_log:
            print "Starting placement of app "+str(appId)+" for client "+str(clientId)
        placed_=False
        for myCommunity in sortedCommunities:
            if clientId in myCommunity[0]:
                if appId in community2AppPlacementDict[myCommunity[0]]:
                    if verbose_log:
                        print "    App "+str(appId)+" already placed in community "+str(myCommunity[0])
                    break
                else:
                    placed_,servicePlacement=placeAppInCommunity(appId, clientId, myCommunity[0])
                    if placed_:
                        if verbose_log:
                            print "    Performed allocation of app "+str(appId)+" in community "+str(myCommunity[0])
                        for servId,deviceId in servicePlacement.iteritems():
                            service2DevicePlacementMatrix[servId][deviceId]=1
                            nodeBussyResources[deviceId]=nodeBussyResources[deviceId]+appsResources[appId][servId]
                        community2AppPlacementDict[myCommunity[0]].add(appId)
                        placed_=True
                        break


writeStatisticsDevices(service2DevicePlacementMatrix)

servicesInCloud = 0
servicesInFog = 0

allAlloc = {}
myAllocationList = list()
for idServ in xrange(numberOfServices):
    for idDevice in xrange(len(G.nodes)):
        if service2DevicePlacementMatrix[idServ][idDevice]==1:
            myAllocation = {}
            myAllocation['app']=mapService2App[idServ]
            myAllocation['module_name']=mapServiceId2ServiceName[idServ]
            myAllocation['id_resource']=idDevice
            myAllocationList.append(myAllocation)
            servicesInFog = servicesInFog +1
    #Independientemente de la politica, todos los servicios estan en el cloud
    myAllocation = {}
    myAllocation['app']=mapService2App[idServ]
    myAllocation['module_name']=mapServiceId2ServiceName[idServ]
    myAllocation['id_resource']=cloudId
    myAllocationList.append(myAllocation)
    servicesInCloud = servicesInCloud +1



print "Number of services in cloud (partition) (servicesInCloud): "+str(servicesInCloud)
print "Number of services in fog (partition) (servicesInFog): "+str(servicesInFog)


allAlloc['initialAllocation']=myAllocationList

file = open("allocDefinition.json","w")
file.write(json.dumps(allAlloc))
file.close()

print str(time.time()-t)+" time for partition-based optimization"


#****************************************************************************************************
#****************************************************************************************************
#****************************************************************************************************
#****************************************************************************************************
#SOLUCION ILP
#****************************************************************************************************
#****************************************************************************************************
#****************************************************************************************************
#****************************************************************************************************


t = time.time()

if ILPoptimization:


    import pulp
    import itertools

#    includeCloud = False



    #def networkDelay(i):
    #    userId = i[0][0]
    #    devId = i[0][1]
    #    processTime=0.0
    #    #processTime = mips_ / float(devices[devId]['IPT']) # tiempo de ejecutar todos los servicios de la app
    #    netTime = nx.shortest_path_length(G,source=userId,target=devId,weight="weight")    #tiempo de red entre cliente y dispositivo
    #    return processTime + netTime


    print "Starting ILP optimization...."

    fognodes = list()
    for i in G.nodes:
        fognodes.append(i)
#    if includeCloud:
#        CLOUD_FAKEID = 9999999999
#        fognodes.append(CLOUD_FAKEID) #999999999 = CLOUD
    fognodes.append(cloudId)

    myServicesResources = {}

    for myapp in appsResources:
        for i in myapp.items():
            myServicesResources[i[0]]=i[1]


    myDevices = {}

    for i,v in enumerate(devices):
        myDevices[i]=v


#    if includeCloud:
#        myDevices[CLOUD_FAKEID]={}
#        myDevices[CLOUD_FAKEID]['RAM']=999999999999999999.9

    userServices = list()
    allTheGtws = set()

    numIoTDevices = 0

    for i,gtwList in enumerate(appsRequests):
        for gtwId in gtwList:
            numIoTDevices = numIoTDevices +1
            for servId in apps[i].nodes:
                userServices.append((gtwId,servId))
                allTheGtws.add(gtwId)


    networkdistances = {}
    for gtwId in allTheGtws:
        for devId in G.nodes:
            networkdistances[(gtwId,devId)]=nx.shortest_path_length(G,source=gtwId,target=devId,weight="weight")

#        if includeCloud:
#            networkdistances[(gtwId,CLOUD_FAKEID)]=999999999999999999.9
        networkdistances[(gtwId,cloudId)]=999999999999999999.9



    total_uservservices = len(userServices)
    total_fognodoes = len(fognodes)

    assignCombinations = list(itertools.product(userServices,fognodes))


    ##### Model
    ## Problem
    problem = pulp.LpProblem('fog', pulp.LpMinimize)


    print "Including variables...."
    ## Variables

    UserServiceDevAssignment = {comb: pulp.LpVariable('sa_%i_%i_%i' % (comb[0][0],comb[0][1], comb[1]), cat='Binary') for comb in assignCombinations}

    ## Objective

    print "Including objectives..."
    problem += pulp.lpSum([
        (
            UserServiceDevAssignment[i] * networkDelay(i)
        ) for i in assignCombinations
    ]), 'Objective'

    # Constraints

    print "Including constraints...."
    # at least one service instantiated for each user
    for usrservId in userServices:

        problem += pulp.lpSum([(UserServiceDevAssignment[(usrservId,devId)] ) for devId in fognodes]) == 1 , 'TaskAssignmentLowerBound_' + str(usrservId)
      #  problem += pulp.lpSum([(UserServiceDevAssignment[(usrservId,devId)] ) for devId in fognodes]) <= 1 , 'TaskAssignmentUpperBound_' + str((usrservId,devId))

    # allocated services less resources than available

    for devId in fognodes:
        problem += pulp.lpSum([(UserServiceDevAssignment[(usrservId,devId)]* myServicesResources[usrservId[1]] ) for usrservId in userServices])<= myDevices[devId]['RAM'], 'DeviceCapacity_' +str(devId)
    #    problem += sum([(UserServiceDevAssignment[(usrservId,devId)]* myServicesResources[usrservId[1]] ) for usrservId in userServices])> -1.0, 'DeviceCapacity_' +str(devId)


    print "************"
    print "Number of nodes (myDevices): "+str(len(myDevices))
    print "Number of services (myServicesResources): "+str(len(myServicesResources))
    print "Number of gateways (allTheGtws): "+str(len(allTheGtws))
    print "Number of IoT devices (numIoTDevices): "+str(numIoTDevices)
    print "Number of IoT devices X services (userServices): "+str(len(userServices))
    print "Number of ILP variables (assignCombinations): "+str(len(assignCombinations))
    print "************"

    print "Solving the problem..."
    problem.solve()


    allAlloc = {}
    myAllocationList = list()

    print "The ILP finished in status "+str(problem.status)

    servicesInCloud = 0
    servicesInFog = 0

    if problem.status == pulp.LpStatusOptimal:
        for i in assignCombinations:
            if UserServiceDevAssignment[i].value() > 0.0:
                if verbose_log:
                    print "-------"
                    print i
                    print UserServiceDevAssignment[i].value()
                assignResult = UserServiceDevAssignment[i].value()
                myAllocation = {}
                if i[0][1]==cloudId:
                    servicesInCloud = servicesInCloud+1
                else:
                    servicesInFog = servicesInFog +1
                    myAllocation['app']=mapService2App[i[0][1]]
                    myAllocation['module_name']=mapServiceId2ServiceName[i[0][1]]
                    myAllocation['id_resource']=i[1]
                    myAllocationList.append(myAllocation)
                    writeStatisticsAllocationILP(i[0][0],i[0][1],i[1]) #clientId, serviceId,devId
                    writeStatisticsDevicesILP(i[0][1],i[1]) #serviceId,devId

        for idServ in xrange(numberOfServices):
            #Independientemente de la politica, todos los servicios estan en el cloud
            myAllocation = {}
            myAllocation['app']=mapService2App[idServ]
            myAllocation['module_name']=mapServiceId2ServiceName[idServ]
            myAllocation['id_resource']=cloudId
            myAllocationList.append(myAllocation)
            servicesInCloud = servicesInCloud+1



        normalizeStatisticsDevicesILP()


    print "Number of services in cloud (ILP) (servicesInCloud): "+str(servicesInCloud)
    print "Number of services in fog (ILP) (servicesInFog): "+str(servicesInFog)


    allAlloc['initialAllocation']=myAllocationList

    file = open("allocDefinitionILP.json","w")
    file.write(json.dumps(allAlloc))
    file.close()


print str(time.time()-t)+" time for ILP-based optimization"


#****************************************************************************************************
#****************************************************************************************************
#****************************************************************************************************
#****************************************************************************************************
#FIN ILP
#****************************************************************************************************
#****************************************************************************************************
#****************************************************************************************************
#****************************************************************************************************




if generatePlots:

    #(deadline,shortestdistance):occurrences
    #statisticsDistanceDeadline = {}

    ####GRAFICO deadline vs distance

    import numpy as np
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    #
    ## Fixing random state for reproducibility
    #np.random.seed(19680801)
    #
    #
    #N = 50

    x=list()
    y=list()
    area=list()

    for i in statisticsDistanceDeadline.items():
        x.append(i[0][1])
        y.append(i[0][0])
        area.append(i[1])

    xILP=list()
    yILP=list()
    areaILP=list()

    for i in statisticsDistanceDeadlineILP.items():

        xILP.append(i[0][1])
        yILP.append(i[0][0])
        areaILP.append(i[1])

    #x = np.random.rand(N)
    #y = np.random.rand(N)
    #colors = np.random.rand(N)
    #area = (30 * np.random.rand(N))**2  # 0 to 15 point radii
    #
    #plt.scatter(x, y, s=area, c='blue', alpha=0.5)
    #plt.show()
    fig, ax = plt.subplots(figsize=(8.0,8.0))
    #fig = plt.figure()
    #fig.suptitle("blablabla", fontsize=18)
    plt.xlabel('distance',fontsize=24)
    plt.ylabel('deadline',fontsize=24)


    plt.scatter(x, y, s=map(lambda x: x * 100,area), c='blue', alpha=0.5,label='partition')
    plt.scatter(xILP, yILP, s=map(lambda x: x * 100,areaILP), c='red', alpha=0.5, label='ilp',marker="X")
    lgnd=plt.legend(fontsize=20,loc='upper left', bbox_to_anchor=(0.15, 1.12),ncol=2)
    plt.yticks(fontsize=24)
    plt.xticks(fontsize=24)

    for handle in lgnd.legendHandles:
        handle.set_sizes([150.0])

    plt.grid()
    if graphicTerminal:
        plt.show()

    fig.savefig('./plots/deadlinevsdistance.pdf',format='pdf')

    plt.close(fig)



    #(service,deadline):occurrences
    #statisticsServiceInstances = {}

    #(deadline,instances):ocurrences
    poststatisticsServiceInstances = {}

    for i in statisticsServiceInstances.items():
        mydeadline_=appsDeadlines[int(mapService2App[i[0][0]])]
        myInstances_=i[1]
        mykey_=(mydeadline_,myInstances_)
        if mykey_ in poststatisticsServiceInstances:
            poststatisticsServiceInstances[mykey_]=poststatisticsServiceInstances[mykey_]+1
        else:
            poststatisticsServiceInstances[mykey_]=1


    #(service,deadline):occurrences
    #statisticsServiceInstances = {}

    #(deadline,instances):ocurrences
    poststatisticsServiceInstancesILP = {}

    for i in statisticsServiceInstancesILP.items():
        mydeadline_=appsDeadlines[int(mapService2App[i[0][0]])]
        myInstances_=i[1]
        mykey_=(mydeadline_,myInstances_)
        if mykey_ in poststatisticsServiceInstancesILP:
            poststatisticsServiceInstancesILP[mykey_]=poststatisticsServiceInstancesILP[mykey_]+1
        else:
            poststatisticsServiceInstancesILP[mykey_]=1


    ####GRAFICO deadline vs instances

    x=list()
    y=list()
    area=list()

    for i in poststatisticsServiceInstances.items():
        x.append(i[0][0])
        y.append(i[0][1])
        area.append(i[1])

    xILP=list()
    yILP=list()
    areaILP=list()

    for i in poststatisticsServiceInstancesILP.items():
        xILP.append(i[0][0])
        yILP.append(i[0][1])
        areaILP.append(i[1])

    #x = np.random.rand(N)
    #y = np.random.rand(N)
    #colors = np.random.rand(N)
    #area = (30 * np.random.rand(N))**2  # 0 to 15 point radii
    #
    #plt.scatter(x, y, s=area, c='blue', alpha=0.5)
    #plt.show()
    fig, ax = plt.subplots(figsize=(8.0,8.0))
    #fig = plt.figure()
    #fig.suptitle("blablabla", fontsize=18)
    plt.xlabel('deadline',fontsize=24)
    plt.ylabel('number of instances',fontsize=24)

    plt.scatter(x, y, s=map(lambda x: x * 100,area), c='blue', alpha=0.5,label='partition')
    plt.scatter(xILP, yILP, s=map(lambda x: x * 100,areaILP), c='red', alpha=0.5,label='ilp',marker="X")
    lgnd=plt.legend(fontsize=20,loc='upper left', bbox_to_anchor=(0.15, 1.12),ncol=2)
    plt.yticks(fontsize=24)
    plt.xticks(fontsize=18)

    for handle in lgnd.legendHandles:
        handle.set_sizes([150.0])

    plt.grid()
    if graphicTerminal:
        plt.show()

    fig.savefig('./plots/deadlinevsinstances.pdf',format='pdf')

    plt.close(fig)





    ####GRAFICO centrality vs resource
    #(centrality,resources):occurrences
    #statisticsCentralityResources = {}

    x=list()
    y=list()
    area=list()

    for i in statisticsCentralityResources.items():
        x.append(i[0][0])
        y.append(i[0][1])
        area.append(i[1])

    xILP=list()
    yILP=list()
    areaILP=list()

    for i in statisticsCentralityResourcesILP.items():
        xILP.append(i[0][0])
        yILP.append(i[0][1])
        areaILP.append(i[1])

    #x = np.random.rand(N)
    #y = np.random.rand(N)
    #colors = np.random.rand(N)
    #area = (30 * np.random.rand(N))**2  # 0 to 15 point radii
    #
    #plt.scatter(x, y, s=area, c='blue', alpha=0.5)
    #plt.show()
    fig, ax = plt.subplots(figsize=(8.0,8.0))
    #fig = plt.figure()
    #fig.suptitle("blablabla", fontsize=18)
    plt.xlabel('centrality',fontsize=24)
    plt.ylabel('resource usage',fontsize=24)

    plt.scatter(x, y, s=map(lambda x: x * 100,area), c='blue', alpha=0.5,label='partition')
    plt.scatter(xILP, yILP, s=map(lambda x: x * 100,areaILP), c='red', alpha=0.5,label='ilp',marker="X")
    lgnd=plt.legend(fontsize=20,loc='upper left', bbox_to_anchor=(0.15, 1.12),ncol=2)
    plt.yticks(fontsize=24)
    plt.xticks(fontsize=24)

    for handle in lgnd.legendHandles:
        handle.set_sizes([150.0])

    plt.grid()
    if graphicTerminal:
        plt.show()

    fig.savefig('./plots/centralityvsresources.pdf',format='pdf')

    plt.close(fig)



    ####GRAFICO distance vs request
    #distance:request
    #statisticsCentralityResources = {}

    x=list()
    y=list()


    for i in statisticsDistancesRequest.items():
        x.append(i[0])
        y.append(i[1])


    xILP=list()
    yILP=list()

    for i in statisticsDistancesRequestILP.items():
        xILP.append(i[0])
        yILP.append(i[1])


    #x = np.random.rand(N)
    #y = np.random.rand(N)
    #colors = np.random.rand(N)
    #area = (30 * np.random.rand(N))**2  # 0 to 15 point radii
    #
    #plt.scatter(x, y, s=area, c='blue', alpha=0.5)
    #plt.show()


    fig, ax = plt.subplots(figsize=(8.0,8.0))
    #fig = plt.figure()
    #fig.suptitle("blablabla", fontsize=18)
    plt.xlabel('distance',fontsize=24)
    plt.ylabel('number of IoT devices',fontsize=24)

    plt.scatter(x, y,s=100, c='blue', alpha=0.5,label='partition')
    plt.scatter(xILP, yILP,s=100, c='red', alpha=0.5,label='ilp',marker="X")
    lgnd=plt.legend(fontsize=20,loc='upper left', bbox_to_anchor=(0.15, 1.12),ncol=2)
    plt.yticks(fontsize=24)
    plt.xticks(fontsize=24)

    for handle in lgnd.legendHandles:
        handle.set_sizes([150.0])

    plt.grid()
    if graphicTerminal:
        plt.show()

    fig.savefig('./plots/distancevsrequest.pdf',format='pdf')

    plt.close(fig)




    ####GRAFICO node id vs requests
    #nodeid:request
    #statisticsNodesRequest = {}

    x=list()
    y=list()


    for i in statisticsNodesRequest.items():
        x.append(i[0])
        y.append(i[1])


    xILP=list()
    yILP=list()

    for i in statisticsNodesRequestILP.items():
        xILP.append(i[0])
        yILP.append(i[1])


    #x = np.random.rand(N)
    #y = np.random.rand(N)
    #colors = np.random.rand(N)
    #area = (30 * np.random.rand(N))**2  # 0 to 15 point radii
    #
    #plt.scatter(x, y, s=area, c='blue', alpha=0.5)
    #plt.show()


    fig, ax = plt.subplots(figsize=(8.0,8.0))
    #fig = plt.figure()
    #fig.suptitle("blablabla", fontsize=18)
    plt.xlabel('device ids',fontsize=24)
    plt.ylabel('number of IoT devices',fontsize=24)

    plt.scatter(x, y,s=100, c='blue', alpha=0.5,label='partition')
    plt.scatter(xILP, yILP,s=100, c='red', alpha=0.5,label='ilp',marker="X")
    lgnd=plt.legend(fontsize=20,loc='upper left', bbox_to_anchor=(0.15, 1.12),ncol=2)
    plt.yticks(fontsize=24)
    plt.xticks(fontsize=24)

    for handle in lgnd.legendHandles:
        handle.set_sizes([150.0])

    plt.grid()
    if graphicTerminal:
        plt.show()

    fig.savefig('./plots/nodeidvsrequest.pdf',format='pdf')

    plt.close(fig)





    ####GRAFICO nodeid vs serviceid
    #(nodeid,serviceid):occurrences
    #statisticsNodesServicesILP = {}

    x=list()
    y=list()
    area=list()

    for i in statisticsNodesServices.items():
        x.append(i[0][0])
        y.append(i[0][1])
        area.append(i[1])

    xILP=list()
    yILP=list()
    areaILP=list()

    for i in statisticsNodesServicesILP.items():
        xILP.append(i[0][0])
        yILP.append(i[0][1])
        areaILP.append(i[1])

    #x = np.random.rand(N)
    #y = np.random.rand(N)
    #colors = np.random.rand(N)
    #area = (30 * np.random.rand(N))**2  # 0 to 15 point radii
    #
    #plt.scatter(x, y, s=area, c='blue', alpha=0.5)
    #plt.show()
    fig, ax = plt.subplots(figsize=(8.0,8.0))
    #fig = plt.figure()
    #fig.suptitle("blablabla", fontsize=18)


    major_ticks = np.arange(-100, 101, 5)
    minor_ticks = np.arange(-100, 101, 1)




    ax.set_xticks(major_ticks)
    ax.set_xticks(minor_ticks, minor=True)
    ax.set_yticks(major_ticks)
    ax.set_yticks(minor_ticks, minor=True)

        # Or if you want different settings for the grids:
#    ax.grid(which='minor', alpha=0.2)
#    ax.grid(which='major', alpha=0.5)
    ax.grid(which='both', alpha=0.5)

    plt.xlabel('node id',fontsize=24)
    plt.ylabel('service id',fontsize=24)

    plt.scatter(x, y, s=map(lambda x: x * 100,area), c='blue', alpha=0.5,label='partition')
    plt.scatter(xILP, yILP, s=map(lambda x: x * 100,areaILP), c='red', alpha=0.5,label='ilp',marker="X")
    lgnd=plt.legend(fontsize=20,loc='upper left', bbox_to_anchor=(0.15, 1.12),ncol=2)
    plt.yticks(fontsize=24)
    plt.xticks(fontsize=24)

    for handle in lgnd.legendHandles:
        handle.set_sizes([150.0])

    #plt.grid()
    if graphicTerminal:
        plt.show()

    fig.savefig('./plots/nodeidvsservid.pdf',format='pdf')

    plt.close(fig)







#top_level_communities = next(communities_generator)
#next_level_communities = next(communities_generator)
#sorted(map(sorted, next_level_communities))
#
#
#
#
#
#
#
#for next_level_communities in itertools.islice(communities_generator,100):
#    print next_level_communities
#
#
#
#dendrogram = generate_dendrogram(G)
#for level in range(len(dendrogram) - 1) :
#    print("partition at level", level, "is", partition_at_level(dendrogram, level))  # NOQA
#
#
#limited = itertools.takewhile(lambda c: True, communities_generator)
#for myCommunity in limited:
#        print myCommunity
#
#
#[[0, 1, 2, 3, 4], [5], [6, 7, 8, 9, 10]]
