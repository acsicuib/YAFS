import json
import networkx as nx

import re
import random
from math import floor
import matplotlib.pyplot as plt

import operator
import os
from yafs import Topology

import myConfig


def stable_placement(graph, app_def='data/appDefinition.json'):

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

debug_mode=True

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
        # self.func_APPGENERATION = "nx.gn_graph(random.randint(2,8))"  # algorithm for the generation of the random applications
        self.func_APPGENERATION = "self.linear_graph(random.randint(2, 4))"  # algorithm for the generation of the random applications (agora linear)
        self.func_SERVICEINSTR = "random.randint(20000,60000)"  # INSTR --> teniedno en cuenta nodespped esto nos da entre 200 y 600 MS
        self.func_SERVICEMESSAGESIZE = "random.randint(1500000,4500000)"  # BYTES y teniendo en cuenta net bandwidth nos da entre 20 y 60 MS

        self.func_SERVICERESOURCES = "random.randint(1,5)"  # MB de ram que consume el servicio, teniendo en cuenta noderesources y appgeneration tenemos que nos caben aprox 1 app por nodo o unos 10 servicios

        self.func_APPDEADLINE = "random.randint(2600,6600)"  # MS

        self.func_NETWORKGENERATION = "nx.barabasi_albert_graph(n, m)"

        self.cnf = lconf
        # self.scenario = lconf.myConfiguration




    def networkGeneration(self, n=20, m=2, path='', file_name='netDefinition.json'):
        # Generation of the network topology

        # Topology genneration

        self.G = eval(self.func_NETWORKGENERATION)

        self.devices = list()

        self.nodeResources = {}
        self.freeNodeResources = {}

        self.nodeSpeed = {}
        for i in self.G.nodes:
            self.nodeResources[i] = eval(self.func_NODERESOURECES)
            self.nodeSpeed[i] = eval(self.func_NODESPEED)

        for e in self.G.edges:
            self.G[e[0]][e[1]]['PR'] = eval(self.func_PROPAGATIONTIME)
            self.G[e[0]][e[1]]['BW'] = eval(self.func_BANDWITDH)

        # JSON EXPORT

        netJson = {}
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
        centralityValues = sorted(centralityValuesNoOrdered.items(), key=operator.itemgetter(1), reverse=True)

        self.gatewaysDevices = set()
        self.cloudgatewaysDevices = set()

        highestCentrality = centralityValues[0][1]

        for device in centralityValues:
            if device[1] == highestCentrality:
                self.cloudgatewaysDevices.add(device[0])  # highest centrality
                self.node_labels[device[0]] = "cloudgateway"

        initialIndx = int(
            (1 - self.PERCENTATGEOFGATEWAYS) * len(self.G.nodes))  # Getting the indexes for the GWs nodes

        for idDev in range(initialIndx, len(self.G.nodes)):
            self.gatewaysDevices.add(centralityValues[idDev][0])  # lowest centralities
            self.node_labels[centralityValues[idDev][0]] = "gateway"

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
        self.freeNodeResources = self.nodeResources

        for cloudGtw in self.cloudgatewaysDevices:
            myLink = {}
            myLink['s'] = cloudGtw
            myLink['d'] = self.cloudId
            myLink['PR'] = self.CLOUDPR
            myLink['BW'] = self.CLOUDBW

            myEdges.append(myLink)

        netJson['entity'] = self.devices
        netJson['link'] = myEdges

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
            nx.draw_networkx_labels(self.G, label_pos, labels=self.node_labels, font_size=8, horizontalalignment='center' )
            plt.show()

        # # Win
        with open(os.path.dirname(__file__) + '\\' + path + file_name, "w") as netFile:
            netFile.write(json.dumps(netJson))

        self.t = Topology()
        self.dataNetwork = json.load(open('netDefinition.json'))
        self.t.load(self.dataNetwork)

        # Unix
        # with open(os.path.dirname(__file__) + '' + path + file_name, "w") as netFile:
        #     netFile.write(json.dumps(netJson))

    def simpleAppsGeneration(self, path='', file_name='appDefinition.json'):

        random_resources = True # resources available to each module (if False, each module's resources match each node"
        # apps = list()
        self.apps = list()

        for n in self.t.G.nodes:
            if 'type' not in self.t.nodeAttributes[n] or (self.t.nodeAttributes[n]['type'].upper() != 'CLOUD'):
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
                    module['RAM'] = self.t.nodeAttributes[n]['RAM']
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

    def linear_graph(self, size):
        g = nx.DiGraph()
        g.add_nodes_from(range(size))
        g.add_edges_from(tuple(zip(range(1, size), range(size - 1))))

        return g

    def appGeneration(self):
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

            # if self.cnf.graphicTerminal:
            #     fig, ax = plt.subplots()
            #     pos = nx.spring_layout(APP, seed=15612357)
            #     nx.draw(APP, pos, labels=mylabels, font_size=8)
            #     # Win
            #     fig.savefig(os.path.dirname(__file__) + '\\' + self.cnf.resultFolder + '\\plots\\app_%s.png' % i)
            #     # Unix
            #     # fig.savefig(os.path.dirname(__file__) + '/' + self.cnf.resultFolder + '/plots/app_%s.png' % i)
            #     plt.close(fig)  # close the figure
            #     plt.show()

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

            # self.appsDeadlines[i] = self.myDeadlines[i]

            # Copies of the application's graph that will be used to create the extra app definitions
            APP_EB = APP.copy()
            APP_DD = APP.copy()

            myApp['id'] = i
            myApp['name'] = str(i)
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

        # Win
        appFile = open(self.cnf.resultFolder + "\\appDefinition.json", "w")
        # Unix
        # appFile = open(self.cnf.resultFolder + "/appDefinition.json", "w")
        # appFileBE = open(self.cnf.resultFolder + "/appDefinitionBE.json", "w")
        appFile.write(json.dumps(appJson))
        appFile.close()

    def rec_placement(self, module_index, current_placement, limit):
        if limit != 0 and len(self.all_placements) == limit:
            return

        if len(current_placement) == len(self.all_modules):
            self.all_placements.append(current_placement.copy())
            return

        current_module = self.all_modules[module_index]

        for node in self.G.nodes:
            if self.freeNodeResources[node] >= current_module['RAM']:
                current_placement[current_module['name']] = node
                self.freeNodeResources[node] -= current_module['RAM']

                self.rec_placement(module_index + 1, current_placement, limit)

                self.freeNodeResources[node] += current_module['RAM']
                current_placement.pop(current_module['name'])

    def randomPlacement(self, path='', file_name='allocDefinition.json'):
        # nodes -> self.devices     apps -> self.apps
        rnd_placement = {}

        for app in self.apps:
            for module in app['module']:
                for i in range(50):
                    index = random.randint(0, (len(self.dataNetwork['entity']) - 1))
                    # Se o node 'index' tiver recursos suficientes para alocar o modulo:
                    if self.freeNodeResources[index] >= module['RAM']:
                        self.freeNodeResources[index] -= module['RAM']
                        if app['id'] not in rnd_placement:
                            rnd_placement[app['id']] = dict()
                        rnd_placement[app['id']][module['name']] = index
                        break

                    if i == 49:
                        print(f"Nao foi possivel alocar o modulo {module} após 50 iterações.")

        # print(rnd_placement)
        # print(self.freeNodeResources)

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
        self.updateJsonResources()

        with open(os.path.dirname(__file__) + '/' + path + file_name, "w") as netFile:
            netFile.write(json.dumps(alloc))

    def updateJsonResources(self, path='', file_name='netDefinition.json'):
        net_json = json.load(open(path+file_name))

        for node in net_json['entity']:
            node['FRAM'] = self.freeNodeResources[node['id']]

        with open(os.path.dirname(__file__) + '/' + path + file_name, "w") as netFile:
            netFile.write(json.dumps(net_json))

    def backtrack_placement(self, path='', file_name='allocDefinition.json', limit=0):

        # n_modules = len([app['module'] for app in self.apps])
        # self.n_modules = sum(len(app['module']) for app in self.apps)

        self.all_modules = []
        for app in self.apps:
            for module in app['module']:
                self.all_modules.append(module)

        # nodes -> self.devices     apps -> self.apps
        self.all_placements = []
        current_placement = {}

        # self.rec_placement(0, current_placement)
        self.rec_placement(0, current_placement, limit)
        if debug_mode:
            print(len(self.all_placements))
            print(self.all_placements)

        # first solution
        solution = self.all_placements[0]

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
        with open(os.path.dirname(__file__) + '\\' + path + "file_name", "w") as netFile:
            netFile.write(json.dumps(alloc))
        # Unix
        # with open(os.path.dirname(__file__) + '/' + path + "/allocDefinition.json", "w") as netFile:
        # with open(os.path.dirname(__file__) + '/' + path + file_name, "w") as netFile:
        #     netFile.write(json.dumps(alloc))

        # TODO atualizar network definition FRAM

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

    def config_generation(self, n=20, m=2, path_network='', file_name_network='netDefinition.json', path_apps='',
                          file_name_apps='appDefinition.json', path_alloc='', file_name_alloc='allocDefinition.json'):
        self.networkGeneration(n, m, path_network, file_name_network)
        self.simpleAppsGeneration(path_apps, file_name_apps)
        self.backtrack_placement(path_alloc, file_name_alloc)

    def bt_min_mods(self, path=''):
        available_res = self.freeNodeResources.copy()
        available_res.pop(max(available_res))

        used_res = list()
        services = list()
        best_solution = list()

        apps = json.load(open('appDefinition.json'))

        for app in apps:
            for mod in app['module']:
                services.append({'module_name': mod['name'], 'RAM': mod['RAM'], 'app': app['id']})

        best_solution = self.bt_min_mods_(available_res, used_res, services, best_solution)

        alloc = dict()

        for index, service in enumerate(services):
            service['id_resource'] = best_solution[index]
            self.freeNodeResources[service['id_resource']] -= service['RAM']        # Subtrai o recurso usado
            service.pop('RAM')

        alloc['initialAllocation'] = services

        # # Win
        with open(os.path.dirname(__file__) + '\\' + path + "allocDefinition.json", "w") as netFile:
            netFile.write(json.dumps(alloc))
        # Unix
        # with open(os.path.dirname(__file__) + '/' + path + "/allocDefinition.json", "w") as netFile:
        # with open(os.path.dirname(__file__) + '/' + path + file_name, "w") as netFile:
        #     netFile.write(json.dumps(alloc))

    def bt_min_mods_(self, available_res, cur_solution, services, best_solution, index=0):

        # Chegando ao fim da arvore de recursao, decide-se qual o melhor placement
        if index == len(services):
            # Caso a solucao atual use - que a melhor, ou seja a 1a a existir, é retornada a solucao atual
            if len(set(cur_solution)) < len(set(best_solution)) or len(best_solution) == 0:
                return cur_solution.copy()

            # Caso as 2 soluções empatem, desempata-se consoante o menor somatorio do espaço livre dos nodes usados
            elif len(set(cur_solution)) == len(set(best_solution)) \
                and sum([available_res[node_index] for node_index in set(cur_solution)]) < \
                    (sum([available_res[node_index] for node_index in set(best_solution)]) - sum(sv['RAM'] for sv in services)):

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


conf = myConfig.myConfig()  # Setting up configuration preferences
random.seed(15612357)

exp_config = ExperimentConfiguration(conf)
# exp_config.config_generation(n=10)

exp_config.networkGeneration(3)
# exp_config.simpleAppsGeneration()


# exp_config.backtrack_placement(limit=1)
# exp_config.randomPlacement()
exp_config.userGeneration()
# exp_config.appGeneration()
exp_config.bt_min_mods()
# print()
