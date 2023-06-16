from yafs.selection import Selection
import networkx as nx
import heapq


class MyPathSelector(Selection):
    """Among all possible shorter paths, returns the first."""
    path_final = []

    def get_path(self, sim, app_name,message, topology_src, alloc_DES, alloc_module, traffic,from_des):

        node_src = topology_src #TOPOLOGY SOURCE where the message is generated
        DES_dst = alloc_module[app_name][message.dst]

        #matriz de adjacencia
        edges = {}
        for edge in sim.topology.get_edges():
            if edge[0] not in edges.keys():
                edges[edge[0]] = list()
            if edge[1] not in edges.keys():
                edges[edge[1]] = list()
            edges[edge[0]].append(edge[1])
            edges[edge[1]].append(edge[0])


        #Among all possible path we choose the smallest
        bestPath = []
        bestDES = []
        for des in DES_dst:
            dst_node = alloc_DES[des]
            path = self.dijkstra_with_bw(sim.topology, node_src, dst_node, edges)
            bestPath = [path]
            bestDES = [des]
            #print (path)
        #print("------------------path------------------\n", bestPath)
        self.path_final = bestPath

        return bestPath, bestDES

    def dijkstra_with_bw(self, topology, start_node, end_node, edges):
        # Create a dictionary to hold the distance from the start node to each node
        distance = {}
        for node in topology.get_nodes():
            distance[node] = float('inf')
        distance[start_node] = 0

        # Create a dictionary to hold the previous node in the shortest path
        previous = {}
        for node in topology.get_nodes():
            previous[node] = None

        # Create a list of unvisited nodes
        unvisited = list(topology.get_nodes())

        # Process nodes until the end node is reached
        while end_node in unvisited:
            # Find the node with the smallest distance
            current_node = None
            current_distance = float('inf')
            for node in unvisited:
                if distance[node] < current_distance:
                    current_node = node
                    current_distance = distance[node]

            # Remove the current node from the unvisited list
            unvisited.remove(current_node)

            # Iterate over the links from the current node to its neighbors

            for dest in edges[current_node]:
                link = topology.get_edge((current_node, dest))
                neighbor = dest

                # Calculate the distance to the neighbor node using the bandwidth as weight
                weight = 1/link["BW"]
                new_distance = current_distance + weight

                # If the new distance is shorter, update the distance and previous node
                if new_distance < distance[neighbor]:
                    distance[neighbor] = new_distance
                    previous[neighbor] = current_node

        # Build the shortest path by following the previous nodes from the end node to the start node
        path = []
        node = end_node
        while node is not None:
            path.append(node)
            node = previous[node]
        path.reverse()

        return path

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
