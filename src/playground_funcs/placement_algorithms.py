import json
import networkx as nx


def placement_algorithm(graph, app_def='data/appDefinition.json'):

    # Alloc será o dicionario convertido para json
    alloc = dict()
    alloc['initialAllocation'] = list()

    apps = json.load(open(app_def))

    n_comunitties = len(apps)

    comms = nx.algorithms.community.asyn_fluidc(graph, n_comunitties)
    comms = [list(x) for x in list(comms)]

    for en, app in enumerate(apps):
        for mod in app['module']:
            temp_dict = dict()
            temp_dict['module_name'] = mod['name']
            temp_dict['app'] = app['id']

            temp_dict['id_resource'] = comms[en][0]
            comms.append(comms.pop(0))
            alloc['initialAllocation'].append(temp_dict)

    with open('data/allocDefinition.json', 'w') as f:
        json.dump(alloc, f)


def placement_algorithm_v2(graph, app_def='data/appDefinition.json'):

    # Alloc será o dicionario convertido para json
    alloc = dict()
    alloc['initialAllocation'] = list()

    apps = json.load(open(app_def))

    n_comunitties = len(apps)
    comms = nx.algorithms.community.asyn_fluidc(graph, n_comunitties)
    spare_nodes = []
    alloc_missing = []

    for app in apps:
        comms = comms.__next__()
        for mod in app['module']:
            temp_dict = dict()
            temp_dict['module_name'] = mod['name']
            temp_dict['app'] = app['id']

            if len(comms) != 0:

                # Se ainda existir algum node da comunidade, utiliza-o
                temp_dict['id_resource'] = min(comms)
                comms.discard(min(comms))
                alloc['initialAllocation'].append(temp_dict)

            else:
                # Senao, utilizará um que sobrar
                alloc_missing.append(temp_dict)

        spare_nodes += list(comms)

    for remaining in alloc_missing:
        # Atribui um dos nós sem recursos
        remaining['id_resource'] = spare_nodes[0]
        spare_nodes.append(spare_nodes.pop(0))
        alloc['initialAllocation'].append(remaining)

    with open('data/allocDefinition.json', 'w') as f:
        json.dump(alloc, f)
