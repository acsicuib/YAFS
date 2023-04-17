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

    def get_path_from_failure(self, graph, message, failed_link):
        # Find the path that avoids the failed link and is the fastest
        path = message.path
        for i, node in enumerate(path):
            if node in failed_link:
                if i == len(path) - 1:
                    # The failed link is at the destination, so there is no other path
                    return [], []
                else:
                    # Find another path that avoids the failed link and is the fastest
                    src = path[i - 1]
                    dst = path[-1]
                    for alt_path in nx.shortest_simple_paths(graph, source=src, target=dst, weight='bandwidth'):
                        if set(failed_link).isdisjoint(set(zip(alt_path, alt_path[1:]))):
                            return [alt_path], []
        # If no alternative path is found, return empty lists
        return [], []