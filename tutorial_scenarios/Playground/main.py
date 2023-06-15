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
import matplotlib.pyplot as plt

import pandas as pd
import numpy as np

from playground_funcs import data_analysis
from yafs.core import Sim
from yafs.application import create_applications_from_json
from yafs.topology import Topology

from yafs.placement import JSONPlacement
from yafs.path_routing import MaxBW, MaxBW_Root
from yafs.distribution import deterministic_distribution


def main(stop_time, it, folder_results):

    """
    TOPOLOGY
    """
    t = Topology()
    dataNetwork = json.load(open('data/network.json'))
    t.load(dataNetwork)

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
    selectorPath = MaxBW_Root()       # <<< Selector path do ze
    graph_file_ = 'root_alg'

    # selectorPath = MaxBW()
    # graph_file_ = 'networkx_alg'


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

    pos = {0: (2, 0), 1: (4, 0), 2: (3, 1), 3: (4, 2), 4: (5, 1), 5: (6, 0), 6: (0, 0)}
    data_analysis.plot_app_path(folder_results, 0, t, graph_file=graph_file_, pos=pos)



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
             it=iteration, folder_results=folder_results)

        print("\n--- %s seconds ---" % (time.time() - start_time))

    print("Simulation Done!")

    # Analysing the results. 
    dfl = pd.read_csv(folder_results+"sim_trace"+"_link.csv")
    print("Number of total messages between nodes: %i"%len(dfl))

    df = pd.read_csv(folder_results+"sim_trace.csv")
    print("Number of requests handled by deployed services: %i"%len(df))

    dfapp = df[df.app == 0].copy() # a new df with the requests handled by app 0
    print(dfapp.head())

    dfapp.loc[:,"transmission_time"] = dfapp.time_emit - dfapp.time_reception # Transmission time
    dfapp.loc[:,"service_time"] = dfapp.time_out - dfapp.time_in

    print("The average service time of app0 is: %0.3f "%dfapp["service_time"].mean())

    print("The app0 is deployed in the folling nodes: %s"%np.unique(dfapp["TOPO.dst"]))
    print("The number of instances of App0 deployed is: %s"%np.unique(dfapp["DES.dst"]))
