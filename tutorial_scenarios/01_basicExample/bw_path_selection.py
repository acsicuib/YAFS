from yafs.selection import Selection
import networkx as nx

class FastestRouteSelection(Selection):

    def __init__(self):
        super(FastestRouteSelection, self).__init__()

    def get_path(self, sim, app_name, message, topology_src, alloc_DES, alloc_module, traffic, from_des):
        node_src = topology_src  # entity that sends the message
        service = message.dst  # Name of the service
        DES_dst = alloc_module[app_name][message.dst]  # module sw that can serve the message

        # Compute the shortest path between source and destination nodes, based on link bandwidth
        try:
            path = nx.shortest_path(sim.topology.G, source=node_src, target=alloc_DES[DES_dst], weight="BW")
        except (nx.NetworkXNoPath, nx.NodeNotFound) as e:
            self.logger.warning("There is no path between two nodes: %s - %s " % (node_src, alloc_DES[DES_dst]))
            return [], None

        # Return the computed path
        return [path], [DES_dst]
