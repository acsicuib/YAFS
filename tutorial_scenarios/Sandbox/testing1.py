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
import shutil
import networkx as nx

from pathlib import Path

import pandas as pd
import numpy as np

# Meus imports
from yafs import plot
from yafs import experiment_configuration as eg, myConfig
from yafs.sandbox_routing import MaxBW, MaxBW_Root

from yafs.core import Sim
from yafs.application import create_applications_from_json
from yafs.topology import Topology

from yafs.placement import JSONPlacement
from yafs.distribution import deterministic_distribution
from yafs.path_routing import DeviceSpeedAwareRouting


NUMBER_OF_APPS = 10
NUMBER_OF_NODES = 10

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


def sum_mods_per_node(placement, nodes):
    for dt in placement.data['initialAllocation']:
        nodes[int(dt['id_resource'])] += 1

def append_mods_per_node(placement, total_mods_per_node):
    mods_per_node = dict()
    for i in range(NUMBER_OF_NODES+1):
        mods_per_node[i] = 0

    for dt in placement.data['initialAllocation']:
        mods_per_node[int(dt['id_resource'])] += 1

    total_mods_per_node[algorithm] += list(mods_per_node.values())


def main(stop_time, it, folder_results,folder_data_processing, algorithm, seed, total_mods_per_node):

    global nodes
    random.seed(seed)
    conf = myConfig.myConfig()
    exp_conf = eg.ExperimentConfiguration(conf, lpath=os.path.dirname(__file__))

    random.seed(seed)
    exp_conf.app_generation(app_struct='linear')
    random.seed(seed)
    exp_conf.networkGeneration(n=NUMBER_OF_NODES, file_name_network='network.json')
    random.seed(seed)
    exp_conf.user_generation()

    # Algoritmo de alloc

    start_clock = time.time()

    if algorithm == 'random':
        exp_conf.randomPlacement(file_name_network='network.json')

    elif algorithm == 'bt_min_mods':
        exp_conf.bt_min_mods()

    elif algorithm == 'near_GW_BW_PR':
        exp_conf.near_GW_placement(weight='BW_PR')

    elif algorithm == 'near_GW_PR':
        exp_conf.near_GW_placement(weight='PR')

    elif algorithm == 'near_GW_BW':
        exp_conf.near_GW_placement(weight='BW')

    elif algorithm == 'greedy_FRAM':
        exp_conf.greedy_algorithm()

    elif algorithm == 'lambda':
        exp_conf.lambda_placement()

    elif algorithm == 'greedy_latency':
        exp_conf.greedy_algorithm_latency()

    placement_clock[algorithm].append(time.time() - start_clock)



    plot_name = algorithm

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

    if it == 0:
        nodes = dict()
        # for n in t.get_nodes():
        #     nodes[int(n)] = 0

        total_mods_per_node[algorithm] = []
        for n in t.get_nodes():
            nodes[int(n)] = 0

    # sum_mods_per_node(placement, nodes)
    append_mods_per_node(placement, total_mods_per_node)


    """
    Defining ROUTING algorithm to define how path messages in the topology among modules
    """
    # selectorPath = MaxBW_Root()       # <<< Selector path do ze
    # selectorPath = DeviceSpeedAwareRouting()
    # graph_file_ = 'root_alg'

    selectorPath = MaxBW()
    graph_file_ = 'networkx_alg'


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
    # data_analysis.plot_occurrencies(folder_results, mode='node_dst')


    if it == nIterations-1:
        # pos = nx.spring_layout(t.G, seed=seed)
        # nx.draw_networkx(t.G, pos)
        # plt.title(algorithm)
        # plt.show()
        # data_analysis.plot_latency(folder_results, plot_name=plot_name)
        plot.plot_avg_latency(folder_results, plot_name=plot_name)

        src_csv = folder_results + "sim_trace_link.csv"
        dst_csv = folder_data_processing + algorithm + "_sim_trace_link.csv"
        shutil.copyfile(src_csv, dst_csv)

        # src_alloc = 'data/allocDefinition.json'
        # dst_alloc = folder_data_processing + algorithm + '_allocDefinition.json'
        # shutil.copyfile(src_alloc, dst_alloc)
        if nIterations > 1:
            for node in nodes.keys():
                nodes[node] /= it
        modules_per_node[algorithm] = nodes

        print(algorithm, 'len\n',len(total_mods_per_node[algorithm]), '\n\n')

        # data_analysis.modules_per_node(placement, t, plot_name=plot_name)
        # data_analysis.plot_nodes_per_time_window(folder_results, t, n_wind=10, plot_name=allocAlg+'_nds_per_tw')


if __name__ == '__main__':
    # LOGGING_CONFIG = Path(__file__).parent / 'logging.ini'
    # logging.config.fileConfig(LOGGING_CONFIG)

    folder_results = Path("results")
    folder_results.mkdir(parents=True, exist_ok=True)
    folder_results = str(folder_results) + '/'  # TODO bool

    folder_data_processing = Path('data_processing')
    folder_data_processing.mkdir(parents=True, exist_ok=True)
    folder_data_processing = str(folder_data_processing) + '/'  # TODO bool

    nIterations = 50  # iteration for each experiment
    simulationDuration = 20000

    god_tier_seed = 15612357
    random_seed = True
    if random_seed:
        seed = int(time.time())
    else:
        seed = god_tier_seed

    seed_list = [random.randint(1, 100000) for _ in range(nIterations)]

    modules_per_node = dict()
    total_mods_per_node = dict()
    placement_clock = dict()

    # algorithm_list = ['randomPlacement', 'bt_min_mods','near_GW_placement', 'greedy_algorithm']
    # algorithm_list = ['bt_min_mods']

    # algorithm_list = ['random', 'greedy_FRAM' ,'greedy_latency', 'near_GW_BW', 'near_GW_PR', 'near_GW_BW_PR', 'lambda' ]
    algorithm_list = ['random', 'greedy_FRAM' ,'greedy_latency', 'near_GW_BW', 'near_GW_PR', 'near_GW_BW_PR']

    for algorithm in algorithm_list:
        placement_clock[algorithm] = []
        print('\n\n', algorithm,'\n')
        # Iteration for each experiment changing the seed of randoms
        for iteration in range(nIterations):
            random.seed(iteration)
            logging.info("Running experiment it: - %i" % iteration)

            start_time = time.time()
            main(stop_time=simulationDuration,
                 it=iteration, folder_results=folder_results, folder_data_processing=folder_data_processing,algorithm=algorithm, seed=seed_list[iteration], total_mods_per_node=total_mods_per_node)
            sim_duration = time.time() - start_time
            print("\n--- %s seconds ---" % (sim_duration))

        print("Simulation Done!")

    print(modules_per_node)
    print(placement_clock)

    plot.scatter_plot_app_latency_per_algorithm(folder_data_processing, algorithm_list)
    plot.plot_latency_per_placement_algorithm(folder_data_processing, algorithm_list)
    plot.boxplot_latency_per_placement_algorithm(folder_data_processing, algorithm_list)
    plot.plot_modules_per_node_per_algorithm(total_mods_per_node)
    plot.plot_max_stress_per_algorithm(total_mods_per_node)
    plot.plot_algorithm_exec_time(placement_clock, nIterations)
    plot.plot_used_nodes_per_algorithm(total_mods_per_node, nIterations)
