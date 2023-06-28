import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
from collections import Counter

# from pathlib import Path


# folder_results = Path("../../tutorial_scenarios/Playground/results/")
# folder_results.mkdir(parents=True, exist_ok=True)
# folder_results = str(folder_results)+"/"


def plot_paths_taken(folder_results):
    dfl = pd.read_csv(folder_results + "sim_trace" + "_link.csv")

    apps_deployed = np.unique(dfl.app)

    pallet = np.linspace(0, 100, len(apps_deployed))

    fig, ax = plt.subplots()

    for en, a in enumerate(apps_deployed):
        ax.scatter(np.array(dfl[dfl.app == a].src), np.array(dfl[dfl.app == a].dst),
                   c=(pallet[en] * np.ones(len(dfl[dfl.app == a].src))), cmap='plasma', vmin=0, vmax=100, marker='x',
                   label=f'App: {a}')

    ax.set_xlabel('Source nodes')
    ax.set_ylabel('Destiny nodes')
    ax.set_title('Simulation hops')
    ax.legend()
    plt.show()


def draw_topology(t, pos):
    # plt.figure(figsize=(7, 3))
    # nx.draw_networkx(t.G, pos, with_labels=True)
    nx.draw_networkx(t.G, pos, arrows=True)
    # nx.draw_networkx_edge_labels(t.G, pos, alpha=0.5, font_size=5, verticalalignment="top" )
    plt.show()

def plot_app_path(folder_results, application, t, pos=None, placement=None):
    if pos is None:
        # random.seed(38)
        pos = nx.spring_layout(t.G, seed=38)

    plt.figure(figsize=(10, 10))
    sml = pd.read_csv(folder_results + "sim_trace_link.csv")
    sm = pd.read_csv(folder_results + "sim_trace.csv")

    path = sml[sml.app == application]
    path = path[path.at[0, 'id'] == path.id]
    # path = sml[(sml.id == 1) & (sml.app == application)]

    path2 = sm[sm.app == application]
    path2 = path2[path2.at[0, 'id'] == path2.id]
    # path2 = sm[(sm.id == 1) & (sm.app == application)]
    # print(type(path))

    highlighted_edges = []
    labels = {}
    for index, hops in path.iterrows():
        highlighted_edges.append([hops.src, hops.dst])
        labels[(hops.src, hops.dst)] = "{}\nBW={}\tPR={}".format(hops.message, t.get_edge((hops.src, hops.dst))['BW'],
                                                                 t.get_edge((hops.src, hops.dst))['PR'])
        # print("{}\nBW={}\tPR={}".format(hops.message, t.get_edge((hops.src, hops.dst))['BW'],
        #                                                          t.get_edge((hops.src, hops.dst))['PR']))
    # print(highlighted_edges)

    x_min, x_max = plt.xlim()
    y_min, y_max = plt.ylim()

    #TODO: convert the time to secondss -> use node attribute with instructions per second
    total_time = path2.at[path2.index[-1], 'time_out'] - path2.at[0, 'time_in']
    plt.text(x_max-0.02, y_min+0.02, total_time, fontsize=12, ha='right', va='bottom', transform=plt.gca().transAxes)
    total_time = "total time = {:.2f}".format(total_time)
    print(total_time)

    if placement is not None:
        node_labels = dict()

        for dt in placement.data['initialAllocation']:
            if int(dt['id_resource']) not in node_labels:
                node_labels[int(dt['id_resource'])] = ([dt['module_name']], [str(dt['app'])])

            else:
                node_labels[int(dt['id_resource'])][0].append(dt['module_name'])
                node_labels[int(dt['id_resource'])][1].append(str(dt['app']))

        for lbl in node_labels:
            node_labels[
                lbl] = f"\n\n\n\nModule: {', '.join(node_labels[lbl][0])}\nApp: {', '.join(node_labels[lbl][1])}"

        nx.draw_networkx_labels(t.G, pos, labels=node_labels, font_size=8)
        nx.draw_networkx(t.G, pos, arrows=True)
    else:
        nx.draw_networkx(t.G, pos, arrows=True)


    nx.draw_networkx_edges(t.G, pos, edge_color='black')
    # # Draw the highlighted edges in red
    nx.draw_networkx_edges(t.G, pos, edgelist=highlighted_edges, edge_color='red', arrows=True, arrowstyle='->')
    nx.draw_networkx_edge_labels(t.G, pos, edge_labels=labels, label_pos=0.5, font_size=8, font_family='Arial')

    plt.show()



def modules_per_node(placement, topology):
    nodes = dict()
    for n in topology.get_nodes():
        nodes[int(n)] = 0

    for dt in placement.data['initialAllocation']:
        # if int(dt['id_resource']) not in nodes:
        #     nodes[int(dt['id_resource'])] = 1
        # else:
        nodes[int(dt['id_resource'])] += 1

    plt.bar(nodes.keys(), nodes.values())
    plt.yticks(range(0, int(max(nodes.values())) + 1))
    plt.xlabel('nodes')
    plt.ylabel('number of modules allocated')
    plt.show()
    # print(nodes)

# def messages_per_node():

# plot_app_path("./results/", 0, t, pos)


def plot_messages_node(folder_results):
    df = pd.read_csv(folder_results + "sim_trace_link.csv")
    res_used = df['dst']

    src_nodes = df.drop_duplicates(subset='id')
    src_nodes = src_nodes['src']

    nodes_used = pd.concat([src_nodes, res_used], axis=0)

    values = Counter(nodes_used)
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