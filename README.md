
![YAFS logo](https://github.com/acsicuib/YAFS/raw/master/docs/_static/yafs_logo.png)

YAFS (Yet Another Fog Simulator) is a simulator tool based on Python of architectures such as: [Fog Computing](https://en.wikipedia.org/wiki/Fog_computing) ecosystems for several analysis regarding with the placement of resources, cost deployment, network design, ... [IoT environments](https://en.wikipedia.org/wiki/Internet_of_things) are the most evident fact of this type of architecture. YAFS is published at [IEEE](https://ieeexplore.ieee.org/document/8758823).


The **highlights** points of YAFS are:
* **Dynamic topology:** entities and network links can be created or removed along the simulation.
* **Dynamic creation of messages sources:** sensors can generate messages from different point access along the simulation.
* And for hence, the **placement allocation algorithm** and **the orchestration algorithm,** that are extended by the user, can run along the simulation.
* The **topology of the network** is based on [Complex Network theory](https://en.wikipedia.org/wiki/Complex_network). Thus, the algorithms can obtain more valuable indicators from topological features.
* The **results** are stored in a raw format in a nosql database. The simpler the format, the easier it is to perform any type of statistics.


YAFS is released under the MIT License. However, we would like to know in which project or publication have you used or mentioned YAFS.

**Please consider use this cite when you use YAFS**:

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

YAFS tutorial (https://yafs.readthedocs.io/en/latest/introduction/index.html)
and user guide (https://www.slideshare.net/wisaaco/yet-another-fog-simulator-yafs-user-guide) are a good starting
point for you. You can also try out some of the Examples (https://yafs.readthedocs.io/en/latest/examples/index.html) shipped with
YAFS but in any case you have to understand the main concepts of Cloud Computing and other related architectures to design and modelling your own model.


Installation
------------

YAFS3 (the branch) supports Python 3.6+ (last compability check on Python 3.9.7)

1. Clone the project in your local folder:

```bash
git clone --branch YAFS3 https://github.com/acsicuib/YAFS
```

2. Install dependencies. 

```bash
cd YAFS/
pip install -r requirements.txt
```


Getting started
---------------

To run tutorial or example projects from a terminal, run the following code (please update the paths according with your system). Alternativaly, you can use a python editor such as: Pycharm, Visual Studio, etc.

```bash
export PYTHONPATH=$PYTHONPATH:~/YAFS/src/
cd YAFS/tutorial_scenarios/01_basicExample
python main.py
```

The tutorial scenarios are in the folder:
```
tutorial_scenarios
├── 01_basicExample
├── 02_serviceMovement
├── 03_topologyChanges
└── 04_userMovement
```

More complex examples or published projects are in the folder **examples**:
Note: they are working with python 3.10.8
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


The [YAFS tutorial](https://yafs.readthedocs.io/en/latest/introduction/index.html) is a good starting
point for you. You can also try out some of the [Examples](https://yafs.readthedocs.io/en/latest/examples/index.html) shipped with
YAFS but in any case you have to understand the main concepts of Cloud Computing and other related architectures to design and modelling your own model.


Graph animations
----------------
As you can implement events (custom strategies), you can generate plots of your network in each event. Thus, you can store png files and at the end of your simulation, you generate a video with the combination all of them using *ffmpeg* command.

You can find some examples in the following *src/examples*: DynamicWorkloads, ConquestService, and mobileTutorial. From *DynamicWorkload* folder and *ConquestService*, we have generate the following animations:

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

The [documentation](https://yafs.readthedocs.io/en/latest/) contains a [tutorial](https://yafs.readthedocs.io/en/latest/introduction/index.html), the [architecture design](https://yafs.readthedocs.io/en/latest/architecture/index.html) explaining key
concepts, a number of [examples](https://yafs.readthedocs.io/en/latest/examples/index.html) and the [API reference](https://yafs.readthedocs.io/en/latest/api_reference/index.html).


For more help, contact with the authors or You must dig through the [source code](https://github.com/acsicuib/YAFS)

Changelog
-----------
- jun / 27 / 2022 Fixing bugs in old examples and tested the project in python 3.9.7 version. Improved examples and add code that analyse some basic results.
- sep. / 12 / 2019 Fixing bugs - All projects work with the attributes defined in the graph var (topology class) using NX library to manage the attributes.
- may / 23 / 2019 New improvements are included. Highlight that workloads/users and mobile endpoints can be represented through *gpx traces*. Geopositional libraries are required
- june / 25 / 2018 Bug Fixed - The DES.src metric of the CSV results is fixed. Identifies the DES-process who sends the message
- june / 20 / 2018 Messages from sources have an unique identifier that is copied in all the transmissions. We can trace each application invocation.

Acknowledgment
--------------

- Authors acknowledge financial support through grant project ORDCOT with number TIN2017-88547-P (AEI/FEDER, UE)
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



Please, [send us your reference to publish it](mailto:isaac.lera@uib.es)! and of course, feel free to add your references or works using YAFS! 
