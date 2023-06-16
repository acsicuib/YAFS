import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd


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

def plot_app_path(folder_results, application, t, pos=None):
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
    print(type(path))

    highlighted_edges = []
    labels = {}
    for index, hops in path.iterrows():
        highlighted_edges.append([hops.src, hops.dst])
        labels[(hops.src, hops.dst)] = "{}\nBW={}\tPR={}".format(hops.message, t.get_edge((hops.src, hops.dst))['BW'],
                                                                 t.get_edge((hops.src, hops.dst))['PR'])
        print("{}\nBW={}\tPR={}".format(hops.message, t.get_edge((hops.src, hops.dst))['BW'],
                                                                 t.get_edge((hops.src, hops.dst))['PR']))
    print(highlighted_edges)

    x_min, x_max = plt.xlim()
    y_min, y_max = plt.ylim()

    #TODO: convert the time to secondss -> use node attribute with insetructions per second
    total_time = path2.at[path2.index[-1], 'time_out'] - path2.at[0, 'time_in']
    plt.text(x_max-0.02, y_min+0.02, total_time, fontsize=12, ha='right', va='bottom', transform=plt.gca().transAxes)
    total_time = "total time = {:.2f}".format(total_time)
    print(total_time)

    nx.draw_networkx(t.G, pos, arrows=True)
    nx.draw_networkx_edges(t.G, pos, edge_color='black')
    # # Draw the highlighted edges in red
    nx.draw_networkx_edges(t.G, pos, edgelist=highlighted_edges, edge_color='red', arrows=True, arrowstyle='->')
    nx.draw_networkx_edge_labels(t.G, pos, edge_labels=labels, label_pos=0.5, font_size=8, font_family='Arial')

    plt.show()



# plot_app_path("./results/", 0, t, pos)
