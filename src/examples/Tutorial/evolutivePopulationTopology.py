from yafs.population import Population
import networkx as nx


class SimpleDynamicChanges(Population):
    """
    This implementation of a population algorithm statically assigns the generation of a source in a node of the topology. It is only invoked in the initialization.

    Extends: :mod: Population
    """
    def __init__(self, run_times, **kwargs):
        self.run_times = run_times
        super(SimpleDynamicChanges, self).__init__(**kwargs)


    def initial_allocation(self,sim,app_name):

        # Assignment of SINK and SOURCE pure modules
        for id_entity in sim.topology.nodeAttributes:
            entity = sim.topology.nodeAttributes[id_entity]
            for ctrl in self.sink_control:
                # A node can have several sinks modules
                if entity["model"]==ctrl["model"]:
                    #In this node there is a sink
                    module = ctrl["module"]
                    for number in range(ctrl["number"]):
                        sim.deploy_sink(app_name, node=id_entity, module=module)
            # end for sink control

            for ctrl in self.src_control:
                # A node can have several source modules
                if entity["model"] == ctrl["model"]:
                    msg = ctrl["message"]
                    dst = ctrl["distribution"]
                    for number in range(ctrl["number"]):
                        idsrc = sim.deploy_source(app_name,id_node=id_entity,msg=msg,distribution=dst)
                        # the idsrc can be used to control the deactivation of the process in a dynamic behaviour

            # end for src control
        # end assignments


    def run(self, sim):

        if self.run_times == 0: # In addition, we can stop the process according to any criteria
            sim.stop_process(sim.get_DES(self.name))
        else:
            self.run_times -=1
            # Run whatever you want
            print("Running Population-Evolution: %i" %self.run_times)

