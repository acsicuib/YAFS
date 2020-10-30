"""
    This is the most simple scenario with a basic topology, some users and a set of apps with only one service.

    @author: Isaac Lera
"""
import os
import time
import json
import random
import logging.config

import networkx as nx
from pathlib import Path

from yafs.core import Sim
from yafs.application import create_applications_from_json
from yafs.topology import Topology

from yafs.placement import JSONPlacement
from yafs.path_routing import DeviceSpeedAwareRouting
from yafs.distribution import deterministic_distribution

def main(stop_time, it):

    folder_results = Path("results/")
    folder_results.mkdir(parents=True, exist_ok=True)
    folder_results = str(folder_results)+"/"

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

    nx.write_gexf(t.G,folder_results+"graph_binomial_tree_%i"%size) # you can export the Graph in multiples format to view in tools like Gephi, and so on.

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
        s.deploy_app(apps[aName], placement, selectorPath) # Note: each app can have a different routing algorithm

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
    RUNNING - last step
    """
    logging.info(" Performing simulation: %i " % it)
    s.run(stop_time)  # To test deployments put test_initial_deploy a TRUE
    s.print_debug_assignaments()


if __name__ == '__main__':

    logging.config.fileConfig(os.getcwd() + '/logging.ini')

    nIterations = 1  # iteration for each experiment
    simulationDuration = 20000

    # Iteration for each experiment changing the seed of randoms
    for iteration in range(nIterations):
        random.seed(iteration)
        logging.info("Running experiment it: - %i" % iteration)

        start_time = time.time()
        main(stop_time=simulationDuration,
             it=iteration)

        print("\n--- %s seconds ---" % (time.time() - start_time))

    print("Simulation Done!")
