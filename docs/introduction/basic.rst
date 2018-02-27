==============
Basic Concepts
==============

In order to run a YAFS simulation you should define the following elements:

----------------
Network Topology
----------------

A topology consists of a set of nodes and links. The nodes are elements of the network that serve as a link between other elements and have the ability to execute or host the application.

That is, a node has associated computing characteristics:

* **IPT** Instructions per simulation time. It is equivalent to IPS but it is the user how fix the unit time (i.e. seconds, milliseconds, etc.). Time simulation units is set by the user.

* **RAM** Memory available

* **COST** Cost per unit time

A link has associated these performance characteristics:

* **BW** Channel Bandwidth: in Bytes
* **PR** Channel Propagation speed
* **Latency** is dynamically computed using: Message.size.bits / BW + PR


A network can be created using a json file or through more complex algorithms (see :ref:`architecture details <architecture>`).


.. code-block:: python

    from sim.topology import Topology
    from sim.topology import Entity

    topology_json = {"entity":[
            {"id":0,"type":Entity.ENTITY_FOG, "model": "F_0", "IPT":1000, "RAM":4, "COST":10},
            {"id":1,"type":Entity.ENTITY_FOG, "model": "F_1", "IPT":1000, "RAM":8, "COST":15},
            {"id":2,"type":Entity.ENTITY_FOG, "model": "F_0", "IPT":1000, "RAM":4, "COST":10},
            {"id":3,"type":Entity.ENTITY_FOG, "model": "F_0", "IPT":1000, "RAM":4, "COST":10},
            {"id":4,"type":Entity.ENTITY_CLUSTER, "model": "C_1", "IPT":100000, "RAM":4000, "COST":15}
            ],
        "link":[
            {"s":0,"d":1,"BW":1,"PR":1},
            {"s":1,"d":2,"BW":10,"PR":1},
            {"s":2,"d":3,"BW":1,"PR":1},
            {"s":3,"d":4,"BW":10,"PR":1},
            {"s":2,"d":4,"BW":10,"PR":1}
        ]}

    t = Topology()
    t.load(topology_json)


-----------
Application
-----------
The applicaiton follows the DDF model, in which an application is modeled as directed graph, the vertices of the directed acyclic graph (DAG) representing modules that perform processing on incoming data and edge denoting data dependencies among modules.

An application is set by a group of modules. A module can create messages (a pure source / sensor), a modul can consume messages (a pure sink  / actuator ) and other modules can do both tasks.

The dependencies among modules are defined through messages.


A **message** is the representation of a request between two modules. A message is set by an unique ID in the same application. It has a source and destiny module, a length of instructions, and a number of bytes. If the message arrive a pure sink this message does not require the last two attributes. In YAFS, it is possible to define *broadcast messages*.

.. code-block:: python

    m_global_game_state = Message("M.Global_Game_State", "Coordinator", "Client", 100, 280)
    m_self_state_update = Message("M.Self_State_Update", "Client", "Display")



We illustrate this example using *EEG_GAME application* [#f1]_ following the idea used in CloudSim [#f2]_ and other similar cloud simulators.

.. note::  User defines the distribution functions that modules use to create and send the different messages. In this example, the user defines: *fractional_selectivity* and *next_time_periodic*.

.. note::  In *sim.utils* package there are defined several distributions

.. code-block:: python

    import random
    from sim.application import Application
    from sim.application import Message

    #A periodic function
    def next_time_periodic(time_shift):
        return time_shift

    #A threshold function
    def fractional_selectivity(threshold):
        return random.random() <= threshold

    def create_aplication(name):
        # APPLICATION
        # App.name is unique
        a = Application(name=name)

        # Modules/Services of the application
        a.modules = ["EGG", "Client", "Calculator", "Coordinator", "Display"]

        #Setting pure source modules or Sensors
        a.set_module(["EGG"], Application.TYPE_SOURCE)
        #Setting pure sink modules or Actuators
        a.set_module(["Display"], Application.TYPE_SINK)

        """
        Messages among MODULES
        """
        m_egg = Message("M.EGG", "EGG", "Client", 2000000000, 500) #Instrucctrions, Bytes
        m_sensor = Message("M.Sensor", "Client", "Calculator", 3500, 750)
        m_concentration = Message("M.Concentration", "Calculator", "Client", 14, 100)
        m_player_game_state = Message("M.Player_Game_State", "Calculator", "Coordinator", 1000000000, 100)
        m_global_game_state = Message("M.Global_Game_State", "Coordinator", "Client", 100, 280)
        m_self_state_update = Message("M.Self_State_Update", "Client", "Display")
        m_global_state_update = Message("M.Global_State_Update", "Client", "Display")

        """
        Defining which messages will be dynamically generated
        """
        a.add_source_messages(m_egg)

        """
        MODULES/SERVICES: Definition of Generators and Consumers
        """
        # MODULE SOURCES: only messages generated by non-pure sources
        a.add_service_source("Calculator", next_time_periodic, m_player_game_state, time_shift=1000.0)
        a.add_service_source("Coordinator", next_time_periodic, m_global_game_state, time_shift=1000.0)
        # MODULE SERVICES
        a.add_service_module("Client", m_egg, m_sensor, fractional_selectivity, threshold=0.9)
        a.add_service_module("Client", m_concentration, m_self_state_update, fractional_selectivity, threshold=1.0)
        a.add_service_module("Client", m_global_game_state, m_global_state_update, fractional_selectivity, threshold=1.0)
        a.add_service_module("Calculator", m_sensor, m_concentration, fractional_selectivity, threshold=1.0)
        a.add_service_module("Coordinator", m_player_game_state)
        a.add_service_module("Display", m_self_state_update)
        a.add_service_module("Display", m_global_state_update)

        return a

    app1 = create_aplication("EGG_GAME")



----------------
Population model
----------------

In real scenarios, sensors can move in the IoT ecosystem which it means, they can invoke services for several access points.
For that reason, each population model is associated to one application and it runs according to a set of events or time distribution.

The association of controls to a node can be dynamic and this process is executed every certain time to change the creation policies associated with the nodes. The population model can be so complex as you wish. More advanced details in :ref:`architecture details <architecture>`.

The most simple case, it is a statical creation of requests. For each message of a pure service source (or sensor), it will have a generation control associated to it.

.. code-block:: python


    from sim.population import Statical

    def next_time_exponential_dist(lambd):
        return random.expovariate(1 / lambd)

    pop = Statical("Statical")
    ctrl_generator = {"msg":app1.get_source_message("M.EGG"),"dist":next_time_exponential_dist,"param":{"lambd":100.0}}
    pop.set_generator_control({"node":0,"src":ctrl_generator})




--------------
Selector model
--------------

This module is the "service orchestration". It is the coordination and arrangement of multiple services exposed as a single aggregate service.

The most simple case is one to one module using the shortest path between both modules.

.. code-block:: python


    from sim.selection import First_ShortestPath

    selector = First_ShortestPath()


-------------------
Placement algorithm
-------------------

In this module is implemented the algorithm to allocation resources.
Placement module has two public methods: *initial_allocation* and *run*. The first is used in the first deployment of the application, the second one is used to move this modules in the topological entities according with some multi-objetive allocation algorithm or whatever idea.

The most usual case is a deployment in the cluster. In this case, sink nodes (actuators) are fixed in the topology.

.. code-block:: python

    class ClusterPlacement(Placement):
        def initial_allocation(self,sim):
            #We loook for the most cheaper cluster
            #We guess that the cluster has the computational resources to serve the whole apps
            cheapest_cost = float("inf")
            id_cheapest = -1
            for id in sim.topology.clusterNodes:
                if cheapest_cost >= sim.entity_metrics["node"][id]["COST"]:
                    cheapest_cost = sim.entity_metrics["node"][id]["COST"]
                    id_cheapest = id

            #Assignment of SERVICES in topology nodes
            for app_name in sim.placement_policy[self.name]["apps"]:
                app = sim.apps[app_name]
                #Double control
                #module --> app.node_entity
                sim.assignaments_app_module[app_name] = dict.fromkeys(app.get_pure_modules(),id_cheapest)
                #entity --> modules.app
                sim.assignaments_entity_module[str(id_cheapest)] = dict({app_name:app.get_pure_modules()})

            #Assignment of SINK pure modules
            for sink_module in self.sink_control:
                node = sink_module["node"]
                module = sink_module["src"]
                sim.deploy_sink(app_name, node=node, module=module)

        def run(self,sim):
            self.logger.debug("Activiting - Placement on CLUSTER")
            None

    p = ClusterPlacement("onCluster", activation_dist=next_time_periodic, time_shift=600)
    p.set_sink_control({"node": 0, "src": app1.get_sink_modules()[0]})  # Asigna "Display" -solo hay uno- en un unico node


---------------------
Running the simulator
---------------------

Once defined the previous elements, we can associate them to the simulator. To do this, you have to *deploy* the application with its respective topology policies. Once this is done, we can launch the simulation.

.. code-block:: python

    s = Sim(t) # t is the topology
    simulation_time = 100000
    s.deploy_app(application,placement,population,selector)
    s.run(simulation_time)


-------
Results
-------

The results are stored in a nosql database in a json format. One of the main events is the registration of each message in each entity of the topology that manages it.
In these types of events, the following attributes are recorded:


* **msg_name** message name
* **app**  application name
* **service**  service time
* **module** Module or service who manages it
* **id_node** identifier of the entity of the topology where is deployed the *module*
* **from_module** Module or service who send this message
* **from_node** identifier of the entity of the topology where is deployed the *from_module*
* **time_emit** time when the message was sent
* **time_int** time when the *module* accepts it
* **time_service** service time
* **time_out** time when the *module* finishes its process
* **type** is an identifier of the record type

.. note:: The **units of time** have the scale defined by the user in the respective distribution units. It means, the results of time are the times of the simulator.


.. code-block:: python

   "4": {
      "id_node": 0,
      "service": 0,
      "app": "EGG_GAME",
      "from_module": "Client",
      "module": "Display",
      "time_reception": 41.43794155095091,
      "msg_name": "M.Self_State_Update",
      "time_emit": 38.43794155095091,
      "time_in": 41.43794155095091,
      "time_out": 41.43794155095091,
      "type": "SINK_M",
      "from_node": 4
    },
    "5": {
      "id_node": 4,
      "service": 20.0,
      "app": "EGG_GAME",
      "from_module": "EGG",
      "module": "Client",
      "time_reception": 202.44473295301344,
      "msg_name": "M.EGG",
      "time_emit": 202.44473295301344,
      "time_in": 202.44473295301344,
      "time_out": 222.44473295301344,
      "type": "COMP_M",
      "from_node": 0
    },


How to obtain statistics of these results depends on the user, although there are a good number of processes implemented to obtain the main stats such as: average response time, average service time, average wait time, node utilization, average link latency, costs, and so on.

You can find this example in the following subsection: :ref:`basic example <tutorial_example>`.

So far, we have explained the main parts of the simulator. Maybe it takes more than 5 minutes to understand this modelling, but the title of the section was attractive with that number. If you want to go deeper, you have to look at the rest of the sections: :ref:`architecture details <architecture>` explaining key concepts, a number of :ref:`examples <examples>` and the :ref:`API reference <api_reference>`.


.. [#f1] Gupta, H., Vahid Dastjerdi, A., Ghosh, S. K., & Buyya, R. (2017). iFogSim: A toolkit for modeling and simulation of resource management techniques in the Internet of Things, Edge and Fog computing environments. Software: Practice and Experience, 47(9), 1275-1296.
.. [#f2] Calheiros, R. N., Ranjan, R., Beloglazov, A., De Rose, C. A., & Buyya, R. (2011). CloudSim: a toolkit for modeling and simulation of cloud computing environments and evaluation of resource provisioning algorithms. Software: Practice and experience, 41(1), 23-50.