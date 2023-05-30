import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import networkx as nx

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


def plot_app_path(folder_results, application, t, pos=None, graph_file='Routes_taken'):
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

    nx.draw_networkx(t.G, pos, arrows=True)
    nx.draw_networkx_edges(t.G, pos, edge_color='black')
    # # Draw the highlighted edges in red
    nx.draw_networkx_edges(t.G, pos, edgelist=highlighted_edges, edge_color='red', arrows=True, arrowstyle='->')
    nx.draw_networkx_edge_labels(t.G, pos, edge_labels=labels, label_pos=0.5, font_size=8, font_family='Arial')

    plt.savefig(graph_file+'.png')
    plt.show()
