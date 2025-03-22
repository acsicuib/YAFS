import random
"""

    This example implements a simple evolutive deployment of fog devices to study the latency of two applications.
    There is a comparison between:
    - One application has a cloud placement
    - Another one (equivalent application) has an evolutive deployement on fog devices

    @author: isaac

"""

import argparse
import itertools
import time
import operator
import copy
import networkx as nx
import numpy as np

from yafs.core import Sim
from yafs.application import Application,Message
from yafs.topology import Topology
from yafs.placement import *
from yafs.distribution import *

from Evolutive_population import Pop_and_Failures
from selection_multipleDeploys import  BroadPath

RANDOM_SEED = 1

def create_application(name):
    # APLICATION
    a = Application(name=name)

    a.set_modules([{"Generator":{"Type":Application.TYPE_SOURCE}},
                   {"Actuator": {"Type": Application.TYPE_SINK}}
                   ])

    m_egg = Message("M.Action", "Generator", "Actuator", instructions=100, bytes=10)
    a.add_source_messages(m_egg)
    return a


# @profile
def main(simulated_time):

    random.seed(RANDOM_SEED)
    np.random.seed(RANDOM_SEED)
    """
    TOPOLOGY from a json
    """

    t = Topology()
    t.G = nx.read_graphml("Euclidean.graphml")

    ls = list(t.G.nodes)
    li = {x: int(x) for x in ls}
    nx.relabel_nodes(t.G, li, False) #Transform str-labels to int-labels


    print("Nodes: %i" %len(t.G.nodes()))
    print("Edges: %i" %len(t.G.edges()))
    #MANDATORY fields of a link
    # Default values =  {"BW": 1, "PR": 1}
    valuesOne = {x :1 for x in t.G.edges()}

    nx.set_edge_attributes(t.G, name='BW', values=valuesOne)
    nx.set_edge_attributes(t.G, name='PR', values=valuesOne)

    centrality = nx.betweenness_centrality(t.G)
    nx.set_node_attributes(t.G, name="centrality", values=centrality)

    sorted_clustMeasure = sorted(centrality.items(), key=operator.itemgetter(1), reverse=True)

    top20_devices =  sorted_clustMeasure[:20]
    main_fog_device = copy.copy(top20_devices[0][0])

    print("-" * 20)
    print("Top 20 centralised nodes:")
    for item in top20_devices:
        print(item)
    print("-"*20)
    """
    APPLICATION
    """
    app1 = create_application("app1")


    """
    PLACEMENT algorithm
    """
    #There are not modules to place.
    placement = NoPlacementOfModules("NoPlacement")

    """
    POPULATION algorithm
    """
    number_generators = int(len(t.G)*0.1)
    print(number_generators)

    #you can use whatever funciton to change the topology
    dStart = deterministicDistributionStartPoint(0, 100, name="Deterministic")
    dStart2 = exponentialDistributionStartPoint(500, 100.0, name="Deterministic")
    pop = Pop_and_Failures(name="mttf-nodes",srcs = number_generators,activation_dist=dStart2 )
    pop.set_sink_control({"ids": top20_devices, "number": 1, "module": app1.get_sink_modules()})

    dDistribution = deterministic_distribution(name="Deterministic", time=10)
    pop.set_src_control(
        {"number": 1, "message": app1.get_message("M.Action"), "distribution": dDistribution})

    #In addition, a source includes a distribution function:


    """--
    SELECTOR algorithm
    """
    selectorPath = BroadPath()


    """
    SIMULATION ENGINE
    """
    s = Sim(t, default_results_path="Results_%s_exp" % (simulated_time))
    s.deploy_app2(app1, placement, pop, selectorPath)


    s.run(simulated_time,test_initial_deploy=False,show_progress_monitor=False)
    # s.draw_allocated_topology() # for debugging
    print("Total nodes available in the  toopology %i" %len(s.topology.G.nodes()))
    print("Total edges available in the  toopology %i" %len(s.topology.G.edges()))

    print(pop.nodes_removed)
    nx.write_gexf(s.topology.G,"final_network.graphml")

if __name__ == '__main__':
    import logging.config
    import os

    logging.config.fileConfig(os.getcwd()+'/logging.ini')

    start_time = time.time()

    main(simulated_time=10000)

    print("\n--- %s seconds ---" % (time.time() - start_time))
