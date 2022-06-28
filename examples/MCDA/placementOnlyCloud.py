"""
This class implements the initialization of the service but only in the cloud. We filter the rest of the assignments from the JSON file

In our case, we take advantatge from a previous study. For that reason, our json file contains more assignments.

"""
import logging

from yafs.placement import Placement

class JSONPlacementOnlyCloud(Placement):

    def __init__(self, json,idcloud,logger = None, **kwargs):
        super(JSONPlacementOnlyCloud, self).__init__(**kwargs)
        self.data = json
        self.idcloud = idcloud
        self.logger = logger or logging.getLogger(__name__)
        self.logger.info(" Placement Initialization of %s in NodeCLOUD: %i"%(self.name,self.idcloud))


    def initial_allocation(self, sim, app_name):
        for item in self.data["initialAllocation"]:
            idtopo = item["id_resource"]
            print idtopo
            if idtopo == self.idcloud:
                # print item
                app_name = item["app"]
                module = item["module_name"]
                app = sim.apps[app_name]
                services = app.services
                # print services[module]
                idDES = sim.deploy_module(app_name, module, services[module], [idtopo])