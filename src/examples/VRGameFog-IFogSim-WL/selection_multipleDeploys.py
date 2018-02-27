
from yafs.selection import Selection
import networkx as nx

class BroadPath(Selection):

    def __init__(self,numOfMobilesPerDept,cloud=True):
        super(BroadPath, self).__init__()
        self.numOfMobilesPerDept = numOfMobilesPerDept
        self.cloud = True
        self.round_robin_module_calculator = {}
        self.round_robin_module_coordinator = -1
        self.round_robin_module_coordinator_cloud = -1
        self.most_near_calculator_to_client = {}
        self.running_services={}


    def compute_most_near(self,node_src,alloc_DES,sim,DES_dst):
        """
        This functions caches the minimun path among client-devices and fog-devices-Module Calculator and it chooses the best calculator process deployed in that node
        """
        #By Placement policy we know that:
        value = {"model": "d-"}
        topoDST = sim.topology.find_IDs(value)
        minLenPath = 99999999999
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

        print self.running_services[last_dest_topo]

        if last_dest_topo not in self.round_robin_module_calculator:
            self.round_robin_module_calculator[last_dest_topo]=0
        else:
            self.round_robin_module_calculator[last_dest_topo] = (self.round_robin_module_calculator[last_dest_topo] + 1) % self.numOfMobilesPerDept

        nextDESServiceAtThatTopology = self.running_services[last_dest_topo][self.round_robin_module_calculator[last_dest_topo]]
        return minPath,nextDESServiceAtThatTopology

    def get_path(self, sim, app_name,message, topology_src, alloc_DES, alloc_module, traffic):
        """
        Get the path between a node of the topology and a module deployed in a node. Furthermore it chooses the process deployed in that node.

        """
        node_src = topology_src  # TOPOLOGY SOURCE where the message is generated

        # print "Node (Topo id): %s" %node_src
        # print "Service DST: %s "%message.dst
        DES_dst = alloc_module[app_name][message.dst]
        # print "DES DST: %s" % DES_dst

        ## SENSOR enrouting works with ca
        if not self.cloud:
            if message.name == "M.Sensor":
                ## CACHING ROUTE - Between NODE_SRC and MESSAGE.DST - MOST NEAR
                # Warning. In this example, our topology is constant
                if node_src not in self.most_near_calculator_to_client.keys():
                    self.most_near_calculator_to_client[node_src] = self.compute_most_near(
                        node_src,alloc_DES, sim,DES_dst)

                path,des = self.most_near_calculator_to_client[node_src]
                #
                # print "PATH ",path
                # print "DES  ",des
                return [path],[des]
        else:
            if message.dst == "Coordinator" and len(DES_dst) > 1:  # ALL OF THEM ARE IN THE SAME ELEMENT  - CLOUD
                if self.round_robin_module_coordinator_cloud < 0:
                    self.round_robin_module_coordinator_cloud = 0
                else:
                    self.round_robin_module_coordinator_cloud = (self.round_robin_module_coordinator_cloud + 1) % len(DES_dst)
                DES_dst = [DES_dst[self.round_robin_module_coordinator_cloud]]



        if message.dst == "Coordinator" and len(DES_dst)>1:  # ALL OF THEM ARE IN THE SAME ELEMENT  - CLOUD
            if self.round_robin_module_coordinator<0:
                self.round_robin_module_coordinator = 0
            else:
                self.round_robin_module_coordinator = (self.round_robin_module_coordinator+1)%len(DES_dst)
            DES_dst = [DES_dst[self.round_robin_module_coordinator]]

        if message.name == "M.Concentration" :
            DES_dst = [message.last_idDes[0]]

        best_path = []
        best_DES = []
        min_path = 99999999999 ## Not so good
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
