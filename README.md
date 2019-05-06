
![YAFS logo](https://github.com/acsicuib/YAFS/raw/master/docs/_static/yafs_logo.png)

YAFS (Yet Another Fog Simulator) is a simulator tool based on Python of architectures such as: [Fog Computing](https://en.wikipedia.org/wiki/Fog_computing) ecosystems for several analysis regarding with the placement of resources, cost deployment, network design, ... [IoT environments](https://en.wikipedia.org/wiki/Internet_of_things) are the most evident fact of this type of architecture.


The **highlights** points of YAFS are:
* **Dinamyc topology:** entities and network links can be created or removed along the simulation.
* **Dinamyc creation of messages sources:** sensors can generate messages from different point access along the simulation.
* And for hence, the **placement allocation algorithm** and **the orchestration algorithm,** that are extended by the user, can run along the simulation.
* The **topology of the network** is based on [Complex Network theory](https://en.wikipedia.org/wiki/Complex_network). Thus, the algorithms can obtain more valuable indicators from topological features.
* The **results** are stored in a raw format in a nosql database. The simpler the format, the easier it is to perform any type of statistics.


YAFS is released under the MIT License. However, we would like to know in which project or publication have you used or mentioned YAFS.

**Please consider use this cite when you use YAFS**:

```bash
    PENDING
```



Installation
------------

YAFS requires Python 2.7 (Python 3.6 or above is not supported)

1. Clone the project in your local folder:

```bash
    $ git clone https://github.com/acsicuib/YAFS

```

2. Install third-libraries:
```bash
    python setup.py install
```
or manually with easy_install or pip commands

YAFS requieres:
* Simpy
* Networkx
* Numpy
* Pandas
* tqdm

3. Perform an execution. In this case, we run src/examples/Tutorial/main1.py
- From console, you can run the next commands in folder /YAFS:
```bash
export PYTHONPATH=$PYTHONPATH:<your/path>YAFS/src/: src/examples/Tutorial/
python src/examples/Tutorial/main1.py 
```
- Or you can use editors such as Spyder or Pycharm (our choice)

 

Getting started
---------------

The [YAFS tutorial](https://yafs.readthedocs.io/en/latest/introduction/index.html) is a good starting
point for you. You can also try out some of the [Examples](https://yafs.readthedocs.io/en/latest/examples/index.html) shipped with
YAFS but in any case you have to understand the main concepts of Cloud Computing and other related architectures to design and modelling your own model.

To run some folder project you can create a simple bash script, with the following lines (please update the path according with your system) or you can use a python editor such as: Pycharm, Spyder, etc.

```bash
export PYTHONPATH=$PYTHONPATH:/<your path>/YAFS/src/:src/examples/Tutorial/
python src/examples/Tutorial/main1.py
```


A "SUPER" TIP: creating custom strategies
-----------------------------------------
We try to implement a wonderful tutorial but our time is limited. Thus, we can introduce this simple tip to create a custom strategy in the simulation.
This example defines a **dynamical** strategy since along the simulation can altered other strategies or even the topology, the applications, or whatever thing that you wish to modify.

For example, in your main.py function, you can declare a custom strategy with a deterministic distribution, and you can include the parameters that you want, i.e. the simulator class, and the routingPath.

```python
dStart = deterministicDistributionStartPoint(400, 100, name="Deterministic")
evol= CustomStrategy()
s.deploy_monitor("EvolutionOfServices",evol,dStart,**{"sim":s,"routing":selectorPath})
```

And finally you define the CustomStrategy() class:

```python
class CustomStrategy():

    def __call__(self, sim,routing):
        sim.print_debug_assignaments()
        routing.print_control_services()
        routing.my_var = False
        #or whatever you want

```
**Note**: the sim variable is type of core.py, it means, it contains all the variables and strategies: topology, placements, applications, etc.


Documentation and Help
----------------------

The [documentation](https://yafs.readthedocs.io/en/latest/) contains a [tutorial](https://yafs.readthedocs.io/en/latest/introduction/index.html), the [architecture design](https://yafs.readthedocs.io/en/latest/architecture/index.html) explaining key
concepts, a number of [examples](https://yafs.readthedocs.io/en/latest/examples/index.html) and the [API reference](https://yafs.readthedocs.io/en/latest/api_reference/index.html).


For more help, contact with the authors or You must dig through the [source code](https://github.com/acsicuib/YAFS)

Improvements
------------
- june / 25 / 2018 Bug Fixed - The DES.src metric of the CSV results is fixed. Identifies the DES-process who sends the message
- june / 20 / 2018 Messages from sources have an unique identifier that is copied in all the transmissions. We can trace each application invocation.

Acknowledgment
--------------

Authors acknowledge financial support through grant project ORDCOT with number TIN2017-88547-P (AEI/FEDER, UE)


REFERENCES
----------

YAFS is used in the following projects:

* Isaac Lera, Carlos Guerrero, Carlos Juiz. Comparing centrality indices for network usage optimization of data placement policies in fog devices. FMEC 2018: 115-122
* Carlos Guerrero, Isaac Lera, Carlos Juiz. Migration-Aware Genetic Optimization for MapReduce Scheduling and Replica Placement in Hadoop. Journal of Grid Computing 2018. 10.1007/s10723-018-9432-8
* Isaac Lera, Carlos Guerrero, Carlos Juiz. Availability-aware Service Placement Policy in Fog Computing Based on Graph Partitions. IEEE Internet of Things Journal 2019. 10.1109/JIOT.2018.2889511



Please, send us your reference to publish it!
