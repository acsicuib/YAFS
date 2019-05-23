"""
Some common functions
"""
import copy
import networkx as nx
import matplotlib.pyplot as plt
import random
import numpy as np
from collections import OrderedDict
import networkx as nx
import pyproj
from shapely.ops import transform
from functools import partial
import math

#DISTRIBUTIONS

# def next_time_uniform_dist(min,max):
#     #Ensure that return value is non negative number and bigger than 0
#     return random.randint(min,max)
#
# def next_time_exponential_dist(lambd):
#     return random.expovariate(1 / lambd)
#
# def next_time_periodic(time_shift):
#     return time_shift
#
# def deterministicDistribution(time_shift):
#     return time_shift
#
def fractional_selectivity(threshold):
    return random.random() <= threshold
#
#
# def start_undeterminedDistribution(start,time_shift):
#     return start


###########

def create_pos(G,scale):
    x = nx.get_node_attributes(G,'x')
    y = nx.get_node_attributes(G,'y')
    pos = {}
    for k in x.keys():
        lat = x[k]*scale
        lng = y[k]*scale
        pos[k]=np.array([lat,lng])
    return pos

def create_points(G):
    x = nx.get_node_attributes(G,'x')
    y = nx.get_node_attributes(G,'y')
    pos = OrderedDict()
    for k in x.keys():
        lat = x[k]
        lng = y[k]
        pos[k]=[lat,lng]
    return pos

def toMeters(geometry):
    project = partial(
    pyproj.transform,
    pyproj.Proj(init='EPSG:4326'),
    pyproj.Proj(init='EPSG:32633'))
    return transform(project,geometry).length

def get_random_node(G):
    return list(G.nodes())[random.randint(0,len(G.nodes())-1)]


def get_shortest_random_path(G):

    counter = 0
    tries = len(G.nodes)*0.2
    while tries>counter:
        try:
            src = get_random_node(G)
            dst = get_random_node(G)
            path = nx.shortest_path(G, src, dst)
            if len(path)>0:
                return path
        except nx.NetworkXNoPath:
            counter += 1


def draw_topology(topology,alloc_entity):
    """
    Draw the modeled topology

    .. Note: This classes can be extended to export the topology (graph) to other visualization tools
    """
    G = copy.copy(topology.G)


    lastID = len(G.nodes())
    labels = dict(zip(range(topology.size()), range(topology.size())))

    nodesM = []
    edgesM = []
    #Generate new edges (and nodes) of each deployed module (pure or not)
    #labels are assigned by module allocated name
    for entity in alloc_entity:
        for value in alloc_entity[entity]:
            G.add_edge(entity, lastID)
            nodesM.append(lastID)
            labels[lastID] = value
            edgesM.append((entity, lastID))
            lastID +=1

    pos = nx.spring_layout(G)

    #Change the labels by model names
    # for key in topology.nodeAttributes:
    #     labels[key]=topology.nodeAttributes[key]["model"]

    fig, ax = plt.subplots()
    nx.draw_networkx_nodes(G, nodelist=G.nodes()-nodesM, node_shape="s",pos=pos,ax=ax)
    nx.draw_networkx_nodes(G, nodelist=nodesM, node_shape="o", pos=pos,linewidths=0.2,node_color="pink",alpha=0.4,ax=ax)
    nx.draw_networkx_labels(G, pos, labels,font_size=6,ax=ax)
    nx.draw_networkx_edges(G, edgelist=edgesM, pos=pos, style="dashed",width=0.8,ax=ax)
    nx.draw_networkx_edges(G, edgelist=G.edges()-edgesM, pos=pos, width=1.2,ax=ax)
    plt.axis('off')

    plt.ion()
    plt.show()

    fig.savefig('app_deployed.png',format='png')
    plt.close(fig)


def haversine_distance(origin, destination):
  """ Haversine formula to calculate the distance between two lat/long points on a sphere """
  radius = 6371.0 # FAA approved globe radius in km

  dlat = math.radians(destination[0]-origin[0])
  dlon = math.radians(destination[1]-origin[1])

  a = math.sin(dlat/2.) * math.sin(dlat/2.) + math.cos(math.radians(origin[0])) \
      * math.cos(math.radians(destination[0])) * math.sin(dlon/2.) * math.sin(dlon/2.)

  c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1-a))
  d = radius * c

  return d #distance in km
