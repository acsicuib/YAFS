"""
Some common functions
"""
import copy
import networkx as nx
import matplotlib.pyplot as plt
import random

#DISTRIBUTIONS

def next_time_uniform_dist(min,max):
    #Ensure that return value is non negative number and bigger than 0
    return random.randint(min,max)

def next_time_exponential_dist(lambd):
    return random.expovariate(1 / lambd)

def next_time_periodic(time_shift):
    return time_shift

def deterministicDistribution(time_shift):
    return time_shift


def fractional_selectivity(threshold):
    return random.random() <= threshold


###########



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
    plt.show()
    #fig.savefig(file_path+'/model.eps',format='eps')
    plt.close(fig)


