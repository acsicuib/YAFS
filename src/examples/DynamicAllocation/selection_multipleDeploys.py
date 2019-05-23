
from yafs.selection import Selection
import networkx as nx
import math
class CloudPath_RR(Selection):


    def __init__(self):
        self.rr = {}  # for a each type of service, we have a mod-counter

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
        super(BroadPath, self).__init__()
        self.most_near_calculator_to_client = {}
        self.invalid_cache_value = -1

    def compute_most_near(self,node_src,alloc_DES,sim,DES_dst):
        """
        This functions caches the minimun path among client-devices and fog-devices-Module Calculator and it chooses the best calculator process deployed in that node
        """
        #By Placement policy we know that:

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

    def get_path(self, sim, app_name, message, topology_src, alloc_DES, alloc_module, traffic, from_des):
        """
        Get the path between a node of the topology and a module deployed in a node. Furthermore it chooses the process deployed in that node.

        """
        node_src = topology_src  # TOPOLOGY SOURCE where the message is generated

        # print "Node (Topo id): %s" %node_src
        # print "Service DST: %s "%message.dst
        DES_dst = alloc_module[app_name][message.dst]

        # print "DES DST: %s" % DES_dst

        if self.invalid_cache_value == len(DES_dst): #Cache updated

            if node_src not in self.most_near_calculator_to_client.keys():
                #This value is not in the cache
                self.most_near_calculator_to_client[node_src] = self.compute_most_near(
                    node_src,alloc_DES, sim,DES_dst)

            path,des = self.most_near_calculator_to_client[node_src]

            # print "\t NEW DES_DST: %s" % DES_dst
            # print "PATH ",path
            # print "DES  ",des

            return [path],[des]

        else:
            self.invalid_cache_value = len(DES_dst)
            # print "\t Invalid cached "
            # print "\t NEW DES_DST: %s" %DES_dst
            self.most_near_calculator_to_client = {} #reset previous path-cached values

            # This value is not in the cache
            self.most_near_calculator_to_client[node_src] = self.compute_most_near(
                    node_src, alloc_DES, sim, DES_dst)

            path, des = self.most_near_calculator_to_client[node_src]

            # print "\t NEW DES_DST: %s" % DES_dst
            # print "PATH ",path
            # print "DES  ",des

            return [path], [des]

