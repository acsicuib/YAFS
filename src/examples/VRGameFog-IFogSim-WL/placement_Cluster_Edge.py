"""
    This type of algorithm have two obligatory functions:

        *initial_allocation*: invoked at the start of the simulation

        *run* invoked according to the assigned temporal distribution.

"""

from yafs.placement import Placement

class CloudPlacement(Placement):
    """
    This implementation locates the services of the application in the cheapest cloud regardless of where the sources or sinks are located.

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


class FogPlacement(Placement):
    """
    This implementation locates the services of the application in the fog-device regardless of where the sources or sinks are located.

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
            if "Coordinator" == module:
                if "Coordinator" in self.scaleServices.keys():
                    for rep in range(0, self.scaleServices["Coordinator"]):
                        idDES = sim.deploy_module(app_name, module, services[module],id_cluster)  # Deploy as many modules as elements in the array
            elif "Calculator" == module:
                if "Calculator" in self.scaleServices.keys():
                    for rep in range(0, self.scaleServices["Calculator"]):
                        idDES = sim.deploy_module(app_name, module, services[module], id_proxies)
            elif "Client" == module:
                idDES = sim.deploy_module(app_name,module, services[module],id_mobiles)



