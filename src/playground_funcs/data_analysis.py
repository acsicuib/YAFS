import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# from pathlib import Path


# folder_results = Path("../../tutorial_scenarios/Playground/results/")
# folder_results.mkdir(parents=True, exist_ok=True)
# folder_results = str(folder_results)+"/"


"""
def plot_paths_taken(folder_results):
    dfl = pd.read_csv(folder_results+"sim_trace"+"_link.csv")

    apps_deployed = np.unique(dfl.app)

    pallet = np.linspace(0, 100, len(apps_deployed))

    colors = np.array([])
    srcs = np.array([])
    dsts = np.array([])

    for en, a in enumerate(apps_deployed):
        colors = np.append(colors, (pallet[en]*np.ones(len(dfl[dfl.app == a].src))))
        srcs = np.append(srcs, np.array(dfl[dfl.app == a].src))
        dsts = np.append(dsts, np.array(dfl[dfl.app == a].dst))

    # print([dfl[dfl.app == 0].src])

    fig, ax = plt.subplots()
    ax.scatter(srcs, dsts, c=colors, cmap='magma', vmin=0, vmax=100, marker='x')
    

    plt.show()
"""


def plot_paths_taken(folder_results):
    dfl = pd.read_csv(folder_results+"sim_trace"+"_link.csv")

    apps_deployed = np.unique(dfl.app)

    pallet = np.linspace(0, 100, len(apps_deployed))

    colors = np.array([])
    srcs = np.array([])
    dsts = np.array([])

    fig, ax = plt.subplots()

    for en, a in enumerate(apps_deployed):
        # colors = np.append(colors, (pallet[en]*np.ones(len(dfl[dfl.app == a].src))))
        # srcs = np.append(srcs, np.array(dfl[dfl.app == a].src))
        # dsts = np.append(dsts, np.array(dfl[dfl.app == a].dst))

        ax.scatter(np.array(dfl[dfl.app == a].src), np.array(dfl[dfl.app == a].dst), c=(pallet[en]*np.ones(len(dfl[dfl.app == a].src))), cmap='magma', vmin=0, vmax=100, marker='x', label=f'App: {a}')

    ax.set_xlabel("Source nodes")
    ax.set_ylabel("Destiny nodes")
    ax.legend()
    plt.show()
