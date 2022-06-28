"""

    Created on Thu Jan 30 15:03:21 2018

    @author: isaac

"""
import random
from audioop import reverse

from yafs.core import Sim
from yafs.application import Application,Message
from yafs.topology import  Topology
from yafs.selection import First_ShortestPath

from yafs.distribution import deterministicDistribution

from CentricityPlacement import NoPlacementOfModules
from CentricityPopulation import Statical
import networkx as nx
import numpy as np
RANDOM_SEED = 1

def create_application(workload_type):
    # APLICATION
    a = Application(name="WL-%s"%workload_type)

    a.set_modules([{"Source" : {"Type":Application.TYPE_SOURCE}},{"Storage": {"Type": Application.TYPE_SINK}}])
    """
    Messages among MODULES (AppEdge in iFogSim)
    """
    m_data = Message("m-st", "Source", "Storage", instructions=2000*10**6, bytes=500)
    """
    Defining which messages will be dynamically generated # the generation is controlled by Population algorithm
    """
    a.add_source_messages(m_data)
    return a



def create_json_topology():
    """
       TOPOLOGY DEFINITION

       Some attributes of fog entities (nodes) are approximate
       """
    #Three types of network resources: cluster, F-fog device, and E-edge device
    topology_json = {"entity": [
        {"id": 0,  "model": "Cluster", "IPT": 1000, "RAM": 40000, "COST": 1, "WATT": 20.0},
        {"id": 1,   "model": "F", "IPT": 1000, "RAM": 40000, "COST": 1, "WATT": 20.0},
        {"id": 2,   "model": "F", "IPT": 1000, "RAM": 4000, "COST": 1, "WATT": 20.0},
        {"id": 3,   "model": "F", "IPT": 1000, "RAM": 4000, "COST": 1, "WATT": 20.0},
        {"id": 4,   "model": "F", "IPT": 1000, "RAM": 4000, "COST": 1, "WATT": 20.0},
        {"id": 5,   "model": "F", "IPT": 1000, "RAM": 4000, "COST": 1, "WATT": 20.0},
        {"id": 6,   "model": "F", "IPT": 1000, "RAM": 4000, "COST": 1, "WATT": 20.0},
        {"id": 7,   "model": "F", "IPT": 1000, "RAM": 4000, "COST": 1, "WATT": 20.0},
        {"id": 8,   "model": "F", "IPT": 1000, "RAM": 4000, "COST": 1, "WATT": 20.0},
        {"id": 9,   "model": "F", "IPT": 1000, "RAM": 4000, "COST": 1, "WATT": 20.0},
        {"id": 10,   "model": "F", "IPT": 1000, "RAM": 4000, "COST": 1, "WATT": 20.0},
        {"id": 11,   "model": "F", "IPT": 1000, "RAM": 4000, "COST": 1, "WATT": 20.0},
        {"id": 12,   "model": "F", "IPT": 1000, "RAM": 4000, "COST": 1, "WATT": 20.0},
        {"id": 13,   "model": "E", "IPT": 1000, "RAM": 4000, "COST": 1, "WATT": 20.0},
        {"id": 14,   "model": "E", "IPT": 1000, "RAM": 4000, "COST": 1, "WATT": 20.0},
        {"id": 15,   "model": "E", "IPT": 1000, "RAM": 4000, "COST": 1, "WATT": 20.0},
        {"id": 16,   "model": "E", "IPT": 1000, "RAM": 4000, "COST": 1, "WATT": 20.0},
        {"id": 17,   "model": "E", "IPT": 1000, "RAM": 4000, "COST": 1, "WATT": 20.0},
        {"id": 18,   "model": "E", "IPT": 1000, "RAM": 4000, "COST": 1, "WATT": 20.0},
        {"id": 19,   "model": "E", "IPT": 1000, "RAM": 4000, "COST": 1, "WATT": 20.0},
        {"id": 20,   "model": "E", "IPT": 1000, "RAM": 4000, "COST": 1, "WATT": 20.0},
        {"id": 21,   "model": "E", "IPT": 1000, "RAM": 4000, "COST": 1, "WATT": 20.0}
    ],
        "link": [
            {"s": 0, "d": 1, "BW": 1, "PR": 1},
            {"s": 1, "d": 4, "BW": 1, "PR": 1},
            {"s": 1, "d": 2, "BW": 1, "PR": 1},
            {"s": 2, "d": 3, "BW": 1, "PR": 1},
            {"s": 2, "d": 4, "BW": 1, "PR": 1},
            {"s": 2, "d": 5, "BW": 1, "PR": 1},
            {"s": 3, "d": 5, "BW": 1, "PR": 1},
            {"s": 4, "d": 6, "BW": 1, "PR": 1},
            {"s": 4, "d": 7, "BW": 1, "PR": 1},
            {"s": 6, "d": 9, "BW": 1, "PR": 1},
            {"s": 7, "d": 9, "BW": 1, "PR": 1},
            {"s": 5, "d": 11, "BW": 1, "PR": 1},
            {"s": 3, "d": 10, "BW": 1, "PR": 1},
            {"s": 5, "d": 10, "BW": 1, "PR": 1},
            {"s": 10, "d": 13, "BW": 1, "PR": 1},
            {"s": 10, "d": 14, "BW": 1, "PR": 1},
            {"s": 6, "d": 11, "BW": 1, "PR": 1},
            {"s": 6, "d": 16, "BW": 1, "PR": 1},
            {"s": 11, "d": 15, "BW": 1, "PR": 1},
            {"s": 11, "d": 12, "BW": 1, "PR": 1},
            {"s": 6, "d": 12, "BW": 1, "PR": 1},
            {"s": 12, "d": 17, "BW": 1, "PR": 1},
            {"s": 9, "d": 18, "BW": 1, "PR": 1},
            {"s": 9, "d": 19, "BW": 1, "PR": 1},
            {"s": 7, "d": 20, "BW": 1, "PR": 1},
            {"s": 7, "d": 8, "BW": 1, "PR": 1},
            {"s": 8, "d": 21, "BW": 1, "PR": 1},
        ]}
    return topology_json


def computingWeights(t,all_nodes_dev,edge_dev,workload_type):
    minPath = {}
    for node in all_nodes_dev:
        for edge in edge_dev:
            if node == edge:
                paths = [[node]]
            else:
                paths = list(nx.all_simple_paths(t.G, source=node, target=edge))
            minsize = 9999999
            for path in paths:
                if len(path) < minsize:
                    minsize = len(path)
                    minPath[(node, edge)] = path

    edges = t.G.edges
    minStep = {} #Vertice x Device
    for vertex in edges:
        for dev in edge_dev:
            minvalue = min(len(minPath[(vertex[0],dev)]),len(minPath[(vertex[1],dev)]))
            minStep[(vertex,dev)]=minvalue

    weight_load = range(0,len(workload_type))
    version_printed_weights2 =range(0,len(workload_type))
    for idx,load in enumerate(workload_type):
        weight_load[idx] = {}
        version_printed_weights2[idx] = {}
        for key in minStep:
            if key[1] in workload_type[idx]:
                if key[0] in weight_load[idx]:
                    weight_load[idx][key[0]] += 1.0/minStep[key]
                    version_printed_weights2[idx][key[0]] += minStep[key]
                else:
                    weight_load[idx][key[0]] = 1.0/minStep[key]
                    version_printed_weights2[idx][key[0]] = minStep[key]
    return weight_load


def main():

    random.seed(RANDOM_SEED)
    np.random.seed(RANDOM_SEED)

    """
    TOPOLOGY from a json
    """
    t = Topology()
    t_json = create_json_topology()
    t.load(t_json)
    # t.write("network_ex1.gexf")

    """
    WORKLOAD DEFINITION
    """
    sensor_workload_types = [[16, 18],[13,14,15,16]]
    lambdas_wl = np.random.randint(low=5, high=10, size=len(sensor_workload_types))
    id_lambdas = zip(range(0,len(lambdas_wl)),lambdas_wl)
    id_lambdas.sort(key=lambda tup: tup[1],reverse=True)  # sorts in place
    print(id_lambdas) # [(1, 9), (0, 8)]

    """
    topology.Centricity
    """
    # Both next ids be extracted from topology.entities
    all_nodes_dev = range(0, 22) #DEVICES.model: F
    edge_dev = range(13, 22) #Devices.model: E

    weights = computingWeights(t,all_nodes_dev,edge_dev,sensor_workload_types)


    """
    APPLICATION
    """
    apps = []
    pops = []
    for idx in range(0,len(sensor_workload_types)):
        apps.append(create_application(idx))
        pops.append(Statical("Statical-%i"%idx))

    """
    PLACEMENT algorithm
    """
    #There is not modules thus placement.functions are empty
    placement = NoPlacementOfModules("empty")

    """--
    SELECTOR algorithm
    """
    # This implementation is already created in selector.class,called: First_ShortestPath
    selectorPath = First_ShortestPath()


    #In this point, the study analizes the behaviour of the deployment of (sink, src) modules (population) in different set of centroide algorithms
    functions = {"Cluster":"Cluster","Eigenvector":nx.eigenvector_centrality,"Current_flow_betweenness_centrality":nx.current_flow_betweenness_centrality,
                 "Betweenness_centrality":nx.betweenness_centrality,"katz_centrality":nx.katz_centrality,"load_centrality":nx.load_centrality}
    # functions = { "Eigenvector": nx.eigenvector_centrality}
    for f in functions:
        """
        POPULATION algorithm
        """
        pops = []
        for idx in range(0, len(sensor_workload_types)):
            pops.append(Statical("Statical-%i" % idx))
        # print "-"*20
        # print "Function: %s" %f
        # print "-"*20


        if "Cluster" in f:
            for idWL in id_lambdas:
                idx = idWL[0]
                # print idx
                ## idWL[0] #index WL
                ## idWL[1] #lambda

                ### ALL SINKS  goes to Cluster ID: NODE 0
                # print "\t", "SINK"
                pops[idx].set_sink_control({"id": [0], "number": 1, "module": apps[idx].get_sink_modules()})
                # print "\t", "SOURCE"
                # In addition, a source includes a distribution function:
                dDistribution = deterministicDistribution(name="Deterministic", time=idWL[1])
                pops[idx].set_src_control(
                    {"id": sensor_workload_types[idx], "number": 1, "message": apps[idx].get_message("m-st"),
                     "distribution": dDistribution })

        else:
            #Computing best device for each WL-type and each centrality function
            centralWL = range(0,len(weights))
            for idx,v in enumerate(sensor_workload_types):
                nx.set_edge_attributes(t.G, values=weights[idx], name="weight")
                centrality = functions[f](t.G, weight="weight")
                # print(['%s %0.2f' % (node, centrality[node]) for node in centrality])
                centralWL[idx]=centrality

            print(centralWL)

            previous_deploy ={} ## DEV -> ID:load
            for idWL in id_lambdas:
                idx = idWL[0]
                # print idx
                ## idWL[0] #index WL
                ## idWL[1] #lambda

                for dev, value in sorted(centralWL[idx].iteritems(), key=lambda (k, v): (v, k),reverse=True):
                    # print "%s: %s" % (dev, value)
                    if not dev in previous_deploy.values():
                        previous_deploy[idx] = dev
                        break



                #TODO chequear que dEV es un device
                # print "\t Previous deploy: ",previous_deploy
                # print "\t NameApp: ",apps[idx].name
                # print "\t Device:",dev
                #Each application have a correspondence SRC/SINK among APPS

                #For each type of sink modules we set a deployment on some type of devices
                #A control sink consists on:
                #  args:
                #  (  id  (int): identifies the device on the topology OR
                #     model (str): identifies the device or devices where the sink is linked )
                #     number (int): quantity of sinks linked in each device
                #     module (str): identifies the module from the app who receives the messages
                # print "\t","SINK"
                pops[idx].set_sink_control({"id":[dev],"number":1,"module":apps[idx].get_sink_modules()})
                # print "\t","SOURCE"
                #In addition, a source includes a distribution function:
                dDistribution = deterministicDistribution(name="Deterministic", time=idWL[1])
                pops[idx].set_src_control({"id": sensor_workload_types[idx], "number":1,"message": apps[idx].get_message("m-st"), "distribution": dDistribution})

        """
        SIMULATION ENGINE
        """
        stop_time = 100 #CHECK
        s = Sim(t)
        for idx,app in enumerate(apps):
            s.deploy_app(app, placement, pops[idx], selectorPath)

        s.run(stop_time,test_initial_deploy=False,show_progress_monitor=False) #In the internal code of iFogSim, that simulator runs by default until 10.000 units of time: In their case,it is until 10s

if __name__ == '__main__':
    import logging.config
    logging.config.fileConfig('logging.ini')
    main()

#EL MENSAJE HA DE VOLVER A SU ORIGEN: NODO topology???? porque sino que client recibe la respuesta???
