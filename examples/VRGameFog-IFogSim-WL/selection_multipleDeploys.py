
from yafs.selection import Selection
import networkx as nx

class CloudPath_RR(Selection):


    def __init__(self):
        self.rr = {}  # for a each type of service, we have a mod-counter

    def get_path(self, sim, app_name, message, topology_src, alloc_DES, alloc_module, traffic,from_des):

        node_src = topology_src
        DES_dst = alloc_module[app_name][message.dst]  # returns an array with all DES process serving

        if message.dst not in self.rr.keys():
            self.rr[message.dst] = 0

        # print "GET PATH"
        # print "\tNode _ src (id_topology): %i" % node_src
        # print "\tRequest service: %s " % (message.dst)
        # print "\tProcess serving that service: %s (pos ID: %i)" % (DES_dst, self.rr[message.dst])

        bestPath = []
        bestDES = []

        if message.name == "M.Sensor" or message.name == "M.Player_Game_State":  # both messages are adressed to modules deployed in cloud
            next_DES_dst = DES_dst[self.rr[message.dst]]
            dst_node = alloc_DES[next_DES_dst]

            path = list(nx.shortest_path(sim.topology.G, source=node_src, target=dst_node))
            bestPath = [path]
            bestDES = [next_DES_dst]
            self.rr[message.dst] = (self.rr[message.dst] + 1) % len(DES_dst)
            return bestPath, bestDES

        if message.name == "M.Concentration":
            DES_dst = [message.last_idDes[0]]

        best_path = []
        best_DES = []
        min_path = float("inf")
        for des in DES_dst:
            dst_node = alloc_DES[des]
            path = list(nx.shortest_path(sim.topology.G, source=node_src, target=dst_node))  ###
            if message.broadcasting:
                best_path.append(path)
                best_DES.append(des)
            else:
                if len(path) <= min_path:
                    min_path = len(path)
                    best_path = [path]
                    best_DES = [des]

        return best_path, best_DES




class BroadPath(Selection):

    def __init__(self,numOfMobilesPerDept):
        super(BroadPath, self).__init__()
        self.numOfMobilesPerDept = numOfMobilesPerDept
        self.round_robin_module_calculator = {}

        self.rr = {}

        self.most_near_calculator_to_client = {}
        self.running_services={}


    def compute_most_near(self,node_src,alloc_DES,sim,DES_dst):
        """
        This functions caches the minimun path among client-devices and fog-devices-Module Calculator and it chooses the best calculator process deployed in that node
        """
        #By Placement policy we know that:
        value = {"model": "d-"}
        topoDST = sim.topology.find_IDs(value)
        minLenPath = float('inf')
        minPath = []
        for dev in topoDST:
            path = list(nx.shortest_path(sim.topology.G, source=node_src, target=dev))
            if len(path)<minLenPath:
                minLenPath = len(path)
                minPath = path

        # print "MIN PATH ",minPath
        last_dest_topo = minPath[len(minPath) - 1]
        if last_dest_topo not in self.running_services.keys():
            run_service = []
            for des in DES_dst:
                if alloc_DES[des] == last_dest_topo:
                    # print "This process are running in this device: ", des  ### Same times that numOfMobilesPerDept by level
                    run_service.append(des)
            self.running_services[last_dest_topo] = run_service

        # print self.running_services[last_dest_topo]

        if last_dest_topo not in self.round_robin_module_calculator:
            self.round_robin_module_calculator[last_dest_topo]=0
        else:
            self.round_robin_module_calculator[last_dest_topo] = (self.round_robin_module_calculator[last_dest_topo] + 1) % self.numOfMobilesPerDept

        nextDESServiceAtThatTopology = self.running_services[last_dest_topo][self.round_robin_module_calculator[last_dest_topo]]
        return minPath,nextDESServiceAtThatTopology

    def get_path(self, sim, app_name,message, topology_src, alloc_DES, alloc_module, traffic,from_des):
        """
        Get the path between a node of the topology and a module deployed in a node. Furthermore it chooses the process deployed in that node.

        """
        node_src = topology_src  # TOPOLOGY SOURCE where the message is generated

        # print "Node (Topo id): %s" %node_src
        # print "Service DST: %s "%message.dst
        DES_dst = alloc_module[app_name][message.dst]
        # print "DES DST: %s" % DES_dst

        ## SENSOR enrouting works with ca
        if message.name == "M.Sensor":
            ## CACHING ROUTE - Between NODE_SRC and MESSAGE.DST - MOST NEAR
            # Warning. In this example, our topology is constant
            if node_src not in self.most_near_calculator_to_client.keys():
                self.most_near_calculator_to_client[node_src] = self.compute_most_near(
                    node_src,alloc_DES, sim,DES_dst)

            path,des = self.most_near_calculator_to_client[node_src]

            # print "PATH ",path
            # print "DES  ",des
            return [path],[des]

        if message.dst == "Coordinator":  # ALL OF THEM ARE IN THE SAME ELEMENT  - CLOUD
            if message.dst not in self.rr.keys():
                self.rr[message.dst] = 0
                for ix, des in enumerate(DES_dst):
                    if self.rr[message.dst] == ix:
                        dst_node = alloc_DES[des]
                        path = list(nx.shortest_path(sim.topology.G, source=node_src, target=dst_node))
                        bestPath = [path]
                        bestDES = [des]
                        self.rr[message.dst] = (self.rr[message.dst] + 1) % len(DES_dst)
                        return bestPath, bestDES

        if message.name == "M.Concentration" :
            DES_dst = [message.last_idDes[0]]

        best_path = []
        best_DES = []
        min_path = float("inf")
        for des in DES_dst:
            dst_node = alloc_DES[des]
            path = list(nx.shortest_path(sim.topology.G, source=node_src, target=dst_node)) ###
            if message.broadcasting:
                best_path.append(path)
                best_DES.append(des)
            else:
                if len(path) <= min_path:
                    min_path = len(path)
                    best_path = [path]
                    best_DES = [des]

        return best_path,best_DES
