import json
import networkx as nx

import re
import random
import time
from math import floor
import matplotlib.pyplot as plt

import operator
import json
import os
from yafs import Topology

# def placement_algorithm(graph, app_def='data/appDefinition.json'):
#
#     # Alloc será o dicionario convertido para json
#     alloc = dict()
#     alloc['initialAllocation'] = list()
#
#     apps = json.load(open(app_def))
#
#     max_res = max([len(app['module']) for app in apps])   #
#     min_res = min([len(app['module']) for app in apps])   #
#     n_comms = 0
#
#     # Decide-se o nr de communities max de forma a conseguir suportar a maior app (caso seja possivel)
#     while n_comms < len(graph.nodes):
#         temp_comms = nx.algorithms.community.asyn_fluidc(graph, n_comms+1)
#
#         if all(len(x) < max_res for x in temp_comms) or any(len(x) < min_res for x in temp_comms):
#             break
#
#         n_comms += 1
#
#     comms = nx.algorithms.community.asyn_fluidc(graph, n_comms)
#     comms = [list(x) for x in list(comms)]
#
#     for app in apps:
#         for mod in app['module']:
#
#             # Vai rodando até encontrar uma community que consiga suportar a app inteira
#             while len(app['module']) > len(comms[0]) and n_comms != 1:
#                 comms.append(comms.pop(0))
#
#             temp_dict = dict()
#             temp_dict['module_name'] = mod['name']
#             temp_dict['app'] = app['id']
#             temp_dict['id_resource'] = comms[0][0]
#
#             comms[0].append(comms[0].pop(0))
#
#             alloc['initialAllocation'].append(temp_dict)
#
#         # Se houver mais do que 1 community, roda
#         if n_comms != 1:
#             comms.append(comms.pop(0))
#
#     with open('data/allocDefinition.json', 'w') as f:
#         json.dump(alloc, f)
#
#
# # func_POWERmax = "random.randint(400,1000)"
# # func_POWERmin = "random.randint(50,300)"
#


# t = Topology()
# # dataNetwork = json.load(open('data/network.json'))
# dataNetwork = json.load(open('netDefinition.json'))
# t.load(dataNetwork)
#
# x = simpleApps(t)
# print()


debug_mode = True


class ExperimentConfiguration:

    def __init__(self, lconf):
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
        self.func_APPGENERATION = "nx.gn_graph(random.randint(2,8))"  # algorithm for the generation of the random applications
        self.func_SERVICEINSTR = "random.randint(20000,60000)"  # INSTR --> teniedno en cuenta nodespped esto nos da entre 200 y 600 MS
        self.func_SERVICEMESSAGESIZE = "random.randint(1500000,4500000)"  # BYTES y teniendo en cuenta net bandwidth nos da entre 20 y 60 MS

        self.func_SERVICERESOURCES = "random.randint(1,5)"  # MB de ram que consume el servicio, teniendo en cuenta noderesources y appgeneration tenemos que nos caben aprox 1 app por nodo o unos 10 servicios

        self.func_APPDEADLINE = "random.randint(2600,6600)"  # MS

        self.func_NETWORKGENERATION = "nx.barabasi_albert_graph(n, m)"

        self.cnf = lconf
        # self.scenario = lconf.myConfiguration

        current_time = int(time.time())
        random.seed(current_time)

    def networkGeneration(self, n=20, m=2, path='', file_name='netDefinition.json'):
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

        initialIndx = int(
            (1 - self.PERCENTATGEOFGATEWAYS) * len(self.G.nodes))  # Getting the indexes for the GWs nodes

        for idDev in range(initialIndx, len(self.G.nodes)):
            self.gatewaysDevices.add(self.centralityValues[idDev][0])  # lowest centralities
            self.node_labels[self.centralityValues[idDev][0]] = "gateway"

        self.cloudId = len(self.G.nodes)
        myNode = {}
        myNode['id'] = self.cloudId
        myNode['RAM'] = self.CLOUDCAPACITY
        myNode['FRAM'] = self.CLOUDCAPACITY
        myNode['IPT'] = self.CLOUDSPEED
        myNode['type'] = 'CLOUD'
        self.devices.append(myNode)
        # Adding Cloud's resource to nodeResources
        self.nodeResources[self.cloudId] = self.CLOUDCAPACITY
        self.node_labels[self.cloudId] = "cloud"

        for cloudGtw in self.cloudgatewaysDevices:
            myLink = {}
            myLink['s'] = cloudGtw
            myLink['d'] = self.cloudId
            myLink['PR'] = self.CLOUDPR
            myLink['BW'] = self.CLOUDBW

            myEdges.append(myLink)

        self.netJson['entity'] = self.devices
        self.netJson['link'] = myEdges

        # Plotting the graph with all the element
        if True:
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

        # # Win
        # with open(os.path.dirname(__file__) + '\\' + path + file_name, "w") as netFile:
        #     netFile.write(json.dumps(self.netJson))
        # Unix
        with open(os.path.dirname(__file__) + '/' + path + file_name, "w") as netFile:
            netFile.write(json.dumps(self.netJson))

    def simpleAppsGeneration(self, path='', file_name='appDefinition.json', random_resources = True):  # resources available to each module (if False, each module's resources match each node"

        self.apps = list()

        t = Topology()
        dataNetwork = json.load(open('netDefinition.json'))
        t.load(dataNetwork)

        for n in t.G.nodes:
            if 'type' not in t.nodeAttributes[n] or (t.nodeAttributes[n]['type'].upper() != 'CLOUD'):
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
                    module['RAM'] = t.nodeAttributes[n]['RAM']
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

                self.apps.append(app)

        with open((path + file_name), 'w') as f:
            json.dump(self.apps, f)
        return self.apps

    def rec_placement(self, module_index, current_placement):
        if self.first_alloc and self.complete_first_allocation:
            return

        if len(current_placement) == len(self.all_modules):
            self.all_placements.append(current_placement.copy())
            if self.first_alloc:
                self.complete_first_allocation = True
                print("first alloc")
            return

        current_module = self.all_modules[module_index]

        # for node in self.G.nodes:
        for node in self.node_order:
            if self.freeNodeResources[node] >= current_module['RAM']:
                current_placement[current_module['name']] = node
                self.freeNodeResources[node] -= current_module['RAM']

                self.rec_placement(module_index + 1, current_placement)

                self.freeNodeResources[node] += current_module['RAM']
                current_placement.pop(current_module['name'])

    def backtrack_placement(self, path='', file_name_alloc='allocDefinition.json', file_name_network='netDefinition.json',first_alloc=False, mode = 'FCFS'):

        self.first_alloc = first_alloc
        self.complete_first_allocation = False

        t = Topology()
        dataNetwork = json.load(open('netDefinition.json'))
        t.load(dataNetwork)

        # n_modules = len([app['module'] for app in self.apps])
        # self.n_modules = sum(len(app['module']) for app in self.apps)

        self.all_modules = []
        for app in self.apps:
            for module in app['module']:
                self.all_modules.append(module)

        self.freeNodeResources = self.nodeResources



        # nodes -> self.devices     apps -> self.apps
        self.all_placements = []
        current_placement = {}


        if mode == 'FCFS':
            self.node_order = self.G.nodes
        elif mode == 'Random':
            self.node_order = list(self.G.nodes.keys())
            random.shuffle(self.node_order)
        elif mode == 'high_centrality':
            self.node_order = [node[0] for node in self.centralityValues]


        self.rec_placement(0, current_placement)
        if debug_mode:
            print(mode , self.node_order)
            print('\n--placements--')
            print(len(self.all_placements))
            print(self.all_placements)

        # first solution
        solution = self.all_placements[0]

        for module, node in solution.items():
            self.netJson['entity'][node]['FRAM'] -= self.apps[int(module.split("_")[0])]['module'][int(module.split("_")[1])-1]['RAM']

        # Alloc será o dicionario convertido para json
        alloc = dict()
        alloc['initialAllocation'] = list()

        for mod in solution:
            temp_dict = dict()
            temp_dict['module_name'] = mod
            temp_dict['app'] = mod.split("_")[0]
            temp_dict['id_resource'] = solution[mod]  # node

            alloc['initialAllocation'].append(temp_dict)

        # # Win
        # with open(os.path.dirname(__file__) + '\\' + path + "file_name, "w") as allocFile:
        #     allocFile.write(json.dumps(alloc))
        # Unix
        # with open(os.path.dirname(__file__) + '/' + path + "/allocDefinition.json", "w") as netFile:
        with open(os.path.dirname(__file__) + '/' + path + file_name_alloc, "w") as allocFile:
            allocFile.write(json.dumps(alloc))

        # # Win
        # with open(os.path.dirname(__file__) + '\\' + path + file_name, "w") as netFile:
        #     netFile.write(json.dumps(self.netJson))
        # Unix
        with open(os.path.dirname(__file__) + '/' + path + file_name_network, "w") as netFile:
            netFile.write(json.dumps(self.netJson))


        # TODO atualizar network definition FRAM

    def config_generation(self, n=20, m=2, path_network='', file_name_network='netDefinition.json', path_apps='',
                          file_name_apps='appDefinition.json', path_alloc='', file_name_alloc='allocDefinition.json'):
        self.networkGeneration(n, m, path_network, file_name_network)
        self.simpleAppsGeneration(path_apps, file_name_apps, random_resources=False)
        self.backtrack_placement(path_alloc, file_name_alloc)

    def config_generation_random_resources(self, n=20, m=2, path_network='', file_name_network='netDefinition.json', path_apps='',
                      file_name_apps='appDefinition.json', path_alloc='', file_name_alloc='allocDefinition.json'):
        self.networkGeneration(n, m, path_network, file_name_network)
        self.simpleAppsGeneration(path_apps, file_name_apps, random_resources=True)
        self.backtrack_placement(path_alloc, file_name_alloc, first_alloc=True, mode='high_centrality') # FCFS - high_centrality - Random


import myConfig

conf = myConfig.myConfig()  # Setting up configuration preferences
random.seed(15612357)

#
exp_config = ExperimentConfiguration(conf)
# exp_config.config_generation(n=10)
exp_config.config_generation_random_resources(n=10)

# exp_config.networkGeneration(10)
# exp_config.simpleAppsGeneration()
# exp_config.backtrack_placement()
# print()
