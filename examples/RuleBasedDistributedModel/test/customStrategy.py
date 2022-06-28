from collections import defaultdict
import random
import pickle
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colors
import matplotlib as mpl
import math
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
import json

import pandas as pd




class CustomStrategy():

    LIMIT_TURNS = 100

    def get_app_name(self, service):
        return service[:service.index("_")]

    def __init__(self,pathExp,pathResults,total_services,draw_grid_topology_dimension,pathCSV):
        self.activation = 0
        # self.pathExp = pathExp
        self.pathResults = pathResults
        self.agents = {} #key(service,node)
        self.pathCSV = pathCSV

        self.__total_services = total_services
        self.__draw_controlUser = {}
        self.__dimension = draw_grid_topology_dimension
        self.__currentOccupation = {}
        self.__my_hash_service_map ={}
        self.__inc_my_map = 1

        self.previous_number_samples = 0

        #Load user contraints
        self.constraints={}
        dataPopulation = json.load(open(pathExp + 'usersDefinition.json'))
        for element in dataPopulation["sources"]:
            node = element["id_resource"]
            app = element["app"]
            self.constraints[(node, app)] = element["constraint"]


    def __str__(self):
        print("Number of evolutions %i" % self.activation)

    def transform_node_name(self, node):
        return self.__dimension * node[0] + node[1]


        # def __my_hash_service(self,str):
    #     hash = 0
    #     # Take ordinal number of char in str, and just add
    #     for x in str: hash += (ord(x))
    #     return (hash % self.totalservices)  # Depending on the range, do a modulo operation.

    def __my_map_service(self,str):
        if str not in self.__my_hash_service_map:
            self.__my_hash_service_map[str]=self.__inc_my_map
            self.__inc_my_map+=1

        return self.__my_hash_service_map[str]



    def deploy_module(self,sim,service,idtopo):
        app_name = service[0:service.index("_")]
        app = sim.apps[app_name]
        services = app.services
        idDES = sim.deploy_module(app_name, service, services[service], [idtopo])

    ### FUNCTION MOVED TO core.py

    # def remove_module(self, sim, service_name, idtopo):
    #
    #     sim.print_debug_assignaments()
    #
    #     app_name = service_name[0:service_name.index("_")]
    #     # Stopping related processes deployed in the module and clearing main structure: alloc_DES
    #     all_des = []
    #     for k, v in sim.alloc_DES.items():
    #         if v == idtopo:
    #             all_des.append(k)
    #
    #     # Clearing other related structures
    #     for des in sim.alloc_module[app_name][service_name]:
    #         if des in all_des:
    #               print "REMOVE PROCESS ", des
    #               sim.alloc_module[app_name][service_name].remove(des)
    #               sim.stop_process(des)
    #               del sim.alloc_DES[des]

    def is_already_deployed(self,sim,service_name,idtopo):
        app_name = service_name[0:service_name.index("_")]

        all_des = []
        for k, v in sim.alloc_DES.items():
            if v == idtopo:
                all_des.append(k)

        # Clearing other related structures
        for des in sim.alloc_module[app_name][service_name]:
            if des in all_des:
                return True

    def get_current_services(self,sim):
        """ returns a dictionary with name_service and a list of node where they are deployed
        example: defaultdict(<type 'list'>, {u'2_19': [15], u'3_22': [5]})
        """
        current_services = sim.get_alloc_entities()

        nodes_with_services = defaultdict(list)

        current_services = dict((k, v) for k, v in current_services.items() if len(v)>0)

        deployed_services = defaultdict(list)
        for k,v  in current_services.items():
            for service_name in v:
                if not "None" in service_name: #[u'2#2_19']
                    deployed_services[service_name[service_name.index("#")+1:]].append(k)
                else:
                    nodes_with_services[k].append(service_name[:service_name.index("#")])

        return deployed_services,nodes_with_services

    def drawNetwork(self,sim,nodes_with_users):

        #CTS
        piesize = .05
        p2 = piesize / 2.

        tab20 = plt.cm.get_cmap('tab20', self.__total_services)
        bounds = range(self.__total_services)
        newcolors = tab20(np.linspace(0, 1, self.__total_services))
        newcolors[0] = np.array([250.0 / 256.0, 250. / 256., 250. / 256., 1])
        newcmp = mpl.colors.ListedColormap(newcolors)
        norm = mpl.colors.BoundaryNorm(bounds, newcmp.N)


        pos = {self.transform_node_name((x, y)): (x, y) for x in range(self.__dimension) for y in range(self.__dimension)}


        fig, ax = plt.subplots(figsize=(16.0, 10.0))
        # Nodes + Egdes
        plt.text(4., -2., "Step: %i" % self.activation, {'color': 'black', 'fontsize': 16})

        nx.draw(sim.topology.G, pos, with_labels=False, node_size=200, node_color="#1260A0", edge_color="gray", node_shape="o",
                font_size=7, font_color="white", ax=ax)

        # Labels on nodes
        for x in range(self.__dimension-1, -1, -1):
            for y in range(self.__dimension-1, -1, -1):
                ax.text(x + piesize * 2.5, y + piesize * 7.5, "%i-%i" % (x, y), fontsize=8)


        # Plotting users dots
        self.__draw_controlUser = {}

        for node in nodes_with_users:
            for app in nodes_with_users[node]:

                for i, v in enumerate(self.__my_hash_service_map.keys()):#getting the index of the app #TODO improve
                    if "%s_"%app in v:
                        break

                self.__draw_showUser(pos[node], i+1, ax, newcolors)

        # LAST STEP ALWAYS: to maintain coordinates
        # Displaying capacity, changing node shape
        trans = ax.transData.transform
        trans2 = fig.transFigure.inverted().transform
        for n in sim.topology.G:
            xx, yy = trans(pos[n])  # figure coordinates
            xa, ya = trans2((xx, yy))  # axes coordinates

            a = plt.axes([xa - p2, ya - p2, piesize, piesize])
            a.set_aspect('equal')

            shape = np.array(eval(sim.topology.G.nodes[n]["capacity"]))
            if n in self.__currentOccupation:
                occ = self.__currentOccupation[n]
            else:
                occ = np.array(eval((sim.topology.G.nodes[n]["occupation"])))

            data = occ.reshape(shape)
            #    data=[[1.,3.,1.]]

            a.imshow(data, cmap=newcmp, interpolation='none', norm=norm)
            #    a.axis('off')
            a.axes.get_yaxis().set_visible(False)
            a.axes.get_xaxis().set_visible(False)


        #plt.text(2, 1000, "Step: %i" % self.activation, {'color': 'C0', 'fontsize': 16})

        fig.savefig(self.pathResults +'net_%03d.png' % self.activation)  # save the figure to file
        plt.close(fig)  # close the figure

    def __draw_showUser(self,node, service,ax,newcolors):
        piesize = .05
        p2 = piesize / 2.

        if node not in self.__draw_controlUser.keys():
            self.__draw_controlUser[node] = 0

        total = self.__draw_controlUser[node]
        line = int(total / 4) + 1

        duy =0.2* line
        dux = 0.15 * (total % 4)
        self.__draw_controlUser[node] += 1

        if node[0] == 0:  # este
            dx = -piesize * 10. - (dux * .8)
            dy = piesize * 8.5 - (duy * 1.4)
        elif node[1] == 0:  # south
            dx = -piesize * 9.5 + duy
            dy = -piesize * 10. - dux
        elif node[0] == self.__dimension-1:  # west
            dx = piesize * 10. + dux
            dy = piesize * 9. - duy
        elif node[1] == self.__dimension-1:  # north
            dx = -piesize * 9 + (duy * .8)
            dy = piesize * 10. + (dux * 1.4)


        ax.scatter(node[0] + dx, node[1] + dy, s=100.0, marker='o', color=newcolors[service])

    def __call__(self, sim, routing,case, stop_time, it):

        #The occupation of a node can be managed by the simulator but to easy integration with the visualization both structures are different
        self.__currentOccupation = {}

        self.activation  +=1
        routing.invalid_cache_value = True

        print("*" * 30)
        print("*" * 30)
        print("STEP: ", self.activation)
        print("*" * 30)
        print("*" * 30)

        ####
        ###
        # Data Gathering - AGENT INTERFACE
        ###
        ####


        # Current utilization of services
        service_calls = defaultdict(list)
        nodes_with_users= defaultdict(list)

        for k,v in routing.controlServices.items():
            service_calls[k[1]].append(v[0])
            #nodes_with_users[v[0][0]].append(k[1])

        print("Current service calls:")
        print(service_calls)
        print("-" * 30)

        nodes_with_deployed_services = defaultdict(list)
        current_services,nodes_with_users = self.get_current_services(sim)

        for service in current_services:
            for node in current_services[service]:
                nodes_with_deployed_services[node].append(service)

        print("Current services:")
        print(current_services)
        print("-" * 30)

        print("Nodes with users: (nodes_with_users)")
        print(nodes_with_users)
        print("-" * 30)

        print("Nodes with deployed services:")
        print(nodes_with_deployed_services)
        print("-" * 30)

        #TODO Extraer ocupacion a otros procesos
        for node in nodes_with_deployed_services:
            if node not in self.__currentOccupation:
                self.__currentOccupation[node] =np.array(eval((sim.topology.G.nodes[node]["occupation"])))

            for service in nodes_with_deployed_services[node]:
                pos = list(self.__currentOccupation[node]).index(0.)  # it could be incremental
                self.__currentOccupation[node][pos] = self.__my_map_service(service)

        print("Current node occupation with service mapped:")
        print(self.__currentOccupation)
        print("-" * 30)

        # Unused deployed services
        services_not_used = defaultdict(list)
        for k in current_services:
            if k not in service_calls.keys():
                # Unused service
                None
            else:
               for service in current_services[k]:
                    found = False
                    for path in service_calls[k]:
                        if path[-1] == service:
                            found = True
                            break
                    #endfor
                    if not found:
                        services_not_used[k].append(service)

        print("Unused deployed services")
        print(services_not_used)
        print("-"*30)


        ####
        ###
        # Taking a picture
        ###
        ####
        self.drawNetwork(sim,nodes_with_users)


        ####
        ##
        # AGENT MIDDLEWARE & QoS from current requests between self.activations
        ##
        ####

        # UPDATE AGENTS status (creation*1, feed-channel, partial-network)
        # It only must be triggered one time (really in self.activation == 1)
        for service, currentnodes in current_services.items():
            app_name = self.get_app_name(service)
            if self.activation == 1:
                # check first time: initial existence (one time)
                # These service are in the cloud, are indelible!
                for node in currentnodes:
                    if (service, node) not in self.agents:
                        a = Agent(service, node)
                        a.time_creation = self.activation
                        a.inCloud = True
                        self.agents[(service, node)] = a

            #checking user paths
            for user_path in service_calls[service]:
                #print(app_name," Current position: ",user_path[-1])
                user_position = user_path[0]
                a = np.array(nodes_with_users[user_position])
                unique, counts = np.unique(a, return_counts=True)
                ocurrences = dict(zip(unique, counts))
                # print("Agent(Service: %s,pos: %i), updating path: %s, ocurrences: %i"%(app_name,user_path[-1],user_path,ocurrences[app_name]))
                self.agents[(service, user_path[-1])].updateNx(user_path,ocurrences[app_name])

        # We analyse the performance of the multiples requests: QoS
        # Force the flush of metrics
        sim.metrics.flush()
        # Loading samples generated along current period (self.activations-1,self.activation)
        df = pd.read_csv(self.pathCSV + ".csv", skiprows=range(1, self.previous_number_samples))  # include header
        # print("Number of samples: %i (from: %i)" % (len(df.index)-1, self.previous_number_samples))
        self.previous_number_samples += len(df.index) - 1  # avoid header

        # print(df.head(3)) ## checks
        # print(df.tail(3))
        df["response"] = df['time_out'] - df['time_emit']
        # The user are separated
        df2 = df.groupby(['DES.dst', 'TOPO.dst', 'TOPO.src', 'module']).agg({"response": ['mean', 'std', 'count'],
                                                                             "service": 'mean'}).reset_index()
        df2.columns = ["USER", "SRC", "DST", "module", "mean", "std", "transmissions", "service"]
        # Same users deployed in same node are grouped
        df2 = df2.groupby(['SRC', 'DST', 'module']).agg({"mean": np.mean, "std": np.mean, "transmissions": np.mean, "service": np.mean}).reset_index()
        for i, row in df2.iterrows():
            service_node= int(row["SRC"])
            service_name = row["module"]
            user_node = int(row["DST"])
            self.agents[(service_name, service_node)].update_response_log(user_node, row[3:])



        ####
        ###
        #
        #  ACTIONS
        #
        # TAKING NEW ACTIONS WITH PREVIOUS INFORMATION
        #
        ###
        ####
        shuffle_agents = list(self.agents.keys())
        attempts = 0
        while len(shuffle_agents)>0 and attempts < CustomStrategy.LIMIT_TURNS:
            k = random.randint(0,len(shuffle_agents)-1)
            key_agent = shuffle_agents[k]
            del shuffle_agents[k]
            action,force_third_agents_actions = self.agents[key_agent].get_action(self.activation,self.constraints) #guardar en el registor del agente, por posibilidad de cambio
            # the action is achievable in the agent's turn
            #first we foce third agent actions
            for agent,action in force_third_agents_actions:
                #perfom third action
                ##perfom_action
                if agent not in shuffle_agents:
                    shuffle_agents.append(agent)

            # perform agent action
            ##perfom_action
            print(key_agent,action)

            attempts+=1

        if attempts >= CustomStrategy.LIMIT_TURNS:
            print("REALLY!? A big war among services is declared. External diplomatic actions are required.")
            exit()

        # # We remove all the services not used but they have been called in a previous step
        # for service_name,nodes in services_not_used.items():
        #     for node in nodes:
        #         app_name = service_name[0:service_name.index("_")]
        #         print("Removing module: %s from node: %i"%(service_name,node))
        #         sim.undeploy_module(app_name,service_name,node)

        # # por cada servicio se toma una decision:
        # # clonarse
        # for service in service_calls:
        #     #TODO other type of operation
        #     if random.random()<1.0:
        #         #clonning
        #         clones = len(service_calls[service]) # numero de veces que se solicita
        #         for clon in range(clones):
        #             path = service_calls[service][clon]
        #             # path[-1] is the current location of the service
        #             if len(path)>2:
        #                 nextLocation = path[-2]
        #                 #TODO capacity control
        #                 if not self.is_already_deployed(sim,service,nextLocation):
        #                     self.deploy_module(sim,service,nextLocation)


        # # controlling things :S
        # entities = sim.get_alloc_entities()
        # f = open(self.pathResults + "/file_alloc_entities_%s_%i_%i_%i.pkl" % (case, stop_time, it,self.activations), "wb")
        # pickle.dump(entities, f)
        # f.close()

        # Debug:  CLOSING CICLE
        print("-__"*30)
        print("AGENTS in cicle: ", self.activation)
        for k, agent in self.agents.items():
            print(agent)
        print("-_-" * 30)

        # FOR TESTING & DEBUGGING CONTROL
        # Debug:
        if self.activation==2:
            print("Activation :", self.activation)
            sim.print_debug_assignaments()
            exit()





        ### LAST STEP Cleaning temporal variables from agent
        for k,agent in self.agents.items():
            agent.clear()
