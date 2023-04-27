from yafs.selection import Selection
import networkx as nx
from collections import Counter

from networkx.algorithms.shortest_paths.generic import _build_paths_from_predecessors


# //single_soure_dikjstra
class FastestRouteSelection(Selection):

    def __init__(self):
        self.cache = {}
        self.counter = Counter(list())
        self.invalid_cache_value = True

        self.controlServices = {}
        # key: a service
        # value : a list of idDevices
        super(FastestRouteSelection, self).__init__()

    # def func(u, v, d):
    #     node_u_wt = sim.topology.G.nodes[u].get("node_weight", 1)
    #     node_v_wt = sim.topology.G.nodes[v].get("node_weight", 1)
    #     edge_wt = d.get("weight", 1)
    #
    #     return node_u_wt / 2 + node_v_wt / 2 + edge_wt

    def compute_BEST_DES(self, node_src, alloc_DES, sim, DES_dst, message):
        try:
            best_time = float('inf')
            minPath = []
            bestDES = []
            moreDES = []
            # print len(DES_dst)
            max_bw = -1
            selected_paths = []

            for dev in DES_dst:
                node_dst = alloc_DES[dev]

                # flow_value, flow_dict = nx.maximum_flow(sim.topology.G, node_src, node_dst, capacity='BW')

                all_paths = nx.all_simple_paths(sim.topology.G, source=node_src, target=node_dst)  # weight

                for path in all_paths:
                    min_bw = min(sim.topology.G.edges[path[i], path[i + 1]]['BW'] for i in range(len(path) - 1))
                    print("min_bw: %d" % min_bw)
                    print(path)
                    if min_bw > max_bw:
                        bestDES = dev
                        selected_paths = [path]
                        max_bw = min_bw
                    elif min_bw == max_bw:
                        selected_paths.append(path)

            if (len(selected_paths) > 1):
                final_path = selected_paths[0]
                for i in range(1, len(selected_paths)):
                    if (len(selected_paths[i]) > len(final_path)):
                        final_path = selected_paths[i]
                return final_path, bestDES
            return selected_paths, bestDES



        except (nx.NetworkXNoPath, nx.NodeNotFound) as e:
            self.logger.warning("There is no path between two nodes: %s - %s " % (node_src, node_dst))
            # print("Simulation must ends?)"
            return [], None

    def get_path(self, sim, app_name, message, topology_src, alloc_DES, alloc_module, traffic, from_des):
        node_src = topology_src  # entity that sends the message
        service = message.dst  # Name of the service
        DES_dst = alloc_module[app_name][message.dst]  # module sw that can serve the message

        # The number of nodes control the updating of the cache. If the number of nodes changes, the cache is totally cleaned.
        path, des = self.compute_BEST_DES(node_src, alloc_DES, sim, DES_dst, message)

        try:
            dc = int(des)
            self.counter[dc] += 1
            self.controlServices[(node_src, service)] = (path, des)
        except TypeError:  # The node is not linked with other nodes
            return [], None

        return [path], [des]

    def clear_routing_cache(self):
        self.invalid_cache_value = False
        self.cache = {}
        self.counter = Counter(list())
        self.controlServices = {}

    def get_path_from_failure(self, sim, message, link, alloc_DES, alloc_module, traffic, ctime, from_des):

        idx = message.path.index(link[0])
        # print "IDX: ",idx
        if idx == len(message.path):
            # The node who serves ... not possible case
            return [], []
        else:
            node_src = message.path[idx]  # In this point to the other entity the system fail
            # print "SRC: ",node_src # 164

            node_dst = message.path[len(message.path) - 1]
            # print "DST: ",node_dst #261
            # print "INT: ",message.dst_int #301

            path, des = self.get_path(sim, message.app_name, message, node_src, alloc_DES, alloc_module, traffic,
                                      from_des)
            if len(path[0]) > 0:
                # print path # [[164, 130, 380, 110, 216]]
                # print des # [40]

                concPath = message.path[0:message.path.index(path[0][0])] + path[0]
                # print concPath # [86, 242, 160, 164, 130, 380, 110, 216]
                newINT = node_src  # path[0][2]
                # print newINT # 380

                message.dst_int = newINT
                return [concPath], des
            else:
                return [], []
