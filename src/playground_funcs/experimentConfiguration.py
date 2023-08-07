import networkx as nx
import operator
import matplotlib.pyplot as plt
import json
import os
import random
import numpy as np
import csv
import copy

from docplex.mp.model import Model
from datetime import datetime
# from itertools import izip

nodeAttributes = {}
LINK_BW = "BW"
LINK_PR = "PR"
NODE_IPT = "IPT"

class experimentConfiguration:

    def __init__(self):
        # Cloud
        self.CLOUDCAPACITY = 9999999999999999
        self.CLOUDSPEED = 10000 # INSTR x MS
        self.CLOUDBW = 125000 # BYTES / MS --> 1000 Mbits/s
        self.CLOUDPR = 500 # MS

        # Network
        self.PERCENTATGEOFGATEWAYS = 0.25
        self.func_PROPAGATIONTIME = "random.randint(2,10)" # MS
        self.func_BANDWITDH = "random.randint(75000,75000)" # BYTES / MS
        self.func_NETWORKGENERATION = "nx.barabasi_albert_graph(n=50, m=2)" # Algorithm for the generation of the network topology
        self.func_NODERESOURECES = "random.randint(10,25)" # MB RAM
        self.func_NODESPEED = "random.randint(500,1000)" # INTS / MS

        # Apps and Services (For future iterations. For now, 1 app → 1 module)
        self.TOTALNUMBEROFAPPS = 10
        self.func_APPGENERATION = "nx.gn_graph(random.randint(2,8))" # Algorithm for the generation of the random applications
        self.func_SERVICEINSTR = "random.randint(20000,60000)"  # INSTR --> Considering the nodespeed the values should be between 200 & 600 MS
        self.func_SERVICEMESSAGESIZE = "random.randint(1500000,4500000)" # BYTES --> Considering the BW the values should be between 20 & 60 MS
        self.func_SERVICERESOURCES = "random.randint(1,5)" # MB of RAM consumed by services. Considering noderesources & appgeneration it will be possible to allocate 1 app or +/- 10 services per node
        self.func_APPDEADLINE = "random.randint(2600,6600)" # MS

        # Users and  IoT devices (We can use these values as reference)
        self.func_REQUESTPROB = "random.random()/4" # App's popularity. This value defines the probability of a source request an application
        self.func_USERREQRAT = "random.randint(200,1000)" # MS

        # random.seed(15612357)
        self.FGraph = None

    def networkGeneration(self):
        # Generation of the network topology

        # Topology genneration

        self.G = eval(self.func_NETWORKGENERATION)

        self.devices = list()

        self.nodeResources = {}
        self.nodeFreeResources = {}
        self.nodeSpeed = {}
        for i in self.G.nodes:
            self.nodeResources[i] = eval(self.func_NODERESOURECES)
            self.nodeSpeed[i] = eval(self.func_NODESPEED)

        for e in self.G.edges:
            self.G[e[0]][e[1]]['PR'] = eval(self.func_PROPAGATIONTIME)
            self.G[e[0]][e[1]]['BW'] = eval(self.func_BANDWITDH)

        # JSON EXPORT

        netJson = {}

        for i in self.G.nodes:
            myNode = {}
            myNode['id'] = i
            myNode['RAM'] = self.nodeResources[i]
            myNode['FRAM'] = self.nodeResources[i]
            myNode['IPT'] = self.nodeSpeed[i]
            self.devices.append(myNode)

        myEdges = list()
        for e in self.G.edges:
            myLink = {}
            myLink['s'] = e[0]
            myLink['d'] = e[1]
            myLink['PR'] = self.G[e[0]][e[1]]['PR']
            myLink['BW'] = self.G[e[0]][e[1]]['BW']

            myEdges.append(myLink)

        centralityValuesNoOrdered = nx.betweenness_centrality(self.G, weight="weight")
        centralityValues = sorted(centralityValuesNoOrdered.items(), key=operator.itemgetter(1), reverse=True)

        self.gatewaysDevices = set()
        self.cloudgatewaysDevices = set()

        highestCentrality = centralityValues[0][1]

        for device in centralityValues:
            if device[1] == highestCentrality:
                self.cloudgatewaysDevices.add(device[0])

        initialIndx = int(
            (1 - self.PERCENTATGEOFGATEWAYS) * len(self.G.nodes))  # Getting the indexes for the GWs nodes

        for idDev in range(initialIndx, len(self.G.nodes)):
            self.gatewaysDevices.add(centralityValues[idDev][0])

        self.cloudId = len(self.G.nodes)
        myNode = {}
        myNode['id'] = self.cloudId
        myNode['RAM'] = self.CLOUDCAPACITY
        myNode['FRAM'] = self.CLOUDCAPACITY
        myNode['IPT'] = self.CLOUDSPEED
        myNode['type'] = 'CLOUD'
        self.devices.append(myNode)
        # Adding Cloud's resource to self.nodeResources
        self.nodeResources[self.cloudId] = self.CLOUDCAPACITY
        # At the begging all the resources on the nodes are free
        self.nodeFreeResources = self.nodeResources

        # Plotting the graph with all the element
        if self.cnf.graphicTerminal:
            self.FGraph = self.G
            self.FGraph.add_node(self.cloudId)
            for gw_node in list(self.cloudgatewaysDevices):
                self.FGraph.add_edge(gw_node, self.cloudId, PR=self.CLOUDPR, BW=self.CLOUDBW)
            fig, ax = plt.subplots()
            pos = nx.spring_layout(self.FGraph, seed=15612357)
            nx.draw(self.FGraph, pos)
            nx.draw_networkx_labels(self.FGraph, pos, font_size=8)
            plt.show()
            # Win
            fig.savefig(os.path.dirname(__file__) + '\\' + self.cnf.resultFolder + '\\plots\\netTopology.png')
            # Unix
            # fig.savefig(os.path.dirname(__file__) + '/' + self.cnf.resultFolder + '/plots/netTopology.png')
            plt.close(fig)  # close the figure


        for cloudGtw in self.cloudgatewaysDevices:
            myLink = {}
            myLink['s'] = cloudGtw
            myLink['d'] = self.cloudId
            myLink['PR'] = self.CLOUDPR
            myLink['BW'] = self.CLOUDBW

            myEdges.append(myLink)

        netJson['entity'] = self.devices
        netJson['link'] = myEdges

        # Win
        netFile = open(os.path.dirname(__file__) + '\\' + self.cnf.resultFolder + "\\netDefinition.json", "w")
        # Unix
        # netFile = open(os.path.dirname(__file__) + '/' + self.cnf.resultFolder + "/netDefinition.json", "w")
        netFile.write(json.dumps(netJson))
        netFile.close()

    def appGeneration(self):
        # Apps generation

        self.numberOfServices = 0
        self.apps = list()
        self.appsDeadlines = {}
        self.appsResources = list()
        self.appsSourceService = list()
        self.appsSourceMessage = list()
        self.appsTotalMIPS = list()
        self.appsTotalServices = list()
        self.mapService2App = list()
        self.mapServiceId2ServiceName = list()

        appJson = list()
        appJsonBE = list()
        appJsonDD = list()
        self.servicesResources = {}

        for i in range(0, self.TOTALNUMBEROFAPPS):
            myApp = {}
            myAppEB = {}
            myAppDD = {}
            APP = eval(self.func_APPGENERATION)

            mylabels = {}

            for n in range(0, len(APP.nodes)):
                mylabels[n] = str(n)

            edgeList_ = list()

            # Reverting the direction of the edges from Source to Modules

            for m in APP.edges:
                edgeList_.append(m)
            for m in edgeList_:
                APP.remove_edge(m[0], m[1])
                APP.add_edge(m[1], m[0])

            if self.cnf.graphicTerminal:
                fig, ax = plt.subplots()
                pos = nx.spring_layout(APP, seed=15612357)
                nx.draw(APP, pos, labels=mylabels, font_size=8)
                # Win
                fig.savefig(os.path.dirname(__file__) + '\\' + self.cnf.resultFolder + '\\plots\\app_%s.png' % i)
                # Unix
                # fig.savefig(os.path.dirname(__file__) + '/' + self.cnf.resultFolder + '/plots/app_%s.png' % i)
                plt.close(fig)  # close the figure
                plt.show()

            mapping = dict(zip(APP.nodes(), range(self.numberOfServices, self.numberOfServices + len(APP.nodes))))
            APP = nx.relabel_nodes(APP, mapping)

            self.numberOfServices = self.numberOfServices + len(APP.nodes)
            self.apps.append(APP)
            for j in APP.nodes:
                self.servicesResources[j] = eval(self.func_SERVICERESOURCES)
            self.appsResources.append(self.servicesResources)

            topologicorder_ = list(nx.topological_sort(APP))
            source = topologicorder_[0]

            self.appsSourceService.append(source)

            self.appsDeadlines[i] = self.myDeadlines[i]

            # Copies of the application's graph that will be use to create the extra app definitions
            APP_EB = APP.copy()
            APP_DD = APP.copy()

            myApp['id'] = i
            myApp['name'] = str(i)
            myApp['deadline'] = self.appsDeadlines[i]

            myApp['module'] = list()

            edgeNumber = 0
            myApp['message'] = list()

            myApp['transmission'] = list()

            totalMIPS = 0

            for n in APP.nodes:
                self.mapService2App.append(str(i))
                self.mapServiceId2ServiceName.append(str(i) + '_' + str(n))
                myNode = {}
                myNode['id'] = n
                myNode['name'] = str(i) + '_' + str(n)
                myNode['RAM'] = self.servicesResources[n]
                # myNode['FRAM'] = self.servicesResources[n]
                myNode['type'] = 'MODULE'
                if source == n:
                    myEdge = {}
                    myEdge['id'] = edgeNumber
                    edgeNumber = edgeNumber + 1
                    myEdge['name'] = "M.USER.APP." + str(i)
                    myEdge['s'] = "None"
                    myEdge['d'] = str(i) + '_' + str(n)
                    myEdge['instructions'] = eval(self.func_SERVICEINSTR)
                    totalMIPS = totalMIPS + myEdge['instructions']
                    myEdge['bytes'] = eval(self.func_SERVICEMESSAGESIZE)
                    myApp['message'].append(myEdge)
                    self.appsSourceMessage.append(myEdge)

                    print("Adding source message")

                    for o in APP.edges:
                        if o[0] == source:
                            myTransmission = {}
                            myTransmission['module'] = str(i) + '_' + str(source)
                            myTransmission['message_in'] = "M.USER.APP." + str(i)
                            myTransmission['message_out'] = str(i) + '_(' + str(o[0]) + "-" + str(o[1]) + ")"
                            myApp['transmission'].append(myTransmission)

                myApp['module'].append(myNode)

            for n in APP.edges:
                myEdge = {}
                myEdge['id'] = edgeNumber
                edgeNumber = edgeNumber + 1
                myEdge['name'] = str(i) + '_(' + str(n[0]) + "-" + str(n[1]) + ")"
                myEdge['s'] = str(i) + '_' + str(n[0])
                myEdge['d'] = str(i) + '_' + str(n[1])
                myEdge['instructions'] = eval(self.func_SERVICEINSTR)
                totalMIPS = totalMIPS + myEdge['instructions']
                myEdge['bytes'] = eval(self.func_SERVICEMESSAGESIZE)
                myApp['message'].append(myEdge)
                destNode = n[1]
                for o in APP.edges:
                    if o[0] == destNode:
                        myTransmission = {}
                        myTransmission['module'] = str(i) + '_' + str(n[1])
                        myTransmission['message_in'] = str(i) + '_(' + str(n[0]) + "-" + str(n[1]) + ")"
                        myTransmission['message_out'] = str(i) + '_(' + str(o[0]) + "-" + str(o[1]) + ")"
                        myApp['transmission'].append(myTransmission)

            for n in APP.nodes:
                outgoingEdges = False
                for m in APP.edges:
                    if m[0] == n:
                        outgoingEdges = True
                        break
                if not outgoingEdges:
                    for m in APP.edges:
                        if m[1] == n:
                            myTransmission = {}
                            myTransmission['module'] = str(i) + '_' + str(n)
                            myTransmission['message_in'] = str(i) + '_(' + str(m[0]) + "-" + str(m[1]) + ")"
                            myApp['transmission'].append(myTransmission)

            self.appsTotalMIPS.append(totalMIPS)
            self.appsTotalServices.append(len(APP.nodes()))

            appJson.append(myApp)

            # Creating the application with a loop between the source and the more distance node

            myAppEB['id'] = i
            myAppEB['name'] = str(i)
            myAppEB['deadline'] = self.appsDeadlines[i]

            myAppEB['module'] = list()

            edgeNumber = 0
            myAppEB['message'] = list()

            myAppEB['transmission'] = list()

            totalMIPS = 0

            # Getting the longest path in the graph
            longest_path = nx.dag_longest_path(APP)
            # More distance node from the source
            distance_node = longest_path[-1]

            if self.cnf.graphicTerminal:
                APP_EB.add_edges_from([(distance_node, source)])
                mapping1 = dict(zip(sorted(list(APP_EB.nodes())), range(0, len(APP_EB.nodes))))
                APP_EB = nx.relabel_nodes(APP_EB, mapping1)
                fig1, ax1 = plt.subplots()
                nx.draw(APP_EB, pos, labels=mylabels, font_size=8, ax=ax1)
                # Win
                fig1.savefig(os.path.dirname(__file__) + '\\' + self.cnf.resultFolder + '\\plots\\app_%s_EB.png' % i)
                # Unix
                # fig.savefig(os.path.dirname(__file__) + '/' + self.cnf.resultFolder + '/plots/app_%s_EB.png' % i)
                plt.close(fig1)  # close the figure
                plt.show()

            for n in APP.nodes:
                # self.mapService2App.append(str(i))
                # self.mapServiceId2ServiceName.append(str(i) + '_' + str(n))
                myNode = {}
                myNode['id'] = n
                myNode['name'] = str(i) + '_' + str(n)
                myNode['RAM'] = self.servicesResources[n]
                # myNode['FRAM'] = self.servicesResources[n]
                myNode['type'] = 'MODULE'
                if source == n:
                    myEdge = {}
                    myEdge['id'] = edgeNumber
                    edgeNumber = edgeNumber + 1
                    myEdge['name'] = "M.USER.APP." + str(i)
                    myEdge['s'] = "None"
                    myEdge['d'] = str(i) + '_' + str(n)
                    myEdge['instructions'] = eval(self.func_SERVICEINSTR)
                    totalMIPS = totalMIPS + myEdge['instructions']
                    myEdge['bytes'] = eval(self.func_SERVICEMESSAGESIZE)
                    myAppEB['message'].append(myEdge)
                    # self.appsSourceMessage.append(myEdge)

                    print("Adding source message")

                    for o in APP.edges:
                        if o[0] == source:
                            myTransmission = {}
                            myTransmission['module'] = str(i) + '_' + str(source)
                            myTransmission['message_in'] = "M.USER.APP." + str(i)
                            myTransmission['message_out'] = str(i) + '_(' + str(o[0]) + "-" + str(o[1]) + ")"
                            myAppEB['transmission'].append(myTransmission)

                myAppEB['module'].append(myNode)

            for n in APP.edges:
                myEdge = {}
                myEdge['id'] = edgeNumber
                edgeNumber = edgeNumber + 1
                myEdge['name'] = str(i) + '_(' + str(n[0]) + "-" + str(n[1]) + ")"
                myEdge['s'] = str(i) + '_' + str(n[0])
                myEdge['d'] = str(i) + '_' + str(n[1])
                myEdge['instructions'] = eval(self.func_SERVICEINSTR)
                totalMIPS = totalMIPS + myEdge['instructions']
                myEdge['bytes'] = eval(self.func_SERVICEMESSAGESIZE)
                myAppEB['message'].append(myEdge)
                # Creating the message that will be sent it between distance_node and source
                if n[1] == distance_node:
                    myEdge = {}
                    myEdge['id'] = edgeNumber
                    edgeNumber = edgeNumber + 1
                    myEdge['name'] = str(i) + '_(' + str(n[1]) + "-" + str(source) + ")"
                    myEdge['s'] = str(i) + '_' + str(n[1])
                    myEdge['d'] = str(i) + '_' + str(source)
                    myEdge['instructions'] = eval(self.func_SERVICEINSTR)
                    totalMIPS = totalMIPS + myEdge['instructions']
                    myEdge['bytes'] = eval(self.func_SERVICEMESSAGESIZE)
                    myAppEB['message'].append(myEdge)
                destNode = n[1]
                for o in APP.edges:
                    if o[0] == destNode:
                        myTransmission = {}
                        myTransmission['module'] = str(i) + '_' + str(n[1])
                        myTransmission['message_in'] = str(i) + '_(' + str(n[0]) + "-" + str(n[1]) + ")"
                        myTransmission['message_out'] = str(i) + '_(' + str(o[0]) + "-" + str(o[1]) + ")"
                        myAppEB['transmission'].append(myTransmission)

            for n in APP.nodes:
                outgoingEdges = False
                for m in APP.edges:
                    if m[0] == n:
                        outgoingEdges = True
                        break
                if not outgoingEdges:
                    for m in APP.edges:
                        if m[1] == n:
                            myTransmission = {}
                            myTransmission['module'] = str(i) + '_' + str(n)
                            myTransmission['message_in'] = str(i) + '_(' + str(m[0]) + "-" + str(m[1]) + ")"
                            # Adding the transmission entry for the loop between source and distance_node
                            if m[1] == distance_node:
                                myTransmission['message_out'] = str(i) + '_(' + str(m[1]) + "-" + str(source) + ")"

                            myAppEB['transmission'].append(myTransmission)

            appJsonBE.append(myAppEB)

            # Creating the application with a loop between nodes

            myAppDD['id'] = i
            myAppDD['name'] = str(i)
            myAppDD['deadline'] = self.appsDeadlines[i]

            myAppDD['module'] = list()

            edgeNumber = 0
            myAppDD['message'] = list()

            myAppDD['transmission'] = list()

            totalMIPS = 0

            # Getting a couple of nodes in the application that will get a loop with the source
            app_nodes = list(APP.nodes())
            # Removing the source element
            app_nodes.remove(source)
            # Selecting the nodes that will create a loop with the source
            fnode = random.choice(app_nodes)
            app_nodes.remove(fnode)
            if len(APP.nodes()) <= 2:
                snode = fnode
            else:
                snode = random.choice(app_nodes)

            if self.cnf.graphicTerminal:
                if fnode == snode:
                    APP_DD.add_edges_from([(fnode, source)])
                else:
                    APP_DD.add_edges_from([(fnode, source), (snode, source)])
                mapping2 = dict(zip(sorted(list(APP_DD.nodes())), range(0, len(APP_DD.nodes))))
                APP_DD = nx.relabel_nodes(APP_DD, mapping2)
                fig2, ax2 = plt.subplots()
                nx.draw(APP_DD, pos, labels=mylabels, font_size=8, ax=ax2)
                # Win
                fig2.savefig(os.path.dirname(__file__) + '\\' + self.cnf.resultFolder + '\\plots\\app_%s_DD.png' % i)
                # Unix
                # fig.savefig(os.path.dirname(__file__) + '/' + self.cnf.resultFolder + '/plots/app_%s_EB.png' % i)
                plt.close(fig2)  # close the figure
                plt.show()

            for n in APP.nodes:
                # self.mapService2App.append(str(i))
                # self.mapServiceId2ServiceName.append(str(i) + '_' + str(n))
                myNode = {}
                myNode['id'] = n
                myNode['name'] = str(i) + '_' + str(n)
                myNode['RAM'] = self.servicesResources[n]
                # myNode['FRAM'] = self.servicesResources[n]
                myNode['type'] = 'MODULE'
                if source == n:
                    myEdge = {}
                    myEdge['id'] = edgeNumber
                    edgeNumber = edgeNumber + 1
                    myEdge['name'] = "M.USER.APP." + str(i)
                    myEdge['s'] = "None"
                    myEdge['d'] = str(i) + '_' + str(n)
                    myEdge['instructions'] = eval(self.func_SERVICEINSTR)
                    totalMIPS = totalMIPS + myEdge['instructions']
                    myEdge['bytes'] = eval(self.func_SERVICEMESSAGESIZE)
                    myAppDD['message'].append(myEdge)
                    # self.appsSourceMessage.append(myEdge)

                    print("Adding source message")

                    for o in APP.edges:
                        if o[0] == source:
                            myTransmission = {}
                            myTransmission['module'] = str(i) + '_' + str(source)
                            myTransmission['message_in'] = "M.USER.APP." + str(i)
                            myTransmission['message_out'] = str(i) + '_(' + str(o[0]) + "-" + str(o[1]) + ")"
                            myAppDD['transmission'].append(myTransmission)

                myAppDD['module'].append(myNode)

            for n in APP.edges:
                myEdge = {}
                myEdge['id'] = edgeNumber
                edgeNumber = edgeNumber + 1
                myEdge['name'] = str(i) + '_(' + str(n[0]) + "-" + str(n[1]) + ")"
                myEdge['s'] = str(i) + '_' + str(n[0])
                myEdge['d'] = str(i) + '_' + str(n[1])
                myEdge['instructions'] = eval(self.func_SERVICEINSTR)
                totalMIPS = totalMIPS + myEdge['instructions']
                myEdge['bytes'] = eval(self.func_SERVICEMESSAGESIZE)
                myAppDD['message'].append(myEdge)
                # Creating the message that will be sent it between fnode, snode and source
                if n[1] == fnode or n[1] == snode:
                    myEdge = {}
                    myEdge['id'] = edgeNumber
                    edgeNumber = edgeNumber + 1
                    myEdge['name'] = str(i) + '_(' + str(n[1]) + "-" + str(source) + ")"
                    myEdge['s'] = str(i) + '_' + str(n[1])
                    myEdge['d'] = str(i) + '_' + str(source)
                    myEdge['instructions'] = eval(self.func_SERVICEINSTR)
                    totalMIPS = totalMIPS + myEdge['instructions']
                    myEdge['bytes'] = eval(self.func_SERVICEMESSAGESIZE)
                    myAppDD['message'].append(myEdge)
                destNode = n[1]
                for o in APP.edges:
                    if o[0] == destNode:
                        myTransmission = {}
                        myTransmission['module'] = str(i) + '_' + str(n[1])
                        myTransmission['message_in'] = str(i) + '_(' + str(n[0]) + "-" + str(n[1]) + ")"
                        myTransmission['message_out'] = str(i) + '_(' + str(o[0]) + "-" + str(o[1]) + ")"
                        myAppDD['transmission'].append(myTransmission)
                    # Adding the transmission entry for the loop between source and fnode, snode
                    if o[0] == destNode and (o[0] == fnode or o[0] == snode):
                        myTransmission = {}
                        myTransmission['module'] = str(i) + '_' + str(n[1])
                        myTransmission['message_in'] = str(i) + '_(' + str(n[0]) + "-" + str(n[1]) + ")"
                        myTransmission['message_out'] = str(i) + '_(' + str(o[0]) + "-" + str(source) + ")"
                        myAppDD['transmission'].append(myTransmission)

            for n in APP.nodes:
                outgoingEdges = False
                for m in APP.edges:
                    if m[0] == n:
                        outgoingEdges = True
                        break
                if not outgoingEdges:
                    for m in APP.edges:
                        if m[1] == n:
                            myTransmission = {}
                            myTransmission['module'] = str(i) + '_' + str(n)
                            myTransmission['message_in'] = str(i) + '_(' + str(m[0]) + "-" + str(m[1]) + ")"
                            # Adding the transmission entry for the loop between source and fnode, snode
                            if m[1] == fnode or m[1] == snode:
                                myTransmission['message_out'] = str(i) + '_(' + str(m[1]) + "-" + str(source) + ")"

                            myAppDD['transmission'].append(myTransmission)

            appJsonDD.append(myAppDD)

        # Win
        appFile = open(self.cnf.resultFolder + "\\appDefinition.json", "w")
        appFileBE = open(self.cnf.resultFolder + "\\appDefinitionBE.json", "w")
        appFileDD = open(self.cnf.resultFolder + "\\appDefinitionDD.json", "w")
        # Unix
        # appFile = open(self.cnf.resultFolder + "/appDefinition.json", "w")
        # appFileBE = open(self.cnf.resultFolder + "/appDefinitionBE.json", "w")
        appFile.write(json.dumps(appJson))
        appFile.close()
        appFileBE.write(json.dumps(appJsonBE))
        appFileBE.close()
        appFileDD.write(json.dumps(appJsonDD))
        appFileDD.close()

    def userGeneration(self):
        # Generation of the IoT devices (users)

        userJson = {}

        self.myUsers = list()

        self.appsRequests = list()
        for i in range(0, self.TOTALNUMBEROFAPPS):
            userRequestList = set()
            probOfRequested = eval(self.func_REQUESTPROB)
            # probOfRequested = -1
            atLeastOneAllocated = False
            for j in self.gatewaysDevices:
                if random.random() < probOfRequested:
                    myOneUser = {}
                    myOneUser['app'] = str(i)
                    myOneUser['message'] = "M.USER.APP." + str(i)
                    myOneUser['id_resource'] = j
                    myOneUser['lambda'] = eval(self.func_USERREQRAT)
                    userRequestList.add(j)
                    self.myUsers.append(myOneUser)
                    atLeastOneAllocated = True
            if not atLeastOneAllocated:
                j = random.randint(0, len(self.gatewaysDevices) - 1)
                myOneUser = {}
                myOneUser['app'] = str(i)
                myOneUser['message'] = "M.USER.APP." + str(i)
                # myOneUser['id_resource'] = j
                myOneUser['id_resource'] = list(self.gatewaysDevices)[j]  # Random GW to host the request
                myOneUser['lambda'] = eval(self.func_USERREQRAT)
                userRequestList.add(list(self.gatewaysDevices)[j])
                self.myUsers.append(myOneUser)
            self.appsRequests.append(userRequestList)

        userJson['sources'] = self.myUsers

        # Win
        userFile = open(self.cnf.resultFolder + "\\usersDefinition.json", "w")
        # Unix
        # userFile = open(self.cnf.resultFolder + "/usersDefinition.json", "w")
        userFile.write(json.dumps(userJson))
        userFile.close()

    def requestsMapping(self):
        # Writting reqDefinition.csv
        # Initializing resquest X app matrix
        self.appReq = np.zeros((len(self.appsRequests), len(self.gatewaysDevices)), dtype=int)
        gws = sorted(list(self.gatewaysDevices))
        for app in range(0, len(self.appsRequests)):
            for index, gw in zip(range(0, len(gws)), gws):
                if gw in list(self.appsRequests[app]):
                    self.appReq[app][index] = 1

        # Win
        with open(os.path.dirname(__file__) + '\\' + self.cnf.resultFolder + '\\reqDefinition.csv',
                  mode='wb') as reqDefinition:
            # Unix
            # with open(os.path.dirname(__file__) + '/' + self.cnf.resultFolder + '/reqDefinition.csv', mode='wb') as reqDefinition:
            reqDefinition_writter = csv.writer(reqDefinition, delimiter=',')

            reqDefinition_writter.writerow(
                [len(self.appsRequests), sum(self.appsTotalServices), len(self.gatewaysDevices)])

            row = []
            for i in range(len(self.appsRequests)):
                for j in range(len(self.gatewaysDevices)):
                    row.append(self.appReq[i][j])
                reqDefinition_writter.writerow(row)
                row = []

        reqDefinition.close()

    def randomPlacement(self):
        servicesInFog = 0
        servicesInCloud = 0
        allAlloc = {}
        myAllocationList = list()
        # random.seed(datetime.now())

        initial_nodeResources = sorted(self.nodeResources.items(), key=operator.itemgetter(0))

        for app_num, app in zip(range(0, len(self.appsRequests)), self.appsRequests):
            for instance in range(0, len(self.appsRequests[app_num])):
                for module in list(self.apps[app_num].nodes):
                    flag = True
                    iterations = 0
                    while flag and iterations < 50:
                        # Random candidate node to host the service
                        index = random.randint(0, (len(self.nodeResources) - 1))
                        # Checking if the node has resource to host the service
                        res_required = self.servicesResources[module]
                        if res_required <= self.nodeFreeResources[index]:
                            self.nodeFreeResources[index] = self.nodeFreeResources[index] - res_required
                            myAllocation = {}
                            myAllocation['app'] = self.mapService2App[module]
                            myAllocation['module_name'] = self.mapServiceId2ServiceName[module]
                            myAllocation['id_resource'] = index
                            flag = False
                            myAllocationList.append(myAllocation)
                            if index != self.cloudId:
                                servicesInFog += 1
                            else:
                                servicesInCloud += 1
                    if iterations == 50:
                        print("After %i iterations it was not possible to place the module %i using the RandomPlacement" \
                              % iterations, module)
                        exit()

        allAlloc['initialAllocation'] = myAllocationList
        # Win
        allocationFile = open(self.cnf.resultFolder + "\\allocDefinitionRandom.json", "w")
        # Unix
        # allocationFile = open(self.cnf.resultFolder + "/allocDefinitionRandom.json", "w")
        allocationFile.write(json.dumps(allAlloc))
        allocationFile.close()

        # Keeping nodes'resources
        final_nodeResources = sorted(self.nodeResources.items(), key=operator.itemgetter(0))

        if os.stat(
                'C:\\Users\\David Perez Abreu\\Sources\\Fog\\YAFS_Master\\src\\examples\\PopularityPlacement\\conf\\node_resources.csv').st_size == 0:
            # The file in empty
            ids = ['node_id']
            values = ['ini_resources']
            token = self.scenario + '_random'
            fvalues = [token]
            for ftuple in initial_nodeResources:
                ids.append(ftuple[0])
                values.append(ftuple[1])
            for stuple in final_nodeResources:
                fvalues.append(stuple[1])
            file = open(
                'C:\\Users\\David Perez Abreu\\Sources\\Fog\\YAFS_Master\\src\\examples\\PopularityPlacement\\conf\\node_resources.csv',
                'a+')
            file.write(",".join(str(item) for item in ids))
            file.write("\n")
            file.write(",".join(str(item) for item in values))
            file.write("\n")
            file.write(",".join(str(item) for item in fvalues))
            file.write("\n")
            file.close()
        else:
            token = self.scenario + '_random'
            fvalues = [token]
            for stuple in final_nodeResources:
                fvalues.append(stuple[1])
            file = open(
                'C:\\Users\\David Perez Abreu\\Sources\\Fog\\YAFS_Master\\src\\examples\\PopularityPlacement\\conf\\node_resources.csv',
                'a+')
            file.write(",".join(str(item) for item in fvalues))
            file.write("\n")
            file.close()

        print("Random initial allocation performed!")

    def create_cost_reach_nodes(self, lgw):
        lcostReachNodes = []
        dest = self.numNodes

        for g in lgw:
            pathDestinations = [list(nx.shortest_path(self.FGraph, source=g, target=i, weight="PR"))
                                for i in range(dest) if i != lgw]
            gw2Nodes = [sum(self.FGraph.edges[(path[i], path[i + 1])]["PR"] for i in range(len(path) - 1))
                        for path in pathDestinations]
            # Adding the cost to reach the same some with is zero because the it is the source of the request
            # gw2Nodes.insert(g, 0)
            lcostReachNodes.append(gw2Nodes)

        return lcostReachNodes

    def create_req_from_app(self):
        lrequestPerApp = {}
        lrequestPerApp.update({(i, j): self.appReq[i][j] for i in range(self.numApplications)
                               for j in range(self.numRequests)})
        return lrequestPerApp

    def create_instance_matrix(self):
        activeServices = {}

        linstanceMatrix = {(i, j): 0 for i in range(self.numApplications) for j in range(self.numServices)}
        for index in range(self.numApplications):
            for mod in list(self.apps[index].nodes):
                linstanceMatrix.update({(index, mod): 1})
        return linstanceMatrix

    def get_nodes_rank(self):
        lnodesRank = []
        nodesSpeed = self.nodeSpeed
        # Adding the speed of the Cloud
        nodesSpeed[len(nodesSpeed)] = self.CLOUDSPEED
        lnodesRank = nodesSpeed.values()
        for i in range(0, len(lnodesRank)):
            lnodesRank[i] = float(lnodesRank[i])
            lnodesRank[i] = 1000 / lnodesRank[i]
        return lnodesRank

    def getPlacementMatrix(self):

        # Getting variables values
        # self.numNodes = len(self.G.nodes) + 1 # Plus one because the cloud is not part of the graph
        self.numNodes = len(self.nodeResources)
        self.numApplications = len(self.apps)
        self.numServices = sum(self.appsTotalServices)
        # requests = [len(i) for i in self.appsRequests]
        # self.numRequests = sum(requests)
        self.numRequests = len(self.gatewaysDevices)
        self.memNodes = self.nodeFreeResources.values()
        self.memSer = self.servicesResources.values()
        # gw_request = [j for i in self.appsRequests for j in list(i)]
        gw_request = sorted(list(self.gatewaysDevices))
        # self.numGWs = len(gw_request)
        self.costReachNode = self.create_cost_reach_nodes(gw_request)
        self.requestPerApp = self.create_req_from_app()
        self.instanceMatrix = self.create_instance_matrix()
        # self.nodesRank = self.get_nodes_rank()
        self.placement_solution = None

        print ('\nStarting the popularity model! Time= %s\n' % str(datetime.now()))

        # Optimization model | First optimization model
        mdl = Model('Popularity')

        # === Variables ===

        # Total of request per application
        totalRequestApp = []
        for i in range(self.numApplications):
            sumTotal = 0
            for j in range(self.numRequests):
                sumTotal += self.requestPerApp[i, j]
            totalRequestApp.append(sumTotal)

        # Total of services per application
        totalServicesApp = []
        for i in range(self.numApplications):
            sumTotal = 0
            for j in range(self.numServices):
                sumTotal += self.instanceMatrix[i, j]
            totalServicesApp.append(sumTotal)

        # Application per Requests structure
        app_req = [(i, j) for i in range(self.numApplications) for j in range(self.numRequests)]

        # Services per Nodes structure
        ser_nodes = [(i, j) for i in range(self.numServices) for j in range(self.numNodes)]

        # Decision variables

        # Acceptance Matrix; applications x requests
        acceptanceMatrix = mdl.binary_var_dict(app_req, name='AM_1')
        # Placement matrix; applications x requests x services x nodes
        placementMatrix = mdl.binary_var_matrix(app_req, ser_nodes, name='PM_1')

        # Objective function
        mdl.maximize(mdl.sum(totalRequestApp[a] * acceptanceMatrix[a, r] for a in range(self.numApplications)
                             for r in range(self.numRequests)))

        # Constraints

        # 1- only accept explicit requests
        # This constraint matches with the Equation #XYZ in the model
        for a in range(self.numApplications):
            for r in range(self.numRequests):
                mdl.add_constraint(acceptanceMatrix[a, r] <= self.requestPerApp[a, r],
                                   ctname='onlyIfRequestExists_app%d_req%d' % (a, r))

        # 2- request completely fulfilled
        # This constraint matches with the Equation #2 in the model #1
        for a in range(self.numApplications):
            for r in range(self.numRequests):
                for s in range(self.numServices):
                    for n in range(self.numNodes):
                        mdl.add_constraint((placementMatrix[(a, r), (s, n)] * self.requestPerApp[a, r])
                                           <= (acceptanceMatrix[a, r] * self.requestPerApp[a, r]),
                                           ctname='allServicesNoneServices_app%d_req%d_ser%d_node%d' % (a, r, s, n))

        # 3- only one server | Service request can be executed on at most one server
        # This constraint matches with the Equation #3 in the model #1
        for a in range(self.numApplications):
            for r in range(self.numRequests):
                for s in range(self.numServices):
                    mdl.add_constraint(self.requestPerApp[a, r] *
                                       mdl.sum(placementMatrix[(a, r), (s, n)] for n in range(self.numNodes))
                                       <= 1, ctname='requestMostOneServer_app%d_req%d_ser%d' % (a, r, s))

        # 4- All services from an application - all services placed in the network per application per request
        # This constraint matches with the Equation #4 in the model #1
        for a in range(self.numApplications):
            for r in range(self.numRequests):
                for s in range(self.numServices):
                    mdl.add_constraint((acceptanceMatrix[a, r] * self.requestPerApp[a, r]) * self.instanceMatrix[a, s]
                                       == self.requestPerApp[a, r] * mdl.sum(placementMatrix[(a, r), (s, n)]
                                                                             for n in range(self.numNodes)),
                                       ctname='servicesLoadedBeforePlace_app%d_req%d_ser%d' % (a, r, s))

        # 5&6&7&8- CPU, memory, and bandwidth constraints per each node | So far just memory
        # This constraint matches with the Equation #5,6,7,8 in the model #1
        for n in range(self.numNodes):
            mdl.add_constraint(mdl.sum((self.requestPerApp[a, r] * placementMatrix[(a, r), (s, n)]) *
                                       self.memSer[s] for a in range(self.numApplications) for r in
                                       range(self.numRequests)
                                       for s in range(self.numServices)) <= self.memNodes[n],
                               ctname='respectNodesCapacitiesMem_%d' % n)

        '''           
        print('\n' + '&&&&&&&&&&' + '\n')
        print(mdl.export_to_string())
        print('\n' + '&&&&&&&&&&' + '\n')
        '''

        solution1 = mdl.solve(log_output=True)

        print('\n' + '##########' + '\n')
        print(mdl.get_solve_status())
        print('\n' + '##########' + '\n')

        solution1.display()

        # Keeping the data structures for used them in the next iteration
        acceptanceMatrixTemp = {(i, j): acceptanceMatrix[i, j].solution_value for i in range(self.numApplications)
                                for j in range(self.numRequests)}
        self.acceptanceM = acceptanceMatrixTemp
        placementMatrixTemp = {((i, j), (k, l)): placementMatrix[(i, j), (k, l)].solution_value
                               for i in range(self.numApplications) for j in range(self.numRequests)
                               for k in range(self.numServices) for l in range(self.numNodes)}

        '''
        # Getting the results of the optimization models to deploy the services accordingly | [(app, ser, node]
        self.placement_solution = [(a, s, n) for a in range(self.numApplications) for r in range(self.numRequests)
                              for s in range(self.numServices) for n in range(self.numNodes)
                              if placementMatrix[(a, r), (s, n)].solution_value >= 0.9]
        '''

        ##################################################

        print('\n++++++++++\n')
        print ('\nThe popularity model has finished! Time= %s\n' % str(datetime.now()))

        print('\n++++++++++\n')
        print ('\nStarting the popularity/cost model! Time=%s\n' % str(datetime.now()))

        # Defining the second optimization model to minimize cost/latency
        mdl2 = Model('Popularity_Cost')

        # Decision variables

        # Final placement matrix; applications x requests x services x nodes
        finalPlacementMatrix = mdl2.binary_var_matrix(app_req, ser_nodes, name='PM_2')

        # Objective function
        '''
        mdl2.minimize(mdl2.sum(
            (self.nodesRank[n] * (self.costReachNode[a][n] * self.requestPerApp[a, r])) * finalPlacementMatrix[
                (a, r), (s, n)]
            for a in range(self.numApplications) for r in range(self.numRequests)
            for s in range(self.numServices) for n in range(self.numNodes)))
        '''
        mdl2.minimize(mdl2.sum(
            (self.costReachNode[r][n] * self.requestPerApp[a, r]) * finalPlacementMatrix[
                (a, r), (s, n)]
            for a in range(self.numApplications) for r in range(self.numRequests)
            for s in range(self.numServices) for n in range(self.numNodes)))

        # Constraints

        # 2- request completely fulfilled - Keep the popular services
        # This constraint matches with the Equation #2 in the model #2
        for a in range(self.numApplications):
            for r in range(self.numRequests):
                for s in range(self.numServices):
                    for n in range(self.numNodes):
                        mdl2.add_constraint((finalPlacementMatrix[(a, r), (s, n)] * self.requestPerApp[a, r])
                                            <= (acceptanceMatrixTemp[a, r] * self.requestPerApp[a, r])
                                            , ctname='allServicesNoneServices_app%d_req%d_ser%d_node%d' % (a, r, s, n))

        # 3- only one server | Service request can be executed on at most one server
        # This constraint matches with the Equation #3 in the model #2
        for a in range(self.numApplications):
            for r in range(self.numRequests):
                for s in range(self.numServices):
                    mdl2.add_constraint(self.requestPerApp[a, r] *
                                        mdl2.sum(finalPlacementMatrix[(a, r), (s, n)] for n in range(self.numNodes))
                                        <= 1, ctname='requestMostOneServer_app%d_req%d_ser%d' % (a, r, s))

        # 4- All services from an application - all services placed in the network per application per request
        # This constraint matches with the Equation #4 in the model #2
        for a in range(self.numApplications):
            for r in range(self.numRequests):
                for s in range(self.numServices):
                    mdl2.add_constraint(
                        (acceptanceMatrixTemp[a, r] * self.requestPerApp[a, r]) * self.instanceMatrix[a, s]
                        == self.requestPerApp[a, r] * mdl2.sum(finalPlacementMatrix[(a, r), (s, n)]
                                                               for n in range(self.numNodes)),
                        ctname='servicesLoadedBeforePlace_app%d_req%d_ser%d' % (a, r, s))

        # 5&6&7&8- CPU, memory, and bandwidth constraints per each node | So far just memory
        # This constraint matches with the Equation #5,6,7,8 in the model #2
        for n in range(self.numNodes):
            mdl2.add_constraint(mdl2.sum((self.requestPerApp[a, r] * finalPlacementMatrix[(a, r), (s, n)]) *
                                         self.memSer[s] for a in range(self.numApplications) for r in
                                         range(self.numRequests)
                                         for s in range(self.numServices)) <= self.memNodes[n],
                                ctname='respectNodesCapacitiesMem_%d' % n)

        '''
        print('\n' + '&&&&&&&&&&' + '\n')
        print(mdl2.export_to_string())
        print('\n' + '&&&&&&&&&&' + '\n')
        '''

        solution2 = mdl2.solve(log_output=True)

        print('\n' + '##########' + '\n')
        print(mdl2.get_solve_status())
        print('\n' + '##########' + '\n')

        solution2.display()

        print('\n++++++++++\n')
        print ('\nThe popularity/cost model has finished! Time= %s\n' % str(datetime.now()))

        # Getting the results of the optimization models to deploy the services accordingly | [(app, ser, node]
        self.placement_solution = [(a, s, n) for a in range(self.numApplications) for r in range(self.numRequests)
                                   for s in range(self.numServices) for n in range(self.numNodes)
                                   if finalPlacementMatrix[(a, r), (s, n)].solution_value >= 0.9]

    def popularityPlacement(self):
        # Get the placement matrix
        self.getPlacementMatrix()
        allAlloc = {}
        myAllocationList = list()

        initial_nodeResources = sorted(self.nodeResources.items(), key=operator.itemgetter(0))

        for app_num in range(0, len(self.appsRequests)):
            to_deploy = False
            deploy_count = 0
            for ps in self.placement_solution:
                if app_num == ps[0]:
                    to_deploy = True
                    deploy_count += 1
                    res_required = self.servicesResources[ps[1]]
                    self.nodeFreeResources[ps[2]] = self.nodeFreeResources[ps[2]] - res_required
                    myAllocation = {}
                    myAllocation['app'] = self.mapService2App[ps[1]]
                    myAllocation['module_name'] = self.mapServiceId2ServiceName[ps[1]]
                    myAllocation['id_resource'] = ps[2]
                    myAllocationList.append(myAllocation)
                    print ("The module %s of the application %s will be deployed at node %i" % (
                    self.mapService2App[app_num], self.mapServiceId2ServiceName[ps[1]], ps[2]))
            print("%i module of the application %i were deployed" % (deploy_count, app_num))
            if not to_deploy:
                print ("Application %s NOT DEPLOYED" % app_num)

        allAlloc['initialAllocation'] = myAllocationList
        # Win
        allocationFile = open(self.cnf.resultFolder + "\\allocDefinitionPopularity.json", "w")
        # Unix
        # allocationFile = open(self.cnf.resultFolder + "/allocDefinitionPopularity.json", "w")
        allocationFile.write(json.dumps(allAlloc))
        allocationFile.close()

        # Keeping nodes'resources
        final_nodeResources = sorted(self.nodeResources.items(), key=operator.itemgetter(0))

        if os.stat(
                'C:\\Users\\David Perez Abreu\\Sources\\Fog\\YAFS_Master\\src\\examples\\PopularityPlacement\\conf\\node_resources.csv').st_size == 0:
            # The file in empty
            ids = ['node_id']
            values = ['ini_resources']
            token = self.scenario + '_popularity'
            fvalues = [token]
            for ftuple in initial_nodeResources:
                ids.append(ftuple[0])
                values.append(ftuple[1])
            for stuple in final_nodeResources:
                fvalues.append(stuple[1])
            file = open(
                'C:\\Users\\David Perez Abreu\\Sources\\Fog\\YAFS_Master\\src\\examples\\PopularityPlacement\\conf\\node_resources.csv',
                'a+')
            file.write(",".join(str(item) for item in ids))
            file.write("\n")
            file.write(",".join(str(item) for item in values))
            file.write("\n")
            file.write(",".join(str(item) for item in fvalues))
            file.write("\n")
            file.close()
        else:
            token = self.scenario + '_popularity'
            fvalues = [token]
            for stuple in final_nodeResources:
                fvalues.append(stuple[1])
            file = open(
                'C:\\Users\\David Perez Abreu\\Sources\\Fog\\YAFS_Master\\src\\examples\\PopularityPlacement\\conf\\node_resources.csv',
                'a+')
            file.write(",".join(str(item) for item in fvalues))
            file.write("\n")
            file.close()

        print("Popularity initial allocation performed!")

    def loadNet(self, data):
        global nodeAttributes
        """
            It generates the topology from a JSON file
            see project example: Tutorial_JSONModelling

            Args:
                 data (str): a json
        """
        G = nx.Graph()
        for edge in data["link"]:
            G.add_edge(edge["s"], edge["d"], BW=edge[LINK_BW], PR=edge[LINK_PR])

        # TODO This part can be removed in next versions
        for node in data["entity"]:
            nodeAttributes[node["id"]] = node
        # end remove

        # Correct way to use custom and mandatory topology attributes

        valuesIPT = {}
        valuesRAM = {}
        for node in data["entity"]:
            try:
                valuesIPT[node["id"]] = node["IPT"]
            except KeyError:
                valuesIPT[node["id"]] = 0
            try:
                valuesRAM[node["id"]] = node["RAM"]
            except KeyError:
                valuesRAM[node["id"]] = 0

        nx.set_node_attributes(G, values=valuesIPT, name="IPT")
        nx.set_node_attributes(G, values=valuesRAM, name="RAM")

        return G

    def buildComunities(self, ltopo):
        # Variables
        min_community = len(ltopo)
        max_community = -1
        mean_size = 0
        lranking = []
        nocommunity_nodes = []
        lranking_list = []
        lranking_complete = []
        temp_dict = {}
        out_dict = {}

        # Adding the GINDEX to the graph. This attribute it will be use to rank the nodes
        for ledge in ltopo.edges:
            ltopo[ledge[0]][ledge[1]]['GINDEX'] = 1 / float(ltopo[ledge[0]][ledge[1]]["PR"])

        # To rank the graph this one should be directed
        aux_topo = ltopo.to_directed()
        # Removing Cloud node
        aux_topo.remove_node(len(aux_topo) - 1)
        # Building the markov chain matrix for the possibles transitions of the graph
        node_rank_google = nx.google_matrix(aux_topo, weight='GINDEX')
        node_rank_google = node_rank_google.tolist()
        for i in range(0, len(node_rank_google)):
            for j in range(0, len(node_rank_google[i])):
                temp_dict[j] = node_rank_google[i][j]
                out_dict[j] = node_rank_google[i][j]

            # This structure will be use to determine the nodes with out any community
            nocommunity_nodes.append(out_dict.copy())

            # Creating the community of each node base on the ranks obtained
            for k, v in temp_dict.items():
                if k ==i:
                    # High priority to the GW
                    temp_dict[k] = len(ltopo)
                if k != i and v < 0.1:
                    del temp_dict[k]

            # Updating min and max community lengths
            value = len(temp_dict)
            mean_size += value

            if value < min_community:
                min_community = value

            if value > max_community:
                max_community = value

            lranking.append(temp_dict.copy())
            temp_dict.clear()
            out_dict.clear()

        # Completing the communities once that all the candidates nodes were selected
        for i, ini_comunity in zip(range(0, len(lranking)), lranking):
            # Copy of the initial community
            fin_community = ini_comunity.copy()
            for node in ini_comunity:
                if node != i:
                    # Avoiding a loop search
                    for item in lranking[node]:
                        # Checking if the node already belong to the community
                        if not item in fin_community:
                            fin_community[item] = lranking[node][item]
            # rr works as the pointer of the Round Robin algorithm for load balancing and it is initialized with the index of the GW
            fin_community['rr'] = 0
            lranking_complete.append(fin_community.copy())
            sorted_temp = sorted(fin_community.items(), key=operator.itemgetter(1), reverse=True)
            lranking_list.append(sorted_temp)
            fin_community.clear()
            sorted_temp = []

        for i in range(0, len(nocommunity_nodes)):
            for k, v in nocommunity_nodes[i].items():
                for kk, vv in lranking_complete[i].items():
                    if k == kk:
                        del nocommunity_nodes[i][k]

        aux_structured = copy.copy(nocommunity_nodes)
        nocommunity_nodes = []
        for item in aux_structured:
            sorted_temp = []
            sorted_temp = sorted(item.items(), key=operator.itemgetter(1), reverse=True)
            nocommunity_nodes.append(sorted_temp)

        # Extended no communities per node order by transition probability
        nocomu_ranking_list = [list(map(list, sub_list)) for sub_list in nocommunity_nodes]
        # Extended communities per node order by transition probability
        rranking_list = [list(map(list, sub_list2)) for sub_list2 in lranking_list]

        return nocomu_ranking_list, rranking_list, (mean_size/len(node_rank_google))

    def heuristicPlacement(self):
        # Getting data structures ready
        wpath = "C:\\Users\\David Perez Abreu\\Sources\\Fog\\YAFS_Master\\src\\examples\\PopularityPlacement"
        data_net = json.load(open(wpath + "\\conf\\netDefinition.json"))
        topo = self.loadNet(data=data_net)
        nocomu_ranking_list, ranking_list, wsize = self.buildComunities(ltopo=topo)
        self.numApplications = len(self.apps)
        self.numRequests = len(self.gatewaysDevices)
        self.requestPerApp = self.create_req_from_app()
        initial_nodeResources = sorted(self.nodeResources.items(), key=operator.itemgetter(0))

        # Total of request per application
        totalRequestApp = []
        for i in range(self.numApplications):
            sumTotal = 0
            for j in range(self.numRequests):
                sumTotal += self.requestPerApp[i, j]
            totalRequestApp.append(sumTotal)
        dic_totalRequestApp = {i: totalRequestApp[i] for i in range(0, len(totalRequestApp))}

        rank_app = sorted(dic_totalRequestApp.items(), key=operator.itemgetter(1), reverse=True)

        # Starting the placement of modules
        servicesInFog = 0
        servicesInCloud = 0
        allAlloc = {}
        myAllocationList = list()
        # random.seed(datetime.now())

        for app_num, app in zip(range(0, len(self.appsRequests)), self.appsRequests):
            # instance will carry the id of the GW where the request was generated
            for instance in list(self.appsRequests[rank_app[app_num][0]]):
                # Getting the index of the rr entry
                rr_index = [index for index, item in zip(range(0, len(ranking_list[instance])),
                                                         ranking_list[instance]) if 'rr' in item]
                for module in list(self.apps[rank_app[app_num][0]].nodes):
                    # Checking if the module could be deployed in this community. Thus it is guarantee the deploy here
                    max_community_resources = -1
                    win = 0
                    community_flag = False
                    count = 1
                    while((max_community_resources < self.servicesResources[module]) and not (win == len(ranking_list[instance]) - 1)):
                        if len(ranking_list[instance]) > (wsize * count):
                            win = wsize * count
                        else:
                            win = len(ranking_list[instance]) - 1
                        community_resources = [self.nodeFreeResources[element[0]]
                                               for element, iwin in zip(ranking_list[instance], range(0, win))
                                               if element[0] != 'rr' and iwin <= win]
                        max_community_resources = max(community_resources)

                        if max_community_resources >= self.servicesResources[module]:
                            community_flag = True
                        count += 1

                    if community_flag:
                        # Getting the id where the rr points
                        index = ranking_list[instance][ranking_list[instance][rr_index[0]][1]][0]
                        res_required = self.servicesResources[module]
                        if res_required <= self.nodeFreeResources[index]:
                            self.nodeFreeResources[index] = self.nodeFreeResources[index] - res_required
                            # Deployment
                            myAllocation = {}
                            myAllocation['app'] = self.mapService2App[module]
                            myAllocation['module_name'] = self.mapServiceId2ServiceName[module]
                            myAllocation['id_resource'] = index
                            myAllocationList.append(myAllocation)
                        else:
                            # Updating the rr pointer to the next community node
                            next_rr = (ranking_list[instance][rr_index[0]][1] + 1) % win
                            if next_rr != rr_index[0]:
                                ranking_list[instance][rr_index[0]][1] = next_rr
                            else:
                                ranking_list[instance][rr_index[0]][1] = next_rr + 1
                            index = ranking_list[instance][ranking_list[instance][rr_index[0]][1]][0]
                            # The rr pointer will be update until find the node that could host the module
                            while res_required > self.nodeFreeResources[index]:
                                # Updating the rr pointer. In the worst scenario it would be necessary to do a full rotation
                                next_rr = (ranking_list[instance][rr_index[0]][1] + 1) % win
                                if next_rr != rr_index[0]:
                                    ranking_list[instance][rr_index[0]][1] = next_rr
                                else:
                                    # This never will be executed
                                    ranking_list[instance][rr_index[0]][1] = next_rr + 1
                                index = ranking_list[instance][ranking_list[instance][rr_index[0]][1]][0]
                            self.nodeFreeResources[index] = self.nodeFreeResources[index] - res_required
                            # Deployment
                            myAllocation = {}
                            myAllocation['app'] = self.mapService2App[module]
                            myAllocation['module_name'] = self.mapServiceId2ServiceName[module]
                            myAllocation['id_resource'] = index
                            myAllocationList.append(myAllocation)
                    else:
                        # Selecting and alternative deployment community that should be the nodes outside of the previous step
                        no_community_resources = [self.nodeFreeResources[element[0]]
                                                  for element in nocomu_ranking_list[instance]]
                        max_no_community_resources = max(no_community_resources)

                        if max_no_community_resources >= self.servicesResources[module]:
                            # Getting the id  of the nodes where the module should be deployed
                            for k, v in nocomu_ranking_list[instance]:
                                if self.nodeFreeResources[nocomu_ranking_list[instance][k][0]] >= self.servicesResources[module]:
                                    break
                            self.nodeFreeResources[index] = self.nodeFreeResources[index] - res_required
                            # Deployment
                            myAllocation = {}
                            myAllocation['app'] = self.mapService2App[module]
                            myAllocation['module_name'] = self.mapServiceId2ServiceName[module]
                            myAllocation['id_resource'] = index
                            myAllocationList.append(myAllocation)
                        else:
                            # The module will be placed in the Cloud
                            index = self.cloudId
                            self.nodeFreeResources[index] = self.nodeFreeResources[index] - res_required
                            # Deployment in the cloud
                            myAllocation = {}
                            myAllocation['app'] = self.mapService2App[module]
                            myAllocation['module_name'] = self.mapServiceId2ServiceName[module]
                            myAllocation['id_resource'] = index
                            myAllocationList.append(myAllocation)
                    # Updating the rr pointer
                    next_rr = (ranking_list[instance][rr_index[0]][1] + 1) % win
                    if next_rr != rr_index[0]:
                        ranking_list[instance][rr_index[0]][1] = next_rr
                    else:
                        ranking_list[instance][rr_index[0]][1] = next_rr + 1
                    # Updating placement metrics
                    if index != self.cloudId:
                        servicesInFog += 1
                    else:
                        servicesInCloud += 1
                '''
                # Updating the rr pointer
                next_rr = (ranking_list[instance][rr_index[0]][1] + 1) % len(ranking_list[instance])
                if next_rr != rr_index[0]:
                    ranking_list[instance][rr_index[0]][1] = next_rr
                else:
                    ranking_list[instance][rr_index[0]][1] = next_rr + 1
                '''

        allAlloc['initialAllocation'] = myAllocationList
        # Win
        allocationFile = open(self.cnf.resultFolder + "\\allocDefinitionHeuristic.json", "w")
        # Unix
        # allocationFile = open(self.cnf.resultFolder + "/allocDefinitionRandom.json", "w")
        allocationFile.write(json.dumps(allAlloc))
        allocationFile.close()

        # Keeping nodes'resources
        final_nodeResources = sorted(self.nodeResources.items(), key=operator.itemgetter(0))

        if os.stat(
                'C:\\Users\\David Perez Abreu\\Sources\\Fog\\YAFS_Master\\src\\examples\\PopularityPlacement\\conf\\node_resources.csv').st_size == 0:
            # The file in empty

            ids = ['node_id']
            values = ['ini_resources']
            token = self.scenario + '_heuristic'
            fvalues = [token]
            for ftuple in initial_nodeResources:
                ids.append(ftuple[0])
                values.append(ftuple[1])
            for stuple in final_nodeResources:
                fvalues.append(stuple[1])
            file = open(
                'C:\\Users\\David Perez Abreu\\Sources\\Fog\\YAFS_Master\\src\\examples\\PopularityPlacement\\conf\\node_resources.csv',
                'a+')
            file.write(",".join(str(item) for item in ids))
            file.write("\n")
            file.write(",".join(str(item) for item in values))
            file.write("\n")
            file.write(",".join(str(item) for item in fvalues))
            file.write("\n")
            file.close()
        else:
            token = self.scenario + '_heuristic'
            fvalues = [token]
            for stuple in final_nodeResources:
                fvalues.append(stuple[1])
            file = open(
                'C:\\Users\\David Perez Abreu\\Sources\\Fog\\YAFS_Master\\src\\examples\\PopularityPlacement\\conf\\node_resources.csv',
                'a+')
            file.write(",".join(str(item) for item in fvalues))
            file.write("\n")
            file.close()

        print("Heuristic initial allocation performed!")

    def firstPlacement(self):
        servicesInFog = 0
        servicesInCloud = 0
        allAlloc = {}
        myAllocationList = list()
        # random.seed(datetime.now())
        initial_nodeResources = sorted(self.nodeResources.items(), key=operator.itemgetter(0))
        aux = sorted(self.nodeResources.items(), key=operator.itemgetter(1))
        # aux = sorted(self.nodeResources.items(), key=operator.itemgetter(0))
        sorted_nodeResources = [list(sub_list) for sub_list in aux]


        for app_num, app in zip(range(0, len(self.appsRequests)), self.appsRequests):
            for instance in range(0, len(self.appsRequests[app_num])):
                for module in list(self.apps[app_num].nodes):
                    flag = True
                    iterations = 0
                    while flag and iterations < (len(sorted_nodeResources) - 1):
                        # Chosing the node with less resources to host the service
                        index = iterations
                        iterations += 1
                        # Checking if the node has resource to host the service
                        res_required = self.servicesResources[module]
                        if res_required <= sorted_nodeResources[index][1]:
                            remaining_resources = sorted_nodeResources[index][1] - res_required
                            # Updating sorted resource list
                            sorted_nodeResources[index][1] = remaining_resources
                            # Updating nodeFreeResources
                            self.nodeFreeResources[sorted_nodeResources[index][0]] = remaining_resources
                            myAllocation = {}
                            myAllocation['app'] = self.mapService2App[module]
                            myAllocation['module_name'] = self.mapServiceId2ServiceName[module]
                            myAllocation['id_resource'] = sorted_nodeResources[index][0]
                            flag = False
                            myAllocationList.append(myAllocation)
                            if sorted_nodeResources[index][0] != self.cloudId:
                                servicesInFog += 1
                            else:
                                servicesInCloud += 1
                    if iterations == (len(sorted_nodeResources) - 1):
                        print("After %i iterations it was not possible to place the module %i using the FirstPlacement" \
                              % iterations, module)
                        exit()
        allAlloc['initialAllocation'] = myAllocationList
        # Win
        allocationFile = open(self.cnf.resultFolder + "\\allocDefinitionFirst.json", "w")
        # Unix
        # allocationFile = open(self.cnf.resultFolder + "/allocDefinitionFirst.json", "w")
        allocationFile.write(json.dumps(allAlloc))
        allocationFile.close()

        # Keeping nodes' resources

        final_nodeResources = sorted(self.nodeResources.items(), key=operator.itemgetter(0))
        if os.stat('C:\\Users\\David Perez Abreu\\Sources\\Fog\\YAFS_Master\\src\\examples\\PopularityPlacement\\conf\\node_resources.csv').st_size == 0:
            # The file in empty
            ids = ['node_id']
            values = ['ini_resources']
            token = self.scenario + '_first'
            fvalues = [token]
            for ftuple in initial_nodeResources:
                ids.append(ftuple[0])
                values.append(ftuple[1])
            for stuple in final_nodeResources:
                fvalues.append(stuple[1])
            file = open('C:\\Users\\David Perez Abreu\\Sources\\Fog\\YAFS_Master\\src\\examples\\PopularityPlacement\\conf\\node_resources.csv', 'a+')
            file.write(",".join(str(item) for item in ids))
            file.write("\n")
            file.write(",".join(str(item) for item in values))
            file.write("\n")
            file.write(",".join(str(item) for item in fvalues))
            file.write("\n")
            file.close()
        else:
            token = self.scenario + '_first'
            fvalues = [token]
            for stuple in final_nodeResources:
                fvalues.append(stuple[1])
            file = open(
                'C:\\Users\\David Perez Abreu\\Sources\\Fog\\YAFS_Master\\src\\examples\\PopularityPlacement\\conf\\node_resources.csv', 'a+')
            file.write(",".join(str(item) for item in fvalues))
            file.write("\n")
            file.close()

        print("First initial allocation performed!")