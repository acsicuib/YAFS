from yafs.selection import Selection
import networkx as nx
import heapq

class My_Path_Selector(Selection):
    """Among all possible shorter paths, returns the first."""
    path_final = []

    def get_path(self, sim, app_name,message, topology_src, alloc_DES, alloc_module, traffic,from_des):
        paths = []
        dst_idDES = []

        node_src = topology_src #TOPOLOGY SOURCE where the message is generated
        DES_dst = alloc_module[app_name][message.dst]
        edges = sim.topology.G.edges;
        edges = {}
        for edge in sim.topology.get_edges():
            if edge[0] not in edges.keys():
                #print ("edge: ", edge)
                edges[edge[0]] = list()
            if edge[1] not in edges.keys():
                #print("edge: ", edge)
                edges[edge[1]] = list()
            edges[edge[0]].append(edge[1])
            edges[edge[1]].append(edge[0])
            #print(sim.topology.get_edges())
            #print ("teste:", sim.topology.get_edge(edge)["BW"])
        #print("didionario: ", edges)


        #Among all possible path we choose the smallest
        bestPath = []
        bestDES = []
        #print ("fun.... ", DES_dst)
        for des in DES_dst:
            dst_node = alloc_DES[des]
            path = self.dijkstra_with_weight(sim.topology, node_src, dst_node, edges)
            bestPath = [path]
            bestDES  = [des]
            #print (path)
        # print("->>>> ", bestPath)
        self.path_final = bestPath
        return bestPath, bestDES

    def dijkstra_with_weight(self, topology, start_node, end_node, edges, weight_unit = 'BW'):
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
                # weight = 1/link[weight_unit]
                # weight = 1/link["BW"]
                # weight = 1/link["PR"]
                weight = 1/link["BW"] + link['PR']

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