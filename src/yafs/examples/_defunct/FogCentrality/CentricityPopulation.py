from yafs.population import Population

class Statical(Population):
    """
    This implementation of a population algorithm statically assigns the generation of a source in a node of the topology. It is only invoked in the initialization.

    Extends: :mod: Population
    """

    def initial_allocation(self,sim,app_name):
        #Assignment of SINK and SOURCE pure modules

        for ctrl in self.sink_control:
            if "id" in ctrl.keys():
                module = ctrl["module"]
                for idx in ctrl["id"]:
                    sim.deploy_sink(app_name, node=idx, module=module)

        for ctrl in self.src_control:
            if "id" in ctrl.keys():
                msg = ctrl["message"]
                dst = ctrl["distribution"]
                for idx in ctrl["id"]:
                    idsrc = sim.deploy_source(app_name, id_node=idx, msg=msg, distribution=dst)


        #end assignments