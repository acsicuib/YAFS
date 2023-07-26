import json
import networkx as nx

import re
import random
from math import floor
import matplotlib.pyplot as plt

import operator
import json
import os

def placement_algorithm(graph, app_def='data/appDefinition.json'):

    # Alloc será o dicionario convertido para json
    alloc = dict()
    alloc['initialAllocation'] = list()

    apps = json.load(open(app_def))

    max_res = max([len(app['module']) for app in apps])   #
    min_res = min([len(app['module']) for app in apps])   #
    n_comms = 0

    # Decide-se o nr de communities max de forma a conseguir suportar a maior app (caso seja possivel)
    while n_comms < len(graph.nodes):
        temp_comms = nx.algorithms.community.asyn_fluidc(graph, n_comms+1)

        if all(len(x) < max_res for x in temp_comms) or any(len(x) < min_res for x in temp_comms):
            break

        n_comms += 1

    comms = nx.algorithms.community.asyn_fluidc(graph, n_comms)
    comms = [list(x) for x in list(comms)]

    for app in apps:
        for mod in app['module']:

            # Vai rodando até encontrar uma community que consiga suportar a app inteira
            while len(app['module']) > len(comms[0]) and n_comms != 1:
                comms.append(comms.pop(0))

            temp_dict = dict()
            temp_dict['module_name'] = mod['name']
            temp_dict['app'] = app['id']
            temp_dict['id_resource'] = comms[0][0]

            comms[0].append(comms[0].pop(0))

            alloc['initialAllocation'].append(temp_dict)

        # Se houver mais do que 1 community, roda
        if n_comms != 1:
            comms.append(comms.pop(0))

    with open('data/allocDefinition.json', 'w') as f:
        json.dump(alloc, f)


# func_POWERmax = "random.randint(400,1000)"
# func_POWERmin = "random.randint(50,300)"


CLOUDCAPACITY = 9999999999999999
CLOUDSPEED = 10000
CLOUDBW = 125000                  ## 1000 Mbits/s ou 125000 BYTES / MS ???
CLOUDPR = 500

PERCENTATGEOFGATEWAYS = 0.25

# EDGE CONFIGURATION
func_PROPAGATIONTIME = "random.randint(2,10)"  # it is change by the tier node value
func_BANDWITDH = "random.randint(75000,75000)"

# NODE CONFIG
func_NODERESOURECES = "random.randint(10,15)"  # random distribution for the resources of the fog devices
func_NODESPEED = "random.randint(500,1000)"  # random distribution for the speed of the fog devices

# USER CONFIG.
func_REQUESTPROB = "random.random()/4"
func_USERREQRAT = "random.randint(200,1000)"

# APP and SERVICES
TOTALNUMBEROFAPPS = 10
func_APPGENERATION = "nx.gn_graph(random.randint(2,8))"  # algorithm for the generation of the random applications
func_SERVICEINSTR = "random.randint(20000,60000)"  # INSTR --> teniedno en cuenta nodespped esto nos da entre 200 y 600 MS
func_SERVICEMESSAGESIZE = "random.randint(1500000,4500000)"  # BYTES y teniendo en cuenta net bandwidth nos da entre 20 y 60 MS

func_SERVICERESOURCES = "random.randint(1,5)"  # MB de ram que consume el servicio, teniendo en cuenta noderesources y appgeneration tenemos que nos caben aprox 1 app por nodo o unos 10 servicios

func_APPDEADLINE="random.randint(2600,6600)" #MS


func_NETWORKGENERATION = "nx.barabasi_albert_graph(n, m=2)"





"""
def networkGeneration(pathTXT, idcloud):
    # ****************************************************************************************************
    # generation of the network topology
    # ****************************************************************************************************

    # TOPOLOGY GENERATION

    cloudgatewaysDevices = list()
    G = eval(func_NETWORKGENERATION)

    # pos = nx.spring_layout(G)
    # nx.draw(G, pos=pos)

    tiers = {}
    
    #with open(pathTXT, "r") as f:
    #f = open(pathTXT, "r")
    #for line in f.readlines():
    #    # There is no documented aShiip format but we assume that if the line
    #    # does not start with a number it is not part of the topology
    #    if line[0].isdigit():
    #        node_ids = re.findall("\d+", line)
    #        if len(node_ids) < 3:
    #            raise ValueError('Invalid input file. Parsing failed while ' \
    #                             'trying to parse a line')
    #        node = int(node_ids[0]) - 1
    #        # THE FIRST NODES is ZERO-id
    #        level = int(node_ids[1])
    #        tiers[node] = level
    #        if level >= 4 and node != idcloud:
    #            cloudgatewaysDevices.append(node)

    #        G.add_node(node, level=level)
    #        for i in range(2, len(node_ids)):
    #            G.add_edge(node, int(node_ids[i]) - 1)

    for node in G.nodes:
        prob = random.random()

        if node == 0:
            tiers[node] = 1
        elif prob < 0.5:
            tiers[node] = 2
        elif prob < 0.75:
            tiers[node] = 3
        else:
            tiers[node] = 4
            if node != idcloud:
                cloudgatewaysDevices.append(node)

    plt.figure()

    label_tier = dict()
    for node in G:
        label_tier[node] = str(node) + ': ' + str(tiers[node])

    pos = nx.spring_layout(G)
    nx.draw_networkx_labels(G, pos, labels=label_tier, font_size=8)
    nx.draw_networkx(G, pos, with_labels=False)

    plt.show()


    nx.write_gexf(G, "topology/tempora-network.gexf")

    nodeResources = {}
    nodeSpeed = {}
    nodePower_min = {}
    nodePower_max = {}
    for i in G.nodes:
        nodeResources[i] = eval(func_NODERESOURECES)
        nodeSpeed[i] = eval(func_NODESPEED)

    print(tiers)
    for e in G.edges:
        tier = tiers[e[0]]
        if tier < tiers[e[1]]:  # getMAX
            tier = tiers[e[1]]
        #        print(tier)
        pr = eval(func_PROPAGATIONTIME) * tier
        print(pr)
        G[e[0]][e[1]]['PR'] = pr
        bw = int(eval(func_BANDWITDH) * (1.0 / float(tier)))
        #        print(bw)
        G[e[0]][e[1]]['BW'] = bw

    # JSON EXPORT
    netJson = {}
    devices = list()
    myEdges = list()

    for i in G.nodes:
        if i == int(idcloud):
            myNode = {}
            myNode['id'] = i
            myNode['RAM'] = CLOUDCAPACITY
            myNode['IPT'] = CLOUDSPEED
            myNode['type'] = 'CLOUD'
            devices.append(myNode)
        else:
            myNode = {}
            myNode['id'] = i
            myNode['RAM'] = nodeResources[i]
            myNode['IPT'] = nodeSpeed[i]
            devices.append(myNode)

    for e in G.edges:
        myLink = {}
        myLink['s'] = e[0]
        myLink['d'] = e[1]
        myLink['PR'] = G[e[0]][e[1]]['PR']
        myLink['BW'] = G[e[0]][e[1]]['BW']
        myEdges.append(myLink)

    netJson['entity'] = devices
    netJson['link'] = myEdges

    return netJson, cloudgatewaysDevices, G
"""






def networkGeneration(n=20, m=2, path=''):
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

    for cloudGtw in cloudgatewaysDevices:
        myLink = {}
        myLink['s'] = cloudGtw
        myLink['d'] = cloudId
        myLink['PR'] = CLOUDPR
        myLink['BW'] = CLOUDBW

        myEdges.append(myLink)

    netJson['entity'] = devices
    netJson['link'] = myEdges

    with open(os.path.dirname(__file__) + '\\' + path + "\\netDefinition.json", "w") as netFile:
        netFile.write(json.dumps(netJson))

    return G


x = networkGeneration(5)
print()
