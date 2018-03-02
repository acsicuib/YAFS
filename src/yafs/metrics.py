import pandas as pd
import numpy as np

import csv
import json

class Metrics:

    TIME_LATENCY = "time_latency"
    TIME_WAIT =  "time_wait"
    TIME_RESPONSE = "time_response"
    TIME_SERVICE = "time_service"
    TIME_TOTAL_RESPONSE = "time_total_response"

    WATT_SERVICE = "byService"
    WATT_UPTIME = "byUptime"


    def __init__(self, default_results_path=None):
        # columns_event = ["type", "app", "module", "service", "time_in", "time_out", "time_emit", "time_reception",
        #                  "msg_name",
        #                  "id_node", "from_node", "from_module", "des"]

        columns_event = ["type", "app", "module", "message","DES.src","DES.dst","TOPO.src","TOPO.dst","module.src","service", "time_in","time_out",
                         "time_emit","time_reception"]
        columns_link = ["type", "src", "dst", "app", "latency", "message", "ctime", "size","buffer"]

        path = "result"
        if  default_results_path is not None:
            path = default_results_path

        self.__filef = open("%s.csv" % path, "w")
        self.__filel = open("%s_link.csv"%path, "w")
        self.__ff = csv.writer(self.__filef)
        self.__ff_link = csv.writer(self.__filel)
        self.__ff.writerow(columns_event)
        self.__ff_link.writerow(columns_link)

    def insert(self,value):

        self.__ff.writerow([value["type"],
                    value["app"],
                    value["module"],
                    value["message"],
                    value["DES.src"],
                    value["DES.dst"],
                    value["TOPO.src"],
                    value["TOPO.dst"],
                    value["module.src"],
                    value["service"],
                    value["time_in"],
                    value["time_out"],
                    value["time_emit"],
                    value["time_reception"]
                            ])
        # None


    def insert_link(self, value):
        self.__ff_link.writerow([value["type"],
                    value["src"],
                    value["dst"],
                    value["app"],
                    value["latency"],
                    value["message"],
                    value["ctime"],
                    value["size"],
                    value["buffer"],

                            ])



    def close(self):
        self.__filef.close()
        self.__filel.close()


    #TODO
    # def bytes_transmitted(self):
    #     return self.__df_link["size"].sum()
    #
    #
    # def utilization(self,id_entity, total_time, from_time=0.0):
    #     if "time_service" not in self.__df.columns: #cached
    #         self.df["time_service"] = self.__df.time_out - self.__df.time_in
    #     values = self.__df.groupby("DES.dst").time_service.agg("sum")
    #     return values[id_entity] / total_time
    #
    # def __compute_times_df(self):
    #     self.__df["time_latency"] = self.__df["time_reception"] - self.__df["time_emit"]
    #     self.__df["time_wait"] = self.__df["time_in"] - self.__df["time_reception"]  #
    #     self.__df["time_service"] = self.__df["time_out"] - self.__df["time_in"]
    #     self.__df["time_response"] = self.__df["time_out"] - self.__df["time_reception"]
    #     self.__df["time_total_response"] = self.__df["time_response"] + self.__df["time_latency"]
    #
    # def times(self,time,value="mean",from_time=0.0):
    #     if "time_response" not in self.__df.columns:
    #         self.__compute_times_df()
    #     # print df
    #
    #     return self.__df.groupby("message").agg({time:value})
    #
    # def loops_response(self,time_loops):
    #     """
    #     No hay chequeo de la existencia del loop: user responsability
    #     """
    #     if "time_response" not in self.__df.columns:
    #         self.__compute_times_df()
    #
    #     resp_msg = self.__df.groupby("message").agg({"time_total_response": "mean"})
    #
    #     results = []
    #     for loop in time_loops:
    #         total = 0.0
    #         for msg in loop:
    #             try:
    #                 total += resp_msg[resp_msg.index == msg].time_total_response[0]
    #             except IndexError:
    #                 total +=0
    #
    #         results.append(total)
    #
    #     return results
    #
    # def get_watt(self,totaltime,topology,by=WATT_SERVICE):
    #     results = {}
    #     nodeInfo = topology.get_info()
    #     if by == Metrics.WATT_SERVICE:
    #         # Tiempo de actividad / runeo
    #         if "time_response" not in self.__df.columns:  # cached
    #             self.__compute_times_df()
    #
    #         nodes = self.__df.groupby("TOPO.dst").agg({"time_service": "sum"})
    #         for id_node in nodes.index:
    #             results[id_node] = {"model": nodeInfo[id_node]["model"], "type": nodeInfo[id_node]["type"],
    #                              "watt": nodes.loc[id_node].time_service * nodeInfo[id_node]["WATT"]}
    #     else:
    #         for node_key in nodeInfo:
    #             if not nodeInfo[node_key]["uptime"][1]:
    #                 end = totaltime
    #             start = nodeInfo[node_key]["uptime"][0]
    #             uptime = end-start
    #             results[node_key] = {"model":nodeInfo[node_key]["model"],"type":nodeInfo[node_key]["type"],"watt":uptime*nodeInfo[node_key]["WATT"],"uptime":uptime}
    #
    #     return results
    #
    # def get_cost_cloud(self, topology):
    #     cost = 0.0
    #     nodeInfo = topology.get_info()
    #     results = {}
    #     # Tiempo de actividad / runeo
    #     if "time_response" not in self.__df.columns:  # cached
    #         self.__compute_times_df()
    #
    #     nodes = self.__df.groupby("TOPO.dst").agg({"time_service": "sum"})
    #
    #     for id_node in nodes.index:
    #         if nodeInfo[id_node]["type"] == Entity.ENTITY_CLUSTER:
    #             results[id_node] = {"model": nodeInfo[id_node]["model"], "type": nodeInfo[id_node]["type"],
    #                                 "watt": nodes.loc[id_node].time_service * nodeInfo[id_node]["WATT"]}
    #             cost += nodes.loc[id_node].time_service * nodeInfo[id_node]["COST"]
    #     return cost,results
    #
    #
    # def showResults(self, total_time, topology, time_loops=None):
    #     print "\tExecution Time: %0.2f" % total_time
    #
    #     if time_loops is not None:
    #         print "\tApplication loops delays:"
    #         results = self.loops_response(time_loops)
    #         for i, loop in enumerate(time_loops):
    #             print "\t\t%i - %s :\t %f" % (i, str(loop), results[i])
    #
    #     print "\tEnergy Consumed (WATTS by UpTime):"
    #     values = self.get_watt(total_time, topology, self.WATT_UPTIME)
    #     for node in values:
    #         print "\t\t%i - %s :\t %.2f" % (node, values[node]["model"], values[node]["watt"])
    #
    #     print "\tEnergy Consumed by Service (WATTS by Service Time):"
    #     values = self.get_watt(total_time, topology, self.WATT_SERVICE)
    #     for node in values:
    #         print "\t\t%i - %s :\t %.2f" % (node, values[node]["model"], values[node]["watt"])
    #
    #     print "\tCost of execution in cloud:"
    #     total, values = self.get_cost_cloud(topology)
    #     print "\t\t%.8f" % total
    #
    #     print "\tNetwork bytes transmitted:"
    #     print "\t\t%.1f" % self.bytes_transmitted()
    #
    #
    # def showResults2(self, total_time, topology, time_loops=None):
    #     print "\tExecution Time: %0.2f" % total_time
    #
    #     if time_loops is not None:
    #         print "\tApplication loops delays:"
    #         results = self.loops_response(time_loops)
    #         for i, loop in enumerate(time_loops):
    #             print "\t\t%i - %s :\t %f" % (i, str(loop), results[i])
    #
    #     print "\tNetwork bytes transmitted:"
    #     print "\t\t%.1f" % self.bytes_transmitted()
    #
    # def store_results(self, name):
    #     self.__df.to_csv(name + "_events.csv")
    #     self.__df_link.to_csv(name + "_links.csv")
    #
    # def load_results(self,name):
    #     self.__df_link = pd.read_csv(name+"_links.csv")
    #     self.__df = pd.read_csv(name+"_events.csv")
    #
    # def get(self):
    #     """
    #     TEST
    #     """
    #     return self.__df,self.__df_link