from yafs.selection import Selection
import networkx as nx
from collections import Counter

from heapq import heappop, heappush
from itertools import count


class DeviceSpeedAwareRouting(Selection):

    def __init__(self):
        self.cache = {}
        self.counter = Counter(list())
        self.invalid_cache_value = True

        self.controlServices = {}
        # key: a service
        # value : a list of idDevices
        super(DeviceSpeedAwareRouting, self).__init__()

    def compute_BEST_DES(self, node_src, alloc_DES, sim, DES_dst, message):
        try:
            bestLong = float('inf')
            minPath = []
            bestDES = []
            moreDES = []
            #print len(DES_dst)
            for dev in DES_dst:
                node_dst = alloc_DES[dev]
                path = list(nx.shortest_path(sim.topology.G, source=node_src, target=node_dst))
                long = len(path)

                if long < bestLong:
                    bestLong = long
                    minPath = path
                    bestDES = dev
                    moreDES = []
                elif long == bestLong:
                    # Another instance service is deployed in the same node
                    if len(moreDES)==0:
                        moreDES.append(bestDES)
                    moreDES.append(dev)


            # There are two or more options in a node: #ROUND ROBIN Schedule
            if len(moreDES)>0:
                ### RETURN
                bestValue = 0
                minCounter =  float('inf')
                for idx,service in enumerate(moreDES):
                    if not service in self.counter:
                        return minPath, service
                    else:
                        if minCounter < self.counter[service]:
                            minCounter = self.counter
                            bestValue = idx
                return minPath, moreDES[bestValue]
            else:
                return minPath, bestDES

        except (nx.NetworkXNoPath, nx.NodeNotFound) as e:
            self.logger.warning("There is no path between two nodes: %s - %s " % (node_src, node_dst))
            # print("Simulation must ends?)"
            return [], None

    def get_path(self, sim, app_name, message, topology_src, alloc_DES, alloc_module, traffic, from_des):
        node_src = topology_src #entity that sends the message
        service = message.dst         # Name of the service
        DES_dst = alloc_module[app_name][message.dst] #module sw that can serve the message

        #The number of nodes control the updating of the cache. If the number of nodes changes, the cache is totally cleaned.
        path, des = self.compute_BEST_DES(node_src, alloc_DES, sim, DES_dst,message)

        try:
            dc = int(des)
            self.counter[dc] += 1
            self.controlServices[(node_src, service)] = (path, des)
        except TypeError: # The node is not linked with other nodes
            return [], None

        return [path], [des]

    def clear_routing_cache(self):
        self.invalid_cache_value = False
        self.cache = {}
        self.counter = Counter(list())
        self.controlServices = {}

    def get_path_from_failure(self, sim, message, link, alloc_DES, alloc_module, traffic, ctime, from_des):

        idx = message.path.index(link[0])
        #print "IDX: ",idx
        if idx == len(message.path):
            # The node who serves ... not possible case
            return [],[]
        else:
            node_src = message.path[idx] #In this point to the other entity the system fail
            # print "SRC: ",node_src # 164

            node_dst = message.path[len(message.path)-1]
            # print "DST: ",node_dst #261
            # print "INT: ",message.dst_int #301

            path, des = self.get_path(sim,message.app_name,message,node_src,alloc_DES,alloc_module,traffic,from_des)
            if len(path[0])>0:
                # print path # [[164, 130, 380, 110, 216]]
                # print des # [40]

                concPath = message.path[0:message.path.index(path[0][0])] + path[0]
                # print concPath # [86, 242, 160, 164, 130, 380, 110, 216]
                newINT = node_src #path[0][2]
                # print newINT # 380

                message.dst_int = newINT
                return [concPath], des
            else:
                return [],[]








def _weight_function(G, weight):
    if callable(weight):
        return weight

    # If the weight keyword argument is not callable, we assume it is a
    # string representing the edge attribute containing the weight of
    # the edge.
    if G.is_multigraph():
        return lambda u, v, d: min(attr.get(weight, 1) for attr in d.values())
    return lambda u, v, data: data.get(weight, 1)


# bidirectional_shortest_path adaptado para cost = cost 1/cost
def maxWeightSelector(G, source, target, weight="weight"):
    if source not in G or target not in G:
        msg = f"Either source {source} or target {target} is not in G"
        raise nx.NodeNotFound(msg)

    if source == target:
        return (0, [source])

    weight = _weight_function(G, weight)
    push = heappush
    pop = heappop
    # Init:  [Forward, Backward]
    dists = [{}, {}]  # dictionary of final distances
    paths = [{source: [source]}, {target: [target]}]  # dictionary of paths
    fringe = [[], []]  # heap of (distance, node) for choosing node to expand
    seen = [{source: 0}, {target: 0}]  # dict of distances to seen nodes
    c = count()
    # initialize fringe heap
    push(fringe[0], (0, next(c), source))
    push(fringe[1], (0, next(c), target))
    # neighs for extracting correct neighbor information
    if G.is_directed():
        neighs = [G._succ, G._pred]
    else:
        neighs = [G._adj, G._adj]
    # variables to hold shortest discovered path
    # finaldist = 1e30000
    finalpath = []
    dir = 1
    while fringe[0] and fringe[1]:
        # choose direction
        # dir == 0 is forward direction and dir == 1 is back
        dir = 1 - dir
        # extract closest to expand
        (dist, _, v) = pop(fringe[dir])
        if v in dists[dir]:
            # Shortest path to v has already been found
            continue
        # update distance
        dists[dir][v] = dist  # equal to seen[dir][v]
        if v in dists[1 - dir]:
            # if we have scanned v in both directions we are done
            # we have now discovered the shortest path
            return (finaldist, finalpath)

        for w, d in neighs[dir][v].items():
            # weight(v, w, d) for forward and weight(w, v, d) for back direction
            cost = weight(v, w, d) if dir == 0 else weight(w, v, d)
            cost = 1/cost                                               # <<<<< alterei aqui
            if cost is None:
                continue
            vwLength = dists[dir][v] + cost
            if w in dists[dir]:
                if vwLength < dists[dir][w]:
                    raise ValueError("Contradictory paths found: negative weights?")
            elif w not in seen[dir] or vwLength < seen[dir][w]:
                # relaxing
                seen[dir][w] = vwLength
                push(fringe[dir], (vwLength, next(c), w))
                paths[dir][w] = paths[dir][v] + [w]
                if w in seen[0] and w in seen[1]:
                    # see if this path is better than the already
                    # discovered shortest path
                    totaldist = seen[0][w] + seen[1][w]
                    if finalpath == [] or finaldist > totaldist:
                        finaldist = totaldist
                        revpath = paths[1][w][:]
                        revpath.reverse()
                        finalpath = paths[0][w] + revpath[1:]
    raise nx.NetworkXNoPath(f"No path between {source} and {target}.")

class MaxBW(Selection):

    def get_path(self, sim, app_name, message, topology_src, alloc_DES, alloc_module, traffic,from_des):

        """
        Computes the minimun path among the source elemento of the topology and the localizations of the module

        Return the path and the identifier of the module deployed in the last element of that path
        """
        node_src = topology_src
        DES_dst = alloc_module[app_name][message.dst]

        # print(("GET PATH"))
        # print(("\tNode _ src (id_topology): %i" %node_src))
        # print(("\tRequest service: %s " %message.dst))
        # print(("\tProcess serving that service: %s " %DES_dst))

        bestPath = []
        bestDES = []

        for des in DES_dst: ## In this case, there are only one deployment
            dst_node = alloc_DES[des]
            # print(("\t\t Looking the path to id_node: %i" %dst_node))

            _, paths = maxWeightSelector(sim.topology.G, node_src, dst_node, "BW")
            path = list(paths)

            bestPath = [path]
            bestDES = [des]

        return bestPath, bestDES



