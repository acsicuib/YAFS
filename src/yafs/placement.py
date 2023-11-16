"""
    This type of algorithm have two obligatory functions:

        *initial_allocation*: invoked at the start of the simulation

        *run* invoked according to the assigned temporal distribution.

"""

import logging


class Placement(object):
    """
    A placement (or allocation) algorithm controls where to locate the service modules and their replicas in the different nodes of the topology, according to load criteria, or other objectives.

    .. note:: A class interface

    Args:
        name (str): associated name

        activation_dist (function): a distribution function to active the *run* function in execution time

    Kwargs:
        param (dict): the parameters of the *activation_dist*

    """

    def __init__(self,name,activation_dist=None,logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.name=name
        self.activation_dist = activation_dist
        self.scaleServices = []


    def scaleService(self,scale):
        self.scaleServices = scale

    def get_next_activation(self):
        """
        Returns:
            the next time to be activated
        """
        return self.activation_dist.next()


    def initial_allocation(self,sim,app_name):
        """
        Given an ecosystem, it starts the allocation of modules in the topology.

        Args:
            sim (:mod:yafs.core.Sim)
            app_name (String)

        .. attention:: override required
        """


    def run(self,sim):
        """
        This method will be invoked during the simulation to change the assignment of the modules to the topology

        Args:
            sim (:mod: yafs.core.Sim)
        """
        self.logger.debug("Activiting - RUN - Placement")

class JSONPlacement(Placement):
    def __init__(self, json, **kwargs):
        super(JSONPlacement, self).__init__(**kwargs)
        self.data = json

    def initial_allocation(self, sim, app_name):
        for item in self.data["initialAllocation"]:
            if app_name == item["app"]:
                # app_name = item["app"]
                module = item["module_name"]
                idtopo = item["id_resource"]
                app = sim.apps[app_name]
                services = app.services
                idDES = sim.deploy_module(app_name, module, services[module],[idtopo])


class JSONPlacementOnCloud(Placement):
    def __init__(self, json,idCloud, **kwargs):
        super(JSONPlacementOnCloud, self).__init__(**kwargs)
        self.data = json
        self.idCloud = idCloud

    def initial_allocation(self, sim, app_name):

        for item in self.data["initialAllocation"]:
            if app_name == item["app"]:
                app_name = item["app"]
                module = item["module_name"]

                app = sim.apps[app_name]
                services = app.services
                idDES = sim.deploy_module(app_name, module, services[module],[self.idCloud])



class ClusterPlacement(Placement):
    """
    This implementation locates the services of the application in the cheapest cluster regardless of where the sources or sinks are located.

    It only runs once, in the initialization.

    """
    def initial_allocation(self, sim, app_name):
        #We find the ID-nodo/resource
        value = {"model": "Cluster"}
        id_cluster = sim.topology.find_IDs(value) #there is only ONE Cluster
        value = {"model": "m-"}
        id_mobiles = sim.topology.find_IDs(value)

        #Given an application we get its modules implemented
        app = sim.apps[app_name]
        services = app.services

        for module in services.keys():
            if "Coordinator" == module:
                if "Coordinator" in self.scaleServices.keys():
                    # print self.scaleServices["Coordinator"]
                    for rep in range(0,self.scaleServices["Coordinator"]):
                        idDES = sim.deploy_module(app_name,module,services[module],id_cluster) #Deploy as many modules as elements in the array

            elif "Calculator" == module:
                if "Calculator" in self.scaleServices.keys():
                    for rep in range(0, self.scaleServices["Calculator"]):
                        idDES = sim.deploy_module(app_name,module,services[module],id_cluster)

            elif "Client" == module:
                idDES = sim.deploy_module(app_name,module, services[module],id_mobiles)

    #end function

    # def run(self, sim):
    #     """
    #     This method will be invoked during the simulation to change the assignment of the modules to the topology
    #
    #     Args:
    #         sim (:mod: yafs.core.Sim)
    #     """
    #     self.logger.debug("Activiting - Cluster Algorithm (do nothing)")


class EdgePlacement(Placement):
    """
    This implementation locates the services of the application in the cheapest cluster regardless of where the sources or sinks are located.

    It only runs once, in the initialization.

    """
    def initial_allocation(self, sim, app_name):
        #We find the ID-nodo/resource
        value = {"model": "Cluster"}
        id_cluster = sim.topology.find_IDs(value) #there is only ONE Cluster
        value = {"model": "d-"}
        id_proxies = sim.topology.find_IDs(value)



        value = {"model": "m-"}
        id_mobiles = sim.topology.find_IDs(value)

        #Given an application we get its modules implemented
        app = sim.apps[app_name]
        services = app.services

        for module in services.keys():

            print (module)

            if "Coordinator" == module:
                idDES = sim.deploy_module(app_name,module,services[module],id_cluster) #Deploy as many modules as elements in the array
            elif "Calculator" == module:
                idDES = sim.deploy_module(app_name,module,services[module],id_proxies)
            elif "Client" == module:
                idDES = sim.deploy_module(app_name,module, services[module],id_mobiles)




class NoPlacementOfModules(Placement):

    """
    This implementation locates the services of the application in the cheapest cluster regardless of where the sources or sinks are located.

    It only runs once, in the initialization.

    """
    def initial_allocation(self, sim, app_name):
        #The are not modules to be allocated
        None

