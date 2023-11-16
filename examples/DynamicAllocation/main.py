import random
"""

    This example implements a simple evolutive deployment of fog devices to study the latency of two applications.
    There is a comparison between:
    - One application has a cloud placement
    - Another one (equivalent application) has an evolutive deployement on fog devices

    @author: isaac

"""

import argparse

from yafs.core import Sim
from yafs.application import Application,Message
from yafs.topology import Topology
from yafs.placement import *
from yafs.distribution import deterministic_distribution,deterministicDistributionStartPoint

from Evolutive_population import Evolutive,Statical
from selection_multipleDeploys import  CloudPath_RR,BroadPath

import networkx as nx
import numpy as np
import copy
import itertools
import time
import operator

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
    attPR_BW = {x: 1 for x in t.G.edges()}

    nx.set_edge_attributes(t.G, name='BW', values=attPR_BW)
    nx.set_edge_attributes(t.G, name='PR', values=attPR_BW)

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
    app2 = create_application("app2")

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
    dDistribution = deterministicDistributionStartPoint(3000,300,name="Deterministic")
    dDistributionSrc = deterministic_distribution(name="Deterministic", time=10)
    pop1 = Evolutive(top20_devices,number_generators,name="top",activation_dist=dDistribution)
    pop1.set_sink_control({"app":app1.name,"number": 1, "module": app1.get_sink_modules()})
    pop1.set_src_control(
        {"number": 1, "message": app1.get_message("M.Action"), "distribution": dDistributionSrc})


    pop2 = Statical(number_generators,name="Statical")
    pop2.set_sink_control({"id": main_fog_device, "number": number_generators, "module": app2.get_sink_modules()})

    pop2.set_src_control(
        {"number": 1, "message": app2.get_message("M.Action"), "distribution": dDistributionSrc})

    #In addition, a source includes a distribution function:


    """--
    SELECTOR algorithm
    """
    selectorPath1 = BroadPath()

    selectorPath2 = CloudPath_RR()


    """
    SIMULATION ENGINE
    """

    s = Sim(t, default_results_path="Results_%s_singleApp1" % (simulated_time))
    s.deploy_app2(app1, placement, pop1, selectorPath1)
    # s.deploy_app(app2, placement, pop2,  selectorPath2)

    s.run(simulated_time,test_initial_deploy=False,show_progress_monitor=False)
    # s.draw_allocated_topology() # for debugging

if __name__ == '__main__':
    import logging.config
    import os

    logging.config.fileConfig(os.getcwd()+'/logging.ini')

    start_time = time.time()

    main(simulated_time=12000)

    print("\n--- %s seconds ---" % (time.time() - start_time))
