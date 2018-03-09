# -*- coding: utf-8 -*-
import logging


import networkx as nx




class Topology:
    """
    This class unifies the functions to deal with **Complex Networks** as a network topology within of the simulator. In addition, it facilitates its creation, and assignment of attributes.
    """

    LINK_BW = "BW"
    "Link feature: Bandwidth"

    LINK_PR = "PR"
    "Link feauture:  Propagation delay"

    # LINK_LATENCY = "LATENCY"
    # " A edge or a network link has a Bandwidth"

    NODE_IPT = "IPT"
    "Node feature: IPS . Instructions per Simulation Time "

    NODE_RAM = "RAM"
    "Node feature: RAM Capacity of a node"

    NODE_COST = "COST"
    "Node feature: Cost per unit time"


    def __init__(self, logger=None):

        self.__idNode = -1
        self.G = None
        #G is a networkx graph

        self.nodeAttributes = {}
        self.cloudNodes = []
        #A simple *cache* to have all cloud  nodes

        self.logger = logger or logging.getLogger(__name__)

    def __init_uptimes(self):
        for key in self.nodeAttributes:
            self.nodeAttributes[key]["uptime"] = (0, None)

    def get_edges(self):
        """
        Returns:
            list: a list of graph edges, i.e.: ((1,0),(0,2),...)
        """
        return self.G.edges

    def get_edge(self,key):
        """
        Args:
            key (str): a edge identifier, i.e. (1,9)

        Returns:
            list: a list of edge attributes
        """
        return self.G.edges[key]

    def get_nodes(self):
        """
        Returns:
            list: a list of all nodes features
        """
        return self.G.nodes

    def get_node(self, key):
        """
        Args:
            key (int): a node identifier

        Returns:
            list: a list of node features
        """
        return self.G.node[key]


    def get_info(self):
        return self.nodeAttributes

    def create_topology_from_graph(self, G):
        """
        It generates the topology from a NetworkX graph

        Args:
             G (*networkx.classes.graph.Graph*)
        """
        if isinstance(G, nx.classes.graph.Graph):
            self.G = G
            self.__idNode = len(G.nodes)
        else:
            raise TypeError

    def create_random_topology(self, nxGraphGenerator, params):
        """
        It generates the topology from a Graph generators of NetworkX

        Args:
             nxGraphGenerator (function): a graph generator function

        Kwargs:
            params (dict): a list of parameters of *nxGraphGenerator* function
        """
        try:
            self.G = nxGraphGenerator(*params)
            self.__idNode = len(self.G.node)
        except:
            raise Exception

    def load(self, data):
        """
            It generates the topology from a JSON file

            Args:
                 data (str): a json
        """
        self.G = nx.Graph()
        for edge in data["link"]:
            self.G.add_edge(edge["s"], edge["d"], BW=edge[self.LINK_BW],PR=edge[self.LINK_PR])

        for node in data["entity"]:
            self.nodeAttributes[node["id"]] = node

        self.__idNode = len(self.G.nodes)
        self.__init_uptimes()

    def load_graphml(self,filename):
        self.G = nx.read_graphml(filename)
        attEdges = {}
        for k in self.G.edges():
            attEdges[k] = {"BW": 1, "PR": 1}
        nx.set_edge_attributes(self.G, values=attEdges)
        attNodes = {}
        for k in self.G.nodes():
            attNodes[k] = {"IPT": 1, "RAM": 1, "COST": 1}
        nx.set_node_attributes(self.G, values=attNodes)
        for k in self.G.nodes():
            self.nodeAttributes[k] = self.G.node[k] #it has "id" att. TODO IMPROVE


    def get_nodes_att(self):
        """
        Returns:
            A dictionary with the features of the nodes
        """
        return self.nodeAttributes

    def find_IDs(self,value):
        """
        Search for nodes with the same attributes that value

        Args:
             value (dict). example value = {"model": "m-"}. Only one key is admitted

        Returns:
            A list with the ID of each node that have the same attribute that the value.value
        """
        keyS = value.keys()[0]

        result = []
        for key in self.nodeAttributes.keys():
            val = self.nodeAttributes[key]
            if keyS in val:
                if value[keyS] == val[keyS]:
                    result.append(key)
        return result


    def size(self):
        """
        Returns:
            an int with the number of nodes
        """
        return len(self.G.nodes)

    def add_node(self, nodes, edges=None):
        """
        Add a list of nodes in the topology

        Args:
            nodes (list): a list of identifiers

            edges (list): a list of destination edges
        """
        self.__idNode = + 1
        self.G.add_node(self.__idNode)
        self.G.add_edges_from(zip(nodes, [self.__idNode] * len(nodes)))

        return self.__idNode

    def remove_node(self, id_node):
        """
        Remove a node of the topology

        Args:
            id_node (int): node identifier
        """

        self.G.remove_node(id_node)
        return self.size()


    def write(self,path):
        nx.write_gexf(self.G, path)