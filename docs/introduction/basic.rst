==============
Basic Concepts
==============

For running a simulation, you must define the following elements (we have used a basic example to explain them tutorial/main1.py) :

----------------
Network Topology
----------------

Firstly, the definition of a topology. A topology consists of a set of nodes and links. The nodes are elements of the network that serve as a link between other elements and have the ability to execute or host the application.

That is, a node has associated computing characteristics:

* **IPT** Instructions per simulation time. It is equivalent to IPS but it is the user how fix the unit time (i.e. seconds, milliseconds, etc.). Time simulation units is set by the user.

* **RAM** Memory available

* **COST** Cost per unit time

A link has associated these performance characteristics:

* **BW** Channel Bandwidth: in Bytes
* **PR** Channel Propagation speed
* The **Latency** is dynamically computed using: (Message.size.bits / BW) + PR)

A network can be created using a dictionary structure (or json file) or through some implemented algorithms from specific libraries compatibles with Networkx (see :ref:`architecture details <architecture>`).

In the definition of your devices, nodes,  you can include your custom tags.

.. code-block:: python

    from yafs.topology import Topology

    topology_json = {}
    topology_json["entity"] = []
    topology_json["link"] = []

    cloud_dev    = {"id": 0, "model": "cloud","mytag":"cloud", "IPT": 5000 * 10 ^ 6, "RAM": 40000,"COST": 3,"WATT":20.0}
    sensor_dev   = {"id": 1, "model": "sensor-device", "IPT": 100* 10 ^ 6, "RAM": 4000,"COST": 3,"WATT":40.0}
    actuator_dev = {"id": 2, "model": "actuator-device", "IPT": 100 * 10 ^ 6, "RAM": 4000,"COST": 3, "WATT": 40.0}

    link1 = {"s": 0, "d": 1, "BW": 1, "PR": 10}
    link2 = {"s": 0, "d": 2, "BW": 1, "PR": 1}

    topology_json["entity"].append(cloud_dev)
    topology_json["entity"].append(sensor_dev)
    topology_json["entity"].append(actuator_dev)
    topology_json["link"].append(link1)
    topology_json["link"].append(link2)

    t = Topology()
    t.load(topology_json)


-----------
Application
-----------
Secondly, the application follows the DDF model, in which an application is modeled as directed graph. The vertices of the directed acyclic graph (DAG) representing modules that perform processing on incoming data and edge denoting data dependencies among modules.

An application is set by a group of modules. A module can create messages (a pure source / sensor), a modul can consume messages (a pure sink  / actuator ) and other modules can do both tasks.

The dependencies among modules are defined through messages.


A **message** is the representation of a request between two modules. A message is set by an unique ID in the same application. It has a source and destiny module, a length of instructions, and a number of bytes. If the message arrive a pure sink this message does not require the last two attributes. In YAFS, it is possible to define *broadcast messages*.

.. code-block:: python

    m_a = Message("M.A", "Sensor", "ServiceA", instructions=20*10^6, bytes=1000)
    m_b = Message("M.B", "ServiceA", "Actuator", instructions=30*10^6, bytes=500)


We illustrate this example using *EEG_GAME application* [#f1]_ following the idea used in CloudSim [#f2]_ and other similar cloud simulators.

.. note::  User defines the distribution functions that modules use to create and send the different messages. In this example, the user defines: *fractional_selectivity* and *next_time_periodic*.

.. note::  In *sim.utils* package there are defined several distributions

.. code-block:: python

    import random
    from yafs.application import Application
    from yafs.application import Message


    def create_application():
        # APLICATION
        a = Application(name="SimpleCase")

        # (S) --> (ServiceA) --> (A)
        a.set_modules([{"Sensor":{"Type":Application.TYPE_SOURCE}},
                       {"ServiceA": {"RAM": 10, "Type": Application.TYPE_MODULE}},
                       {"Actuator": {"Type": Application.TYPE_SINK}}
                       ])
        """
        Messages among MODULES (AppEdge in iFogSim)
        """
        m_a = Message("M.A", "Sensor", "ServiceA", instructions=20*10^6, bytes=1000)
        m_b = Message("M.B", "ServiceA", "Actuator", instructions=30*10^6, bytes=500)

        """
        Defining which messages will be dynamically generated # the generation is controlled by Population algorithm
        """
        a.add_source_messages(m_a)

        """
        MODULES/SERVICES: Definition of Generators and Consumers (AppEdges and TupleMappings in iFogSim)
        """
        # MODULE SERVICES
        a.add_service_module("ServiceA", m_a, m_b, fractional_selectivity, threshold=1.0)

        return a

    app1 = create_aplication("Tutorial1")



----------------
Population model
----------------

In real scenarios, sensors can move in the IoT ecosystem which it means, they can invoke services for several access points.
For that reason, each population model is associated to one application and it runs according to a set of events or time distribution.

The association of controls to a node can be dynamic and this process is executed every certain time to change the creation policies associated with the nodes. The population model can be so complex as you wish. More advanced details in :ref:`architecture details <architecture>`.

The most simple case, it is a statical creation of requests. For each message of a pure service source (or sensor), it will have a generation control associated to it.

.. code-block:: python


    from yafs.population import Statical

    pop = Statical("Statical")
    pop.set_src_control({"model": "sensor-device", "number":1,"message": app.get_message("M.A"), "distribution": deterministicDistribution,"param": {"time_shift": 100}})#5.1}})
    pop.set_sink_control({"model": "actuator-device","number":1,"module":app.get_sink_modules()})





--------------
Selector model
--------------

This module is the "service orchestration". It is the coordination and arrangement of multiple services exposed as a single aggregate service.

The most simple case is one to one module using the shortest path between both modules.

.. code-block:: python

    selectorPath = MinimunPath()


where internally this function is customized by the user. Mandatory returns are two arrays ( bestpath and bestdes). The first one is an array among id-nodes of the topology. The second one is also a sequence of id-process who are deployed in that nodes.

.. code-block:: python

    class MinimunPath(Selection):

        def get_path(self, sim, app_name, message, topology_src, alloc_DES, alloc_module, traffic):
            """
            Computes the minimun path among the source elemento of the topology and the localizations of the module

            Return the path and the identifier of the module deployed in the last element of that path
            """
            node_src = topology_src
            DES_dst = alloc_module[app_name][message.dst]

            print "GET PATH"
            print "\tNode _ src (id_topology): %i" %node_src
            print "\tRequest service: %s " %message.dst
            print "\tProcess serving that service: %s " %DES_dst

            bestPath = []
            bestDES = []

            for des in DES_dst: ## In this case, there are only one deployment
                dst_node = alloc_DES[des]
                print "\t\t Looking the path to id_node: %i" %dst_node

                path = list(nx.shortest_path(sim.topology.G, source=node_src, target=dst_node))

                bestPath = [path]
                bestDES = [des]

            return bestPath, bestDES


-------------------
Placement algorithm
-------------------

In this module is implemented the algorithm to allocation resources.
Placement module has two public methods: *initial_allocation* and *run*. The first is used in the first deployment of the application, the second one is used to move this modules in the topological entities according with some multi-objetive allocation algorithm or whatever idea.

The most usual case is a deployment in the cluster. In this case, sink nodes (actuators) are fixed in the topology.

.. code-block:: python

    placement = CloudPlacement("onCloud") # it defines the deployed rules: module-device
    placement.scaleService({"ServiceA": 1})

where:
.. code-block:: python

    from yafs.placement import Placement

    class CloudPlacement(Placement):

        def initial_allocation(self, sim, app_name):
            #We find the ID-nodo/resource
            value = {"mytag": "cloud"} # or whatever tag

            id_cluster = sim.topology.find_IDs(value)
            app = sim.apps[app_name]
            services = app.services

            for module in services:
                if module in self.scaleServices:
                    for rep in range(0, self.scaleServices[module]):
                        idDES = sim.deploy_module(app_name,module,services[module],id_cluster)

---------------------
Running the simulator
---------------------

Once defined the previous elements, we can associate them to the simulator. To do this, you have to *deploy* the application with its respective topology policies. Once this is done, we can launch the simulation.

.. code-block:: python

    s = Sim(t) # t is the topology
    simulation_time = 100000
    s.deploy_app(app, placement, pop, selectorPath)
    s.run(simulation_time,show_progress_monitor=False)


-------
Results
-------

The results are stored in a csv format in two files.  One of the main events is the registration of each message in each entity of the topology that manages it.
In these types of events, the following attributes are recorded:


* **type** It represent the entity who run the taks: a module (COMP_M) or an actuator (SINK_M)
* **app**  application name
* **module** Module or service who manages it
* **service**  service time
* **message** message name
* **DES.src** DES process who send this message
* **DES.dst** DES process who receive this message (the previous module(
* **TOPO.src** ID node topology where the DES.src module is deployed
* **TOPO.dst** ID node topology where the DES.dst module is deployed
* **module.src** the module or service who send this message
* **service** service time
* **time_in** time when the *module* accepts it
* **time_out** time when the *module* finishes its process
* **time_emit** time when the message was sent
* **time_reception** time when the message is accepted by the module


.. note:: The **units of time** have the scale defined by the user in the respective distribution units. It means, the results of time are the times of the simulator.



.. code-block:: python

    type,app,module,message,DES.src,DES.dst,TOPO.src,TOPO.dst,module.src,service,time_in,time_out,time_emit,time_reception
    COMP_M,SimpleCase,ServiceA,M.A,0,2,1,0,Sensor,0.004119505659320882,110.008,110.01211950565931,100.0,110.008
    SINK_M,SimpleCase,Actuator,M.B,2,1,0,2,ServiceA,0,111.01611950565932,111.01611950565932,110.01211950565931,111.01611950565932
    COMP_M,SimpleCase,ServiceA,M.A,0,2,1,0,Sensor,0.004119505659320882,210.008,210.01211950565934,200.0,210.008
    SINK_M,SimpleCase,Actuator,M.B,2,1,0,2,ServiceA,0,211.01611950565933,211.01611950565933,210.01211950565934,211.01611950565933
    COMP_M,SimpleCase,ServiceA,M.A,0,2,1,0,Sensor,0.004119505659320882,310.008,310.0121195056593,300.0,310.008
    SINK_M,SimpleCase,Actuator,M.B,2,1,0,2,ServiceA,0,311.01611950565933,311.01611950565933,310.0121195056593,311.01611950565933
    COMP_M,SimpleCase,ServiceA,M.A,0,2,1,0,Sensor,0.004119505659320882,410.008,410.0121195056593,400.0,410.008


The other file storages the transmission process in the network


.. code-block:: python


    type,src,dst,app,latency,message,ctime,size,buffer
    LINK,1,0,SimpleCase,10.008,M.A,100,1000,0
    LINK,0,2,SimpleCase,1.004,M.B,110.01211950565931,500,0
    LINK,1,0,SimpleCase,10.008,M.A,200,1000,0
    LINK,0,2,SimpleCase,1.004,M.B,210.01211950565934,500,0
    LINK,1,0,SimpleCase,10.008,M.A,300,1000,0
    LINK,0,2,SimpleCase,1.004,M.B,310.0121195056593,500,0


In these types of events, the following attributes are recorded:


* **type** Link type
* **src**  Source of the message - ID node topology
* **dst**  Destination of the message - ID node topology
* **app**  application name
* **latency** the time taken to transmit the message between both nodes.
* **message** message name
* **ctime** simulation time
* **size** size of the message
* **buffer** This variable represents the number of waiting messages in all the links.



How to obtain statistics of these results depends on the user, although there are a good number of processes implemented to obtain the main stats such as: average response time, average service time, average wait time, node utilization, average link latency, costs, and so on.

You can find this example in the following subsection: :ref:`basic example <tutorial_example>`.

So far, we have explained the main parts of the simulator. Maybe it takes more than 5 minutes to understand this modelling, but the title of the section was attractive with that number. If you want to go deeper, you have to look at the rest of the sections: :ref:`architecture details <architecture>` explaining key concepts, a number of :ref:`examples <examples>` and the :ref:`API reference <api_reference>`.


.. [#f1] Gupta, H., Vahid Dastjerdi, A., Ghosh, S. K., & Buyya, R. (2017). iFogSim: A toolkit for modeling and simulation of resource management techniques in the Internet of Things, Edge and Fog computing environments. Software: Practice and Experience, 47(9), 1275-1296.
.. [#f2] Calheiros, R. N., Ranjan, R., Beloglazov, A., De Rose, C. A., & Buyya, R. (2011). CloudSim: a toolkit for modeling and simulation of cloud computing environments and evaluation of resource provisioning algorithms. Software: Practice and experience, 41(1), 23-50.