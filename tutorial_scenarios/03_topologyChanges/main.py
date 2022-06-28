"""
    In this simulation, the number of nodes changes randomly each time.


    @author: Isaac Lera
"""
import os
import time
import json
import random
import logging.config

import pandas as pd
import numpy as np
import networkx as nx
from pathlib import Path

from yafs.core import Sim
from yafs.application import create_applications_from_json
from yafs.topology import Topology

from yafs.placement import JSONPlacement
from yafs.path_routing import DeviceSpeedAwareRouting
from yafs.distribution import deterministic_distribution,deterministicDistributionStartPoint
from collections import defaultdict




class CustomStrategy():

    def __init__(self,pathResults):
        self.activations = 0
        self.pathResults = pathResults

    def deploy_module(self,sim,service,node):
        app_name = int(service[0:service.index("_")])
        app = sim.apps[app_name]
        services = app.services
        idDES = sim.deploy_module(app_name, service, services[service], [node])
        # with this `identifier of the DES process` (idDES) you can control it

    def undeploy_module(self,sim,service,node):
        app_name = int(service[0:service.index("_")])
        des = sim.get_DES_from_Service_In_Node(node, app_name, service)
        sim.undeploy_module(app_name, service,des)

    def is_already_deployed(self,sim,service_name,node):
        app_name = service_name[0:service_name.index("_")]

        all_des = []
        for k, v in sim.alloc_DES.items():
            if v == node:
                all_des.append(k)

        # Clearing other related structures
        for des in sim.alloc_module[int(app_name)][service_name]:
            if des in all_des:
                return True


    def get_current_services(self,sim):
        """ returns a dictionary with name_service and a list of node where they are deployed
        example: defaultdict(<type 'list'>, {u'2_19': [15], u'3_22': [5]})
        """
        # it returns all entities related to a node: modules, sources/users, etc.
        current_services = sim.get_alloc_entities()
        # here, we only need modules (not users)
        current_services = dict((k, v) for k, v in current_services.items() if len(v)>0)
        deployed_services = defaultdict(list)
        for node,services in current_services.items():
            for service_name in services:
                if not "None" in service_name:
                     deployed_services[service_name[service_name.index("#")+1:]].append(node)


        return deployed_services


    def __call__(self, sim, routing):

        # logging.info("Activating Custom process - number %i "%self.activations)
        self.activations += 1
        routing.invalid_cache_value = True # when the topology changes the cache of the Path.routing is outdated.

        if random.random()<0.7:
        # We create a new node, between two other nodes.
            node1 = random.sample(sim.topology.G.nodes(),1)[0]
            node2 = random.sample(sim.topology.G.nodes(), 1)[0]
            newId = list(sim.topology.G.nodes())[-1]
            try:
                newId = newId+1
            except:
                print("Be careful with the type of IDs in your Jsons (str or int)!!!!!")
                exit()

            # We create the new node and we define mandatory attr.
            att = {"IPT":100}
            sim.topology.G.add_node(int(newId),**att)

            att = {"BW": 10, "PR": 10}
            sim.topology.G.add_edge(int(node1), int(newId), **att)
            sim.topology.G.add_edge(int(newId), int(node2), **att)

            logging.info(" A new node is created between %i and %i with ID: %i"%(node1,node2,newId))
        else:
        # We drop a node.
            code = random.sample(sim.topology.G.nodes(), 1)[0]
            try:
                ## ONE WAY
                # edges_to_remove = [e for e in sim.topology.G.edges() if int(code) in e]
                # for edge in edges_to_remove:
                #     att = sim.topology.G[edge[0]][edge[1]]
                #     sim.topology.G.remove_edge(*edge)

                ## OTHER WAY
                # sim.topology.G.remove_node(code)

                ## Elegant way - we remove all process linked on it
                if code!=0:
                    sim.remove_node(code)

            except nx.NetworkXError:
                None



def main(stop_time, it, folder_results):


    """
    TOPOLOGY
    """
    t = Topology()

    # You also can create a topology using JSONs files. Check out examples folder
    size = 5
    t.G = nx.generators.binomial_tree(size) # In NX-lib there are a lot of Graphs generators

    # Definition of mandatory attributes of a Topology
    ## Attr. on edges
    # PR and BW are 1 unit
    attPR_BW = {x: 1 for x in t.G.edges()}
    nx.set_edge_attributes(t.G, name="PR", values=attPR_BW)
    nx.set_edge_attributes(t.G, name="BW", values=attPR_BW)
    ## Attr. on nodes
    # IPT
    attIPT = {x: 100 for x in t.G.nodes()}
    nx.set_node_attributes(t.G, name="IPT", values=attIPT)

    nx.write_gexf(t.G,folder_results+"graph_binomial_tree_%i.gexf"%size) # you can export the Graph in multiples format to view in tools like Gephi, and so on.

    print(t.G.nodes()) # nodes id can be str or int


    """
    APPLICATION or SERVICES
    """
    dataApp = json.load(open('data/appDefinition.json'))
    apps = create_applications_from_json(dataApp)

    """
    SERVICE PLACEMENT 
    """
    placementJson = json.load(open('data/allocDefinition.json'))
    placement = JSONPlacement(name="Placement", json=placementJson)

    """
    Defining ROUTING algorithm to define how path messages in the topology among modules
    """
    selectorPath = DeviceSpeedAwareRouting()

    """
    SIMULATION ENGINE
    """
    s = Sim(t, default_results_path=folder_results+"sim_trace")

    """
    Deploy services == APP's modules
    """
    for aName in apps.keys():
        s.deploy_app(apps[aName], placement, selectorPath)

    """
    Deploy users
    """
    userJSON = json.load(open('data/usersDefinition.json'))
    for user in userJSON["sources"]:
        app_name = user["app"]
        app = s.apps[app_name]
        msg = app.get_message(user["message"])
        node = user["id_resource"]
        dist = deterministic_distribution(100, name="Deterministic")
        idDES = s.deploy_source(app_name, id_node=node, msg=msg, distribution=dist)


    """
    This internal monitor in the simulator (a DES process) changes the sim's behaviour. 
    You can have multiples monitors doing different or same tasks.
    
    In this case: it changes the topology.
    """
    dist = deterministicDistributionStartPoint(stop_time/4., stop_time/2.0/10.0, name="Deterministic")
    evol = CustomStrategy(folder_results)
    s.deploy_monitor("CrazyTopology",
                     evol,
                     dist,
                     **{"sim": s, "routing": selectorPath}) # __call__ args 



    """
    RUNNING - last step
    """
    logging.info(" Performing simulation: %i " % it)
    s.run(stop_time)  # To test deployments put test_initial_deploy a TRUE
    s.print_debug_assignaments()

    """
    We store the new topology
    """
    nx.write_gexf(s.topology.G,folder_results+"theNew_topology.gexf") 
    

if __name__ == '__main__':

    LOGGING_CONFIG = Path(__file__).parent / 'logging.ini'
    logging.config.fileConfig(LOGGING_CONFIG)

    folder_results = Path("results/")
    folder_results.mkdir(parents=True, exist_ok=True)
    folder_results = str(folder_results)+"/"


    nIterations = 1  # iteration for each experiment
    simulationDuration = 20000

    # Iteration for each experiment changing the seed of randoms
    for iteration in range(nIterations):
        random.seed(iteration)
        logging.info("Running experiment it: - %i" % iteration)

        start_time = time.time()
        main(stop_time=simulationDuration,
             it=iteration,folder_results=folder_results)

        print("\n--- %s seconds ---" % (time.time() - start_time))

    print("Simulation Done!")

    
    # Analysing the results. 
    dfl = pd.read_csv(folder_results+"sim_trace"+"_link.csv")
    print("Number of total messages between nodes: %i"%len(dfl))

