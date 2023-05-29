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

from yafs.core import Sim
from yafs.application import create_applications_from_json
from yafs.topology import Topology

from yafs.placement import JSONPlacement

# from yafs.path_routing import DeviceSpeedAwareRouting
# from yafs.fastestpath_routing import FastestRouteSelection
# from yafs.selection_multipleDeploys import DeviceSpeedAwareRouting
from yafs.Ze_dijkstra_3000inator import My_Path_Selector
# from shortest_path import MinimunPath

from yafs.distribution import deterministic_distribution

def draw_topology(t, pos):
    plt.figure(figsize=(7, 3))
    # nx.draw_networkx(t.G, pos, with_labels=True)
    nx.draw_networkx(t.G, pos, arrows=True)
    # nx.draw_networkx_edge_labels(t.G, pos, alpha=0.5, font_size=5, verticalalignment="top" )
    plt.show()


def plot_app_path(folder_results, application, t, pos):
    plt.figure(figsize=(10, 5))
    sml = pd.read_csv(folder_results + "sim_trace_link.csv")
    sm = pd.read_csv(folder_results + "sim_trace.csv")

    path = sml[sml.app == application]
    path = path[sml.at[0, 'id'] == sml.id]
    # path = sml[(sml.id == 1) & (sml.app == application)]

    path2 = sm[sm.app == application]
    path2 = sm[sm.at[0, 'id'] == sm.id]
    # path2 = sm[(sm.id == 1) & (sm.app == application)]
    print(type(path))

    highlighted_edges = []
    labels = {}
    for index, hops in path.iterrows():
        highlighted_edges.append([hops.src, hops.dst])
        labels[(hops.src, hops.dst)] = "{}\nBW={}\tPR={}".format( hops.message , t.get_edge((hops.src, hops.dst))['BW'], t.get_edge((hops.src, hops.dst))['PR'])
    print(highlighted_edges)

    print('tempo total')

    total_time = path2.at[path2.index[-1], 'time_out'] - path2.at[0, 'time_in']
    total_time = "total time = {:.2f}".format(total_time)
    plt.text(11, 0.3, total_time, fontsize=12, ha='right')

    nx.draw_networkx(t.G, pos, arrows=True)
    nx.draw_networkx_edges(t.G, pos, edge_color='black')
    # # Draw the highlighted edges in red
    nx.draw_networkx_edges(t.G, pos, edgelist=highlighted_edges, edge_color='red', arrows=True, arrowstyle='->')
    nx.draw_networkx_edge_labels(t.G, pos, edge_labels=labels, label_pos=0.5, font_size=8, font_family='Arial')

    plt.show()

def main(stop_time, it, folder_results):
    """
    TOPOLOGY
    """
    t = Topology()
    # dataNetwork = json.load(open('data/network.json')) #network em cadeia
    # dataNetwork = json.load(open('data/network2.json')) #network2 link 1->5->2 and 1->2
    dataNetwork = json.load(open('data/network3.json'))  # network3 link 1->5->2 and 1->6->2

    t.load(dataNetwork)

    # pos = nx.spring_layout(t.G)
    pos = {0: (0, 1), 1: (2, 1), 2: (6, 1), 3: (8, 1), 4: (10, 1), 5: (4, 0.4), 6: (4, 1.6)}
    # draw_topology(t, pos)


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

    # selectorPath = DeviceSpeedAwareRouting()
    selectorPath = My_Path_Selector()

    # selectorPath = FastestRouteSelection()
    # selectorPath = MinimunPath()

    """
    SIMULATION ENGINE
    """
    s = Sim(t, default_results_path=folder_results + "sim_trace")

    """
    Deploy services == APP's modules
    """
    for aName in apps.keys():
        s.deploy_app(apps[aName], placement, selectorPath)  # Note: each app can have a different routing algorithm

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

    plot_app_path("./results/", 0, t, pos)


if __name__ == '__main__':
    LOGGING_CONFIG = Path(__file__).parent / 'logging.ini'
    logging.config.fileConfig(LOGGING_CONFIG)

    folder_results = Path("results/")
    folder_results.mkdir(parents=True, exist_ok=True)
    folder_results = str(folder_results) + "/"

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
    dfl = pd.read_csv(folder_results + "sim_trace" + "_link.csv")
    print("Number of total messages between nodes: %i" % len(dfl))

    df = pd.read_csv(folder_results + "sim_trace.csv")
    print("Number of requests handled by deployed services: %i" % len(df))

    dfapp2 = df[df.app == 0].copy()  # a new df with the requests handled by app 0
    print(dfapp2.head())

    dfapp2.loc[:, "transmission_time"] = dfapp2.time_emit - dfapp2.time_reception  # Transmission time
    dfapp2.loc[:, "service_time"] = dfapp2.time_out - dfapp2.time_in

    print("The average service time of app2 is: %0.3f " % dfapp2["service_time"].mean())

    print("The app2 is deployed in the folling nodes: %s" % np.unique(dfapp2["TOPO.dst"]))
    print("The number of instances of App2 deployed is: %s" % np.unique(dfapp2["DES.dst"]))


