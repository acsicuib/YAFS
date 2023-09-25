import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import networkx as nx
from math import ceil, floor
from collections import Counter
# from pathlib import Path


# folder_results = Path("../../tutorial_scenarios/Playground/results/")
# folder_results.mkdir(parents=True, exist_ok=True)
# folder_results = str(folder_results)+"/"

# colors
import matplotlib.colors as mcolors
import random


# generate list of n different colors
def generate_colors(n):
    colors = list(mcolors.CSS4_COLORS.keys())

    # Randomly select n colors
    selected_colors = random.sample(colors, n)
    return selected_colors


def save_plot(plot_name):
    try:
        os.stat('data_analysis\\')
    except:
        os.mkdir('data_analysis\\')

    plt.savefig('data_analysis\\' + plot_name)


def plot_paths_taken(folder_results, plot_name=None):
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
    ax.legend()

    if plot_name is None:
        ax.set_title(f'Simulation hops')

    else:
        plot_name += '_sim_hops'
        ax.set_title(plot_name)
        save_plot(plot_name)

    plt.show()


def plot_app_path(folder_results, application, t, pos=None, placement=None, plot_name=None):
    if pos is None:
        pos = nx.spring_layout(t.G)

    plt.figure(figsize=(10, 5))
    sml = pd.read_csv(folder_results + "sim_trace_temp_link.csv")
    sm = pd.read_csv(folder_results + "sim_trace_temp.csv")

    path = sml[sml.app == application]

    path = path[path.id == min(path.id)]

    # path = path[sml.at[0, 'id'] == sml.id]            # << antigo
    # Na versao anterior só funcionava se o link com id 1 fosse o da aplicação que se quer ver

    path2 = sm[sm.app == application]
    path2 = sm[sm.at[0, 'id'] == sm.id]
    # path2 = sm[(sm.id == 1) & (sm.app == application)]
    print(type(path))

    highlighted_edges = []
    labels = {}
    for index, hops in path.iterrows():
        highlighted_edges.append([hops.src, hops.dst])
        labels[(hops.src, hops.dst)] = "{}\nBW={}\tPR={}".format(hops.message, t.get_edge((hops.src, hops.dst))['BW'],
                                                                 t.get_edge((hops.src, hops.dst))['PR'])
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

    if plot_name is not None:
        save_plot(plot_name + f'_{application}_path')

    plt.show()


def plot_occurrences(folder_results, mode='module', plot_name=None):
    df = pd.read_csv(folder_results + "sim_trace.csv")

    if mode == 'module':
        res_used = df.module
    elif mode == 'node':
        res_used = df['TOPO.src'] + df['TOPO.dst']
    elif mode == 'node_src':
        res_used = df['TOPO.src']
    else:  # elif mode == 'node_dst':
        res_used = df['TOPO.dst']

    unique_values, occurrence_count = np.unique(res_used, return_counts=True)

    ax = plt.subplot()

    plt.bar(unique_values, occurrence_count)

    ax.set_xlabel(mode.title())
    ax.set_ylabel('Occurrences')

    if plot_name is None:
        ax.set_title(f'Times a {mode.title()} is used')

    else:
        plot_name += '_occur'
        ax.set_title(plot_name)
        save_plot(plot_name)

    plt.show()


def plot_latency(folder_results, plot_name=None):
    dfl = pd.read_csv(folder_results + "sim_trace_link.csv")

    apps_deployed = np.unique(dfl.app)

    app_lat = []

    for app_ in apps_deployed:
        app_lat.append(np.array(dfl[dfl.app == app_].latency))

    ax = plt.subplot()

    plt.boxplot(app_lat)
    plt.xticks(range(1, len(apps_deployed) + 1), apps_deployed)

    ax.set_xlabel(f'Apps')
    ax.set_ylabel('Latency')

    if plot_name is None:
        ax.set_title('Latency')

    else:
        plot_name += '_latency'
        ax.set_title(plot_name)
        save_plot(plot_name)

    plt.show()


def plot_avg_latency(folder_results, plot_name=None):
    dfl = pd.read_csv(folder_results + "sim_trace_link.csv")

    apps_deployed = np.unique(dfl.app)

    app_lat = []

    for app_ in apps_deployed:
        app_lat.append(np.average(np.array(dfl[dfl.app == app_].latency)))

    ax = plt.subplot()

    # plt.boxplot(app_lat)
    plt.bar(range(0, len(apps_deployed)), app_lat)
    plt.xticks(range(0, len(apps_deployed)), apps_deployed)

    ax.set_xlabel(f'Apps')
    ax.set_ylabel('Latency')

    if plot_name is None:
        ax.set_title('Average Latency')

    else:
        plot_name += '_avg_latency'
        ax.set_title(plot_name)
        save_plot(plot_name)
    plt.show()


def scatter_plot_app_latency_per_algorithm(folder_data_processing, algorithm_list):
    colors = ['red', 'green', 'blue', 'purple', 'orange']
    # dfl = pd.read_csv(folder_results + "algorithm1")
    i = 0
    mean = []
    labels = []
    for algorithm in algorithm_list:
        dfl = pd.read_csv(folder_data_processing + algorithm + "_sim_trace_link.csv")
        apps_deployed = np.unique(dfl.app)

        app_lat = []
        for app_ in apps_deployed:
            app_lat.append(np.average(np.array(dfl[dfl.app == app_].latency)))
        mean+=app_lat
        plt.scatter(range(len(app_lat)), app_lat, label=algorithm, c=colors[i], marker='o')
        labels.append(algorithm)
        i = (i + 1) % len(colors)
        ticks = range(len(app_lat))

    # media = sum(mean)/len(mean)
    plt.ylim(0, ((sum(mean)/len(mean))*1.5))
    plt.xticks(ticks)
    plt.xlabel(f'Apps')
    plt.ylabel('Latency')
    plt.title('Average App Latency per algorithm')
    plt.legend(labels, loc='upper right')
    save_plot('Average App Latency per algorithm')
    plt.show()



def plot_latency_per_placement_algorithm(folder_data_processing, algorithm_list):
    colors = ['red', 'green', 'blue', 'purple', 'orange']
    mean = []

    for algorithm in algorithm_list:
        dfl = pd.read_csv(folder_data_processing + algorithm + "_sim_trace_link.csv")
        apps_deployed = np.unique(dfl.app)

        app_lat = []
        for app_ in apps_deployed:
            app_lat.append(np.average(np.array(dfl[dfl.app == app_].latency)))
        mean.append(sum(app_lat) / len(app_lat))

    bars = plt.bar(algorithm_list, mean, color=colors)

    # media = sum(mean)/len(mean)
    plt.ylim(0, max(mean) * 1.1)
    # plt.xticks(ticks)
    plt.xlabel(f'Placement Algorithms')
    plt.ylabel('Latency')
    plt.title('Latency Per Placement Algorithm')
    # plt.legend(algorithm_list, loc='upper right')

    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, yval, round(yval, 2), va='bottom', ha='center')

    save_plot('barplot_latency_per_placement_algorithm')
    plt.show()

def boxplot_latency_per_placement_algorithm(folder_data_processing, algorithm_list):
    colors = ['red', 'green', 'blue', 'purple', 'orange']
    algorithm_latency = [[] for x in range(len(algorithm_list))]

    i = 0
    for algorithm in algorithm_list:
        dfl = pd.read_csv(folder_data_processing + algorithm + "_sim_trace_link.csv")
        apps_deployed = np.unique(dfl.app)

        for app_ in apps_deployed:
            algorithm_latency[i] += list(np.array(dfl[dfl.app == app_].latency))
        i+=1

    plt.boxplot(algorithm_latency, labels=algorithm_list, showfliers=False)

    plt.xlabel(f'Placement Algorithms')
    plt.ylabel('Latency')
    plt.title('Latency Per Placement Algorithm')

    save_plot('boxplot_latency_per_placement_algorithm')
    plt.show()

def plot_nodes_per_time_window(folder_results, t, n_wind=10, graph_type=None, show_values=False, plot_name=None):
    df = pd.read_csv(folder_results + "sim_trace.csv")

    max_time = max(df['time_out'])
    window_sz = ceil(max_time / n_wind)

    nodes_per_window = []
    window_rate = []
    n_nodes = len(t.G.nodes)

    for i in range(n_wind):
        add = np.unique(
            np.concatenate((df[(df['time_out'] < ((i + 1) * window_sz)) & (df['time_out'] > i * window_sz)]['TOPO.src'],
                            df[(df['time_out'] < ((i + 1) * window_sz)) & (df['time_out'] > i * window_sz)][
                                'TOPO.dst'])))
        nodes_per_window.append(add)

        window_rate.append(len(nodes_per_window[i]) * 100 / n_nodes)

    ax = plt.subplot()

    plt.ylim(0, 100)

    x_min, x_max = plt.xlim()
    y_min, y_max = plt.ylim()
    plt.text(x_max - 0.02, y_min + 0.02, f'# Topology Nodes: {n_nodes}', fontsize=10, ha='right', va='bottom',
             transform=plt.gca().transAxes)

    if graph_type is None:
        plt.plot(range(len(window_rate)), window_rate)
        plt.scatter(range(len(window_rate)), window_rate, marker='x')
    elif graph_type == 'bar':
        plt.bar(range(len(window_rate)), window_rate)

    if show_values:
        for enum, rate in enumerate(window_rate):
            plt.text(enum, rate, f'{int(floor((rate * n_nodes) / 100))}')

    ax.set_xlabel(f'Window')
    ax.set_ylabel('% Used Nodes')

    if plot_name is not None:
        save_plot(plot_name)
    plt.show()


def modules_per_node(placement, topology, plot_name=None):
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

    ax = plt.subplot()

    if plot_name is None:
        ax.set_title('Modules per node')
    else:
        plot_name += '_mods_per_nds'
        ax.set_title(plot_name)
        save_plot(plot_name)

    plt.show()

#
# def plot_modules_per_node_per_algorithm(algorithm_list, modules_per_node):
#     # colors = ['red', 'green', 'blue', 'purple', 'orange']
#     # dfl = pd.read_csv(folder_results + "algorithm1")
#
#     i = 0
#     ymax=0
#     mean = dict()
#     labels = []
#     for algorithm in algorithm_list:
#
#         mean[algorithm] = sum(modules_per_node[algorithm].values())/len(modules_per_node[algorithm])
#         labels.append(algorithm)
#         ymax = max(ymax, int(max(modules_per_node[algorithm].values())) + 1)
#         # i = (i + 1) % len(colors)
#
#     plt.bar(mean.keys(), mean.values())
#     # plt.scatter(range(len(app_lat)), app_lat, label=algorithm, c=colors[i], marker='o')
#
#     # plt.yticks(range(0, ymax + 1))
#     plt.xlabel('algorithm')
#     plt.ylabel('mean number of modules allocated per node')
#
#     plt.legend(labels, loc='upper right')
#     plt.show()

def plot_modules_per_node_per_algorithm(total_mods_per_node):
    data_list = [list(total_mods_per_node[algorithm]) for algorithm in total_mods_per_node.keys()]
    print(data_list)
    plt.boxplot(data_list, labels=total_mods_per_node.keys())
    plt.yticks(range(max(max(data) for data in data_list)+1))
    plt.xlabel('Algorithms')
    plt.ylabel('Modules per node')
    plt.title('Modules per node of each algorithm')
    save_plot('modules_per_node_of_each_algorithm')
    plt.show()

def plot_max_stress_per_algorithm(total_mods_per_node):
    colors = ['red', 'green', 'blue', 'purple', 'orange']
    data_list = [max(list(total_mods_per_node[algorithm])) for algorithm in total_mods_per_node.keys()]
    bars = plt.bar(total_mods_per_node.keys(), data_list, color=colors)
    plt.xlabel('Algorithms')
    plt.ylabel('Max modules per node')
    plt.title('Max modules in a node for each algorithm')
    save_plot('modules_per_node_of_each_algorithm')

    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, yval, round(yval, 2), va='bottom', ha='center')
    plt.show()

def plot_messages_node(folder_results, plot_name=None):
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

    if plot_name is None:
        ax.set_title('Number of Messages')
    else:
        plot_name += '_nr_msgs'
        ax.set_title(plot_name)
        save_plot(plot_name)
    plt.show()