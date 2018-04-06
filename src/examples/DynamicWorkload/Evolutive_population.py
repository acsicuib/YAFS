
from yafs.population import Population

import random
import networkx as nx

class Population_Move(Population):

    def __init__(self,srcs,node_dst, **kwargs):
        self.number_generators = srcs
        self.node_dst = node_dst
        super(Population_Move, self).__init__(**kwargs)

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
            best_device = ctrl["id"]
            for number in range(ctrl["number"]):
                sim.deploy_sink(app_name, node=best_device, module=module)


    def run(self, sim):
        self.logger.debug("Activiting - Population movement")
        #para cada modulo generador desplegado en la topologia
        #-- trazo el camino mas cercano hacia un modulo
        #    -- muevo dicho generador hasta el siguiente path -1 del anterior trazado
        for key in sim.alloc_source.keys():
            node_src = sim.alloc_DES[key]
            path = list(nx.shortest_path(sim.topology.G, source=node_src, target=self.node_dst))
            print path
            if len(path)>2:
                next_src_position = path[1]
                #print path,next_src_position
                sim.alloc_DES[key] =  next_src_position
            else:
                None
                #This source cannot move more


        #print "-" * 40
        #print "DES\t| TOPO \t| Src.Mod \t| Modules"
        #print "-" * 40
        #for k in sim.alloc_DES:
        #    print k, "\t|", self.alloc_DES[k], "\t|", self.alloc_source[k][
        #        "module"] if k in self.alloc_source.keys() else "--", "\t\t|", fullAssignation[k][
        #        "Module"] if k in fullAssignation.keys() else "--"
        #print "-" * 40


