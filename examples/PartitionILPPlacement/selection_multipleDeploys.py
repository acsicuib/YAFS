from yafs.selection import Selection
from yafs.topology import *
import networkx as nx

class DeviceSpeedAwareRouting(Selection):
    def __init__(self):
        self.cache = {}
        self.invalid_cache_value = -1
        self.previous_number_of_nodes = -1
        super(DeviceSpeedAwareRouting, self).__init__()



    def compute_DSAR(self, node_src, alloc_DES, sim, DES_dst,message):
        try:
            bestSpeed = float('inf')
            minPath = []
            bestDES = []
            #print len(DES_dst)
            for dev in DES_dst:
                #print "DES :",dev
                node_dst = alloc_DES[dev]
                path = list(nx.shortest_path(sim.topology.G, source=node_src, target=node_dst))
                speed = 0
                for i in range(len(path) - 1):
                    link = (path[i], path[i + 1])
                   # print "LINK : ",link
                   # print " BYTES :", message.bytes
                    speed += sim.topology.G.edges[link][Topology.LINK_PR] + (message.bytes/sim.topology.G.edges[link][Topology.LINK_BW])
                    #print sim.topology.G.edges[link][Topology.LINK_BW]

                att_node = sim.topology.get_nodes_att()[path[-1]]

                time_service = message.inst / float(att_node["IPT"])
                speed += time_service  # HW - computation of last node
                #print "SPEED: ",speed
                if  speed < bestSpeed:
                    bestSpeed = speed
                    minPath = path
                    bestDES = dev

            #print bestDES,minPath
            return minPath, bestDES

        except (nx.NetworkXNoPath, nx.NodeNotFound) as e:
            self.logger.warning("There is no path between two nodes: %s - %s " % (node_src, node_dst))
            # print "Simulation ends?"
            return [], None

    def get_path(self, sim, app_name, message, topology_src, alloc_DES, alloc_module, traffic, from_des):
        node_src = topology_src #entity that sends the message

        DES_dst = alloc_module[app_name][message.dst] #module sw that can serve the message

        #print "Enrouting from SRC: %i  -<->- DES %s"%(node_src,DES_dst)

        #The number of nodes control the updating of the cache. If the number of nodes changes, the cache is totally cleaned.
        currentNodes = len(sim.topology.G.nodes)
        if not self.invalid_cache_value == currentNodes:
            self.invalid_cache_value = currentNodes
            self.cache = {}


        if (node_src,tuple(DES_dst)) not in self.cache.keys():
            self.cache[node_src,tuple(DES_dst)] = self.compute_DSAR(node_src, alloc_DES, sim, DES_dst,message)

        path, des = self.cache[node_src,tuple(DES_dst)]

        return [path], [des]

    def get_path_from_failure(self, sim, message, link, alloc_DES, alloc_module, traffic, ctime, from_des):
        # print "Example of enrouting"
        #print message.path # [86, 242, 160, 164, 130, 301, 281, 216]
        #print message.dst_int  # 301
        #print link #(130, 301) link is broken! 301 is unreacheble

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


