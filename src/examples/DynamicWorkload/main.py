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

from Evolutive_population import Population_Move
from selection_multipleDeploys import  CloudPath_RR


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

    top20_devices =  sorted_clustMeasure[0:20]
    main_fog_device = copy.copy(top20_devices[0][0])

    print "-" * 20
    print "Best top centralized device: ",main_fog_device
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
    print "Number of generators %i"%number_generators

    #you can use whatever funciton to change the topology
    dStart = deterministicDistributionStartPoint(500, 400, name="Deterministic")
    pop = Population_Move(name="mttf-nodes",srcs = number_generators,node_dst=main_fog_device,activation_dist=dStart)
    pop.set_sink_control({"id": main_fog_device, "number": number_generators, "module": app1.get_sink_modules()})



    dDistribution = deterministicDistribution(name="Deterministic", time=100)
    pop.set_src_control(
        {"number": 1, "message": app1.get_message("M.Action"), "distribution": dDistribution})

    #In addition, a source includes a distribution function:


    """--
    SELECTOR algorithm
    """
    selectorPath = CloudPath_RR()


    """
    SIMULATION ENGINE
    """
    s = Sim(t, default_results_path="Results_%s" % (simulated_time))
    s.deploy_app(app1, placement, pop, selectorPath)

    s.run(simulated_time,test_initial_deploy=False,show_progress_monitor=False)

    print pop.list_src

    # s.draw_allocated_topology() # for debugging
    s.print_debug_assignaments()


if __name__ == '__main__':
    import logging.config
    import os

    logging.config.fileConfig(os.getcwd()+'/logging.ini')

    start_time = time.time()

    main(simulated_time=10000)

    print("\n--- %s seconds ---" % (time.time() - start_time))
