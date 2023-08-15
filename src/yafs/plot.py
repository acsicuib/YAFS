from math import ceil

import matplotlib.pyplot as plt
from collections import Counter
import numpy as np
import pandas as pd
import networkx as nx
import json

# from pathlib import Path


# folder_results = Path("../../tutorial_scenarios/Playground/results/")
# folder_results.mkdir(parents=True, exist_ok=True)
# folder_results = str(folder_results)+"/"


def plot_paths_taken(folder_results):
    dfl = pd.read_csv(folder_results+"sim_trace"+"_link.csv")

    apps_deployed = np.unique(dfl.app)

    pallet = np.linspace(0, 100, len(apps_deployed))

    fig, ax = plt.subplots()

    for en, a in enumerate(apps_deployed):
        ax.scatter(np.array(dfl[dfl.app == a].src), np.array(dfl[dfl.app == a].dst),
                   c=(pallet[en]*np.ones(len(dfl[dfl.app == a].src))), cmap='plasma', vmin=0, vmax=100, marker='x',
                   label=f'App: {a}')

    ax.set_xlabel('Source nodes')
    ax.set_ylabel('Destiny nodes')
    ax.set_title('Simulation hops')
    ax.legend()
    plt.show()


def plot_app_path(folder_results, application, t, pos=None, graph_file='Routes_taken', placement=None):
    if pos is None:
        pos = nx.spring_layout(t.G)

    plt.figure(figsize=(10, 5))
    sml = pd.read_csv(folder_results + "sim_trace_link.csv")
    sm = pd.read_csv(folder_results + "sim_trace.csv")

    path = sml[sml.app == application]
    path = path[sml.at[0, 'id'] == sml.id]
    # path = sml[(sml.id == 1) & (sml.app == application)]

    path2 = sm[sm.app == application]
    path2 = sm[sm.at[0, 'id'] == sm.id]
    # path2 = sm[(sm.id == 1) & (sm.app == application)]
    print(type(path))

    highlighted_edges = []
    labels = {}
    for index, hops in path.iterrows():
        highlighted_edges.append([hops.src, hops.dst])
        labels[(hops.src, hops.dst)] = "{}\nBW={}\tPR={}".format( hops.message , t.get_edge((hops.src, hops.dst))['BW'], t.get_edge((hops.src, hops.dst))['PR'])
    print(highlighted_edges)

    print('tempo total')

    total_time = path2.at[path2.index[-1], 'time_out'] - path2.at[0, 'time_in']
    total_time = "total time = {:.2f}".format(total_time)
    plt.text(11, 0.3, total_time, fontsize=12, ha='right')

    if placement is not None:
        node_labels = dict()

        for dt in placement.data['initialAllocation']:
            if int(dt['id_resource']) not in node_labels:
                node_labels[int(dt['id_resource'])] = ([dt['module_name']], [str(dt['app'])])

            else:
                node_labels[int(dt['id_resource'])][0].append(dt['module_name'])
                node_labels[int(dt['id_resource'])][1].append(str(dt['app']))

        for lbl in node_labels:
            node_labels[lbl] = f"\n\n\n\nModule: {', '.join(node_labels[lbl][0])}\nApp: {', '.join(node_labels[lbl][1])}"

        nx.draw_networkx_labels(t.G, pos, labels=node_labels, font_size=8)
        nx.draw_networkx(t.G, pos, arrows=True)
    else:
        nx.draw_networkx(t.G, pos, arrows=True)
    nx.draw_networkx_edges(t.G, pos, edge_color='black')
    # # Draw the highlighted edges in red
    nx.draw_networkx_edges(t.G, pos, edgelist=highlighted_edges, edge_color='red', arrows=True, arrowstyle='->')
    nx.draw_networkx_edge_labels(t.G, pos, edge_labels=labels, label_pos=0.5, font_size=8, font_family='Arial')

    plt.savefig(graph_file+'.png')
    plt.show()


def plot_messages_node(folder_results):
    df = pd.read_csv(folder_results + "sim_trace_link.csv")
    res_used = df['dst']


    values = Counter(res_used)
    x = [i for i in range(max(values.keys()) + 1)]
    y = [values[i] if i in values.keys() else 0 for i in x]

    ax = plt.subplot()

    plt.bar(x, y)

    for i in range(len(x)):
        plt.text(i, y[i] + 0.005 * max(y), y[i], ha='center')

    ax.set_xlabel('Node')
    ax.set_xticks(x)
    ax.set_ylabel('Occurrences')
    ax.set_title('Number of Messages')
    plt.show()


def plot_occurrences(folder_results, mode='module'):
    df = pd.read_csv(folder_results + "sim_trace.csv")

    if mode == 'module':
        res_used = df.module
    elif mode == 'node':
        res_used = list(df['TOPO.dst'])
    elif mode == 'node_src':
        res_used = df['TOPO.src']
    else:                               # elif mode == 'node_dst':
        res_used = df['TOPO.dst']

    unique_values, occurrence_count = np.unique(res_used, return_counts=True)

    ax = plt.subplot()

    plt.bar(unique_values, occurrence_count)
    for i in range(len(unique_values)):
        plt.text(i, occurrence_count[i] + 0.005 * max(occurrence_count), occurrence_count[i], ha='center')

    ax.set_xlabel(mode.title())
    ax.set_ylabel('Occurrences')
    ax.set_title(f'Times a {mode.title()} is used')
    plt.show()


def plot_latency(folder_results):
    dfl = pd.read_csv(folder_results + "sim_trace_link.csv")

    apps_deployed = np.unique(dfl.app)

    app_lat = []

    for app_ in apps_deployed:
        app_lat.append(np.array(dfl[dfl.app == app_].latency))

    ax = plt.subplot()

    plt.boxplot(app_lat)
    plt.xticks(range(1, len(apps_deployed)+1), apps_deployed)

    ax.set_xlabel(f'Apps')
    ax.set_ylabel('Latency')
    plt.show()


def plot_nodes_per_time_window(folder_results, t, n_wind=30, graph_type=None):

    df = pd.read_csv(folder_results + "sim_trace.csv")

    max_time = max(df['time_out'])
    window_sz = ceil(max_time / n_wind)

    nodes_per_window = []
    window_rate = []
    n_nodes = len(t.G.nodes)

    for i in range(n_wind):
        # add = df[(df['time_out'] < ((i+1)*window_sz)) & (df['time_out'] > i*window_sz)][]
        add = np.unique(np.concatenate((df[(df['time_out'] < ((i+1)*window_sz)) & (df['time_out'] > i*window_sz)]['TOPO.src'],
                                        df[(df['time_out'] < ((i+1)*window_sz)) & (df['time_out'] > i*window_sz)]['TOPO.dst'])))
        nodes_per_window.append(add)

        window_rate.append(len(nodes_per_window[i]) * 100 / n_nodes)

    ax = plt.subplot()

    if graph_type is None:
        plt.plot(range(len(window_rate)), window_rate)
    elif graph_type == 'bar':
        plt.bar(range(len(window_rate)), window_rate)

    ax.set_xlabel(f'Window')
    ax.set_ylabel('% Used Nodes')
    plt.show()


def module_placement(alloc_def='data/allocDefinition.json'): #incluir ou não nós sem modulos?

    modules = json.load(open(alloc_def))['initialAllocation']

    nodes = dict()
    for module in modules:
        if module['id_resource'] not in nodes.keys():
            nodes[module['id_resource']] = 0

        nodes[module['id_resource']] += 1

    sorted_nodes = {k: v for k, v in sorted(nodes.items())}

    plt.bar(sorted_nodes.keys(), sorted_nodes.values())
    print(sorted_nodes.keys())
    plt.xlabel('Nodes')
    plt.ylabel('Number of Modules')
    plt.title('Initial Module Allocation')
    plt.show()



