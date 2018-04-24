.. only:: html

    .. figure:: _static/yafs_logo.png
        :align: center

        Yet Another Fog Simulator for Python

        `PyPI <https://pypi.python.org/pypi/yafs>`_

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
The most simple way to install yafs library is using pip installer.

.. code-block:: python

   sudo pip install yafs



Cite this work
^^^^^^^^^^^^^^

Please, consider including this reference in your works or publications:

.. code-block:: python

    PENDING

.. code-block:: python

    PENDING

Please let it knows us if you use this project in your research. We will cite them. Thank you


===========
Acknowledge
===========
Authors acknowledge financial support through project ORD-CoT (TIN2017-88547-P MINECO, SPAIN).