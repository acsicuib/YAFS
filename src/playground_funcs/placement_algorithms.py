import json
import networkx as nx

import re
import random
from math import floor
import matplotlib.pyplot as plt

import operator
import json
import os

def placement_algorithm(graph, app_def='data/appDefinition.json'):

    # Alloc será o dicionario convertido para json
    alloc = dict()
    alloc['initialAllocation'] = list()

    apps = json.load(open(app_def))

    max_res = max([len(app['module']) for app in apps])   #
    min_res = min([len(app['module']) for app in apps])   #
    n_comms = 0

    # Decide-se o nr de communities max de forma a conseguir suportar a maior app (caso seja possivel)
    while n_comms < len(graph.nodes):
        temp_comms = nx.algorithms.community.asyn_fluidc(graph, n_comms+1)

        if all(len(x) < max_res for x in temp_comms) or any(len(x) < min_res for x in temp_comms):
            break

        n_comms += 1

    comms = nx.algorithms.community.asyn_fluidc(graph, n_comms)
    comms = [list(x) for x in list(comms)]

    for app in apps:
        for mod in app['module']:

            # Vai rodando até encontrar uma community que consiga suportar a app inteira
            while len(app['module']) > len(comms[0]) and n_comms != 1:
                comms.append(comms.pop(0))

            temp_dict = dict()
            temp_dict['module_name'] = mod['name']
            temp_dict['app'] = app['id']
            temp_dict['id_resource'] = comms[0][0]

            comms[0].append(comms[0].pop(0))

            alloc['initialAllocation'].append(temp_dict)

        # Se houver mais do que 1 community, roda
        if n_comms != 1:
            comms.append(comms.pop(0))

    with open('data/allocDefinition.json', 'w') as f:
        json.dump(alloc, f)
