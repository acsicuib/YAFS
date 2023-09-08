import networkx as nx
import random
import json
from yafs import Topology
from yafs.application import create_applications_from_json


def simpleApps(topo, path='', file_name='appDefinition.json'):
    func_SERVICEINSTR = "random.randint(20000,60000)"
    func_SERVICEMESSAGESIZE = "random.randint(1500000,4500000)"  # BYTES --> Considering the BW

    apps = list()

    for n in topo.G.nodes:
        if 'type' not in topo.nodeAttributes[n] or (topo.nodeAttributes[n]['type'].upper() != 'CLOUD'):
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
            module['RAM'] = topo.nodeAttributes[n]['RAM']

            app['module'].append(module)

            app['message'] = list()

            msg = dict()
            msg['id'] = 0
            msg['name'] = 'M.USER.APP.' + str(n)
            msg['s'] = 'None'
            msg['d'] = module['name']
            msg['bytes'] = eval(func_SERVICEMESSAGESIZE)
            msg['instructions'] = eval(func_SERVICEINSTR)

            app['message'].append(msg)

            apps.append(app)

    with open((path + file_name), 'w') as f:
        json.dump(apps, f)
    return apps


t = Topology()
dataNetwork = json.load(open('data/network.json'))
t.load(dataNetwork)

x = simpleApps(t, path='data\\')

sum = 0
for app in x:
    sum += len(app['module'])

print()


def is_runnable(node_attr, apps=None, default_path='data/appDefinition.json'):
    if apps is None:
        dataApp = json.load(open(default_path))
        apps = create_applications_from_json(dataApp)
        print()

is_runnable(t)




"""
import operator
import os
import copy


def buildComunities(ltopo):
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

    # Adding the GINDEX to the graph. This attribute it will be used to rank the nodes
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

        # This structure will be used to determine the nodes without any community
        nocommunity_nodes.append(out_dict.copy())

        # Creating the community of each node base on the ranks obtained
        for k, v in temp_dict.items():
            if k == i:
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
        # rr works as the pointer of the Round Robin algorithm for load balancing, and it is initialized with the index of the GW
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

    return nocomu_ranking_list, rranking_list, (mean_size / len(node_rank_google))

def create_req_from_app(self):
    lrequestPerApp = {}
    lrequestPerApp.update({(i, j): self.appReq[i][j] for i in range(self.numApplications)
                           for j in range(self.numRequests)})
    return lrequestPerApp


def heuristicPlacement(topo):
    func_SERVICERESOURCES = "random.randint(1,5)"
    TOTALNUMBEROFAPPS = 10

    apps = simpleApps(topo, path='', file_name='appDefinition.json')

    servicesResources = dict()
    for j in enumerate(apps):
        servicesResources[j] = eval(func_SERVICERESOURCES)

    mapService2App = list()
    mapServiceId2ServiceName = list()

    for i in range(0, TOTALNUMBEROFAPPS):
        mapService2App.append(str(i))
        mapServiceId2ServiceName.append(str(i) + '_0')

    # Getting data structures ready
    wpath = ""
    data_net = json.load(open(wpath + "conf\\netDefinition.json"))
    nocomu_ranking_list, ranking_list, wsize = buildComunities(ltopo=topo)
    numApplications = len(apps)
    numRequests = len(gatewaysDevices)
    requestPerApp = create_req_from_app()
    initial_nodeResources = sorted(nodeResources.items(), key=operator.itemgetter(0))

    # Total of request per application
    totalRequestApp = []
    for i in range(numApplications):
        sumTotal = 0
        for j in range(numRequests):
            sumTotal += requestPerApp[i, j]
        totalRequestApp.append(sumTotal)
    dic_totalRequestApp = {i: totalRequestApp[i] for i in range(0, len(totalRequestApp))}

    rank_app = sorted(dic_totalRequestApp.items(), key=operator.itemgetter(1), reverse=True)

    # Starting the placement of modules
    servicesInFog = 0
    servicesInCloud = 0
    allAlloc = {}
    myAllocationList = list()
    # random.seed(datetime.now())

    for app_num, app in zip(range(0, len(appsRequests)), appsRequests):
        # instance will carry the id of the GW where the request was generated
        for instance in list(appsRequests[rank_app[app_num][0]]):
            # Getting the index of the rr entry
            rr_index = [index for index, item in zip(range(0, len(ranking_list[instance])),
                                                     ranking_list[instance]) if 'rr' in item]
            for module in list(apps[rank_app[app_num][0]].nodes):
                # Checking if the module could be deployed in this community. Thus it is guarantee the deploy here
                max_community_resources = -1
                win = 0
                community_flag = False
                count = 1
                while ((max_community_resources < servicesResources[module]) and not (
                        win == len(ranking_list[instance]) - 1)):
                    if len(ranking_list[instance]) > (wsize * count):
                        win = wsize * count
                    else:
                        win = len(ranking_list[instance]) - 1
                    community_resources = [nodeFreeResources[element[0]]
                                           for element, iwin in zip(ranking_list[instance], range(0, win))
                                           if element[0] != 'rr' and iwin <= win]
                    max_community_resources = max(community_resources)

                    if max_community_resources >= servicesResources[module]:
                        community_flag = True
                    count += 1

                if community_flag:
                    # Getting the id where the rr points
                    index = ranking_list[instance][ranking_list[instance][rr_index[0]][1]][0]
                    res_required = servicesResources[module]
                    if res_required <= nodeFreeResources[index]:
                        nodeFreeResources[index] = nodeFreeResources[index] - res_required
                        # Deployment
                        myAllocation = {}
                        myAllocation['app'] = mapService2App[module]
                        myAllocation['module_name'] = mapServiceId2ServiceName[module]
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
                        while res_required > nodeFreeResources[index]:
                            # Updating the rr pointer. In the worst scenario it would be necessary to do a full rotation
                            next_rr = (ranking_list[instance][rr_index[0]][1] + 1) % win
                            if next_rr != rr_index[0]:
                                ranking_list[instance][rr_index[0]][1] = next_rr
                            else:
                                # This never will be executed
                                ranking_list[instance][rr_index[0]][1] = next_rr + 1
                            index = ranking_list[instance][ranking_list[instance][rr_index[0]][1]][0]
                        nodeFreeResources[index] = nodeFreeResources[index] - res_required
                        # Deployment
                        myAllocation = {}
                        myAllocation['app'] = mapService2App[module]
                        myAllocation['module_name'] = mapServiceId2ServiceName[module]
                        myAllocation['id_resource'] = index
                        myAllocationList.append(myAllocation)
                else:
                    # Selecting and alternative deployment community that should be the nodes outside of the previous step
                    no_community_resources = [nodeFreeResources[element[0]]
                                              for element in nocomu_ranking_list[instance]]
                    max_no_community_resources = max(no_community_resources)

                    if max_no_community_resources >= servicesResources[module]:
                        # Getting the id  of the nodes where the module should be deployed
                        for k, v in nocomu_ranking_list[instance]:
                            if nodeFreeResources[nocomu_ranking_list[instance][k][0]] >= servicesResources[module]:
                                break
                        nodeFreeResources[index] = nodeFreeResources[index] - res_required
                        # Deployment
                        myAllocation = {}
                        myAllocation['app'] = mapService2App[module]
                        myAllocation['module_name'] = mapServiceId2ServiceName[module]
                        myAllocation['id_resource'] = index
                        myAllocationList.append(myAllocation)
                    else:
                        # The module will be placed in the Cloud
                        index = cloudId
                        nodeFreeResources[index] = nodeFreeResources[index] - res_required
                        # Deployment in the cloud
                        myAllocation = {}
                        myAllocation['app'] = mapService2App[module]
                        myAllocation['module_name'] = mapServiceId2ServiceName[module]
                        myAllocation['id_resource'] = index
                        myAllocationList.append(myAllocation)
                # Updating the rr pointer
                next_rr = (ranking_list[instance][rr_index[0]][1] + 1) % win
                if next_rr != rr_index[0]:
                    ranking_list[instance][rr_index[0]][1] = next_rr
                else:
                    ranking_list[instance][rr_index[0]][1] = next_rr + 1
                # Updating placement metrics
                if index != cloudId:
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
    allocationFile = open("allocDefinitionHeuristic.json", "w")
    # Unix
    # allocationFile = open(cnf.resultFolder + "/allocDefinitionRandom.json", "w")
    allocationFile.write(json.dumps(allAlloc))
    allocationFile.close()

    # Keeping nodes'resources
    final_nodeResources = sorted(nodeResources.items(), key=operator.itemgetter(0))

    if os.stat('conf\\node_resources.csv').st_size == 0:
        # The file in empty

        ids = ['node_id']
        values = ['ini_resources']
        token = 'scenario' + '_heuristic'
        fvalues = [token]
        for ftuple in initial_nodeResources:
            ids.append(ftuple[0])
            values.append(ftuple[1])
        for stuple in final_nodeResources:
            fvalues.append(stuple[1])
        file = open('conf\\node_resources.csv', 'a+')
        file.write(",".join(str(item) for item in ids))
        file.write("\n")
        file.write(",".join(str(item) for item in values))
        file.write("\n")
        file.write(",".join(str(item) for item in fvalues))
        file.write("\n")
        file.close()
    else:
        token = 'scenario' + '_heuristic'
        fvalues = [token]
        for stuple in final_nodeResources:
            fvalues.append(stuple[1])
        file = open('conf\\node_resources.csv', 'a+')
        file.write(",".join(str(item) for item in fvalues))
        file.write("\n")
        file.close()

    print("Heuristic initial allocation performed!")


def simpleUsers(topo, path='', file_name='appDefinition.json'):
    func_REQUESTPROB = "random.random()/4"  # App's popularity. This value defines the probability of a source request an application
    func_USERREQRAT = "random.randint(200,1000)"  # MS






"""