
![YAFS logo](https://github.com/acsicuib/YAFS/raw/master/docs/_static/yafs_logo.png)

YAFS (Yet Another Fog Simulator) is designed to create simulations of [Fog Computing](https://en.wikipedia.org/wiki/Fog_computing) ecosystems for several analysis regarding with the placement of resources, cost deployment, network design, ... [IoT environments](https://en.wikipedia.org/wiki/Internet_of_things) are the most evident fact of this type of architecture.


The **highlights** of YAFS are:
* **Dinamyc topology:** entities and network links can be created or removed along the simulation.
* **Dinamyc creation of messages sources:** sensors can generate messages from different point access along the simulation.
* And for hence, the **placement allocation algorithm** and **the orchestration algorithm,** that are extended by the user, can run along the simulation.
* The **topology of the network** is based on [Complex Network theory](https://en.wikipedia.org/wiki/Complex_network). Thus, the algorithms can obtain more valuable indicators from topological features.
* The **results** are stored in a raw format in a nosql database. The simpler the format, the easier it is to perform any type of statistics.


YAFS is released under the MIT License.

**Please consider use this cite when you use YAFS**:

```bash
    PENDING
```



Installation
------------

YAFS requires Python 2.7, PyPy 2.0 or above.

You can install YAFS easily via [pip](<http://pypi.python.org/pypi/pip>):

```bash
    $ pip install -U yafs
```

You can also download and install YAFS manually:

```bash
    $ cd where/you/put/yafs/
    $ python setup.py install
```


Getting started
---------------

The [YAFS tutorial](https://yafs.readthedocs.io/en/latest/introduction/index.html) is a good starting
point for you. You can also try out some of the [Examples](https://yafs.readthedocs.io/en/latest/examples/index.html) shipped with
YAFS but in any case you have to understand the main concepts of Cloud Computing and other related architectures to design and modelling your own model.


Documentation and Help
----------------------

The [documentation](https://yafs.readthedocs.io/en/latest/) contains a [tutorial](https://yafs.readthedocs.io/en/latest/introduction/index.html), the [architecture design](https://yafs.readthedocs.io/en/latest/architecture/index.html) explaining key
concepts, a number of [examples](https://yafs.readthedocs.io/en/latest/examples/index.html) and the [API reference](https://yafs.readthedocs.io/en/latest/api_reference/index.html).


For more help, contact the YAFS [mailing
list](mailto:python-yafs@googlegroups.com). You must dig through the [source code](https://github.com/wisaaco/YAFS)



Similar libraries
-----------------

Some similar libraries are available in:

- [CloudSim](<http://www.cloudbus.org/cloudsim/>) (JAVA)



Acknowledge
-----------

Authors acknowledge financial support through project ORD-CoT (TIN2017-88547-P MINECO, SPAIN).