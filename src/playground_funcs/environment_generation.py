import heapq
import json
from operator import itemgetter

import networkx as nx

import re
import random
import time
from math import floor
import matplotlib.pyplot as plt
import copy

import operator
import json
import os
from yafs import Topology
# import myConfig #! 27/08

debug_mode = True


def linear_graph(size):
    g = nx.DiGraph()
    g.add_nodes_from(range(size))
    if size >= 1:
        g.add_edges_from(tuple(zip(range(1, size), range(size - 1))))

    return g


class ExperimentConfiguration:

    def __init__(self, lconf, lpath=os.path.dirname(__file__)):
        self.path = lpath

        self.CLOUDCAPACITY = 9999999999999999
        self.CLOUDSPEED = 10000
        self.CLOUDBW = 125000  ## 1000 Mbits/s ou 125000 BYTES / MS ???
        self.CLOUDPR = 500

        self.PERCENTATGEOFGATEWAYS = 0.25

        # EDGE CONFIGURATION
        self.func_PROPAGATIONTIME = "random.randint(2,10)"  # it is change by the tier node value
        self.func_BANDWITDH = "random.randint(75000,75000)"

        # NODE CONFIG
        self.func_NODERESOURECES = "random.randint(10,25)"  # random distribution for the resources of the fog devices
        self.func_NODESPEED = "random.randint(500,1000)"  # random distribution for the speed of the fog devices

        # USER CONFIG.
        self.func_REQUESTPROB = "random.random()/4"
        self.func_USERREQRAT = "random.randint(200,1000)"

        # APP and SERVICES
        self.TOTALNUMBEROFAPPS = 10
        # !!!
        self.func_APPGENERATION = "nx.gn_graph(random.randint(2,4))"  # algorithm for the generation of the random applications
        # self.func_APPGENERATION = "linear_graph(random.randint(2, 4))"  # algorithm for the generation of the random applications (agora linear)
        self.func_SERVICEINSTR = "random.randint(20000,60000)"  # INSTR --> teniedno en cuenta nodespped esto nos da entre 200 y 600 MS
        self.func_SERVICEMESSAGESIZE = "random.randint(1500000,4500000)"  # BYTES y teniendo en cuenta net bandwidth nos da entre 20 y 60 MS

        self.func_SERVICERESOURCES = "random.randint(1,5)"  # MB de ram que consume el servicio, teniendo en cuenta noderesources y appgeneration tenemos que nos caben aprox 1 app por nodo o unos 10 servicios

        self.func_APPDEADLINE = "random.randint(2600,6600)"  # MS

        self.func_NETWORKGENERATION = "nx.barabasi_albert_graph(n, m)"

        self.cnf = lconf
        # self.scenario = lconf.myConfiguration

        current_time = int(time.time())
        random.seed(current_time)

    def networkGeneration(self, n=20, m=2, file_name_network='netDefinition.json'):
        # Generation of the network topology

        # Topology genneration

        self.G = eval(self.func_NETWORKGENERATION)

        self.devices = list()

        self.nodeResources = {}
        self.nodeSpeed = {}


        for i in self.G.nodes:
            self.nodeResources[i] = eval(self.func_NODERESOURECES)
            self.nodeSpeed[i] = eval(self.func_NODESPEED)

        for e in self.G.edges:
            self.G[e[0]][e[1]]['PR'] = eval(self.func_PROPAGATIONTIME)
            self.G[e[0]][e[1]]['BW'] = eval(self.func_BANDWITDH)

        # JSON EXPORT

        self.netJson = {}
        self.node_labels = {}

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
        self.centralityValues = sorted(centralityValuesNoOrdered.items(), key=operator.itemgetter(1), reverse=True)

        self.gatewaysDevices = set()
        self.cloudgatewaysDevices = set()

        highestCentrality = self.centralityValues[0][1]

        for device in self.centralityValues:
            if device[1] == highestCentrality:
                self.cloudgatewaysDevices.add(device[0])  # highest centrality

                self.node_labels[device[0]] = "cloudgateway"
                self.devices[device[0]]['tier'] = 0

        initialIndx = int(
            (1 - self.PERCENTATGEOFGATEWAYS) * len(self.G.nodes))  # Getting the indexes for the GWs nodes

        for idDev in range(initialIndx, len(self.G.nodes)):
            self.gatewaysDevices.add(self.centralityValues[idDev][0])  # lowest centralities
            self.node_labels[self.centralityValues[idDev][0]] = "gateway"
            self.devices[self.centralityValues[idDev][0]]['tier'] = 2

        self.cloudId = len(self.G.nodes)
        myNode = {}
        myNode['id'] = self.cloudId
        myNode['RAM'] = self.CLOUDCAPACITY
        myNode['FRAM'] = self.CLOUDCAPACITY
        myNode['IPT'] = self.CLOUDSPEED
        myNode['type'] = 'CLOUD'
        myNode['tier'] = 0
        self.devices.append(myNode)
        # Adding Cloud's resource to nodeResources
        self.nodeResources[self.cloudId] = self.CLOUDCAPACITY
        self.node_labels[self.cloudId] = "cloud"
        self.freeNodeResources = self.nodeResources.copy()


        for cloudGtw in self.cloudgatewaysDevices:
            myLink = {}
            myLink['s'] = cloudGtw
            myLink['d'] = self.cloudId
            myLink['PR'] = self.CLOUDPR
            myLink['BW'] = self.CLOUDBW

            myEdges.append(myLink)

        for node in self.devices:
            if 'tier' not in node:
                node['tier'] = 1

        self.netJson['entity'] = self.devices
        self.netJson['link'] = myEdges

        # Plotting the graph with all the element
        if debug_mode:
            tempGraph = self.G
            tempGraph.add_node(self.cloudId)
            for gw_node in list(self.cloudgatewaysDevices):
                tempGraph.add_edge(gw_node, self.cloudId, PR=self.CLOUDPR, BW=self.CLOUDBW)
            pos = nx.spring_layout(tempGraph)

            displacement = -0.09
            label_pos = {node: (x, y + displacement) for node, (x, y) in pos.items()}

            nx.draw(tempGraph, pos)
            nx.draw_networkx_labels(tempGraph, pos, font_size=8)
            nx.draw_networkx_labels(self.G, label_pos, labels=self.node_labels, font_size=8,
                                    horizontalalignment='center')
            plt.show()

        # Win
        with open(self.path + '\\' + self.cnf.resultFolder + '\\' + file_name_network, "w") as netFile:
            netFile.write(json.dumps(self.netJson))
        # Unix
        # with open('/' + self.path + '/' + self.cnf.resultFolder + '/' + file_name_network, "w") as netFile:
        #     netFile.write(json.dumps(self.netJson))

    def simpleAppsGeneration(self, file_name_apps='appDefinition.json',
                             random_resources=True):  # resources available to each module (if False, each module's resources match each node")

        self.appJson = list()

        if random_resources:
            number_of_apps = len(self.netJson['entity']) - 1
        else:
            number_of_apps = self.TOTALNUMBEROFAPPS

        # for n in range(len(self.netJson['entity'])-1): # number of nodes excluding cloud
        for n in range(number_of_apps):
            # if 'type' not in t.nodeAttributes[n] or (t.nodeAttributes[n]['type'].upper() != 'CLOUD'):
            app = dict()
            app['id'] = n
            app['name'] = n

            app['transmission'] = list()

            transmission = dict()
            transmission['message_in'] = ('M.USER.APP.' + str(n))
            transmission['module'] = (str(n) + '_01')

            app['transmission'].append(transmission)

            app['module'] = list()

            module = dict()
            module['id'] = 1
            module['name'] = (str(n) + '_01')
            module['type'] = 'MODULE'
            if random_resources:
                module['RAM'] = eval(self.func_SERVICERESOURCES)
            else:
                module['RAM'] = self.netJson['entity'][n]
            app['module'].append(module)

            app['message'] = list()

            msg = dict()
            msg['id'] = 0
            msg['name'] = 'M.USER.APP.' + str(n)
            msg['s'] = 'None'
            msg['d'] = module['name']
            msg['bytes'] = eval(self.func_SERVICEMESSAGESIZE)
            msg['instructions'] = eval(self.func_SERVICEINSTR)

            app['message'].append(msg)

            self.appJson.append(app)

        #  Win
        with open(self.path + '\\' + self.cnf.resultFolder + '\\' + file_name_apps, 'w') as f:
           json.dump(self.appJson, f)
        # Unix
        # with open(self.path + '/' + self.cnf.resultFolder + '/' + file_name_apps, 'w') as f:
        #     json.dump(self.appJson, f)

        # app popularity
        for app_index in range(len(self.appJson)):
            self.appJson[app_index]['popularity'] = eval(self.func_REQUESTPROB)
        return self.appJson

    def app_generation(self, file_name_apps='appDefinition.json', app_struct='tree'):
        self.apps = list()

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

        self.appJson = list()
        # appJsonBE = list()
        # appJsonDD = list()
        self.servicesResources = {}

        for i in range(0, self.TOTALNUMBEROFAPPS):
            myApp = {}
            # myAppEB = {}
            # myAppDD = {}
            if app_struct == 'linear':
                self.func_APPGENERATION = "linear_graph(random.randint(2, 4))"
            elif app_struct == 'simple':
                self.func_APPGENERATION = "linear_graph(1)"
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

            # if self.cnf.graphicTerminal:
            #     fig, ax = plt.subplots()
            #     pos = nx.spring_layout(APP, seed=15612357)
            #     nx.draw(APP, pos, labels=mylabels, font_size=8)
            #     # Win
            #     fig.savefig(self.path + '\\' + self.cnf.resultFolder + '\\plots\\app_%s.png' % i)
            #     # Unix
            #     # fig.savefig(self.path + '/' + self.cnf.resultFolder + '/plots/app_%s.png' % i)
            #     plt.close(fig)  # close the figure
            #     plt.show()

            mapping = dict(zip(APP.nodes(), range(0, self.numberOfServices + len(APP.nodes))))
            APP = nx.relabel_nodes(APP, mapping)

            self.numberOfServices = self.numberOfServices + len(APP.nodes)
            self.apps.append(APP)
            for j in APP.nodes:
                self.servicesResources[j] = eval(self.func_SERVICERESOURCES)
            self.appsResources.append(self.servicesResources)

            topologicorder_ = list(nx.topological_sort(APP))
            source = topologicorder_[0]

            self.appsSourceService.append(source)

            # self.appsDeadlines[i] = self.myDeadlines[i]

            # Copies of the application's graph that will be used to create the extra app definitions
            # APP_EB = APP.copy()
            # APP_DD = APP.copy()

            myApp['id'] = i
            myApp['name'] = int(i)  # ! int() -> str()    (antes dava erro na sim)
            # myApp['deadline'] = self.appsDeadlines[i]

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
                    if self.cnf.verbose_log:
                        print("Adding source message")
                    for o in APP.edges:
                        if o[0] == source:
                            myTransmission = {}
                            myTransmission['module'] = str(i) + '_' + str(source)
                            myTransmission['message_in'] = "M.USER.APP." + str(i)
                            myTransmission['message_out'] = str(i) + '_(' + str(o[0]) + "-" + str(o[1]) + ")"
                            myApp['transmission'].append(myTransmission)

                    if app_struct == 'simple':
                        myTransmission = {}
                        myTransmission['module'] = str(i) + '_' + str(source)
                        myTransmission['message_in'] = "M.USER.APP." + str(i)
                        myApp['transmission'].append(myTransmission)

                myApp['module'].append(myNode)

            # Acrescentei isto para utilizar nos algoritmos de placement
            nx.set_node_attributes(APP,
                                   dict(zip(range(len(myApp['module'])), [node['name'] for node in myApp['module']])),
                                   "module")
            nx.set_node_attributes(APP,
                                   dict(zip(range(len(myApp['module'])), [node['RAM'] for node in myApp['module']])),
                                   "cost")

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

            self.appJson.append(myApp)

        # Win
        appFile = open(self.path + '\\' + self.cnf.resultFolder + '\\' + file_name_apps, "w")
        # Unix
        # appFile = open(self.cnf.resultFolder + "/appDefinition.json", "w")
        # appFileBE = open(self.cnf.resultFolder + "/appDefinitionBE.json", "w")
        appFile.write(json.dumps(self.appJson))
        appFile.close()

        for app_index in range(len(self.appJson)):
            self.appJson[app_index]['popularity'] = eval(self.func_REQUESTPROB)

    def user_generation(self, file_name_users='usersDefinition.json'):
        # Generation of the IoT devices (users)

        userJson = {}

        self.myUsers = list()

        self.appsRequests = list()
        for i in range(0, self.TOTALNUMBEROFAPPS):
            userRequestList = set()
            # probOfRequested = self.appJson[i]['popularity']
            probOfRequested = eval(self.func_REQUESTPROB)
            # probOfRequested = -1
            atLeastOneAllocated = False
            for j in self.gatewaysDevices:
                if random.random() < probOfRequested:
                    myOneUser = {}
                    myOneUser['app'] = int(i)  # !!!
                    myOneUser['message'] = "M.USER.APP." + str(i)
                    myOneUser['id_resource'] = j
                    myOneUser['lambda'] = eval(self.func_USERREQRAT)
                    userRequestList.add(j)
                    self.myUsers.append(myOneUser)
                    atLeastOneAllocated = True
            if not atLeastOneAllocated:
                j = random.randint(0, len(self.gatewaysDevices) - 1)
                myOneUser = {}
                myOneUser['app'] = int(i)  # !!!
                myOneUser['message'] = "M.USER.APP." + str(i)
                # myOneUser['id_resource'] = j
                myOneUser['id_resource'] = list(self.gatewaysDevices)[j]  # Random GW to host the request
                myOneUser['lambda'] = eval(self.func_USERREQRAT)
                userRequestList.add(list(self.gatewaysDevices)[j])
                self.myUsers.append(myOneUser)
            self.appsRequests.append(userRequestList)

        userJson['sources'] = self.myUsers

        # Win
        userFile = open(self.path + '\\' + self.cnf.resultFolder + "\\" + file_name_users, "w")
        # Unix
        # userFile = open(self.cnf.resultFolder + "/usersDefinition.json", "w")
        userFile.write(json.dumps(userJson))
        userFile.close()

    def rec_placement(self, module_index, current_placement):
        if self.first_alloc and self.complete_first_allocation:
            return

        if len(current_placement) == len(self.all_modules):
            self.all_placements.append(current_placement.copy())
            if self.first_alloc:
                self.complete_first_allocation = True

                if debug_mode:
                    print("first alloc")
            return

        current_module = self.all_modules[module_index]

        # for node in self.G.nodes:
        for node in self.node_order:
            if self.freeNodeResources[node] >= current_module['RAM']:
                current_placement[current_module['name']] = node
                self.freeNodeResources[node] -= current_module['RAM']
                if debug_mode:
                    print('node', node, ':', self.freeNodeResources[node], '\tmodule', current_module['name'], ':',
                          current_module['RAM'])
                self.rec_placement(module_index + 1, current_placement)

                self.freeNodeResources[node] += current_module['RAM']
                current_placement.pop(current_module['name'])

    def backtrack_placement(self, file_name_alloc='allocDefinition.json', file_name_network='netDefinition.json',
                            first_alloc=False, mode='FCFS'):

        self.first_alloc = first_alloc
        self.complete_first_allocation = False  # indicates if the first solution has been found

        # t = Topology()
        # dataNetwork = json.load(open('netDefinition.json'))
        # t.load(dataNetwork)

        # nodes -> self.devices     apps -> self.apps
        current_placement = {}
        self.all_placements = []

        # TODO deep copy
        if mode == 'FCFS':
            self.node_order = self.G.nodes
            self.app_order = self.appJson
        elif mode == 'Random':
            self.node_order = list(self.G.nodes.keys())
            random.shuffle(self.node_order)
            self.app_order = self.appJson
        elif mode == 'high_centrality':
            self.node_order = [node[0] for node in self.centralityValues]
            self.app_order = self.appJson
        elif mode == 'high_centrality_and_app_popularity':
            self.node_order = [node[0] for node in self.centralityValues]
            self.app_order = sorted(self.appJson, key=itemgetter('popularity'), reverse=True)

        self.all_modules = []
        for app in self.app_order:
            for module in app['module']:
                self.all_modules.append(module)

        self.rec_placement(0, current_placement)

        if debug_mode:
            print(mode + "\nnode_oder ->", self.node_order, "\napp_order ->", list(app['id'] for app in self.app_order),
                  "\napp_popularity ->", list((app['id'], app['popularity']) for app in self.appJson))
            print('\n--placements--')
            print(len(self.all_placements))
            print(self.all_placements)

        # first solution.apps
        solution = self.all_placements[0]

        for module, node in solution.items():
            self.netJson['entity'][node]['FRAM'] -= \
            self.appJson[int(module.split("_")[0])]['module'][int(module.split("_")[1]) - 1]['RAM']

            if debug_mode:
                print('node: ', node, '\tapp / module : ', int(module.split("_")[0]), '/', int(module.split("_")[1]),
                      '\tFRAM: ', self.netJson['entity'][node]['FRAM'], '\tRAM: ',
                      self.appJson[int(module.split("_")[0])]['module'][int(module.split("_")[1]) - 1]['RAM'])

        # Alloc será o dicionario convertido para json
        alloc = dict()
        alloc['initialAllocation'] = list()

        for mod in solution:
            temp_dict = dict()
            temp_dict['module_name'] = mod
            temp_dict['app'] = int(mod.split("_")[0])
            temp_dict['id_resource'] = solution[mod]  # node

            alloc['initialAllocation'].append(temp_dict)

        # Win
        with open(self.path + '\\' + self.cnf.resultFolder + '\\' + file_name_alloc, "w") as allocFile:
            allocFile.write(json.dumps(alloc))
        # Unix
        # with open(self.path + '/' + self.cnf.resultFolder + '/' + file_name_alloc, "w") as allocFile:
        #     allocFile.write(json.dumps(alloc))

        # Update FRAM network Json
        # Win
        with open(self.path + '\\' + self.cnf.resultFolder + '\\' + file_name_network, "w") as netFile:
            netFile.write(json.dumps(self.netJson))
        # Unix
        # with open('/' + self.path + '/' + self.cnf.resultFolder + '/' + file_name_network, "w") as netFile:
        #     netFile.write(json.dumps(self.netJson))

    def greedy_algorithm(self, file_name_alloc='allocDefinition.json', file_name_network='netDefinition.json'):
        # best choice for each iteration - node with more FRAM
        # objective ->  maximize the use of resources while avoiding overloading nodes
        # optimal score to achieve = 0
        # score is the "Maximum deviation" (largest difference between the FRAM of a given set of nodes and its mean)
        # firstly, the set of nodes considered are only the gateways, only after the remaining nodes have to be used those nodes are taken into account for the score

        #  popular apps will be allocated, preferably, in lower tier nodes
        self.app_order = sorted(self.appJson, key=itemgetter('popularity'), reverse=True)
        self.all_modules = []
        for app in self.app_order:
            for module in app['module']:
                self.all_modules.append(module)


        # tier2_list = [element for element in self.netJson['entity'] if element['tier'] == 2]  # Filtering gateway nodes
        # tier1_list = [element for element in self.netJson['entity'] if element['tier'] == 1]  # Filtering fog nodes
        # tier0_list = self.netJson['entity'][len(self.netJson['entity']) - 1] # Cloud node
        # tier1_used = False
        # tier0_used = False
        # total_nodes_used = len(tier2_list) - 1

        #initial score
        # total_FRAM = sum(i['FRAM'] for i in tier2_list)
        # mean_score = total_FRAM / total_nodes_used
        # score = max_deviation = max(tier2_list, key=lambda node_: deviation_from_mean(node['FRAM'], mean_score))


        # score in each iteration
        # total_FRAM -= self.netJson['entity'][node_id]['FRAM']
        # mean_score = total_FRAM / total_nodes_used
        # max_deviation = max(tier2_list, key=lambda node_: deviation_from_mean(node['FRAM'], mean_score))
        # if tier1_used:
        #     max_deviation = max(max_deviation, max(tier1_list, key=lambda node_: deviation_from_mean(node['FRAM'], mean_score)))
        #     if tier0_used:
        #         max_deviation = max(max_deviation, deviation_from_mean(tier0_list['FRAM'], mean_score))
        # score = max_deviation


        placement = {}

        # creating original heap
        nodes_heap = []
        heapq.heapify(nodes_heap)
        for node in self.netJson['entity']:
            heapq.heappush(nodes_heap, (-node['tier'], -node['FRAM'], node['id']))

        # # retrieve one node and update FRAM on dict
        # _, _, node_id = heapq.heappop(nodes_heap)
        # self.netJson['entity'][node_id]['FRAM'] -= 0  # module['RAM']
        # # add the node back to the heap
        # heapq.heappush(nodes_heap,
        #                (-self.netJson['entity'][node_id]['tier'], -self.netJson['entity'][node_id]['FRAM'], node_id))

        for current_module in self.all_modules:
            if debug_mode:
                sorted_nodes = sorted(self.netJson['entity'], key=lambda node: (-node['tier'], -node['FRAM']))

                if debug_mode:
                    for node in sorted_nodes:
                        print("ID:", node['id'], "FRAM:", node['FRAM'], "Tier:", node['tier'])
                    print()

            nodes_retrieved = []
            module_placed = False
            while (not module_placed) and len(nodes_heap):
                node_tier, node_FRAM, node_id = heapq.heappop(nodes_heap)
                if self.netJson['entity'][node_id]['FRAM'] >= current_module['RAM']:
                    if debug_mode:
                        print(current_module['name'], 'module RAM: ', current_module['RAM'], '-->> node' , node_id ,'\n')
                    self.netJson['entity'][node_id]['FRAM'] -= current_module['RAM']
                    placement[current_module['name']] = node_id
                    module_placed = True
                    heapq.heappush(nodes_heap,(-self.netJson['entity'][node_id]['tier'], -self.netJson['entity'][node_id]['FRAM'],node_id))
                    # print(sorted((node['id'],node['FRAM']) for node in self.netJson) )

                else:
                    nodes_retrieved.append((node_tier, node_FRAM, node_id))
            if len(nodes_heap)==0:
                print('NO FRAM LEFT FOR MODULE ', current_module['name'])
            if nodes_retrieved:
                for node_retrieved in nodes_retrieved:
                    heapq.heappush(nodes_heap, (node_retrieved[0], node_retrieved[1], node_retrieved[2]))
        if debug_mode:
            print(placement)

        # Alloc será o dicionario convertido para json
        alloc = dict()
        alloc['initialAllocation'] = list()

        for module in placement:
            temp_dict = dict()
            temp_dict['module_name'] = module
            temp_dict['app'] = int(module.split("_")[0])
            temp_dict['id_resource'] = placement[module]  # node

            alloc['initialAllocation'].append(temp_dict)

        # Win
        with open(self.path + '\\' + self.cnf.resultFolder + '\\' + file_name_alloc, "w") as allocFile:
            allocFile.write(json.dumps(alloc))
        # Unix
        # with open(self.path + '/' + self.cnf.resultFolder + '/' + file_name_alloc, "w") as allocFile:
        #     allocFile.write(json.dumps(alloc))

        # Update FRAM network Json
        # # Win
        with open(self.path + '\\' + self.cnf.resultFolder + '\\' + file_name_network, "w") as netFile:
            netFile.write(json.dumps(self.netJson))
        # # Unix
        # with open('/' + self.path + '/' + self.cnf.resultFolder + '/' + file_name_network, "w") as netFile:
        #     netFile.write(json.dumps(self.netJson))

    def bt_min_mods(self, file_name_apps='appDefinition.json', file_name_alloc='allocDefinition.json'):
        available_res = self.freeNodeResources.copy()
        available_res.pop(max(available_res))  # Remove-se o node da Cloud

        used_res = list()
        services = list()
        best_solution = list()

        apps = json.load(open(self.path + '\\' + self.cnf.resultFolder + '\\' + file_name_apps))

        for app in apps:
            for mod in app['module']:
                services.append({'module_name': mod['name'], 'RAM': mod['RAM'], 'app': app['id']})

        best_solution = self.bt_min_mods_(available_res, used_res, services, best_solution)

        alloc = dict()

        for index, service in enumerate(services):
            service['id_resource'] = best_solution[index]
            self.freeNodeResources[service['id_resource']] -= service['RAM']  # Subtrai o recurso usado
            service.pop('RAM')

        alloc['initialAllocation'] = services

        # # Win
        with open(self.path + '\\' + self.cnf.resultFolder + "\\" + file_name_alloc, "w") as netFile:
            netFile.write(json.dumps(alloc))
        # Unix
        # with open(self.path + '/' + path + "/allocDefinition.json", "w") as netFile:
        # with open(self.path + '/' + path + file_name, "w") as netFile:
        #     netFile.write(json.dumps(alloc))

    def bt_min_mods_(self, available_res, cur_solution, services, best_solution, index=0):

        # Chegando ao fim da arvore de recursao, decide-se qual o melhor placement
        if index == len(services):
            # Caso a solucao atual use - que a melhor, ou seja a 1a a existir, é retornada a solucao atual
            if len(set(cur_solution)) < len(set(best_solution)) or len(best_solution) == 0:
                return cur_solution.copy()

            # Caso as 2 soluções empatem, é considerada a opção que utilizar os nodes com - recursos
            elif len(set(cur_solution)) == len(set(best_solution)) \
                    and sum([self.nodeResources[node_index] for node_index in set(cur_solution)]) < \
                    sum([self.nodeResources[node_index] for node_index in set(best_solution)]):

                return cur_solution.copy()

            else:
                return best_solution

        for node_index in available_res:
            if available_res[node_index] >= services[index]['RAM']:
                available_res[node_index] -= services[index]['RAM']
                cur_solution.append(node_index)

                if len(set(cur_solution)) <= len(set(best_solution)) or len(best_solution) == 0:
                    best_solution = self.bt_min_mods_(available_res, cur_solution, services, best_solution, index + 1)

                available_res[node_index] += services[index]['RAM']
                cur_solution.pop(index)

        return best_solution

    def resilient_placement(self, file_name_apps='appDefinition.json'):
        # Nota: Este algoritmo de placement tinha em conta que um node só poderia ter um module

        # Alloc será o dicionario convertido para json
        alloc = dict()
        alloc['initialAllocation'] = list()

        max_res = max([len(app['module']) for app in self.appJson])  # Obtem-se o # max e min de modulos de uma app
        min_res = min([len(app['module']) for app in self.appJson])  #
        n_comms = 0

        # Decide-se o nr de communities max de forma a conseguir suportar a maior app (caso seja possivel)
        while n_comms < len(self.netJson['entity']):
            temp_comms = nx.algorithms.community.asyn_fluidc(self.G, n_comms + 1)

            if all(len(x) < max_res for x in temp_comms) or any(len(x) < min_res for x in temp_comms):
                break

            n_comms += 1

        comms = nx.algorithms.community.asyn_fluidc(self.G, n_comms)
        comms = [list(x) for x in list(comms)]

        for app in self.appJson:
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

        # Win
        with open(self.path + '\\' + self.cnf.resultFolder + '\\' + file_name_apps, 'w') as f:
            json.dump(alloc, f)

        # # Unix
        # with open(self.path + '/' + self.cnf.resultFolder + '/' + file_name_apps, 'w') as f:
        #     json.dump(alloc, f)

    def near_GW_placement(self, file_name_alloc='allocDefinition.json', weight='PR'):

        # Funcao de peso utilizada no algoritmo de routing de min_path (o meu)
        if weight == 'BW_PR':
            weight = lambda src, dst, data: 1 / data.get('BW') + data.get('PR')

        elif weight == 'BW':
            weight = lambda src, dst, data: 1 / data.get('BW')

        elif weight == 'IPT':
            weight = lambda src, dst, data: 1 / self.netJson['entity'][dst]['IPT']

        alloc = dict()
        module2app_map = dict()

        origin_lens = dict()

        # Separam-se os nodes por comprimentos até à origem
        for app_i, app in enumerate(self.apps):
            for cand_nd in app:

                length = len(nx.shortest_path(app, 0, cand_nd)) - 1

                if length not in origin_lens:
                    origin_lens[length] = dict()

                if app_i not in origin_lens[length]:
                    origin_lens[length][app_i] = list()

                origin_lens[length][app_i].append(cand_nd)

        max_branch_len = max(origin_lens.keys())

        for length in range(max_branch_len + 1):
            for app_i, app in enumerate(self.apps):
                if length == 0:
                    cost = app.nodes[0]['cost']

                    # Array com os nodes que conseguem abarcar o 1o modulo da app
                    candidate_nodes = [nd for nd, res in self.freeNodeResources.items() if res >= cost and nd != self.cloudId]

                    if len(candidate_nodes) == 0:
                        chosen_node = self.cloudId
                    else:
                        # Calcula-se o sumatorio das distancias aos GW's
                        GW_dists = [sum(nx.shortest_path_length(self.G, source=GW, target=cnd_nd, weight=weight)
                                        for GW in self.gatewaysDevices) for cnd_nd in candidate_nodes]

                        # Dentro destes, escolhe-se os com distancia <
                        candidate_nodes = [node for i, node in enumerate(candidate_nodes) if GW_dists[i] == min(GW_dists)]

                        chosen_node_FRAM = max(self.freeNodeResources[n] for n in candidate_nodes)

                        # Dentro destes, escolhe-se o com FRAM >
                        chosen_node = [nd for nd in candidate_nodes if self.freeNodeResources[nd] == chosen_node_FRAM][0]

                    self.freeNodeResources[chosen_node] -= cost
                    app.nodes[0]['id_resource'] = chosen_node

                    alloc[app.nodes[0]['module']] = chosen_node
                    module2app_map[app.nodes[0]['module']] = app_i

                else:
                    # Verifica se existe algum elemento desse comprimento na app
                    if app_i not in origin_lens[length]:
                        continue

                    for app_node in origin_lens[length][app_i]:
                        cost = app.nodes[app_node]['cost']

                        parent_app_nd = [edge[0] for edge in app.edges()][0]
                        parent_id_res = alloc[app.nodes[parent_app_nd]['module']]

                        candidate_nodes = [parent_id_res]
                        visited_nodes = list()

                        while True:
                            # Se, apos todos os nodes serem vistos, nao foi possivel alocar o modulo, aloca-se na cloud
                            if len(candidate_nodes) == 0:
                                chosen_node = self.cloudId
                                break

                            # lista que guarda temporariamente os nodes que nao conseguem abarcar o modulo
                            insuf_res = list()

                            # guardam-se os nodes que nao conseguem abarcar o modulo
                            for i, nd in enumerate(candidate_nodes):
                                if self.freeNodeResources[nd] < cost:
                                    insuf_res.append(candidate_nodes.pop(i))

                            # Calcula-se o sumatorio de PR usado para chegar aos GW's
                            GW_dists = [nx.shortest_path_length(self.G, source=parent_id_res, target=cnd_nd, weight=weight) for cnd_nd in candidate_nodes]

                            # Dentro destes, escolhe-se os com peso <
                            candidate_nodes = [node for i, node in enumerate(candidate_nodes) if GW_dists[i] == min(GW_dists)]

                            if len(candidate_nodes) != 0:
                                chosen_node_FRAM = max(self.freeNodeResources[n] for n in candidate_nodes)
                                chosen_node = [nd for nd in candidate_nodes if self.freeNodeResources[nd] == chosen_node_FRAM][0]
                                break

                            else:
                                # Voltam-se a adicionar os insuf_res para considerarmos os seus vizinhos
                                candidate_nodes += insuf_res

                                # Atualiza a lista de nodes já visitados
                                visited_nodes += candidate_nodes

                                # Vao se buscar os nodes vizinhos dos candidate anteriores
                                candidate_nodes = [e[1] for e in self.G.edges if e[0] in candidate_nodes] + \
                                                  [e[0] for e in self.G.edges if e[1] in candidate_nodes]

                                # Removem-se elementos repetidos (vizinhos em comum) e os já vistos
                                candidate_nodes = list(set(candidate_nodes))
                                candidate_nodes = [nd for nd in candidate_nodes if nd not in visited_nodes]

                        self.freeNodeResources[chosen_node] -= app.nodes[app_node]['cost']

                        app.nodes[app_node]['id_resource'] = chosen_node
                        alloc[app.nodes[app_node]['module']] = chosen_node
                        module2app_map[app.nodes[app_node]['module']] = app_i

        allocDef = dict()
        allocDef["initialAllocation"] = list()
        for mod, id_res in alloc.items():
            temp_dict = dict()

            temp_dict['module_name'] = mod
            temp_dict['id_resource'] = id_res
            temp_dict['app'] = module2app_map[mod]

            allocDef["initialAllocation"].append(temp_dict)

        # Win
        with open(self.path + '\\' + self.cnf.resultFolder + '\\' + file_name_alloc, 'w') as f:
            json.dump(allocDef, f)

        # # Unix
        # with open(self.path + '/' + s

    def lambda_placement(self, file_name_alloc='allocDefinition.json', comm_nr=3):
        # comm_nr = len(self.G.nodes)

        mod2cost = dict()
        for app_ind in self.appJson:
            for mod in app_ind['module']:
                mod2cost[mod['name']] = mod['RAM']

        # lista que irá guardar as comms em que index = resolution correspondente
        comms_list = list()

        # Começa com 1 node <=> 1 community
        max_res = 0

        while True:
            # Calculam-se as communities para a respetiva resolution
            comms = nx.community.louvain_communities(self.G, resolution=max_res,
                                                     weight=lambda src, dst, data: 1 / data.get('BW') + data.get('PR'))
            # Add na lista
            comms_list.insert(0, comms)

            # Se o nr de communities for = ao nr de nodes, já nao dá para subdividir mais a TOPO
            if len(comms) >= comm_nr or len(comms) == len(self.G.nodes):
                break
            # Senao passa-se para a resolution seguinte
            else:
                max_res += 1

        # dict {app: min lambda}
        min_lambda = dict()
        for user in self.myUsers:
            if user['app'] not in min_lambda or min_lambda[user['app']] > user['lambda']:
                min_lambda[user['app']] = user['lambda']

        # a partir de dict_key as apps sao ordenadas pela sua "urgencia"
        app_order = list(min_lambda.keys())
        app_order.sort(key=lambda e: min_lambda[e])

        # dict {node: sum das distancias a cada GW}
        node2GW_dists = dict()
        for nd in self.G.nodes():
            node2GW_dists[nd] = sum(nx.shortest_path_length(self.G, nd, GW,
                                                            weight=lambda src, dst, data: 1 / data.get('BW') + data.get('PR')) for GW in self.gatewaysDevices)

        # dict {app: {modulo: [id_res, cost]}}
        temp_alloc = dict()

        # Ordem de communities: +resolution (+ comms) ---> -resolution (- comms)

        for communities in comms_list:

            # Reordenam-se as communities com a resolucao atual pela distancia as GWs
            communities.sort(key=lambda e: sum([node2GW_dists[n] for n in e]) / len(e))

            for app_ind in app_order:
                # app = self.apps[app_ind]

                for comm in communities:

                    allocated = self.lambda_placement_(comm, node2GW_dists, temp_alloc, app_ind)

                    # Se uma comm nao suportar 1 app, procura na seguinte
                    if not allocated:
                        if app_ind in temp_alloc:
                            # Reverte alloc da app
                            for app_nd in temp_alloc[app_ind]:
                                self.freeNodeResources[temp_alloc[app_ind][app_nd]['id_resource']] += mod2cost[temp_alloc[app_ind][app_nd]['module_name']]

                            del temp_alloc[app_ind]

                    # Se já conseguiu allocar nalguma community, passa para a proxima app
                    else:
                        break

                # Se não conseguir em nenhuma das comms, reverte a allocacao e passa para uma resolução <
                if not allocated:
                    # Reverte toda a allocação

                    for app_alloc in temp_alloc:
                        # Reverte alloc da app
                        for app_nd in temp_alloc[app_alloc]:
                            self.freeNodeResources[temp_alloc[app_alloc][app_nd]['id_resource']] += mod2cost[temp_alloc[app_alloc][app_nd]['module_name']]

                    temp_alloc = dict()
                    break

            # Se conseguiu allocar com a resolution anterior, nao tentar com outra <
            if allocated:
                break

        allocDef = {'initialAllocation': list()}
        for app in temp_alloc:
            for app_nd in temp_alloc[app]:
                allocDef['initialAllocation'].append({"module_name": temp_alloc[app][app_nd]["module_name"], "id_resource": temp_alloc[app][app_nd]["id_resource"], "app": app})

        # Win
        with open(self.path + '\\' + self.cnf.resultFolder + '\\' + file_name_alloc, 'w') as f:
            json.dump(allocDef, f)

    def lambda_placement_(self, comm, node2GW_dists, temp_alloc, app_i, app_nd=0):
        # retorna True se a app foi allocada na community com sucesso, ou False senao

        cost = self.apps[app_i].nodes[app_nd]['cost']
        candidate_nds = [nd for nd in comm if self.freeNodeResources[nd] >= cost]

        if len(candidate_nds) == 0:
            return False

        if app_nd == 0:
            temp_alloc[app_i] = dict()

            # São escolhidos os nodes + proximos
            candidate_nds = [nd for nd in candidate_nds if node2GW_dists[nd] == min([node2GW_dists[n] for n in candidate_nds])]

        else:
            # prnt_nd da app
            prnt_nd = [edge[0] for edge in self.apps[app_i].edges if edge[1] == app_nd][0]
            # prnt_nd da TOPO
            prnt_nd = temp_alloc[app_i][prnt_nd]['id_resource']

            # minimal distance to parent
            min_dist = min([nx.shortest_path_length(self.G, prnt_nd, nd,
                                             weight=lambda src, dst, data: 1 / data.get('BW') + data.get('PR')) for nd in candidate_nds])

            # candidate_nds = nodes com - distancia ao node pai
            candidate_nds = [nd for nd in candidate_nds
                             if nx.shortest_path_length(self.G, prnt_nd, nd,
                                                 weight=lambda src, dst, data: 1 / data.get('BW') + data.get('PR')) == min_dist]

        if len(candidate_nds) != 0:
            chosen_nd = candidate_nds[0]
            temp_alloc[app_i][app_nd] = {'id_resource': chosen_nd, 'module_name': self.apps[app_i].nodes[app_nd]['module']}
            self.freeNodeResources[chosen_nd] -= cost

        else:
            return False

        dests = [edge[1] for edge in self.apps[app_i].edges if edge[0] == app_nd]

        for nd_son in dests:
            return self.lambda_placement_(comm, node2GW_dists, temp_alloc, app_i, nd_son)

        return True

    def randomPlacement(self, file_name_alloc='allocDefinition.json', file_name_network='netDefinition.json'):
        # nodes -> self.devices     apps -> self.apps
        rnd_placement = {}

        for app in self.appJson:
            for module in app['module']:
                for i in range(50):
                    index = random.randint(0, (len(self.netJson['entity']) - 1))
                    # Se o node 'index' tiver recursos suficientes para alocar o modulo:
                    if self.freeNodeResources[index] >= module['RAM']:
                        self.freeNodeResources[index] -= module['RAM']
                        if app['id'] not in rnd_placement:
                            rnd_placement[app['id']] = dict()
                        rnd_placement[app['id']][module['name']] = index
                        break

                    if i == 49:
                        print(f"Nao foi possivel alocar o modulo {module} após 50 iterações.")

        alloc = dict()
        alloc['initialAllocation'] = list()

        for app in rnd_placement:
            for mod, res in rnd_placement[app].items():
                temp_dict = dict()
                temp_dict["module_name"] = mod
                temp_dict["app"] = app
                temp_dict["id_resource"] = res

                alloc['initialAllocation'].append(temp_dict)

        # atualiza valores de FRAM
        net_json = json.load(open(self.path + '\\' + self.cnf.resultFolder + '\\' + file_name_network))

        for node in net_json['entity']:
            node['FRAM'] = self.freeNodeResources[node['id']]

        with open(self.path + '\\' + self.cnf.resultFolder + '\\' + file_name_network, "w") as netFile:
            netFile.write(json.dumps(net_json))

        # Guarda a alocação no .json
        with open(self.path + '\\' + self.cnf.resultFolder + '\\' + file_name_alloc, "w") as netFile:
            netFile.write(json.dumps(alloc))

    def config_generation(self, n=20, m=2, path_network='', file_name_network='netDefinition.json', path_apps='',
                          file_name_apps='appDefinition.json', path_alloc='', file_name_alloc='allocDefinition.json'):
        self.networkGeneration(n, m, path_network, file_name_network)
        self.simpleAppsGeneration(path_apps, file_name_apps, random_resources=False)
        self.backtrack_placement(path_alloc, file_name_alloc)

    def config_generation_random_resources(self, n=20, m=2, path_network='', file_name_network='netDefinition.json',
                                           path_apps='',
                                           file_name_apps='appDefinition.json', path_alloc='',
                                           file_name_alloc='allocDefinition.json'):
        self.networkGeneration(n, m, path_network, file_name_network)
        self.simpleAppsGeneration(path_apps, file_name_apps, random_resources=True)
        self.backtrack_placement(path_alloc, file_name_alloc, first_alloc=True,
                                 mode='high_centrality_and_app_popularity')  # FCFS - high_centrality - Random - high_centrality_and_app_popularity

    def config_generation_timer(self, n=20, m=2, file_name_network='netDefinition.json',
                                              file_name_apps='appDefinition.json',
                                              file_name_users='usersDefinition.json',
                                              file_name_alloc='allocDefinition.json',
                                              placement_alg='backtrack_placement',
                                              seed=100000):
        random.seed(seed)
        self.networkGeneration(n, m, file_name_network)
        random.seed(seed)
        self.app_generation(file_name_apps, 'simple')
        random.seed(seed)
        self.user_generation(file_name_users)

        random.seed(seed)
        ti = time.time()

        if placement_alg == 'backtrack_placement':
            self.backtrack_placement(file_name_alloc=file_name_alloc, file_name_network=file_name_network, first_alloc=True,
                                     mode='high_centrality_and_app_popularity')  # FCFS - high_centrality - Random - high_centrality_and_app_popularity

        elif placement_alg == 'randomPlacement':
            self.randomPlacement(file_name_network=file_name_network)
        elif placement_alg == 'bt_min_mods':
            self.bt_min_mods()
        elif placement_alg == 'near_GW_placement':
            self.near_GW_placement()
        elif placement_alg == 'greedy_algorithm':
            self.greedy_algorithm()

        tf = time.time()

        return tf-ti




# conf = myConfig.myConfig()  # Setting up configuration preferences                                                    #! 27/08
# random.seed(15612357)                                                                                                 #! 27/08

#
# exp_config = ExperimentConfiguration(conf)                                                                            #! 27/08
# exp_config.config_generation(n=10)
# exp_config.config_generation_random_resources(n=10)                                                                   #! 27/08

# exp_config.networkGeneration(10)
# exp_config.simpleAppsGeneration()
# exp_config.backtrack_placement()
# print()
