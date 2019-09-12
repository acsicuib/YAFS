# -*- coding: utf-8 -*-
"""
This module unifies the event-discrete simulation environment with the rest of modules: placement, topology, selection, population, utils and metrics.

"""


import logging
import random
import copy

import simpy
import scipy.spatial
from tqdm import tqdm
import networkx as nx

from yafs.topology import Topology
from yafs.application import Application
from yafs.metrics import Metrics
from yafs.distribution import *
from yafs import utils

from trackanimation.animation import AnimationTrack

import numpy as np
import smopy
from PIL import Image as pimg

EVENT_UP_ENTITY = "node_up"
EVENT_DOWN_ENTITY = "node_down"

NETWORK_LIMIT = 100000000

class Sim:
    """

    This class contains the cloud event-discrete simulation environment and it controls the structure variables.


    Args:
       topology (object) - the associate (:mod:`Topology`) of the environment. There is only one.

    Kwargs:
       name_register (str): database file name where are registered the events.

       purge_register (boolean): True - clean the database

       logger (logger) - logger


    **Main variables to coordinate with algorithm:**


    """
    NODE_METRIC = "COMP_M"
    SOURCE_METRIC = "SRC_M"
    FORWARD_METRIC = "FWD_M"
    SINK_METRIC = "SINK_M"
    LINK_METRIC = "LINK"

    def __init__(self, topology, name_register='events_log.json', link_register='links_log.json', redis=None, purge_register=True, logger=None, default_results_path=None):

        self.env = simpy.Environment()
        """
        the discrete-event simulator (aka DES)
        """

        self.__idProcess = -1
        # an unique indentifier for each process in the DES

        self.__idMessage = 0
        # an unique indentifier for each message

        self.network_ctrl_pipe = simpy.Store(self.env)
        self.network_pump = 0
        # a shared resource that control the exchange of messagess in the topology

        self.stop = False
        """
        Any algorithm can stop internally the simulation putting these value to True. By default is False.
        """

        self.topology = topology
        self.logger = logger or logging.getLogger(__name__)
        self.apps = {}

        self.until = 0 #End time simulation
        #self.db = TinyDB(name_register)
        self.metrics = Metrics(default_results_path=default_results_path)

        self.unreachabled_links = 0

        "Contains the database where all events are recorded"



        """
        Clear the database
        """

        self.entity_metrics = self.__init_metrics()
        """
        Current consumed metrics of each element topology: Nodes & Edges
        """

        self.placement_policy = {}
        # for app.name the placement algorithm

        self.population_policy = {}
        # for app.name the population algorithm

        # for app.nmae
        # self.process_topology = {}

        self.des_process_running = {}
        # Start/stop flag for each pure source
        # key: id.source.process
        # value: Boolean

        self.des_control_process = {}
        # key: app.name
        # value: des process

        self.alloc_source = {}
        """
        Relationship of pure source with topology entity

        id.source.process -> value: dict("id","app","module")

          .. code-block:: python

            alloc_source[34] = {"id":id_node,"app":app_name,"module":source module}

        """

        self.consumer_pipes = {}
        # Queues for each message
        # App+module+idDES -> pipe

        self.alloc_module = {}
        """
        Represents the deployment of a module in a DES PROCESS each DES has a one topology.node.id (see alloc_des var.)

        It used for (:mod:`Placement`) class interaction.

        A dictionary where the key is an app.name and value is a dictionary with key is a module and value an array of id DES process

        .. code-block:: python

            {"EGG_GAME":{"Controller":[1,3,4],"Client":[4]}}

        """


        self.alloc_DES = {}
        """
        The relationship between DES process and topology.node.id

        It is necessary to identify the message.source (topology.node)
        1.N. DES process -> 1. topology.node

        """

        self.selector_path = {}
        # Store for each app.name the selection policy
        # app.name -> Selector

        self.last_busy_time = {}  # must be updated with up/down nodes
        # This variable control the lag of each busy network links. It avoids the generation of a DES-process for each link
        # edge -> last_use_channel (float) = Simulation time




        """
        MOBILE ADAPTATIONS
        """
        self.service_coverage = {}
        self.tolerance = 0.0001
        self.user_tracks = None

        #v2
        self.endpoints = []
        self.user_tracks = None
        self.map = None
        self.coverage = None
        self.control_movement_class = None

    # self.__send_message(app_name, message, idDES, self.SOURCE_METRIC)
    def __send_message(self, app_name, message, idDES, type):
        """
        Any exchange of messages between modules is done with this function and updates the metrics when the message achieves the destination module

        Args:
            app_name (string)º

            message: (:mod:`Message`)

        Kwargs:
            id_src (int) identifier of a pure source module
        """
        #TODO IMPROVE asignation of topo = alloc_DES(IdDES) , It has to move to the get_path process
        try:
            paths,DES_dst = self.selector_path[app_name].get_path(self,app_name, message, self.alloc_DES[idDES], self.alloc_DES, self.alloc_module, self.last_busy_time,from_des=idDES)

            if DES_dst == [None] or DES_dst==[[]]:
                self.logger.warning(
                    "(#DES:%i)\t--- Unreacheable DST:\t%s: PATH:%s " % (idDES, message.name, paths))

                if self.logger.isEnabledFor("Debug"):
                    self.logger.debug("From __send_message function: ")
                    # self.print_debug_assignaments()
                    # print "NODES (%i): %s"%(len(self.topology.G.nodes()),self.topology.G.nodes())
                    self.logger.debug("NODES (%i)" % len(self.topology.G.nodes()))

                    if self.control_movement_class is not None:
                        self.logger.debug("STEP : ",self.control_movement_class.current_step)

            else:

                self.logger.debug("(#DES:%i)\t--- SENDING Message:\t%s: PATH:%s  DES:%s" % (idDES, message.name,paths,DES_dst))

                # print "MESSAGES"
                #May be, the selector of path decides broadcasting multiples paths
                for idx,path in enumerate(paths):
                    msg = copy.copy(message)
                    msg.path = copy.copy(path)
                    msg.app_name = app_name
                    msg.idDES = DES_dst[idx]

                    self.network_ctrl_pipe.put(msg)
        except KeyError:
            self.logger.warning("(#DES:%i)\t--- Unreacheable DST:\t%s " % (idDES, message.name))


    def __network_process(self):
        """
        This is an internal DES-process who manages the latency of messages sent in the network.
        Performs the simulation of packages within the path between src and dst entities decided by the selection algorithm.
        In this way, the message has a transmission latency.
        """
        edges = self.topology.get_edges().keys()
        self.last_busy_time = {}  # dict(zip(edges, [0.0] * len(edges)))

        while not self.stop:
            message = yield self.network_ctrl_pipe.get()

            # print "NetworkProcess --- Current time %d " %self.env.now
            # print "name " + message.name
            # print "Path:",message.path
            # print "DST_INT:",message.dst_int
            # #print message.timestamp
            # print "DST",message.dst


            # If same SRC and PATH or the message has achieved the penultimate node to reach the dst
            if not message.path or message.path[-1] == message.dst_int or len(message.path)==1:

                pipe_id = "%s%s%i" %(message.app_name,message.dst,message.idDES)  # app_name + module_name (dst) + idDES
                # Timestamp reception message in the module
                message.timestamp_rec = self.env.now
                # The message is sent to the module.pipe
                self.consumer_pipes[pipe_id].put(message)
            else:
                # The message is sent at first time or it sent more times.
                if message.dst_int < 0:
                    src_int = message.path[0]
                    message.dst_int = message.path[1]
                else:
                    src_int = message.dst_int
                    message.dst_int = message.path[message.path.index(message.dst_int) + 1]
                # arista set by (src_int,message.dst_int)
                link = (src_int, message.dst_int)


                # Links in the topology are bidirectional: (a,b) == (b,a)
                try:
                    last_used = self.last_busy_time[link]
                except KeyError:
                    last_used = 0.0
                    # self.last_busy_time[link] = last_used

                    #link = (message.dst_int, src_int)
                    #last_used = self.last_busy_time[link]
                """
                Computing message latency
                """
                size_bits = message.bytes
                #size_bits = message.bytes * 8
                try:
                   # transmit = size_bits / (self.topology.get_edge(link)[Topology.LINK_BW] * 1000000.0)  # MBITS!
                    transmit = size_bits / (self.topology.get_edge(link)[Topology.LINK_BW] * 1000000.0)  # MBITS!
                    propagation = self.topology.get_edge(link)[Topology.LINK_PR]
                    latency_msg_link = transmit + propagation

                    #print "-link: %s -- lat: %d" %(link,latency_msg_link)

                    # update link metrics
                    self.metrics.insert_link(
                        {"id":message.id,"type": self.LINK_METRIC,"src":link[0],"dst":link[1],"app":message.app_name,"latency":latency_msg_link,"message": message.name,"ctime":self.env.now,"size":message.bytes,"buffer":self.network_pump})#"path":message.path})

                    # We compute the future latency considering the current utilization of the link
                    if last_used < self.env.now:
                        shift_time = 0.0
                        last_used = latency_msg_link + self.env.now  # future arrival time
                    else:
                        shift_time = last_used - self.env.now
                        last_used = self.env.now + shift_time + latency_msg_link

                    # print "Send next WakeUp : ", last_used
                    # print "-" * 30

                    self.last_busy_time[link] = last_used
                    self.env.process(self.__wait_message(message, latency_msg_link, shift_time))
                except:
                    #This fact is produced when a node or edge the topology is changed or disappeared
                    self.logger.warning("The initial path assigned is unreachabled. Link: (%i,%i). Routing a new one. %i"%(link[0],link[1],self.env.now))

                    paths, DES_dst = self.selector_path[message.app_name].get_path_from_failure(self, message, link, self.alloc_DES,self.alloc_module, self.last_busy_time,self.env.now,from_des=message.idDES)

                    if DES_dst == [] and paths==[]:
                        #Message communication ending:
                        #The message have arrived to the destination node but it is unavailable.
                        None
                        self.logger.debug("\t No path given. Message is lost")
                    else:

                        message.path = copy.copy(paths[0])
                        message.idDES = DES_dst[0]
                        self.logger.debug("(\t New path given. Message is enrouting again.")
                        # print "\t",msg.path
                        self.network_ctrl_pipe.put(message)



    def __wait_message(self, msg, latency, shift_time):
        """
        Simulates the transfer behavior of a message on a link
        """
        self.network_pump += 1
        yield self.env.timeout(latency + shift_time)
        self.network_pump -= 1
        self.network_ctrl_pipe.put(msg)

    def __get_id_process(self):
        """
        A DES-process has an unique identifier
        """
        self.__idProcess += 1
        return self.__idProcess

    def __init_metrics(self):
        """
        Each entity and node metrics are initialized with empty values
        """
        nodes_att = self.topology.get_nodes_att()
        measures = {"node": {}, "link": {}}
        for key in nodes_att:
            measures["node"][key] = {}

        for edge in self.topology.get_edges():
            measures["link"][edge] = {Topology.LINK_PR: self.topology.get_edge(edge)[self.topology.LINK_PR],
                                      Topology.LINK_BW: self.topology.get_edge(edge)[self.topology.LINK_BW]}
        return measures

    def __add_placement_process(self, placement):
        """
        A DES-process who controls the invocation of Placement.run
        """
        myId = self.__get_id_process()
        self.des_process_running[myId] = True
        self.des_control_process[placement.name]=myId

        self.logger.debug("Added_Process - Placement Algorithm\t#DES:%i" % myId)
        while not self.stop and self.des_process_running[myId]:
            yield self.env.timeout(placement.get_next_activation())
            placement.run(self)
            self.logger.debug("(DES:%i) %7.4f Run - Placement Policy: %s " % (myId, self.env.now, self.stop))  # Rewrite
        self.logger.debug("STOP_Process - Placement Algorithm\t#DES:%i" % myId)

    def __add_population_process(self, population):
        """
        A DES-process who controls the invocation of Population.run
        """
        myId = self.__get_id_process()
        self.des_process_running[myId] = True
        self.des_control_process[population.name] = myId

        self.logger.debug("Added_Process - Population Algorithm\t#DES:%i" % myId)
        while not self.stop and self.des_process_running[myId]:
            yield self.env.timeout(population.get_next_activation())
            self.logger.debug("(DES:%i) %7.4f Run - Population Policy: %s " % (myId, self.env.now, self.stop))  # REWRITE
            population.run(self)
        self.logger.debug("STOP_Process - Population Algorithm\t#DES:%i" % myId)

    def __getIDMessage(self):
        self.__idMessage +=1
        return self.__idMessage

    def __add_source_population(self, idDES, name_app, message, distribution):
        """
        A DES-process who controls the invocation of several Pure Source Modules
        """
        self.logger.debug("Added_Process - Module Pure Source\t#DES:%i" % idDES)
        while not self.stop and self.des_process_running[idDES]:
            nextTime = distribution.next()
            yield self.env.timeout(nextTime)
            if self.des_process_running[idDES]:
                self.logger.debug("(App:%s#DES:%i)\tModule - Generating Message: %s \t(T:%d)" % (name_app, idDES, message.name,self.env.now))

                msg = copy.copy(message)
                msg.timestamp = self.env.now
                msg.id = self.__getIDMessage()

                self.__send_message(name_app, msg, idDES, self.SOURCE_METRIC)

        self.logger.debug("STOP_Process - Module Pure Source\t#DES:%i" % idDES)

    def __update_node_metrics(self, app, module, message, des, type):
        try:
            """
            It computes the service time in processing a message and record this event
            """
            if module in self.apps[app].get_sink_modules():
                """
                The module is a SINK (Actuactor)
                """
                id_node  = self.alloc_DES[des]
                time_service = 0
            else:
                """
                The module is a processing module
                """
                id_node = self.alloc_DES[des]

                # att_node = self.topology.get_nodes_att()[id_node] # WARNING DEPRECATED from V1.0
                att_node = self.topology.G.nodes[id_node]

                time_service = message.inst / float(att_node["IPT"])


            """
            it records the entity.id who sends this message
            """
            # if not message.path:
            #     from_id_source = id_node  # same src like dst
            # else:
            #     from_id_source = message.path[0]
            #
     # # if message.id == 1072:
     #        print "-"*50
     #        print "Module: ",module # module that receives the request (RtR)
     #        print "DES ",des # DES process who RtR
     #        print "ID MODULE: ",id_node  #Topology entity who RtR
     #        print "Message.name ",message.name # Message name
     #        print "Message.id ", message.id #Message generator id
     #        print "Message.path ",message.path #enrouting path
     #        print "Message src ",message.src #module source who send the request
     #        print "Message dst ",message.dst #module dst (the entity that RtR)
     #        print "Message idDEs ",message.idDES #DES intermediate process that process the request
     #        print "TOPO.src ", message.path[0] #entity that RtR
     #        print "TOPO.dst ", int(self.alloc_DES[des]) #DES process that RtR
     #        print "time service ",time_service
     #        exit()

     #
            # # print "MODULE: ",self.alloc_module[app][module]
            # # tmp = []
            # # for it in self.alloc_module[app][module]:
            # #     tmp.append(self.alloc_DES[it])
            # # print "ALLOC:  ", tmp
            # # print "PATH 0: " ,message.path[0]



            #WARNING. If there are more than two equal modules deployed in the same entity, it will not be possible to determine which process sent this package at this point. That information will have to be calculated by the trace of the message (message.id)
            sourceDES = -1
            try:
                DES_possible = self.alloc_module[app][message.src]
                for eDES in DES_possible:
                    if self.alloc_DES[eDES] == message.path[0]:
                        sourceDES = eDES
            except:
                for k in self.alloc_source.keys():
                    if self.alloc_source[k]['id'] == message.path[0]:
                        sourceDES = k

            # print "Source DES ",sourceDES
            # print "-" * 50

            self.metrics.insert(
                {"id":message.id,"type": type, "app": app, "module": module, "message": message.name,
                 "DES.src": sourceDES, "DES.dst":des,"module.src": message.src,
                 "TOPO.src": message.path[0], "TOPO.dst": id_node,

                 "service": time_service, "time_in": self.env.now,
                 "time_out": time_service + self.env.now, "time_emit": float(message.timestamp),
                 "time_reception": float(message.timestamp_rec)

                 })

            return time_service
        except KeyError:
            # The node can be removed
            self.logger.critical("Make sure that this node has been removed or it has all mandatory attributes - Node: DES:%i" % des)
            return 0


        # self.logger.debug("TS[%s] - DES: %i - %d"%(module,des,time_service))
        # except:
        #     self.logger.warning("This module has been removed previously to the arrival time of this message. DES: %i"%des)
        #     return 0

    """
    MEJORAR - ASOCIAR UN PROCESO QUE LOS CONTROLES®.
    """

    def __add_up_node_process(self, next_event, **param):
        myId = self.__get_id_process()
        self.logger.debug("Added_Process - UP entity Creation\t#DES:%i" % myId)
        while not self.stop:
            # TODO Define function to ADD a new NODE in topology
            yield self.env.timeout(next_event(**param))
            self.logger.debug("(DES:%i) %7.4f Node " % (myId, self.env.now))
        self.logger.debug("STOP_Process - UP entity Creation\t#DES%i" % myId)

    """
    MEJORAR - ASOCIAR UN PROCESO QUE LOS CONTROLES.
    """

    def __add_down_node_process(self, next_event, **param):
        myId = self.__get_id_process()
        self.des_process_running[myId] = True
        self.logger.debug("Added_Process - Down entity Creation\t#DES:%i" % myId)
        while not self.stop and self.des_process_running[myId]:
            yield self.env.timeout(next_event(**param))
            self.logger.debug("(DES:%i) %7.4f Node " % (myId, self.env.now))

        self.logger.debug("STOP_Process - Down entity Creation\t#DES%i" % myId)

    def __add_source_module(self, idDES, app_name, module, message, distribution, **param):
        """
        It generates a DES process associated to a compute module for the generation of messages
        """
        self.logger.debug("Added_Process - Module Source: %s\t#DES:%i" % (module, idDES))
        while (not self.stop) and self.des_process_running[idDES]:
            yield self.env.timeout(distribution.next())
            if self.des_process_running[idDES]:
                self.logger.debug(
                    "(App:%s#DES:%i#%s)\tModule - Generating Message:\t%s" % (app_name, idDES, module, message.name))
                msg = copy.copy(message)
                msg.timestamp = self.env.now
                self.__send_message(app_name, msg, idDES,self.SOURCE_METRIC)

        self.logger.debug("STOP_Process - Module Source: %s\t#DES:%i" % (module, idDES))


    def __add_consumer_module(self, ides, app_name, module, register_consumer_msg):
        """
        It generates a DES process associated to a compute module
        """
        self.logger.debug("Added_Process - Module Consumer: %s\t#DES:%i" % (module, ides))
        while not self.stop and self.des_process_running[ides]:
            if self.des_process_running[ides]:
                msg = yield self.consumer_pipes["%s%s%i"%(app_name,module,ides)].get()
                # One pipe for each module name

                m = self.apps[app_name].services[module]

                # for ser in m:
                #     if "message_in" in ser.keys():
                #         try:
                #             print "\t\t M_In: %s  -> M_Out: %s " % (ser["message_in"].name, ser["message_out"].name)
                #         except:
                #             print "\t\t M_In: %s  -> M_Out: [NOTHING] " % (ser["message_in"].name)

                # print "Registers len: %i" %len(register_consumer_msg)
                doBefore = False
                for register in register_consumer_msg:
                    if msg.name == register["message_in"].name:
                        # The message can be treated by this module
                        """
                        Processing the message
                        """
                        # if ides == 3:
                        #     print "Consumer Message: %d " % self.env.now
                        #     print "MODULE DES: ",ides
                        #     print "id ",msg.id
                        #     print "name ",msg.name
                        #     print msg.path
                        #     print msg.dst_int
                        #     print msg.timestamp
                        #     print msg.dst
                        #
                        #     print "-" * 30

                        #The module only computes this type of message one time.
                        #It records once
                        if not doBefore:
                            self.logger.debug(
                                "(App:%s#DES:%i#%s)\tModule - Recording the message:\t%s" % (app_name, ides, module, msg.name))
                            type = self.NODE_METRIC

                            service_time = self.__update_node_metrics(app_name, module, msg, ides, type)

                            yield self.env.timeout(service_time)
                            doBefore = True

                        """
                        Transferring the message
                        """
                        if not register["message_out"]:
                            """
                            Sink behaviour (nothing to send)
                            """
                            self.logger.debug(
                                "(App:%s#DES:%i#%s)\tModule - Sink Message:\t%s" % (app_name, ides, module, msg.name))
                            continue
                        else:
                            if register["dist"](**register["param"]): ### THRESHOLD DISTRIBUTION to Accept the message from source
                                if not register["module_dest"]:
                                    # it is not a broadcasting message
                                    self.logger.debug("(App:%s#DES:%i#%s)\tModule - Transmit Message:\t%s" % (
                                        app_name, ides, module, register["message_out"].name))

                                    msg_out = copy.copy(register["message_out"])
                                    msg_out.timestamp = self.env.now
                                    msg_out.id = msg.id
                                    msg_out.last_idDes = copy.copy(msg.last_idDes)
                                    msg_out.last_idDes.append(ides)


                                    self.__send_message(app_name, msg_out,ides, self.FORWARD_METRIC)

                                else:
                                    # it is a broadcasting message
                                    self.logger.debug("(App:%s#DES:%i#%s)\tModule - Broadcasting Message:\t%s" % (
                                        app_name, ides, module, register["message_out"].name))

                                    msg_out = copy.copy(register["message_out"])
                                    msg_out.timestamp = self.env.now
                                    msg_out.last_idDes = copy.copy(msg.last_idDes)
                                    msg_out.id = msg.id
                                    msg_out.last_idDes = msg.last_idDes.append(ides)
                                    for idx, module_dst in enumerate(register["module_dest"]):
                                        if random.random() <= register["p"][idx]:
                                            self.__send_message(app_name, msg_out, ides,self.FORWARD_METRIC)

                            else:
                                self.logger.debug("(App:%s#DES:%i#%s)\tModule - Stopped Message:\t%s" % (
                                    app_name, ides, module, register["message_out"].name))

        self.logger.debug("STOP_Process - Module Consumer: %s\t#DES:%i" % (module, ides))

    def __add_sink_module(self, ides, app_name, module):
        """
        It generates a DES process associated to a SINK module
        """
        self.logger.debug("Added_Process - Module Pure Sink: %s\t#DES:%i" % (module, ides))
        while not self.stop and self.des_process_running[ides]:
            msg = yield self.consumer_pipes["%s%s%i" % (app_name, module, ides)].get()
            """
            Processing the message
            """
            self.logger.debug(
                "(App:%s#DES:%i#%s)\tModule Pure - Sink Message:\t%s" % (app_name, ides, module, msg.name))
            type = self.SINK_METRIC
            service_time = self.__update_node_metrics(app_name, module, msg, ides, type)
            yield self.env.timeout(service_time)  # service time is 0

        self.logger.debug("STOP_Process - Module Pure Sink: %s\t#DES:%i" % (module, ides))


    def __add_stop_monitor(self, name, function, distribution,show_progress_monitor, **param):
        """
        Add a DES process for Stop/Progress bar monitor
        """
        myId = self.__get_id_process()
        self.logger.debug("Added_Process - Internal Monitor: %s\t#DES:%i" % (name,myId))
        if show_progress_monitor:
            self.pbar = tqdm(total=self.until)
        while not self.stop:
            yield self.env.timeout(distribution.next())
            function(show_progress_monitor,**param)
        self.logger.debug("STOP_Process - Internal Monitor: %s\t#DES:%i" % (name, myId))


    def __add_monitor(self, name, function, distribution, **param):
        """
        Add a DES process for user purpose
        """
        myId = self.__get_id_process()
        self.logger.debug("Added_Process - Internal Monitor: %s\t#DES:%i" % (name, myId))
        while not self.stop:
            yield self.env.timeout(distribution.next())
            function(**param)
        self.logger.debug("STOP_Process - Internal Monitor: %s\t#DES:%i" % (name, myId))


    def __add_consumer_service_pipe(self,app_name,module,idDES):
        self.logger.debug("Creating PIPE: %s%s%i "%(app_name,module,idDES))

        self.consumer_pipes["%s%s%i"%(app_name,module,idDES)] = simpy.Store(self.env)



    def __ctrl_progress_monitor(self,show_progress_monitor,time_shift):
        """
        The *simpy.run.until* function doesnot stop the execution until all pipes are empty.
        We force the stop our DES process using *self.stop* boolean

        """
        if self.until:
            if show_progress_monitor:
                self.pbar.update(time_shift)
            if self.env.now >= self.until:
                self.stop = True
                if show_progress_monitor:
                    self.pbar.close()
                self.logger.info("! Stop simulation at time: %f !" % self.env.now)

    """
    DEPRECATED
    """
    def __update_internal_structures_from_DES_remove(self, DES):
        try:
            self.alloc_DES.pop(DES, None)
            for app in self.alloc_module:
                for module in self.alloc_module[app]:
                    self.alloc_module[app][module].remove(DES)
        except:
            None


    """
    SECTION FOR PUBLIC METHODS
    """

    def get_DES(self,name):
        return self.des_control_process[name]

    def deploy_monitor(self, name, function, distribution, **param):
        """
        Add a DES process for user purpose

        Args:
            name (string) name of monitor

            function (function): function that will be invoked within the simulator with the user's code

            distribution (function): a temporary distribution function

        Kwargs:
            param (dict): the parameters of the *distribution* function

        """
        self.env.process(self.__add_monitor(name, function, distribution, **param))

    def register_event_entity(self, next_event_dist, event_type=EVENT_UP_ENTITY, **args):
        """
        TODO
        """
        if event_type == EVENT_UP_ENTITY:
            self.env.process(self.__add_up_node_process( next_event_dist, **args))
        elif event_type == EVENT_DOWN_ENTITY:
            self.env.process(self.__add_down_node_process( next_event_dist, **args))

    def deploy_source(self, app_name, id_node, msg, distribution):
        """
        Add a DES process for deploy pure source modules (sensors)
        This function its used by (:mod:`Population`) algorithm

        Args:
            app_name (str): application name

            id_node (int): entity.id of the topology who will create the messages

            distribution (function): a temporary distribution function

        Kwargs:
            param - the parameters of the *distribution* function

        Returns:
            id (int) the same input *id*

        """
        idDES = self.__get_id_process()
        self.des_process_running[idDES] = True
        self.env.process(self.__add_source_population(idDES, app_name, msg, distribution))
        self.alloc_DES[idDES] = id_node
        self.alloc_source[idDES] = {"id":id_node,"app":app_name,"module":msg.src,"name":msg.name}
        return idDES



    def __deploy_source_module(self, app_name, module, id_node, msg, distribution):
        """
        Add a DES process for deploy  source modules
        This function its used by (:mod:`Population`) algorithm

        Args:
            app_name (str): application name

            id_node (int): entity.id of the topology who will create the messages

            distribution (function): a temporary distribution function

        Kwargs:
            param - the parameters of the *distribution* function

        Returns:
            id (int) the same input *id*

        """
        idDES = self.__get_id_process()
        self.des_process_running[idDES] = True
        self.env.process(self.__add_source_module(idDES, app_name, module,msg, distribution))
        self.alloc_DES[idDES] = id_node
        return idDES

    # idsrc = sim.deploy_module(app_name, module, id_node, register_consumer_msg)
    def __deploy_module(self, app_name, module, id_node, register_consumer_msg):
        """
        Add a DES process for deploy  modules
        This function its used by (:mod:`Population`) algorithm

        Args:
            app_name (str): application name

            id_node (int): entity.id of the topology who will create the messages

            module (str): module name

            msg (str): message?

        Kwargs:
            param - the parameters of the *distribution* function

        Returns:
            id (int) the same input *id*

        """
        idDES = self.__get_id_process()
        self.des_process_running[idDES] = True
        self.env.process(self.__add_consumer_module(idDES,app_name, module,register_consumer_msg))
        # To generate the QUEUE of a SERVICE module
        self.__add_consumer_service_pipe(app_name, module, idDES)

        self.alloc_DES[idDES] = id_node
        if module not in self.alloc_module[app_name]:
            self.alloc_module[app_name][module] = []
        self.alloc_module[app_name][module].append(idDES)

        return idDES


    def deploy_sink(self, app_name, node, module):
        """
        Add a DES process for deploy pure SINK modules (actuators)
        This function its used by (:mod:`Placement`): algorithm
        Internatlly, there is not a DES PROCESS for this type of behaviour

        Args:
            app_name (str): application name

            node (int): entity.id of the topology who will create the messages

            module (str): module
        """
        idDES = self.__get_id_process()
        self.des_process_running[idDES] = True
        self.alloc_DES[idDES] = node
        self.__add_consumer_service_pipe(app_name, module, idDES)
        # Update the relathionships among module-entity
        if app_name in self.alloc_module:
            if module not in self.alloc_module[app_name]:
                self.alloc_module[app_name][module] = []
        self.alloc_module[app_name][module].append(idDES)
        self.env.process(self.__add_sink_module(idDES,app_name, module))



    def stop_process(self, id):
        """
        All pure source modules (sensors) are controlled by this boolean.
        Using this function (:mod:`Population`) algorithm can stop one source

        Args:
            id.source (int): the identifier of the DES process.
        """
        self.des_process_running[id] = False

    def start_process(self, id):
        """
        All pure source modules (sensors) are controlled by this boolean.
        Using this function (:mod:`Population`) algorithm can start one source

        Args:
            id.source (int): the identifier of the DES process.
        """
        self.des_process_running[id] = True



    def deploy_app(self, app, placement, population, selector):
        """
        This process is responsible for linking the *application* to the different algorithms (placement, population, and service)

        Args:
            app (object): :mod:`Application` class

            placement (object): :mod:`Placement` class

            population (object): :mod:`Population` class

            selector (object): :mod:`Selector` class
        """
        # Application
        self.apps[app.name] = app

        # Initialization
        self.alloc_module[app.name] = {}

        # Add Placement controls to the App
        if not placement.name in self.placement_policy.keys():  # First Time
            self.placement_policy[placement.name] = {"placement_policy": placement, "apps": []}
            if placement.activation_dist is not None:
                self.env.process(self.__add_placement_process(placement))
        self.placement_policy[placement.name]["apps"].append(app.name)

        # Add Population control to the App

        if not population.name in self.population_policy.keys():  # First Time
            self.population_policy[population.name] = {"population_policy": population, "apps": []}
            if population.activation_dist is not None:
                self.env.process(self.__add_population_process(population))
        self.population_policy[population.name]["apps"].append(app.name)

        # Add Selection control to the App
        self.selector_path[app.name] = selector


    def get_alloc_entities(self):
        """ It returns a dictionary of deployed services
        key : id-node
        value: a list of deployed services
        """
        alloc_entities = {}
        for key in self.topology.G.nodes:
            alloc_entities[key] = []


        for id_des_process in self.alloc_source:
            src_deployed = self.alloc_source[id_des_process]
            # print "Module (SRC): %s(%s) - deployed at entity.id: %s" %(src_deployed["module"],src_deployed["app"],src_deployed["id"])
            alloc_entities[src_deployed["id"]].append(src_deployed["app"]+"#"+src_deployed["module"])

        for app in self.alloc_module:
            for module in self.alloc_module[app]:
                # print "Module (MOD): %s(%s) - deployed at entities.id: %s" % (module,app,self.alloc_module[app][module])
                for idDES in self.alloc_module[app][module]:
                    alloc_entities[self.alloc_DES[idDES]].append(app+"#"+module)

        return alloc_entities


    def deploy_module(self,app_name,module, services,ids):
        register_consumer_msg = []
        id_DES =[]

        # print module
        for service in services:
            """
            A module can manage multiples messages as well as pass them as create them.
            """
            if service["type"] == Application.TYPE_SOURCE:
                """
                The MODULE can generate messages according with a distribution:
                It adds a DES process for mananging it:  __add_source_module
                """
                for id_topology in ids:
                    id_DES.append(self.__deploy_source_module(app_name, module, distribution=service["dist"],
                                                     msg=service["message_out"],
                                                     id_node=id_topology))
            else:
                """
                The MODULE can deal with different messages, "tuppleMapping (iFogSim)",
                all of them are add a list to be managed in only one DES process
                MODULE TYPE CONSUMER : adding process:  __add_consumer_module
                """
                # 1 module puede consumir N type de messages con diferentes funciones de distribucion
                register_consumer_msg.append(
                    {"message_in": service["message_in"], "message_out": service["message_out"],
                     "module_dest": service["module_dest"], "dist": service["dist"], "param": service["param"]})


        if len(register_consumer_msg) > 0:
            for id_topology in ids:
                id_DES.append(self.__deploy_module(app_name, module, id_topology, register_consumer_msg))

        return id_DES


    def undeploy_module(self, app_name,service_name, idtopo):
        """ removes all modules deployed in a node
        modules with the same name = service_name
        from app_name
        deployed in id_topo
        """
        all_des = []
        for k, v in self.alloc_DES.items():
            if v == idtopo:
                all_des.append(k)

        # Clearing related structures
        for des in self.alloc_module[app_name][service_name]:
            if des in all_des:
                self.alloc_module[app_name][service_name].remove(des)
                self.stop_process(des)
                del self.alloc_DES[des]

    def remove_node(self, id_node_topology):
        # Stopping related processes deployed in the module and clearing main structure: alloc_DES
        des_tmp=[]
        if id_node_topology in self.alloc_DES.values():
            for k, v in self.alloc_DES.items():
                if v == id_node_topology:
                    des_tmp.append(k)
                    self.stop_process(k)
                    del self.alloc_DES[k]

        # Clearing other related structures
        for k, v in self.alloc_module.items():
            for k2, v2 in self.alloc_module[k].items():
                for item in des_tmp:
                    if item in v2:
                        v2.remove(item)

        # Finally removing node from topology
        self.topology.G.remove_node(id_node_topology)

    def draw_allocated_topology(self):
        entities = self.get_alloc_entities()
        utils.draw_topology(self.topology,entities)


    def get_DES_from_Service_In_Node(self, node, app_name, service):
        deployed = self.alloc_module[app_name][service]
        for des in deployed:
            if self.alloc_DES[des] == node:
                return des
        return []

    def get_assigned_structured_modules_from_DES(self):
        fullAssignation = {}
        for app in self.alloc_module:
            for module in self.alloc_module[app]:
                deployed = self.alloc_module[app][module]
                for des in deployed:
                    fullAssignation[des] = {"DES": self.alloc_DES[des], "module": module}
        return fullAssignation


    def print_debug_assignaments(self):
        """
        This functions prints debug information about the assignment of DES process - Topology ID - Source Module or Modules
        """
        fullAssignation = {}

        for app in self.alloc_module:
            for module in self.alloc_module[app]:
                deployed = self.alloc_module[app][module]
                for des in deployed:
                    fullAssignation[des] = {"ID":self.alloc_DES[des],"Module":module} #DES process are unique for each module/element

        print "-"*40
        print "DES\t| TOPO \t| Src.Mod \t| Modules"
        print ("-" * 40)
        for k in self.alloc_DES:
            print k,"\t|",self.alloc_DES[k],"\t|",self.alloc_source[k]["name"] if k in self.alloc_source.keys() else "--","\t\t|",fullAssignation[k]["Module"] if k in fullAssignation.keys() else "--"
        print "-" * 40
        # exit()

    #
    # ### MOBILE ADAPTATION SECTION
    # def update_service_coverage(self):
    #     if self.street_network is not None:
    #         points = utils.create_points(self.topology.G)
    #         point_streets = utils.create_points(self.street_network)
    #
    #         tree = scipy.spatial.KDTree(points.values())
    #         points_within_tolerance = tree.query_ball_point(point_streets.values(), self.tolerance)
    #
    #         # key = node network
    #         # value = id - module SW
    #
    #         self.service_coverage = {}
    #         for idx, pt in enumerate(points_within_tolerance):
    #             ## MODULE SW
    #             key2 = point_streets.keys()[idx]
    #             nG2 = self.street_network.nodes[key2]
    #             # print "%s is close to " % nG2["model"]
    #             ## Street coverage
    #             for p in pt:
    #                 key = points.keys()[p]
    #                 # service_coverage[(G.nodes[key]['x'],G.nodes[key]['y'])]=nG2["model"]
    #                 self.service_coverage[key] = nG2["id"]



    # def setMobilityUserBehaviour(self,dataPopulation):
    #     self.user_behaviour = dataPopulation #TODO CHECK SYNTAX

    def __add_mobile_agent(self,ides, gme):
        #The mobile starts

        yield self.env.timeout(gme.start)
        self.logger.info("(#DES:%i)\t--- Mobile Entity STARTS :\t%s " % (ides, gme._id))
        while (len(gme.path) - 1 > gme.current_position) and not self.stop and self.des_process_running[ides]:
            e = (gme.path[gme.current_position], gme.path[gme.current_position + 1])
            data = self.street_network.get_edge_data(*e)
            try:
                next_time = int(utils.toMeters(data[0]["geometry"]) / gme.speed)
            except KeyError:
                next_time = 1  # default time by roundabout or other Spatial THINGS

            # take an action?
            gme.next_time = next_time

            self.logger.info("(#DES:%i)\t--- DO ACTION :\t%s " % (ides, gme._id))
            gme.do.action(gme)

            #TODO Can the MA wait more time in that node?

            yield self.env.timeout(next_time)
            gme.current_position += 1

        # Last movement
        if self.des_process_running[ides] and not self.stop:
            gme.do.action(gme)

        self.logger.info("(#DES:%i)\t--- Mobile Entity ENDS :\t%s " % (ides, gme._id))
        # print "Mobile agent: %s ends " % gme.plate



    def add_mobile_agent(self,gme):
        ides = self.__get_id_process()
        self.des_process_running[ides] = True
        self.env.process(self.__add_mobile_agent(ides, gme))

        ### ATENCION COONTROLAR VAR: INTERNAS
        #self.alloc_DES[ides] = id_node

        return ides

    def load_user_tracks(self,tracks):
        self.user_tracks = tracks

        # self.user_tracks = AnimationTrack(df_points=tracks, dpi=300, bg_map=False, map_transparency=0.5)

        # for i, (point, nextpoint) in enumerate(fig.compute_points()):
        #     print i, point, nextpoint
        #     if i == 2: break
        # exit()

    def generate_animation(self,pathFile):
        if len(self.endpoints)==0: self.__update_connection_points()
        if self.map == None: self.__load_map()

        #map_endpoints = [self.map.to_pixels(i[0], i[1]) for i in self.endpoints]
        #map_endpoints = np.array(map_endpoints)
        self.map.img.save(pathFile+"_map_background.png")

        animation = AnimationTrack(self, dpi=100, bg_map=True, aspect='equal')
        animation.make_video(output_file=pathFile, framerate=10, linewidth=1.0,G=self.topology.G)


    # def generate_snapshot(self, pathFile,event):
    #     if len(self.endpoints) == 0: self.__update_connection_points()
    #     if self.map == None: self.__load_map()
    #
    #     #map_endpoints = [self.map.to_pixels(i[0], i[1]) for i in self.endpoints]
    #     #map_endpoints = np.array(map_endpoints)
    #
    #     animation = AnimationTrack(self, dpi=100, bg_map=True, aspect='equal')
    #     animation.make_video(output_file=pathFile, framerate=10, linewidth=1.0)

    def __load_map(self):
        trk_bounds = self.user_tracks.get_bounds()
        min_lat = trk_bounds.min_latitude
        max_lat = trk_bounds.max_latitude
        min_lng = trk_bounds.min_longitude
        max_lng = trk_bounds.max_longitude

        self.map = smopy.Map((min_lat, min_lng, max_lat, max_lng), z=12)


    def __update_connection_points(self):
        level = nx.get_node_attributes(self.topology.G, 'level')
        lat = nx.get_node_attributes(self.topology.G, 'lat')
        lng = nx.get_node_attributes(self.topology.G, 'lng')

        self.endpoints = []
        self.name_endpoints = {}
        pos = 0
        for n in level:
            if level[n] == 0:
                self.endpoints.append([lat[n], lng[n]])
                self.name_endpoints[pos]=n
                pos +=1
        self.endpoints = np.array(self.endpoints)


    def set_coverage_class(self, class_name,**kwargs):
        if len(self.endpoints)==0: self.__update_connection_points()
        if self.map == None: self.__load_map()

        self.coverage = class_name(self.map,self.endpoints,**kwargs)

    def set_mobile_fog_entities(self,mobile_fog_entities):
        self.mobile_fog_entities = mobile_fog_entities

    def set_movement_control(self,evol):
        self.control_movement_class = evol

    def run(self, until,test_initial_deploy=False,show_progress_monitor=True,mobile_behaviour=False):
        """
        Start the simulation

        Args:
            until (int): Defines a stop time. If None the simulation runs until some internal algorithm changes the var *yafs.core.sim.stop* to True
        """
        self.env.process(self.__network_process())

        """
        Creating app.sources and deploy the sources in the topology
        """
        for pop in self.population_policy.itervalues():
            for app_name in pop["apps"]:
                pop["population_policy"].initial_allocation(self, app_name)

        """
        Creating initial deploy of services
        """
        for place in self.placement_policy.itervalues():
            for app_name in place["apps"]:

                print "APP_NAME ",app_name
                place["placement_policy"].initial_allocation(self, app_name)  # internally consideres the apps in charge

        """
        A internal DES process will stop the simulation,
        *Simpy.run.until* wait to all pipers are empty. So, hundreds of messages should be service... We force with the stop
        """
        time_shift = 200
        distribution = deterministic_distribution(name="SIM_Deterministic", time=time_shift)
        self.env.process(self.__add_stop_monitor("Stop_Control_Monitor",self.__ctrl_progress_monitor,distribution,show_progress_monitor,time_shift=time_shift))

        # if mobile_behaviour:
        #     """
        #     Updating control variables of mobile environment
        #     """
        #     self.update_service_coverage()


        self.print_debug_assignaments()


        """
        RUN
        """
        self.until = until
        if not test_initial_deploy:
            self.env.run(until=until) #This does not stop the simpy.simulation at time. We have to force the stop

        self.metrics.close()
