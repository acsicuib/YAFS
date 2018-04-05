
from yafs.population import Population

import random


class Evolutive(Population):

    def __init__(self,fog,srcs, **kwargs):
       #TODO arreglar en otros casos
        self.fog_devices = fog
        self.number_generators = srcs
        super(Evolutive, self).__init__(**kwargs)

    def initial_allocation(self, sim, app_name):
        #ASSIGNAMENT of SOURCE - GENERATORS - ACTUATORS
        id_nodes = list(sim.topology.G.nodes())
        for ctrl in self.src_control:
            msg = ctrl["message"]
            dst = ctrl["distribution"]
            for item in range(self.number_generators):
                id = random.choice(id_nodes)
                for number in range(ctrl["number"]):
                    idsrc = sim.deploy_source(app_name, id_node=id, msg=msg, distribution=dst)

        # ASSIGNAMENT of the first SINK
        fog_device = self.fog_devices[0][0]
        del self.fog_devices[0]
        for ctrl in self.sink_control:
            module = ctrl["module"]
            for number in range(ctrl["number"]):
                sim.deploy_sink(app_name, node=fog_device, module=module)


    def run(self, sim):
        if len(self.fog_devices)>0:
            fog_device = self.fog_devices[0][0]
            del self.fog_devices[0]
            self.logger.debug("Activiting - RUN - Evolutive - Deploying a new actuator at position: %i"%fog_device)
            for ctrl in self.sink_control:
                module = ctrl["module"]
                app_name = ctrl["app"]
                for number in range(ctrl["number"]):
                    sim.deploy_sink(app_name, node=fog_device, module=module)


class Statical(Population):

    def __init__(self,srcs,**kwargs):
        self.number_generators = srcs
        super(Statical, self).__init__(**kwargs)

    def initial_allocation(self, sim, app_name):
        #ASSIGNAMENT of SOURCE - GENERATORS - ACTUATORS
        id_nodes = list(sim.topology.G.nodes())
        for ctrl in self.src_control:
            msg = ctrl["message"]
            dst = ctrl["distribution"]
            param = ctrl["param"]
            for item in range(self.number_generators):
                id = random.choice(id_nodes)
                for number in range(ctrl["number"]):
                    idsrc = sim.deploy_source(app_name, id_node=id, msg=msg, distribution=dst, param=param)

        # ASSIGNAMENT of the only one SINK
        for ctrl in self.sink_control:
            module = ctrl["module"]
            best_device  = ctrl["id"]
            for number in range(ctrl["number"]):
                sim.deploy_sink(app_name, node=best_device, module=module)
