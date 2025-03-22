import logging
from yafs.topology import *
import json
import sys
from collections import defaultdict
import pandas as pd
import numpy as np

class PolicyManager():

    def __get_latency(self,path,topology):
        speed = 0
        for i in range(len(path) - 1):
            link = (path[i], path[i + 1])
            speed += topology.G.edges[link][Topology.LINK_PR]
        return speed

    def __get_current_services(self,sim):
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

    def __init__(self,DES,name,pathCSV):

        self.DES = DES
        self.name = name
        self.active = True
        self.pathCSV = pathCSV

        self.logger = logging.getLogger(__name__)

        self.previous_number_samples = 0
        self.agents = {}
        # data = json.load(open(path + 'usersDefinition.json'))



    def __call__(self, sim, routing):
        if self.active:
            print("Hello world from instance %s: %i"%(self.name,self.DES))

            print("\t ALL Routes: ",routing.controlServices)
            routes = []
            for (path,des) in routing.controlServices.values():
                if des==self.DES:
                    print("\t Path:",path)
                    routes.append([self.__get_latency(path,sim.topology),path])

            print("\t(Latencies & Routes)",routes)
            deployed_services, user_req_services = self.__get_current_services(sim)
            print("Deployed services:",deployed_services)
            print("Users with services:",user_req_services)

            # We analyse the performance of the multiples requests: QoS
            # Force the flush of metrics
            sim.metrics.flush()
            # Loading samples generated along current period (self.activations-1,self.activation)
            df = pd.read_csv(self.pathCSV + ".csv", skiprows=range(1, self.previous_number_samples))  # include header
            df = df[df["DES.dst"]==self.DES]
            if len(df)>0:
                # print("Number of samples: %i (from: %i)" % (len(df.index)-1, self.previous_number_samples))
                self.previous_number_samples += len(df.index) - 1  # avoid header

                print(df.head(3)) ## checks
                print(df["DES.dst"])
                print(df.columns)
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

                print(self.agents)
            else:
                print("Not information yet")