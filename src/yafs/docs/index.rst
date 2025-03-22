.. only:: html

    .. figure:: _static/yafs_logo.png
        :align: center

        Yet Another Fog Simulator for Python


.. only:: html

    .. sidebar:: Documentation

        :ref:`Tutorial <intro>`
            learn the basics

        :ref:`Topical Guides <architecture>`
            guides covering various features of this architecture

        :ref:`Examples <examples>`
            usage examples

        :ref:`API Reference <api_reference>`
            detailed description of YAFS' API

        :ref:`About <about>`
            authors, history, license, citing, ...

========
OVERVIEW
========

YAFS (Yet Another Fog Simulator) is a simulation library for Cloud, Edge or `Fog Computing <https://en.wikipedia.org/wiki/Fog_computing>`_ ecosystems enabling several analysis regarding with the allocation of resources, billing management, network design, and so on.

It is a lightweight, robust and highly configurable simulator based on Simpy library (discrete event simulator) and Complex Network theory. YAFS is set by a reduced number of classes (only 7) thus we believe the learning curve is quite low compared
to other similar simulators. This number of classes offer an absolute control to the user for the implementation of several customized policies and environment characteristics. We highlight the following points:

* **Topology** The infrastructure is modelled using `Complex Networks <https://en.wikipedia.org/wiki/Complex_network>`_ theory. Any element (network devices, cloud abstractions, software modules, workloads, etc.) are represented by nodes and the links represents the possible network connection between them. In addition, Complex Networks theory provides useful topological features in order to control the deployment of services, the allocation of resources, network design considerations and other customized user policies.
* **Dynamic control** All process that the user can extend can be define dynamically, such as topology (i.e. new nodes, links failures, etc.), allocation policies, orchestration, etc.
* **Request evolution**  Service requests in FOG environments is not always reduced to the same access points along the whole simulation.  Requests can be generated from any point of the network following a temporary distribution.
* **Placement algorithm** Yet another classical module that decides how to assign module applications to the topology.
* **Selection algorithm** In a network, routing can be controlled by network devices but with new Fog applications the applications can controlled these messages, it depends on the user abstraction level. It offers new analytical models for the adaptation of traffic.
* **Customized distribution** User can generate events to control policies or whatever action in the simulator using customized distributions as for example a simple array of timestamps to deploy software modules.

YAFS gathers the main events in a raw format. There is not hidden variables or *stranger things* where this data is stored. This data can be accessed from any point of the simulator so any module has access to the stats.

The documentation contains a :ref:`tutorial <intro>`, :ref:`architecture details <architecture>` explaining key concepts, a number of :ref:`examples <examples>` and the :ref:`API reference <api_reference>`.


YAFS is released under the MIT License.

Installation
^^^^^^^^^^^^

YAFS requires Python 2.7 (Python 3.6 or above is not supported)

You can download and install YAFS manually:

.. code-block:: bash

    git clone https://github.com/acsicuib/YAFS



Cite this work
^^^^^^^^^^^^^^

Please, consider including this reference in your works or publications:

.. code-block:: python

    Isaac Lera, Carlos Guerrero, Carlos Juiz. YAFS: A simulator for IoT scenarios in fog computing. IEEE Access. Vol. 7(1), pages 91745-91758,
    10.1109/ACCESS.2019.2927895, Jul 10 2019.

    https://ieeexplore.ieee.org/document/8758823

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


Please let it knows us if you use this project in your research. We will cite them. Thank you

You can find other related works developed with YAFS in the readme of YAFS git hub repository.

===========
Acknowledge
===========
Authors acknowledge financial support through project ORD-CoT (TIN2017-88547-P MINECO, SPAIN).