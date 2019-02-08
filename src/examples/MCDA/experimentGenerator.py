#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 16 12:41:44 2018

@author: isaaclera
"""

import re
import networkx as nx
import json
import random

import numpy as np

CLOUDCAPACITY = 9999999999999999
CLOUDSPEED = 9999
CLOUDBW = 999
CLOUDPOWERmin = 5000
CLOUDPOWERmax = 10000
CLOUDPR = 99

PERCENTATGEOFGATEWAYS = 0.2

# EDGE CONFIGURATION
func_PROPAGATIONTIME = "random.randint(5,20)" #it is change by the tier node value
func_BANDWITDH = "random.randint(10,20)"

# NODE CONFIG
func_NODERESOURECES = "random.randint(1,1)" #random distribution for the resources of the fog devices
func_NODESPEED = "random.randint(20,60)" #random distribution for the speed of the fog devices

func_POWERmax = "random.randint(400,1000)"
func_POWERmin = "random.randint(50,300)"
    
# USER CONFIG.
func_REQUESTPROB=".08"
func_USERREQRAT="random.randint(100,1000)"    

#APP and SERVICES
TOTALNUMBEROFAPPS = 10
func_APPGENERATION = "nx.gn_graph(random.randint(2,10))" #algorithm for the generation of the random applications
func_SERVICEINSTR = "random.randint(20000,60000)" #INSTR --> teniedno en cuenta nodespped esto nos da entre 200 y 600 MS
func_SERVICEMESSAGESIZE = "random.randint(1500000,4500000)" #BYTES y teniendo en cuenta net bandwidth nos da entre 20 y 60 MS

func_SERVICERESOURCES = "random.randint(1,6)" #MB de ram que consume el servicio, teniendo en cuenta noderesources y appgeneration tenemos que nos caben aprox 1 app por nodo o unos 10 servicios

func_APPDEADLINE="random.randint(2600,6600)" #MS

myDeadlines = [487203.22, 487203.22,487203.22,474.51,302.05,831.04,793.26,1582.21,2214.64,374046.40,420476.14,2464.69,97999.14,2159.73,915.16,1659.97,1059.97,322898.56,1817.51,406034.73]

#pathGML ="topology/test_GLP.gml"

def networkGeneration(pathTXT,idcloud): 
    #****************************************************************************************************
    #generation of the network topology
    #****************************************************************************************************

    #TOPOLOGY GENERATION
  
    cloudgatewaysDevices = list()
    G = nx.Graph()
    tiers = {}
    with open(pathTXT, "r") as f:
        f = open(pathTXT, "r")
        for line in f.readlines():
            # There is no documented aShiip format but we assume that if the line
            # does not start with a number it is not part of the topology
            if line[0].isdigit():
                node_ids = re.findall("\d+", line)
                if len(node_ids) < 3:
                    raise ValueError('Invalid input file. Parsing failed while '\
                                     'trying to parse a line')
                node = int(node_ids[0])-1 
                # THE FIRST NODES is ZERO-id
                level = int(node_ids[1])
                tiers[node] = level
                if level >=4 and node != idcloud:
                    cloudgatewaysDevices.append(node)
                    
                G.add_node(node, level=level)
                for i in range(2, len(node_ids)):
                    G.add_edge(node, int(node_ids[i])-1)
    
    nx.write_gexf(G,"topology/tempora-network.gexf")
    nodeResources = {}
    nodeSpeed = {}
    nodePower_min = {}
    nodePower_max = {}
    for i in G.nodes:
        nodeResources[i]=eval(func_NODERESOURECES)
        nodeSpeed[i]=eval(func_NODESPEED)
        nodePower_min[i]=eval(func_POWERmin)
        nodePower_max[i]=nodePower_min[i]+eval(func_POWERmax)
    
    print tiers
    for e in G.edges:
        tier = tiers[e[0]]
        if tier<tiers[e[1]]: #getMAX
            tier = tiers[e[1]]
#        print tier
        pr = eval(func_PROPAGATIONTIME)*tier
        print pr
        G[e[0]][e[1]]['PR']= pr
        bw = int(eval(func_BANDWITDH)*(1.0/float(tier)))
#        print bw
        G[e[0]][e[1]]['BW']=bw
    
    
    #JSON EXPORT
    netJson={}
    devices = list()
    myEdges = list()
    
    for i in G.nodes:
        if i == int(idcloud):
            myNode ={}
            myNode['id']=i
            myNode['RAM']=CLOUDCAPACITY
            myNode['IPT']=CLOUDSPEED
            myNode['POWERmin']=CLOUDPOWERmin
            myNode['POWERmax']=CLOUDPOWERmax
            myNode['type']='CLOUD'
            devices.append(myNode)
        else:
            myNode ={}
            myNode['id']=i
            myNode['RAM']=nodeResources[i]
            myNode['IPT']=nodeSpeed[i]
            myNode['POWERmin']=nodePower_min[i]
            myNode['POWERmax']=nodePower_max[i]
            devices.append(myNode)
        
    for e in G.edges:
        myLink={}
        myLink['s']=e[0]
        myLink['d']=e[1]
        myLink['PR']=G[e[0]][e[1]]['PR']
        myLink['BW']=G[e[0]][e[1]]['BW']
        myEdges.append(myLink)
   
    
    netJson['entity']=devices
    netJson['link']=myEdges
    
    return netJson,cloudgatewaysDevices,G
    
def userGeneration(id_gateways,G):
        #****************************************************************************************************
        #generation of the IoT devices (users) 
        #****************************************************************************************************

        level = nx.get_node_attributes(G, 'level')
        ll = {x: y for x, y in level.items() if y > 3}

        userJson ={}
       
        myUsers=list()
        
        appsRequests = list()
        for i in range(TOTALNUMBEROFAPPS):
            userRequestList = set()
            probOfRequested = eval(func_REQUESTPROB)
            atLeastOneAllocated = False
            for j in ll.keys():
                j = int(j)
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
#                j=random.randint(0,len(id_gateways)-1)
                j=random.choice(ll.keys())
                j = int(j)
                myOneUser={}
                myOneUser['app']=str(i)
                myOneUser['message']="M.USER.APP."+str(i)
                myOneUser['id_resource']=j
                myOneUser['lambda']=eval(func_USERREQRAT)
                userRequestList.add(j)
                myUsers.append(myOneUser)
            appsRequests.append(userRequestList)
        
        print "Usuarios creados : %i "%len(myUsers)
        userJson['sources']=myUsers
        
        return userJson

def appGeneration():
    
    #****************************************************************************************************
    #application generation
    #****************************************************************************************************
    
    numberOfServices=0
    apps = list()
    appsDeadlines = {}
    appsResources = list()
    appsSourceService = list()
    appsSourceMessage = list()
    appsTotalMIPS = list()
    mapService2App = list()
    mapServiceId2ServiceName = list()
    
    appJson = list()
    servicesResources = {}
    
    
    for i in range(TOTALNUMBEROFAPPS):
        print "CREANDDO APP :%i "%i
        
        myApp = {}
        APP = eval(func_APPGENERATION)
    
        mylabels = {}
    
        for n in range(0,len(APP.nodes)):
            mylabels[n]=str(n)
    
        edgeList_=list()
    
        for m in APP.edges:
            edgeList_.append(m)
        for m in edgeList_:
            APP.remove_edge(m[0],m[1])
            APP.add_edge(m[1],m[0])
    
    
    
        mapping=dict(zip(APP.nodes(),range(numberOfServices,numberOfServices+len(APP.nodes))))
        APP=nx.relabel_nodes(APP,mapping)
    
        numberOfServices = numberOfServices + len(APP.nodes)
        apps.append(APP)
        for j in APP.nodes:
            servicesResources[j]=eval(func_SERVICERESOURCES)
        appsResources.append(servicesResources)
    
        topologicorder_ = list(nx.topological_sort(APP))
        source = topologicorder_[0]

    
        appsSourceService.append(source)
    
        
        #appsDeadlines[i]=eval(func_APPDEADLINE)
        appsDeadlines[i] = myDeadlines[i]
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
                
                for o in APP.edges:
                    if o[0]==source:
                        myTransmission = {}
                        myTransmission['module']=str(i)+'_'+str(source)
                        myTransmission['message_in']="M.USER.APP."+str(i)
                        myTransmission['message_out']=str(i)+'_('+str(o[0])+"-"+str(o[1])+")"
                        myApp['transmission'].append(myTransmission)

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
    
        appJson.append(myApp)
    return appJson
    
def initialAllocationCloud(apps,idcloud):
    mod = {}
    allc = []
    for app in apps:
        for module in app["module"]:
            allc.append({"module_name":module["name"],"app":app["name"],"id_resource":idcloud})
        
    mod["initialAllocation"] = allc
    return mod
        
if __name__ == '__main__':
    random.seed(0)

    pathTXT = "topology/GLP-400n-idc94.txt"
    pathTXT = "topology/GLP-200n-idc153.txt"

    idcloud = 153

    netjson,cloudgatewaysDevices,G = networkGeneration(pathTXT,idcloud)

    with open("topology/networkDefinition.json","w") as f:
        f.write(json.dumps(netjson))

    userJson = userGeneration(cloudgatewaysDevices,G)
    with open("topology/usersDefinition.json","w") as f:
        f.write(json.dumps(userJson))
        
    appJson = appGeneration()
    with open("topology/appDefinition.json","w") as f:
        f.write(json.dumps(appJson))

  
    initjson = initialAllocationCloud(appJson,idcloud)
    with open("topology/allocDefinitionMCDA.json","w") as f:
        f.write(json.dumps(initjson))

    
    
