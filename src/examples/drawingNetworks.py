"""
This application create a graphml with some information from Dynamic* algorithms to draw the network in GEPHI.
"""

import networkx as nx
import itertools
import numpy as np

G = nx.read_graphml("Euclidean.graphml")
G = nx.convert_node_labels_to_integers(G, first_label=0, ordering='default', label_attribute=None)

centrality = nx.betweenness_centrality(G)
nx.set_node_attributes(G, name="centrality", values=centrality)

# This data is obtained by three Dynamic* algorithms

# Failures on Nodes
failures_exp=[{'id': 398, 'module': False, 'time': 500}, {'id': 343, 'module': False, 'time': 694}, {'id': 48, 'module': False, 'time': 1070}, {'id': 133, 'module': True, 'time': 1072}, {'id': 288, 'module': False, 'time': 1136}, {'id': 283, 'module': False, 'time': 1323}, {'id': 374, 'module': False, 'time': 1451}, {'id': 168, 'module': False, 'time': 1471}, {'id': 331, 'module': False, 'time': 1493}, {'id': 265, 'module': False, 'time': 1691}, {'id': 119, 'module': False, 'time': 1694}, {'id': 233, 'module': False, 'time': 1722}, {'id': 353, 'module': False, 'time': 1837}, {'id': 337, 'module': True, 'time': 1838}, {'id': 199, 'module': False, 'time': 1858}, {'id': 232, 'module': False, 'time': 2393}, {'id': 13, 'module': False, 'time': 2419}, {'id': 95, 'module': False, 'time': 2723}, {'id': 317, 'module': False, 'time': 2814}, {'id': 163, 'module': False, 'time': 2919}, {'id': 67, 'module': False, 'time': 3012}, {'id': 279, 'module': True, 'time': 3077}, {'id': 267, 'module': False, 'time': 3112}, {'id': 147, 'module': False, 'time': 3296}, {'id': 174, 'module': False, 'time': 3353}, {'id': 202, 'module': False, 'time': 3489}, {'id': 310, 'module': False, 'time': 3579}, {'id': 206, 'module': False, 'time': 3647}, {'id': 153, 'module': False, 'time': 3752}, {'id': 193, 'module': False, 'time': 3804}, {'id': 17, 'module': False, 'time': 3825}, {'id': 281, 'module': False, 'time': 3928}, {'id': 393, 'module': False, 'time': 4107}, {'id': 236, 'module': False, 'time': 4173}, {'id': 65, 'module': True, 'time': 4372}, {'id': 197, 'module': False, 'time': 4642}, {'id': 392, 'module': False, 'time': 4737}, {'id': 307, 'module': False, 'time': 4832}, {'id': 213, 'module': False, 'time': 4950}, {'id': 345, 'module': False, 'time': 5128}, {'id': 201, 'module': False, 'time': 5312}, {'id': 380, 'module': False, 'time': 5323}, {'id': 227, 'module': False, 'time': 5366}, {'id': 177, 'module': False, 'time': 5413}, {'id': 216, 'module': True, 'time': 5740}, {'id': 382, 'module': False, 'time': 5789}, {'id': 2, 'module': False, 'time': 5840}, {'id': 312, 'module': False, 'time': 6326}, {'id': 326, 'module': False, 'time': 6338}, {'id': 354, 'module': False, 'time': 6344}, {'id': 292, 'module': False, 'time': 6395}, {'id': 321, 'module': False, 'time': 6529}, {'id': 218, 'module': False, 'time': 6539}, {'id': 159, 'module': False, 'time': 6566}, {'id': 22, 'module': False, 'time': 6830}, {'id': 348, 'module': False, 'time': 6847}, {'id': 222, 'module': False, 'time': 6999}, {'id': 75, 'module': False, 'time': 7053}, {'id': 191, 'module': False, 'time': 7315}, {'id': 183, 'module': False, 'time': 7370}, {'id': 131, 'module': False, 'time': 7440}, {'id': 127, 'module': False, 'time': 7466}, {'id': 210, 'module': False, 'time': 7584}, {'id': 247, 'module': False, 'time': 7706}, {'id': 243, 'module': False, 'time': 7748}, {'id': 171, 'module': False, 'time': 8281}, {'id': 84, 'module': False, 'time': 8343}, {'id': 64, 'module': False, 'time': 8366}, {'id': 231, 'module': False, 'time': 8389}, {'id': 344, 'module': False, 'time': 8447}, {'id': 318, 'module': False, 'time': 8616}, {'id': 325, 'module': False, 'time': 8970}, {'id': 264, 'module': False, 'time': 9031}, {'id': 31, 'module': False, 'time': 9125}, {'id': 6, 'module': False, 'time': 9424}, {'id': 5, 'module': False, 'time': 9526}, {'id': 299, 'module': True, 'time': 9572}, {'id': 42, 'module': False, 'time': 9701}, {'id': 248, 'module': False, 'time': 9867}, {'id': 126, 'module': False, 'time': 9891}, {'id': 28, 'module': False, 'time': 9916}, {'id': 61, 'module': True, 'time': 9928}]

# Nodes with sensor app
src = [53, 339, 306, 102, 198, 180, 261, 316, 37, 11, 335, 173, 305, 0, 178, 289, 91, 379, 361, 12, 10, 217, 376, 152, 86, 169, 11, 88, 175, 198, 93, 92, 87, 184, 116, 8, 335, 223, 257, 74]

# Nodes with sensor app (Dynamic Workload)
finalSRC = [337, 110, 21, 230, 230, 110, 21, 238, 230, 70, 21, 21, 70, 110, 21, 21, 279, 230, 21, 21, 21, 21, 21, 110, 110, 230, 70, 110, 110, 230, 238, 238, 337, 238, 230, 279, 21, 21, 238, 230]

valuesOne = dict(itertools.izip(G.nodes(), np.zeros(len(G.nodes())).tolist()))
valuesSRC = dict(itertools.izip(G.nodes(), np.zeros(len(G.nodes())).tolist()))
valuesFIN = dict(itertools.izip(G.nodes(), np.zeros(len(G.nodes())).tolist()))


for item in failures_exp:
    valuesOne[item["id"]]=1.0

for item in src:
    valuesSRC[item]=1.0

for item in finalSRC:
    valuesFIN[item]=1.0

nx.set_node_attributes(G, name='removed', values=valuesOne)
nx.set_node_attributes(G, name='src', values=valuesSRC)
nx.set_node_attributes(G, name='srcMove', values=valuesFIN)

nx.write_graphml(G, "Euclidean-removed.graphml")

