"""
    This is the most simple scenario with a basic topology, some users and a set of apps with only one service.

    @author: Isaac Lera
"""
import csv
import os
import time
import json
import random
import logging.config

import networkx as nx

from pathlib import Path

import pandas as pd
import numpy as np

# Meus imports
from playground_funcs import data_analysis
from playground_funcs import environment_generation as eg, myConfig
from playground_funcs.routing_algorithms import MaxBW, MaxBW_Root

from yafs.core import Sim
from yafs.application import create_applications_from_json
from yafs.topology import Topology

from yafs.placement import JSONPlacement
from yafs.distribution import deterministic_distribution
from yafs.path_routing import DeviceSpeedAwareRouting


def append_results(it, path):
    if it == 0:
        last_node_id = 0
        last_link_id = 0

        # Se for a primeria iteração apaga os dados anteriores
        with open(path + "sim_trace.csv", "w") as f_nodes, open(path + "sim_trace_link.csv", "w") as f_links:
            f_links.close()
            f_nodes.close()

    else:
        last_node_id = max(pd.read_csv(path + "sim_trace.csv").id)
        last_link_id = max(pd.read_csv(path + "sim_trace_link.csv").id)

    with open(path + "sim_trace_temp.csv", newline='') as f_src, open(path + 'sim_trace.csv', 'a', newline='') as f_dst:
        reader = csv.reader(f_src)
        writer = csv.writer(f_dst)
        for enum, row in enumerate(reader):
            if it == 0 or (enum != 0 and enum != 1):
                converted_row = [int(val) if val.isdigit() else float(val) if val.replace('.', '', 1).isdigit() else val for val in row]
                if it != 0 and len(converted_row) != 0:
                    converted_row[0] += last_node_id
                writer.writerow(converted_row)

    with open(path + "sim_trace_temp_link.csv", newline='') as f_src, open(path + 'sim_trace_link.csv', 'a', newline='') as f_dst:
        reader = csv.reader(f_src)
        writer = csv.writer(f_dst)
        for enum, row in enumerate(reader):
            if it == 0 or (enum != 0 and enum != 1):
                converted_row = [int(val) if val.isdigit() else float(val) if val.replace('.', '', 1).isdigit() else val for val in row]
                if it != 0 and len(converted_row) != 0:
                    converted_row[0] += last_link_id
                writer.writerow(converted_row)


def main(stop_time, it, folder_results):

    allocAlg = 'near_GW_placement'
    allocAlg = 'bt_min_mods'

    conf = myConfig.myConfig()
    exp_conf = eg.ExperimentConfiguration(conf, lpath=os.path.dirname(__file__))
    exp_conf.networkGeneration(n=10, file_name_network='network.json')
    exp_conf.user_generation()
    exp_conf.simpleAppsGeneration()
    exp_conf.app_generation(app_struct='simple')
    eval('exp_conf.' + allocAlg + '()')
    # exp_conf.bt_min_mods()


    """
    TOPOLOGY
    """
    t = Topology()
    dataNetwork = json.load(open('data/network.json'))

    t.load(dataNetwork)

    # if it >= 1:
    #     t.remove_node(1)
#
    # stable_placement(t.G)

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
    # selectorPath = MaxBW_Root()       # <<< Selector path do ze
    selectorPath = DeviceSpeedAwareRouting()
    graph_file_ = 'root_alg'

    # selectorPath = MaxBW()
    # graph_file_ = 'networkx_alg'


    """
    SIMULATION ENGINE
    """
    s = Sim(t, default_results_path=folder_results+"sim_trace_temp")

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

    append_results(it, folder_results)

    # pos = {0: (2, 0), 1: (4, 0), 2: (3, 1), 3: (4, 2), 4: (5, 1), 5: (6, 0), 6: (0, 0)}
    pos = {0: (0, 1), 1: (1, 2), 2: (2, 1), 3: (1, 0), 4: (3, 1), 5: (4, 2), 6: (5, 1), 7: (4, 0)}

    # teste = nx.algorithms.community.asyn_fluidc(t.G, 4, max_iter=100, seed=None)
    # teste = nx.pagerank(t.G, alpha=0.85, personalization=None, max_iter=100, tol=1e-06, nstart=None, weight='weight', dangling=None)

    #!!! data_analysis.plot_app_path(folder_results, 0, t, graph_file=graph_file_, pos=pos, placement=placement)
    # data_analysis.plot_nodes_per_time_window(folder_results, t, n_wind=10)
    # data_analysis.plot_occurrencies(folder_results, mode='node_dst')

    data_analysis.plot_latency(folder_results, allocAlg)


if __name__ == '__main__':
    LOGGING_CONFIG = Path(__file__).parent / 'logging.ini'
    logging.config.fileConfig(LOGGING_CONFIG)

    folder_results = Path("results/")
    folder_results.mkdir(parents=True, exist_ok=True)
    folder_results = str(folder_results)+"\\" #!123

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

    # data_analysis.plot_latency(folder_results)
    # data_analysis.plot_node_services(folder_results)

