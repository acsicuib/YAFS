import os
import time
import json
import random
import logging.config

import networkx as nx
from pathlib import Path
import matplotlib.pyplot as plt

import pandas as pd
import numpy as np

from yafs.core import Sim
from yafs.application import create_applications_from_json
from yafs.topology import Topology

from yafs.placement import JSONPlacement
from yafs.path_routing import DeviceSpeedAwareRouting
from yafs.selection import First_ShortestPath
from yafs.bw_path_selection import MyPathSelector
from yafs.distribution import deterministic_distribution
from yafs.plot import plot_app_path, plot_latency, plot_messages_node, plot_occurrences



def networkGeneration():
    # Generation of the network topology

    # Topology genneration

    G = eval(func_NETWORKGENERATION)

    devices = list()

    nodeResources = {}
    nodeFreeResources = {}
    nodeSpeed = {}
    for i in G.nodes:
        nodeResources[i] = eval(func_NODERESOURECES)
        nodeSpeed[i] = eval(func_NODESPEED)

    for e in G.edges:
        G[e[0]][e[1]]['PR'] = eval(func_PROPAGATIONTIME)
        G[e[0]][e[1]]['BW'] = eval(func_BANDWITDH)

    # JSON EXPORT

    netJson = {}

    for i in G.nodes:
        myNode = {}
        myNode['id'] = i
        myNode['RAM'] = nodeResources[i]
        myNode['FRAM'] = nodeResources[i]
        myNode['IPT'] = nodeSpeed[i]
        devices.append(myNode)

    myEdges = list()
    for e in G.edges:
        myLink = {}
        myLink['s'] = e[0]
        myLink['d'] = e[1]
        myLink['PR'] = G[e[0]][e[1]]['PR']
        myLink['BW'] = G[e[0]][e[1]]['BW']

        myEdges.append(myLink)

    centralityValuesNoOrdered = nx.betweenness_centrality(G, weight="weight")
    centralityValues = sorted(centralityValuesNoOrdered.items(), key=operator.itemgetter(1), reverse=True)

    gatewaysDevices = set()
    cloudgatewaysDevices = set()

    highestCentrality = centralityValues[0][1]

    for device in centralityValues:
        if device[1] == highestCentrality:
            cloudgatewaysDevices.add(device[0])

    initialIndx = int(
        (1 - PERCENTATGEOFGATEWAYS) * len(G.nodes))  # Getting the indexes for the GWs nodes

    for idDev in range(initialIndx, len(G.nodes)):
        gatewaysDevices.add(centralityValues[idDev][0])

    cloudId = len(G.nodes)
    myNode = {}
    myNode['id'] = cloudId
    myNode['RAM'] = CLOUDCAPACITY
    myNode['FRAM'] = CLOUDCAPACITY
    myNode['IPT'] = CLOUDSPEED
    myNode['type'] = 'CLOUD'
    devices.append(myNode)
    # Adding Cloud's resource to nodeResources
    nodeResources[cloudId] = CLOUDCAPACITY
    # At the begging all the resources on the nodes are free
    nodeFreeResources = nodeResources

    for cloudGtw in cloudgatewaysDevices:
        myLink = {}
        myLink['s'] = cloudGtw
        myLink['d'] = cloudId
        myLink['PR'] = CLOUDPR
        myLink['BW'] = CLOUDBW

        myEdges.append(myLink)

    netJson['entity'] = devices
    netJson['link'] = myEdges

    with open(os.path.dirname(_file_) + '\\' + "\\netDefinition.json", "w") as netFile:
        netFile.write(json.dumps(netJson))