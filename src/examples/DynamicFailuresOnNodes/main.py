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
from yafs.distribution import *

from Evolutive_population import Pop_and_Failures
from selection_multipleDeploys import  BroadPath


import itertools
import time
import operator
import copy
import networkx as nx
import numpy as np

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
    t.G = nx.convert_node_labels_to_integers(t.G, first_label=0, ordering='default', label_attribute=None)

    print "Nodes: %i" %len(t.G.nodes())
    print "Edges: %i" %len(t.G.edges())
    #MANDATORY fields of a link
    # Default values =  {"BW": 1, "PR": 1}
    valuesOne = dict(itertools.izip(t.G.edges(),np.ones(len(t.G.edges()))))

    nx.set_edge_attributes(t.G, name='BW', values=valuesOne)
    nx.set_edge_attributes(t.G, name='PR', values=valuesOne)

    centrality = nx.betweenness_centrality(t.G)
    nx.set_node_attributes(t.G, name="centrality", values=centrality)

    sorted_clustMeasure = sorted(centrality.items(), key=operator.itemgetter(1), reverse=True)

    top20_devices =  sorted_clustMeasure[:20]
    main_fog_device = copy.copy(top20_devices[0][0])

    print "-" * 20
    print "Top 20 centralised nodes:"
    for item in top20_devices:
        print item
    print "-"*20
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
    print number_generators

    #you can use whatever funciton to change the topology
    dStart = deterministicDistributionStartPoint(0, 100, name="Deterministic")
    dStart2 = exponentialDistributionStartPoint(500, 100.0, name="Deterministic")
    pop = Pop_and_Failures(name="mttf-nodes",srcs = number_generators,activation_dist=dStart2 )
    pop.set_sink_control({"ids": top20_devices, "number": 1, "module": app1.get_sink_modules()})

    dDistribution = deterministicDistribution(name="Deterministic", time=10)
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
    s.deploy_app(app1, placement, pop, selectorPath)


    s.run(simulated_time,test_initial_deploy=False,show_progress_monitor=False)
    # s.draw_allocated_topology() # for debugging
    print "Total nodes available in the  toopology %i" %len(s.topology.G.nodes())
    print "Total edges available in the  toopology %i" %len(s.topology.G.edges())

    print pop.nodes_removed

if __name__ == '__main__':
    import logging.config
    import os

    logging.config.fileConfig(os.getcwd()+'/logging.ini')

    start_time = time.time()

    main(simulated_time=10000)

    print("\n--- %s seconds ---" % (time.time() - start_time))
