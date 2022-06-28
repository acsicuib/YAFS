from yafs.selection import Selection
import networkx as nx

class MinShortPath(Selection):

    def __init__(self):
        super(MinShortPath, self).__init__()
        #Always it choices the first DES process, It means only one controller.
        #This implementations is so simple, please see the VRGameFog-IfogSim-WL Selection placement to understand better the selection process

    def get_path(self, sim, app_name, message, topology_src, alloc_DES, alloc_module, traffic, from_des):
        """
        Get the path between a node of the topology and a module deployed in a node. Furthermore it chooses the process deployed in that node.
        """
        node_src = topology_src  # TOPOLOGY SOURCE where the message is generated

        # print "Node (Topo id): %s" %node_src
        # print "Service DST: %s "%message.dst
        DES_dst = alloc_module[app_name][message.dst]
        # print "DES DST: %s" % DES_dst
        minLenPath = float('inf')
        minPath = []
        bestDES = 0
        for des in DES_dst:
            node_dst = sim.alloc_DES[des]
            path = list(nx.shortest_path(sim.topology.G, source=node_src, target=node_dst))
            if len(path) < minLenPath:
                minLenPath = len(path)
                minPath = [path]
                bestDES = [des]

        return minPath, bestDES


