> [!NOTE]
> There is an enhanced version of the simulator available called **YAIFS**. 
> It features several improvements and a unified API with full compatibility with YAFS.
> Check it out at: [YAIFS](https://github.com/acsicuib/YAIFS)

![YAFS logo](https://github.com/acsicuib/YAFS/raw/master/docs/_static/yafs_logo.png)

YAFS (Yet Another Fog Simulator) is a Python-based simulator for architectures such as [Fog Computing](https://en.wikipedia.org/wiki/Fog_computing) ecosystems. It supports multiple types of analysis related to resource placement, deployment cost, network design, and more. [IoT environments](https://en.wikipedia.org/wiki/Internet_of_things) are the most common example of this type of architecture. YAFS is published in [IEEE](https://ieeexplore.ieee.org/document/8758823).


The **highlighted features** of YAFS are:
* **Dynamic topology:** entities and network links can be created or removed during the simulation.
* **Dynamic creation of message sources:** sensors can generate messages from different access points during the simulation.
* **Placement and orchestration during runtime:** the **placement allocation algorithm** and **orchestration algorithm**, which are extended by the user, can be executed while the simulation is running.
* **Network topology based on Complex Network theory:** the **topology of the network** is based on [Complex Network theory](https://en.wikipedia.org/wiki/Complex_network). Thus, algorithms can obtain more meaningful indicators from topological features.
* **Simple, analysis-friendly output:** **results** are stored in a raw format in a NoSQL database. The simpler the format, the easier it is to perform any type of statistical analysis.


YAFS is released under the MIT License. However, we would like to know in which projects or publications you have used or mentioned YAFS.

**Please consider using the following citation when you use YAFS**:

```bash
    Isaac Lera, Carlos Guerrero and Carlos Juiz. YAFS: A simulator for IoT scenarios in fog computing. IEEE Access. Vol. 7(1), pages 91745-91758,
    10.1109/ACCESS.2019.2927895, Jul 10 2019. 
```

Bibtex:
```
    @ARTICLE{8758823,
    author={I. {Lera} and C. {Guerrero} and C. {Juiz}},
    journal={IEEE Access},
    title={YAFS: A Simulator for IoT Scenarios in Fog Computing},
    year={2019},
    volume={7},
    number={},
    pages={91745-91758},
    keywords={Relays;Large scale integration;Wireless communication;OFDM;Interference cancellation;Channel estimation;Real-time systems;Complex networks;fog computing;Internet of Things;simulator},
    doi={10.1109/ACCESS.2019.2927895},
    ISSN={2169-3536},
    month={},
    }
```

Resources
---------

The YAFS tutorial (`https://yafs.readthedocs.io/en/latest/introduction/index.html`)
and user guide (`https://www.slideshare.net/wisaaco/yet-another-fog-simulator-yafs-user-guide`) are a good starting
point. You can also try out some of the examples (`https://yafs.readthedocs.io/en/latest/examples/index.html`) shipped with
YAFS, but in any case you should understand the main concepts of Cloud Computing and related architectures in order to design and model your own system.


Installation
------------

YAFS 3.1 (this branch) supports Python 3.12 (last compatibility check on Python 3.12).  YAFS uses [uv](https://docs.astral.sh/uv/) as python project manager.

1. Clone the project in your local folder:

```bash
git clone --branch YAFS3.1 https://github.com/acsicuib/YAFS
```

2. Install dependencies:

```bash
cd YAFS/
uv sync
uv pip install -e .
```


Getting started
---------------

To run tutorial or example projects from a terminal, execute the following commands (please update the paths according to your system). Alternatively, you can use a Python editor such as PyCharm, Visual Studio Code, etc.

```bash
uv run tutorial_scenarios/01_basicExample/main.py
```

Or, in case of subfolder dependencies such as `data/`, run:

```bash
cd tutorial_scenarios/02_serviceMovement
uv run main.py
```

The available tutorial scenarios are:
```
tutorial_scenarios
├── 01_basicExample
├── 02_serviceMovement
├── 03_topologyChanges
└── 04_userMovement
```

More complex examples or published projects are in the **examples** folder:
Note: these have been tested with Python 3.10.8.
```
examples
├── ConquestService                 # tested. Published at [6]
├── DynamicAllocation               # tested. Published at [1]
├── DynamicFailuresOnNodes          # tested. Published at [1]
├── DynamicWorkload                 # tested. Published at [1]
├── FogCentrality                   # works on YAFS2 (aka. master branch). Published at [2]
├── FogTorchPI-Integration          # works on YAFS2. An integration with: https://github.com/di-unipi-socc/FogTorchPI
├── MCDA                            # works on YAFS2. Published at [5]
├── MapReduceModel                  # works on YAFS2. Published at [3]
├── PartitionILPPlacement           # works on YAFS2. Published at [4]
├── RuleBasedDistributedModel       # works on YAFS2. Project to analyze the feasibility of a more complex proposal: [7,8]
├── TestJsons                       # works on YAFS2. A basic project to check JSON formats. NM.
├── Tutorial                        # works on YAFS2. iFogSim examples but in YAFS [1]
├── Tutorial_JSONModelling          # works on YAFS2. Examples in yafs' readthedocs.
├── VRGameFog-IFogSim-WL            # works on YAFS2. EGG_GAME by IFogSim implementation [1]
└── mobileTutorial                  # works on YAFS2. An unpublished extension to incorporate general functions on dynamic connections.
```


The [YAFS tutorial](https://yafs.readthedocs.io/en/latest/introduction/index.html) is a good starting point.
You can also try out some of the [examples](https://yafs.readthedocs.io/en/latest/examples/index.html) shipped with
YAFS, but in any case you should understand the main concepts of Cloud Computing and related architectures to design and model your own system.


Graph animations
----------------
Because you can implement events (custom strategies), you can generate plots of your network at each event. Thus, you can store PNG files and, at the end of your simulation, generate a video by combining all of them using the `ffmpeg` command.

You can find some examples in `src/examples`: `DynamicWorkload`, `ConquestService`, and `mobileTutorial`. From the `DynamicWorkload` and `ConquestService` folders, we have generated the following animations:

```
ffmpeg -r 1 -i net_%03d.png -c:v libx264 -vf fps=1 -pix_fmt yuv420p out.mp4
ffmpeg -i out.mp4 -pix_fmt rgb24  out.gif

```

<img src="https://github.com/acsicuib/YAFS/raw/master/src/examples/DynamicWorkload/figure/out.gif" width="350" height="350"/></a>

<img src="https://github.com/acsicuib/YAFS/raw/master/src/examples/ConquestService/out.gif" width="350" height="350"/></a>

<img src="https://github.com/acsicuib/YAFS/raw/master/src/examples/mobileTutorial/exp/results_20190326/out.gif" width="350" height="350"/></a>

<img src="https://github.com/acsicuib/YAFS/raw/master/src/examples/mobileTutorial/exp/results_20190326/out2.gif" width="350" height="350"/></a>

- From "[Declarative Application Management in the Fog: A Bacteria-Inspired Decentralised Approach" project](https://github.com/acsicuib/MARIO/tree/MarioII) (click to play in Youtube): 
[![Watch the video](https://img.youtube.com/vi/Vu9u3DSQdY4/hqdefault.jpg)](https://youtu.be/Vu9u3DSQdY4)

Documentation and Help
----------------------

The [documentation](https://yafs.readthedocs.io/en/latest/) contains a [tutorial](https://yafs.readthedocs.io/en/latest/introduction/index.html), an [architecture overview](https://yafs.readthedocs.io/en/latest/architecture/index.html) explaining key
concepts, several [examples](https://yafs.readthedocs.io/en/latest/examples/index.html), and the [API reference](https://yafs.readthedocs.io/en/latest/api_reference/index.html).


For more help, contact the authors or explore the [source code](https://github.com/acsicuib/YAFS).

Changelog
-----------
- Dec 15, 2025: YAFS 3.1 is an extensively refactored version, with many improvements and updated compatibility with current libraries.
- Jun 27, 2022: Fixed bugs in older examples and tested the project with Python 3.9.7. Improved examples and added code to analyze some basic results.
- Sep 12, 2019: Fixed bugs. All projects now work with the attributes defined in the `graph` variable (topology class), using the NetworkX library to manage the attributes.
- May 23, 2019: Included new improvements. Notably, workloads/users and mobile endpoints can be represented through *gpx traces* (geopositional libraries are required).
- Jun 25, 2018: Bug fix. The `DES.src` metric of the CSV results is fixed and correctly identifies the DES process that sends each message.
- Jun 20, 2018: Messages from sources now have a unique identifier that is copied in all transmissions, allowing each application invocation to be traced.

Acknowledgment
--------------

- The authors acknowledge financial support through grant project ORDCOT, number TIN2017-88547-P (AEI/FEDER, UE).
- Thanks to the small community of contributors who have been improving the code and providing new suggestions over the years.


REFERENCES
----------

YAFS is used in the following projects:

* [1] Isaac Lera, Carlos Guerrero, Carlos Juiz. YAFS: A simulator for IoT scenarios in fog computing. IEEE Access. Vol. 7(1), pages 91745-91758, 10.1109/ACCESS.2019.2927895, Jul 10 2019.
* [2] Isaac Lera, Carlos Guerrero, Carlos Juiz. Comparing centrality indices for network usage optimization of data placement policies in fog devices. FMEC 2018: 115-122
* [3]  Carlos Guerrero, Isaac Lera, Carlos Juiz. Migration-Aware Genetic Optimization for MapReduce Scheduling and Replica Placement in Hadoop. Journal of Grid Computing 2018. 10.1007/s10723-018-9432-8
* [4] Isaac Lera, Carlos Guerrero, Carlos Juiz. Availability-aware Service Placement Policy in Fog Computing Based on Graph Partitions. IEEE Internet of Things Journal 2019. 10.1109/JIOT.2018.2889511
* [5] Isaac Lera, Carlos Guerrero, Carlos Juiz. Analysing the Applicability of a Multi-Criteria Decision Method in Fog Computing
Placement Problem. FMEC 2019
* [6] Isaac Lera, Carlos Guerrero, and Carlos Juiz. Algoritmo descentralizado para la asignación de servicios en arquitecturas de Fog Computing basado en un proceso expansivo de migración de instancias. Jornadas Sarteco, 2019. 
* [7] Forti, S, Lera, I, Guerrero, C, Brogi, A. Osmotic management of distributed complex systems: A declarative decentralised approach. J Softw Evol Proc. 2021;e2405. doi:10.1002/smr.2405
* [8] Brogi, A., Forti, S., Guerrero, C. et al. Declarative Application Management in the Fog. J Grid Computing 19, 45 (2021). https://doi.org/10.1007/s10723-021-09582-y



Please [send us your reference so we can publish it](mailto:isaac.lera@uib.es)! And of course, feel free to add your references or works using YAFS! 
