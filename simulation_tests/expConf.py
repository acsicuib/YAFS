import json
import networkx as nx


import operator
import os
import copy

LINK_BW = "BW"
LINK_PR = "PR"
NODE_IPT = "IPT"


class ExperimentConfiguration:

    def __init__(self):
        self.CLOUDCAPACITY = 9999999999999999
        self.CLOUDSPEED = 10000
        self.CLOUDBW = 125000                  ## 1000 Mbits/s ou 125000 BYTES / MS ???
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

        self.func_APPDEADLINE="random.randint(2600,6600)" #MS

        self.func_NETWORKGENERATION = "nx.barabasi_albert_graph(n, m)"

        self.scenario = ''


    def networkGeneration(self, n=20, m=2, path=''):
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
        # Adding Cloud's resource to nodeResources
        self.nodeResources[self.cloudId] = self.CLOUDCAPACITY

        for cloudGtw in self.cloudgatewaysDevices:
            myLink = {}
            myLink['s'] = cloudGtw
            myLink['d'] = self.cloudId
            myLink['PR'] = self.CLOUDPR
            myLink['BW'] = self.CLOUDBW

            myEdges.append(myLink)

        netJson['entity'] = self.devices
        netJson['link'] = myEdges

        # # Win
        # with open(os.path.dirname(__file__) + '\\' + path + "\\netDefinition.json", "w") as netFile:
        #     netFile.write(json.dumps(netJson))
        # Unix
        with open(os.path.dirname(__file__) + '/' + path + "/netDefinition.json", "w") as netFile:
            netFile.write(json.dumps(netJson))


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
        wpath = ""
        data_net = json.load(open(wpath + "conf\\netDefinition.json"))
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


exp_config = ExperimentConfiguration()
exp_config.networkGeneration(10)
print()
