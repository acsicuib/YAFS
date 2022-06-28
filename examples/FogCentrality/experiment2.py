"""

    Created on Thu Jan 30 15:03:21 2018

    @author: isaac

"""

from yafs.core import Sim
from yafs.application import Application,Message
from yafs.topology import  Topology
from yafs.distribution import deterministicDistribution
from yafs.utils import fractional_selectivity

from CentricityPlacement import NoPlacementOfModules
from CentricityPopulation import Statical
from CentricitySelection import First_ShortestPath
import networkx as nx
import numpy as np
import pandas as pd
import random

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
    links = []
    # file = open("p2p-Gnutella08.txt","r")
    # file = open("data/as19990104.csv","r")
    data = pd.read_csv("data/as19990104.csv", sep=";")

    nodes = {}
    for it, value in data.iterrows():
        nodes[value.src] = 0
        nodes[value.dst] = 0
        v = {"s": value.src, "d": value.dst, "BW": 10, "PR": 1}
        links.append(v)

    entities = []
    for nid in nodes.keys():
        value = {"id": nid, "model": "F", "IPT": 1, "RAM": 1, "COST": 1}
        entities.append(value)

    topology_json = {"entity": entities, "link": links}

    return topology_json


def computingWeights(t,all_nodes_dev,edge_dev,workload_type):
    minPath = {}
    for node in all_nodes_dev:
        for edge in edge_dev:
            if node == edge:
                paths = [[node]]
            else:
                paths = list(nx.shortest_path(t.G, source=node, target=edge))
            minPath[(node, edge)] = paths

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

def generate_communities(size,edge,minPath,minDis,threshold_population_edge,cloud_device):
    threshold = int(len(edge.keys()) * threshold_population_edge)
    community = range(0, size)
    com = {}
    for w in range(0, size):
        # Select one random edge device
        n = random.choice(edge.keys())
        if n == cloud_device:
            n = random.choice(edge.keys()) ## MAY BE, Cloud can be a Comm
        community[w] = []
        community[w].append(n)
        com[n] = {"community": w}
        valueMin = sorted(minDis[n])[threshold]
        counter = 0
        while True:
            someone = random.choice(edge.keys())
            if someone == n: continue
            if someone == cloud_device: continue
            if someone in community[w]: continue
            try:
                if len(minPath[(n, someone)]) <= valueMin:
                    community[w].append(someone)
                    com[someone] = {"community": w}
                    counter += 1
                    if counter > threshold: break
            except:
                if len(minPath[(someone, n)]) <= valueMin:
                    community[w].append(someone)
                    com[someone] = {"community": w}
                    counter += 1
                    if counter > threshold: break

    return community,com

def main():

    random.seed(RANDOM_SEED)
    np.random.seed(RANDOM_SEED)

    """
    Detalles
    """

    topologies = {

        "Grid": "data/grid200.graphml",
        "BarabasiAlbert": "data/BarabasiAlbert2.graphml",
        "RandomEuclidean": "data/RandomEuclidean.graphml",
        "Lobster": "data/Lobster.graphml",

    }
    community_size = [50,100,150,200,300]
    threshold_population_edge = 0.010

    ltopo = []
    lnodes = []
    ledges = []
    lavepath = []
    leddev = []

    try:
        for key_topo in topologies.keys():
            """
            TOPOLOGY from a json
            """
            t = Topology()
            # t_json = create_json_topology()
            # t.load(t_json)

            t.load_graphml(topologies[key_topo])
            print "TOPOLOGY: %s" %key_topo
            print "Total Nodes: %i" %len(t.G.nodes())
            print "Total Vertexs: %i" % len(t.G.edges())
            print "Average shortest path: %s" %nx.average_shortest_path_length(t.G)
            # t.write("network_ex2.gexf")

            ltopo.append(key_topo)
            lnodes.append(len(t.G.nodes()))
            ledges.append(len(t.G.edges()))
            lavepath.append(nx.average_shortest_path_length(t.G))

            ### COMPUTING Node degrees
            ### Stablish the Edge devices (acc. with Algoritm.nodedegree >... 1)
            ### Identify Cloud Device (max. degree)
            deg = {}
            edge = {}
            cloud_device = 0
            bestDeg = -1
            for n in t.G.nodes():
                d = t.G.degree(n)
                if d > bestDeg:
                    bestDeg = d
                    cloud_device = int(n)
                deg[n] = {"degree": d}
                #### MUST BE IMPROVED
                if key_topo in ["BarabasiAlbert","Lobster"]:
                    if d == 1:
                        edge[n] = -1

                elif key_topo in ["Grid"]:
                    if d <=3:
                        edge[n] = -1

                elif key_topo in ["RandomEuclidean"]:
                    if d > 14:
                        edge[n] = -1

            print "Total Edge-Devices: %i" %len(edge.keys())
            leddev.append(len(edge.keys()))





            """
            OJO
            """
            #TODO
            if key_topo in ["Grid"]:
                cloud_device = 320


            print "ID of Cloud-Device: %i" %cloud_device
            continue


            #print "Total edges devices: %i" % len(edge.keys())
            #nx.set_node_attributes(t.G, values=deg)

            ## COMPUTING MATRIX SHORTEST PATH among EDGE-devices
            minPath = {}
            minDis = {}
            for d in edge.keys():
                minDis[d] = []
                for d1 in edge.keys():
                    if d == d1: continue
                    path = list(nx.shortest_path(t.G, source=d, target=d1))
                    minPath[(d, d1)] = path
                    minDis[d].append(len(path))



            """
            WORKLOAD DEFINITION & REGION SENSORS (=Communities)
            """

            for size in community_size:

                print "SIZE Of Community: %i" %size


                communities,com = generate_communities(size, edge, minPath, minDis, threshold_population_edge,cloud_device)
                #print "Computed Communities"
                # print communities
                #for idx,c in enumerate(communities):
                #    print "\t %i - size: %i -: %s" %(idx,len(c),c)
                ### WRITING NETWORK
                nx.set_node_attributes(t.G, values=com)
                t.write("tmp/network-communities-%s-%i.gexf"%(key_topo,size))

                # exit()

                #TODO suposicion cada comunidad es un tipo de carga
                sensor_workload_types = communities

                lambdas_wl = np.random.randint(low=5, high=10, size=len(sensor_workload_types))
                id_lambdas = zip(range(0,len(lambdas_wl)),lambdas_wl)
                id_lambdas.sort(key=lambda tup: tup[1],reverse=True)  # sorts in place
                #print id_lambdas # [(1, 9), (0, 8)]

                """
                topology.Centricity
                """
                # Both next ids be extracted from topology.entities
                all_nodes_dev = t.G.nodes()
                edge_dev = edge.keys()

                weights = computingWeights(t,all_nodes_dev,edge_dev,sensor_workload_types)
                print "Computed weights"

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
                #functions = {"Cluster":"Cluster","Eigenvector":nx.eigenvector_centrality,"Current_flow_betweenness_centrality":nx.current_flow_betweenness_centrality,
                #            "Betweenness_centrality":nx.betweenness_centrality,"load_centrality":nx.load_centrality} #"katz_centrality":nx.katz_centrality,
                #functions = {"Current_flow_betweenness_centrality":nx.current_flow_betweenness_centrality}

                functions = {"Cluster": "Cluster",
                             "Eigenvector": nx.eigenvector_centrality,
                             "Current_flow_betweenness_centrality": nx.current_flow_betweenness_centrality,
                             "Betweenness_centrality": nx.betweenness_centrality,
                             #"Load_centrality": nx.load_centrality
                             }  # "katz_centrality":nx.katz_centrality,

                for f in functions:

                    print "Analysing network with algorithm: %s "%f
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
                            pops[idx].set_sink_control({"id": [cloud_device], "number": 1, "module": apps[idx].get_sink_modules()})
                            # print "\t", "SOURCE"
                            # In addition, a source includes a distribution function:

                            dDistribution = deterministicDistribution(name="Deterministic", time=idWL[1])
                            pops[idx].set_src_control(
                                {"id": sensor_workload_types[idx], "number": 1, "message": apps[idx].get_message("m-st"),
                                 "distribution": dDistribution})

                    else:
                        #Computing best device for each WL-type and each centrality function
                        print "\t Computando centralidad "
                        centralWL = range(0,len(weights))
                        for idx,v in enumerate(sensor_workload_types):
                            if idx%20 ==0:
                                print "\t\t%i%%",idx
                            nx.set_edge_attributes(t.G, values=weights[idx], name="weight")
                            centrality = functions[f](t.G, weight="weight")
                            # print(['%s %0.2f' % (node, centrality[node]) for node in centrality])
                            centralWL[idx]=centrality

                        print "\t Generando SINK/SRCs centralidad "
                        previous_deploy ={} ## DEV -> ID:load
                        for idWL in id_lambdas:
                            idx = idWL[0]
                            ## idWL[0] #index WL
                            ## idWL[1] #lambda

                            for dev, value in sorted(centralWL[idx].iteritems(), key=lambda (k, v): (v, k),reverse=True):
                                # print "%s: %s" % (dev, value)
                                #TODO CONTTOLAR LA CAPACIDAD DEL DISPOSITO HERE
                                if not dev in previous_deploy.values():
                                    previous_deploy[idx] = dev
                                    break
                            #TODO chequear que dEV es un device
                            # print "\t Previous deploy: ",previous_deploy
                            # print "\t NameApp: ",apps[idx].name
                            # print "\t Device:",dev
                            #Each application have a correspondence SRC/SINK among APPS


                            pops[idx].set_sink_control({"id":[dev],"number":1,"module":apps[idx].get_sink_modules()})
                            dDistribution = deterministicDistribution(name="Deterministic", time=idWL[1])
                            #In addition, a source includes a distribution function:
                            pops[idx].set_src_control({"id": sensor_workload_types[idx], "number":1,"message": apps[idx].get_message("m-st"), "distribution": dDistribution})

                    """
                    SIMULATION ENGINE
                    """
                    stop_time = 100 #CHECK
                    s = Sim(t)
                    for idx,app in enumerate(apps):
                        s.deploy_app(app, placement, pops[idx], selectorPath)

                    s.run(stop_time,test_initial_deploy=False,show_progress_monitor=False)

                #end for algorithms
            #end for communities size
        #end for topology change

        print ltopo
        print lnodes
        print ledges
        print lavepath
        print leddev

    #end try

    except:
        print "Some error??"

if __name__ == '__main__':
    import logging.config
    logging.config.fileConfig('logging.ini')
    main()


