
from yafs.selection import Selection
import networkx as nx
import copy
import math
class CloudPath_RR(Selection):


    def __init__(self):
        self.rr = {}  # for a each type of service, we have a mod-counter
        self.messages_affected = []


    def get_path(self, sim, app_name, message, topology_src, alloc_DES, alloc_module, traffic, from_des):

        node_src = topology_src
        DES_dst = alloc_module[app_name][message.dst]  # returns an array with all DES process serving

        if message.dst not in self.rr.keys():
            self.rr[message.dst] = 0

        # print "GET PATH"
        # print "\tNode _ src (id_topology): %i" % node_src
        # print "\tRequest service: %s " % (message.dst)
        # print "\tProcess serving that service: %s (pos ID: %i)" % (DES_dst, self.rr[message.dst])

        next_DES_dst =DES_dst[self.rr[message.dst]]

        dst_node = alloc_DES[next_DES_dst]
        path = list(nx.shortest_path(sim.topology.G, source=node_src, target=dst_node))
        bestPath = [path]
        bestDES = [next_DES_dst]
        self.rr[message.dst] = (self.rr[message.dst] + 1) % len(DES_dst)

        return bestPath, bestDES

class BroadPath(Selection):

    def __init__(self):
        self.most_near_calculator_to_client = {}
        self.invalid_cache_value = -1
        super(BroadPath, self).__init__()

    def compute_most_near(self,node_src,alloc_DES,sim,DES_dst):
        """
        This functions caches the minimun path among client-devices and fog-devices-Module Calculator and it chooses the best calculator process deployed in that node
        """
        #By Placement policy we know that:
        try:
            minLenPath = float('inf')
            minPath = []
            bestDES = []
            for dev in DES_dst:
                node_dst = alloc_DES[dev]
                path = list(nx.shortest_path(sim.topology.G, source=node_src, target=node_dst))
                if len(path)<minLenPath:
                    minLenPath = len(path)
                    minPath = path
                    bestDES = dev

            return minPath,bestDES
        except nx.NetworkXNoPath as e:
            self.logger.warning("There is no path between two nodes: %s - %s " % (node_src, node_dst))
            print("Simulation ends?. Time:", sim.env.now)
            # sim.stop = True ## You can stop all DES process
            return [], None

        except nx.NodeNotFound as e:
            self.logger.warning("Node not found: %s - %s "%(node_src,node_dst))
            print("Simulation ends?. Time:",sim.env.now)
            # sim.stop = True ## You can stop all DES process
            return [],None

    def get_path(self, sim, app_name, message, topology_src, alloc_DES, alloc_module, traffic, from_des):
        """
        Get the path between a node of the topology and a module deployed in a node. Furthermore it chooses the process deployed in that node.


        """
        #In this case, there is not a cached system.
        node_src = topology_src

        # print "Node (Topo id): %s" %node_src
        # print "Service DST: %s "%message.dst
        DES_dst = alloc_module[app_name][message.dst]

        currentNodes = len(sim.topology.G.nodes())

        # print "DES DST: %s" % DES_dst

        if not self.invalid_cache_value == currentNodes:  # Cache updated
            self.invalid_cache_value = copy.copy(currentNodes)
            self.most_near_calculator_to_client = {}
            self.logger.warning("Cache will be updated")
            # print "Cache updated"

        # self.most_near_calculator_to_client = {}

        if node_src not in self.most_near_calculator_to_client.keys():
            self.most_near_calculator_to_client[node_src] = self.compute_most_near(
                 node_src,alloc_DES, sim,DES_dst)

        path,des = self.most_near_calculator_to_client[node_src]

            # print "\t NEW DES_DST: %s" % DES_dst
            # print "PATH ",path
            # print "DES  ",des

        return [path],[des]


    def get_path_from_failure(self, sim, message, link, alloc_DES, alloc_module, traffic, ctime, from_des):
        # print "Example of enrouting"
        # print message.path # [86, 242, 160, 164, 130, 301, 281, 216]
        # print message.dst_int  # 301
        # print link #(130, 301) link is broken! 301 is unreacheble

        idx = message.path.index(link[0])
        # print "idx: ", idx

        if idx == len(message.path):
            # The node who serves ... not possible case
            return [],[]
        else:
            node_src = message.path[idx-1]
            # print "SRC: ",node_src # 164

            node_dst = message.path[len(message.path)-1]
            #print "DST: ",node_dst #261
            #print "INT: ",message.dst_int #301


            path, des = self.get_path(sim, message.app_name, message, node_src, alloc_DES, alloc_module, traffic,
                                      from_des)




            if len(path[0]) > 1:
                # print "PAHT ",path # [[164, 130, 380, 110, 216]]
                # print "DES ",des # [40]

                concPath = message.path[0:message.path.index(path[0][0])] + path[0]
                # print "CPATH ",concPath # [86, 242, 160, 164, 130, 380, 110, 216]
                newINT = path[0][2]
                # print "NI ",newINT # 380

                message.dst_int = newINT
                return [concPath], des
            else:
                return [], []


