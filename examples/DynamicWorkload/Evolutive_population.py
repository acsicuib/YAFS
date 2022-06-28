
from yafs.population import Population

import random
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd

class Population_Move(Population):

    def __init__(self,srcs,node_dst, **kwargs):
        self.number_generators = srcs
        self.node_dst = node_dst
        self.pos = None
        self.activation = 0
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
        if self.pos == None:
            self.pos = {}
            df = pd.read_csv("pos_network.csv")
            for r in df.iterrows():
                self.pos[r[0]] = (r[1].x, r[1].y)
            del df

        fig = plt.figure(figsize=(10, 8), dpi=100)
        ax = fig.add_subplot(111)
        nx.draw(sim.topology.G, with_labels=True, pos=self.pos, node_size=60, node_color="orange", font_size=5)

        # fig, ax = plt.subplots(nrows=1, ncols=1)  # create figure & 1 axis
        for node in sim.alloc_DES.values():
            # for id_s, service in enumerate(current_services):
            # for node in current_services[service]:
            #     node = sim.alloc_DES[key]
            #     print "WL in node: ",node
                if node != 72:
                    circle2 = plt.Circle(self.pos[node], 40, color="green", alpha=0.8)
                    ax.add_artist(circle2)

        #top centralized device
        circle2 = plt.Circle(self.pos[72], 60, color="red", alpha=0.8)
        ax.add_artist(circle2)

        # nx.draw(sim.topology.G, self.pos, node_color='gray', alpha=0.4)



        # labels = nx.draw_networkx_labels(sim.topology.G, self.pos)

        plt.text(2, 1000, "Step: %i" %self.activation , {'color': 'C0', 'fontsize': 16})
        # for i in range(10):
        #     plt.text(i, -.7, i, {'color': 'C2', 'fontsize': 10 + (i * .5)})  # app2
        # for i in range(10):
        #     plt.text(i, -1.2, 9 - i, {'color': 'C1', 'fontsize': 10 + (9 - i) * 0.5})  # app3

        fig.savefig('figure/net_%03d.png' % self.activation)  # save the figure to file
        plt.close(fig)  # close the figure
        # exit()


        #para cada modulo generador desplegado en la topologia
        #-- trazo el camino mas cercano hacia un modulo
        #    -- muevo dicho generador hasta el siguiente path -1 del anterior trazado




        for key in sim.alloc_source.keys():
            node_src = sim.alloc_DES[key]
            path = list(nx.shortest_path(sim.topology.G, source=node_src, target=self.node_dst))
            print(path)
            if len(path)>2:
                next_src_position = path[1]
                #print path,next_src_position
                sim.alloc_DES[key] =  next_src_position
            else:
                None
                #This source cannot move more



        self.activation +=1

        #print "-" * 40
        #print "DES\t| TOPO \t| Src.Mod \t| Modules"
        #print "-" * 40
        #for k in sim.alloc_DES:
        #    print k, "\t|", self.alloc_DES[k], "\t|", self.alloc_source[k][
        #        "module"] if k in self.alloc_source.keys() else "--", "\t\t|", fullAssignation[k][
        #        "Module"] if k in fullAssignation.keys() else "--"
        #print "-" * 40




