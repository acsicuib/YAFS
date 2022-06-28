from yafs.selection import Selection
import networkx as nx

class First_ShortestPath(Selection):
    """Among all possible shorter paths, returns the first."""

    def get_path(self, sim, app_name, message, topology_src, alloc_DES, alloc_module, traffic, from_des):

        node_src = topology_src

        DES_dst = alloc_module[app_name][message.dst]

        bestPath = []
        bestDES = []
        for des in DES_dst:
            dst_node = alloc_DES[des]

       #     print type(node_src)
        #    print type(dst_node)
         #   print "NODE SRC: %s" %node_src
          #  print "NODE DST: %s" %dst_node

            path = list(nx.shortest_path(sim.topology.G, source=node_src, target=str(dst_node)))
           # print path

            bestPath = [path]
            bestDES  = [des]

        return bestPath,bestDES
