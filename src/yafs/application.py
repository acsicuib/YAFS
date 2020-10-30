# -*- coding: utf-8 -*-
import random

class Message:
    """
    A message is set by the following values:

    Args:
        name (str): a name, unique for each application

        src (str): the name of module who send this message

        dst (dst): the nsame of module who receive this message

        inst (int): the number of instructions to be executed ((by default 0), Instead of MIPS, we use IPt since the time is relative to the simulation units.

        bytes (int): the size in bytes (by default 0)

    Internal args used in the **yafs.core** are:
        timestamp (float): simulation time. Instant of time that was created.

        path (list): a list of entities of the topology that has to travel to reach its target module from its source module.

        dst_int (int): an identifier of the intermediate entity in which it is in the process of transmission.

        app_name (str): the name of the application
    """

    def __init__(self, name, src, dst, instructions=0, bytes=0,broadcasting=False):
        self.name = name
        self.src = src
        self.dst = dst
        self.inst = instructions
        self.bytes = bytes

        self.timestamp = 0
        self.path = []
        self.dst_int = -1
        self.app_name = None
        self.timestamp_rec = 0

        self.idDES = None
        self.broadcasting = broadcasting
        self.last_idDes = []
        self.id = -1

        self.original_DES_src = None #This attribute identifies the user when multiple users are in the same node

    def __str__(self):
        print  ("{--")
        print (" Name: %s (%s)" %(self.name,self.id))
        print (" From (src): %s  to (dst): %s" %(self.src,self.dst))
        print (" --}")
        return ("")

def fractional_selectivity(threshold):
    return random.random() <= threshold


def create_applications_from_json(data):
    applications = {}
    for app in data:
        a = Application(name=app["name"])
        modules = [{"None": {"Type": Application.TYPE_SOURCE}}]
        for module in app["module"]:
            modules.append({module["name"]: {"RAM": module["RAM"], "Type": Application.TYPE_MODULE}})
        a.set_modules(modules)

        ms = {}
        for message in app["message"]:
            # print "Creando mensaje: %s" %message["name"]
            ms[message["name"]] = Message(message["name"], message["s"], message["d"],
                                          instructions=message["instructions"], bytes=message["bytes"])
            if message["s"] == "None":
                a.add_source_messages(ms[message["name"]])

        # print "Total mensajes creados %i" %len(ms.keys())
        for idx, message in enumerate(app["transmission"]):
            if "message_out" in message.keys():
                a.add_service_module(message["module"], ms[message["message_in"]], ms[message["message_out"]],
                                     fractional_selectivity, threshold=1.0)
            else:
                a.add_service_module(message["module"], ms[message["message_in"]])

        applications[app["name"]] = a

    return applications


class Application:
    """
    An application is defined by a DAG between modules that generate, compute and receive messages.

    Args:
        name (str): The name must be unique within the same topology.

    Returns:
        an application

    """
    TYPE_SOURCE = "SOURCE"  # "SENSOR"
    "A source is like sensor"

    TYPE_MODULE = "MODULE"
    "A module"

    TYPE_SINK = "SINK"
    "A sink is like actuator"

    def __init__(self, name):
        self.name = name
        self.services = {}
        self.messages = {}
        self.modules = []
        self.modules_src = []
        self.modules_sink = []
        self.data = {}

    def __str__(self):
        print ("___ APP. Name: %s" % self.name)
        print (" __ Transmissions ")
        for m in self.messages.values():
            print ("\tModule: None : M_In: %s  -> M_Out: %s " %(m.src,m.dst))

        for modulename in self.services.keys():
            m = self.services[modulename]
            print ("\t",modulename)
            for ser in m:
                if "message_in" in ser.keys():
                    try:
                            print ("\t\t M_In: %s  -> M_Out: %s " % (ser["message_in"].name, ser["message_out"].name))
                    except:
                            print ("\t\t M_In: %s  -> M_Out: [NOTHING] " % (ser["message_in"].name))
        return ""

    def set_modules(self,data):
        """
        Pure source or sink modules must be typified

        Args:
            data (dict) : a set of characteristic of modules
        """
        for module in data:
            name = list(module.keys())[0]
            type = list(module.values())[0]["Type"]
            if type == self.TYPE_SOURCE:
                self.modules_src.append(name)
            elif type == self.TYPE_SINK:
                self.modules_sink = name

            self.modules.append(name)

        self.data = data

        # self.modules_sink = modules
    # def set_module(self, modules, type_module):
    #     """
    #     Pure source or sink modules must be typified
    #
    #     Args:
    #         modules (list): a list of modules names
    #         type_module (str): TYPE_SOURCE or TYPE_SINK
    #     """
    #     if type_module == self.TYPE_SOURCE:
    #         self.modules_src = modules
    #     elif type_module == self.TYPE_SINK:
    #         self.modules_sink = modules
    #     elif type_module == self.TYPE_MODULE:
    #         self.modules_pure = modules

    def get_pure_modules(self):
        """
        Returns:
            a list of pure source and sink modules
        """
        return [s for s in self.modules if s not in self.modules_src and s not in self.modules_sink]

    def get_sink_modules(self):
        """
        Returns:
            a list of sink modules
        """
        return self.modules_sink

    def add_source_messages(self, msg):
        """
        Add in the application those messages that come from pure sources (sensors). This distinction allows them to be controlled by the (:mod:`Population`) algorithm
        """
        self.messages[msg.name] = msg


    def get_message(self,name):
        """
        Returns: a message instance from the identifier name
        """
        return self.messages[name]

    """
    ADD SERVICE
    """

    def add_service_source(self, module_name, distribution=None, message=None, module_dest=[], p=[]):
        """
        Link to each non-pure module a management for creating messages

        Args:
            module_name (str): module name

            distribution (function): a function with a distribution function

            message (Message): the message

            module_dest (list): a list of modules who can receive this message. Broadcasting.

            p (list): a list of probabilities to send this message. Broadcasting

        Kwargs:
            param_distribution (dict): the parameters for *distribution* function

        """
        if distribution is not None:
            if module_name not in self.services:
                self.services[module_name] = []
            self.services[module_name].append(
                {"type": Application.TYPE_SOURCE, "dist": distribution,
                 "message_out": message, "module_dest": module_dest, "p": p})

    def add_service_module(self, module_name, message_in, message_out="", distribution="", module_dest=[], p=[],
                           **param):

        """
        Link to each non-pure module a management of transfering of messages

        Args:
            module_name (str): module name

            message_in (Message): input message

            message_out (Message): output message. If Empty the module is a sink

            distribution (function): a function with a distribution function

            module_dest (list): a list of modules who can receive this message. Broadcasting.

            p (list): a list of probabilities to send this message. Broadcasting

        Kwargs:
            param (dict): the parameters for *distribution* function

        """
        if not module_name in self.services:
            self.services[module_name] = []

        self.services[module_name].append({"type": Application.TYPE_MODULE, "dist": distribution, "param": param,
                                           "message_in": message_in, "message_out": message_out,
                                           "module_dest": module_dest, "p": p})
