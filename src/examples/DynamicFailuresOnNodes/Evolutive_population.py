
from yafs.population import Population

import random


class Pop_and_Failures(Population):

    def __init__(self,srcs, **kwargs):
        self.number_generators = srcs
        self.nodes_removed = []
        self.count_down = 20
        self.limit = 200
        super(Pop_and_Failures, self).__init__(**kwargs)

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

        for ctrl in self.sink_control:
            module = ctrl["module"]
            ids_coefficient = ctrl["ids"]
            for id in ids_coefficient:
                for number in range(ctrl["number"]):
                    sim.deploy_sink(app_name, node=id[0], module=module)


    def getProcessFromThatNode(self,sim,node_to_remove):
        if node_to_remove in sim.alloc_DES.values():
            someModuleDeployed = False
            keys = []
            # This node can have multiples DES processes on itself
            for k, v in sim.alloc_DES.items():
                if v == node_to_remove:
                    keys.append(k)
            # key = sim.alloc_DES.keys()[sim.alloc_DES.values().index(node_to_remove)]
            for key in keys:
                # Information
                # print "\tNode %i - with a DES process: %i" % (node_to_remove, key)
                # This assignamnet can be a source/sensor module:
                if key in sim.alloc_source.keys():
                    # print "\t\t a sensor: %s" % sim.alloc_source[key]["module"]
                    ## Sources/Sensors modules are not removed
                    return False,[],False
                someModuleAssignament = sim.get_assigned_structured_modules_from_DES()
                if key in someModuleAssignament.keys():
                    # print "\t\t a module: %s" % someModuleAssignament[key]["module"]
                    if self.count_down<3:
                        return False, [], False
                    else:
                        self.count_down-=1
                        someModuleDeployed = True

            return True,keys,someModuleDeployed
        else:
            return True,[],False


    def run(self, sim):
        self.logger.debug("Activiting - Failure -  Removing a topology nodo == a network element, including edges")
        if self.limit >0:
            nodes =list(sim.topology.G.nodes())
            #print sim.alloc_DES
            is_removable = False
            node_to_remove = -1
            someModuleDeployed = False
            while not is_removable: ## WARNING: In this case there is a possibility of an infinite loop
                node_to_remove = random.choice(nodes)
                is_removable,keys_DES,someModuleDeployed = self.getProcessFromThatNode(sim,node_to_remove)

            self.logger.debug("Removing node: %i, Total nodes: %i" % (node_to_remove, len(nodes)))
            print("\tStopping some DES processes: %s"%keys_DES)

            self.nodes_removed.append({"id":node_to_remove,"module":someModuleDeployed,"time":sim.env.now})

            sim.remove_node(node_to_remove)
            

            self.limit -=1



