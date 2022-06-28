"""
    In this simulation, the users moves in different nodes. There are linked to another nodes.

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

    def __init__(self,pathResults,listIdApps):
        self.activations = 0
        self.pathResults = pathResults
        self.listUsers = []
        self.numberMaxUsers = 100
        self.listIdApps = listIdApps
        self.placeAt = {}
    def createUser(self,sim):
        app_name = random.sample(self.listIdApps, 1)[0]
        app = sim.apps[app_name]
        msg = app.get_message("M.USER.APP.%i" % app_name)
        dist = deterministic_distribution(30, name="Deterministic")
        node = random.sample(sim.topology.G.nodes(), 1)[0]
        idDES = sim.deploy_source(app_name, id_node=node, msg=msg, distribution=dist)
        self.listUsers.append(idDES)
        self.placeAt[idDES] = node
        return idDES

    def __call__(self, sim, routing):
        # logging.info("Activating Custom process - number %i " % self.activations)
        self.activations += 1
        # In this case, the new users not change the topology
        # routing.invalid_cache_value = True # when the service change the cache of the Path.routing is outdated.


        # We can introduce a new user or we move it
        if len(self.listUsers)==0:
            self.createUser(sim)

        if random.random()<0.6:
            # we create a new user
            idDES = self.createUser(sim)
            logging.info(" Creating a new user %i on node %i"%(idDES,self.placeAt[idDES]))

        elif random.random()<0.8:
            # we move a user from one node to other
            userDES = random.sample(self.listUsers, 1)[0]
            newNode = random.sample(sim.topology.G.nodes(), 1)[0]
            logging.info(" Moving a user %i from node %i to %i" % (userDES, self.placeAt[userDES],newNode))
            sim.alloc_DES[self.placeAt[userDES]] = newNode
        else:
            # we remove an user
            userDES = random.sample(self.listUsers,1)[0]
            sim.undeploy_source(userDES)
            self.listUsers.remove(userDES)
            logging.info(" Removing a user %i on node %i" % (userDES, self.placeAt[userDES]))



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
    ### IN THIS CASE, We control the users from our custom strategy

    # userJSON = json.load(open('data/usersDefinition.json'))
    # for user in userJSON["sources"]:
    #     app_name = user["app"]
    #     app = s.apps[app_name]
    #     msg = app.get_message(user["message"])
    #     node = user["id_resource"]
    #     dist = deterministic_distribution(100, name="Deterministic")
    #     idDES = s.deploy_source(app_name, id_node=node, msg=msg, distribution=dist)


    """
    This internal monitor in the simulator (a DES process) changes the sim's behaviour. 
    You can have multiples monitors doing different or same tasks.
    
    In this case, it changes the number or movement of users.
    """
    listIdApps = [x["id"] for x in dataApp]
    dist = deterministicDistributionStartPoint(stop_time/4., stop_time/2.0/10.0, name="Deterministic")
    evol = CustomStrategy(folder_results,listIdApps)
    s.deploy_monitor("RandomAllocation",
                     evol,
                     dist,
                     **{"sim": s, "routing": selectorPath}) # __call__ args



    """
    RUNNING - last step
    """
    logging.info(" Performing simulation: %i " % it)
    s.run(stop_time)  # To test deployments put test_initial_deploy a TRUE
    s.print_debug_assignaments()

    print("Number of new users: %i"%len(evol.listUsers))


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

    df = pd.read_csv(folder_results+"sim_trace.csv")
    print("Number of requests handled by deployed services: %i"%len(df))

    print(df.head())
    print("Requested Apps %s"%np.unique(df.app)) #only few apps are required from the new users

    dfapp6 = df[df.app == 6].copy()
    
    position_of_users_app6 = np.unique(dfapp6[dfapp6["module.src"] == "None"]["TOPO.src"])
    print("Positions of the new users requesting app6: %s"%position_of_users_app6)