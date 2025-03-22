import pandas as pd
import numpy as np

from yafs.metrics import Metrics


class Stats:

    def __init__(self,defaultPath="result"):
        self.df_link = pd.read_csv(defaultPath + "_link.csv")
        self.df = pd.read_csv(defaultPath + ".csv")


    def bytes_transmitted(self):
        return self.df_link["size"].sum()

    def count_messages(self):
        return len(self.df_link)


    def utilization(self,id_entity, total_time, from_time=0.0):
        if "time_service" not in self.df.columns: #cached
            self.df["time_service"] = self.df.time_out - self.df.time_in
        values = self.df.groupby("DES.dst").time_service.agg("sum")
        return values[id_entity] / total_time

    def compute_times_df(self):
        self.df["time_latency"] = self.df["time_reception"] - self.df["time_emit"]
        self.df["time_wait"] = self.df["time_in"] - self.df["time_reception"]  #
        self.df["time_service"] = self.df["time_out"] - self.df["time_in"]
        self.df["time_response"] = self.df["time_out"] - self.df["time_reception"]
        self.df["time_total_response"] = self.df["time_response"] + self.df["time_latency"]

    def times(self,time,value="mean"):
        if "time_response" not in self.df.columns:
            self.compute_times_df()
        return self.df.groupby("message").agg({time:value})



    def average_loop_response(self,time_loops):
        """
        No hay chequeo de la existencia del loop: user responsability
        """
        if "time_response" not in self.df.columns:
            self.compute_times_df()

        resp_msg = self.df.groupby("message").agg({"time_total_response": ["mean","count"]}) #Its not necessary to have "count"
        resp_msg.columns = ['_'.join(col).strip() for col in resp_msg.columns.values]
        results = []

        for loop in time_loops:
            total = 0.0
            for msg in loop:
                try:
                    total += resp_msg[resp_msg.index == msg].time_total_response_mean[0]
                except IndexError:
                    total +=0

            results.append(total)

        return results

    def get_watt(self,totaltime,topology,by=Metrics.WATT_SERVICE):
        results = {}
        nodeInfo = topology.get_info()
        if by == Metrics.WATT_SERVICE:
            # Tiempo de actividad / runeo
            if "time_response" not in self.df.columns:  # cached
                self.compute_times_df()

            nodes = self.df.groupby("TOPO.dst").agg({"time_service": "sum"})
            for id_node in nodes.index:
                results[id_node] = {"model": nodeInfo[id_node]["model"], "type": nodeInfo[id_node]["type"],
                                 "watt": nodes.loc[id_node].time_service * nodeInfo[id_node]["WATT"]}
        else:
            for node_key in nodeInfo:
                if not nodeInfo[node_key]["uptime"][1]:
                    end = totaltime
                start = nodeInfo[node_key]["uptime"][0]
                uptime = end-start
                results[node_key] = {"model":nodeInfo[node_key]["model"],"type":nodeInfo[node_key]["type"],"watt":uptime*nodeInfo[node_key]["WATT"],"uptime":uptime}

        return results

    # def get_cost_cloud(self, topology):
    #     cost = 0.0
    #     nodeInfo = topology.get_info()
    #     results = {}
    #     # Tiempo de actividad / runeo
    #     if "time_response" not in self.df.columns:  # cached
    #         self.__compute_times_df()
    #
    #     nodes = self.df.groupby("TOPO.dst").agg({"time_service": "sum"})
    #
    #     for id_node in nodes.index:
    #         if nodeInfo[id_node]["type"] == Entity.ENTITY_CLOUD:
    #             results[id_node] = {"model": nodeInfo[id_node]["model"], "type": nodeInfo[id_node]["type"],
    #                                 "watt": nodes.loc[id_node].time_service * nodeInfo[id_node]["WATT"]}
    #             cost += nodes.loc[id_node].time_service * nodeInfo[id_node]["COST"]
    #     return cost,results

    def showLoops(self,time_loops):
        results = self.average_loop_response(time_loops)
        for i, loop in enumerate(time_loops):
            print ("\t\t%i - %s :\t %f" % (i, str(loop), results[i]))
        return results




    def showResults(self, total_time, topology, time_loops=None):
        print ("\tSimulation Time: %0.2f" % total_time)

        if time_loops is not None:
            print ("\tApplication loops delays:")
            results = self.average_loop_response(time_loops)
            for i, loop in enumerate(time_loops):
                print ("\t\t%i - %s :\t %f" % (i, str(loop), results[i]))

        print ("\tEnergy Consumed (WATTS by UpTime):")
        values = self.get_watt(total_time, topology, Metrics.WATT_UPTIME)
        for node in values:
            print ("\t\t%i - %s :\t %.2f" % (node, values[node]["model"], values[node]["watt"]))

        print ("\tEnergy Consumed by Service (WATTS by Service Time):")
        values = self.get_watt(total_time, topology, Metrics.WATT_SERVICE)
        for node in values:
            print ("\t\t%i - %s :\t %.2f" % (node, values[node]["model"], values[node]["watt"]))

        print ("\tCost of execution in cloud:")
        total, values = self.get_cost_cloud(topology)
        print ("\t\t%.8f" % total)

        print ("\tNetwork bytes transmitted:")
        print ("\t\t%.1f" % self.bytes_transmitted())


    def showResults2(self, total_time, time_loops=None):
        print ("\tSimulation Time: %0.2f" % total_time)

        if time_loops is not None:
            print ("\tApplication loops delays:")
            results = self.average_loop_response(time_loops)
            for i, loop in enumerate(time_loops):
                print ("\t\t%i - %s :\t %f" % (i, str(loop), results[i]))

        print ("\tNetwork bytes transmitted:")
        print ("\t\t%.1f" % self.bytes_transmitted())

    """ONLYE THE FIRST ONE : DEBUG"""
    def valueLoop(self, total_time, time_loops=None):
            if time_loops is not None:
                results = self.average_loop_response(time_loops)
                for i, loop in enumerate(time_loops):
                    return results[i]

    def average_messages_not_transmitted(self):
        return np.mean(self.df_link.buffer)

    def peak_messages_not_transmitted(self):
        return np.max(self.df_link.buffer)

    def messages_not_transmitted(self):
        return self.df_link.buffer[-1:]

    def get_df_modules(self):
        g = self.df.groupby(["module", "DES.dst"]).agg({"service": ['mean', 'sum', 'count']})
        return g.reset_index()

    def get_df_service_utilization(self,service,time):
        """
        Returns the utilization(%) of a specific module
        """
        g = self.df.groupby(["module", "DES.dst"]).agg({"service": ['mean', 'sum', 'count']})
        g.reset_index(inplace=True)
        h = pd.DataFrame()
        h["module"] = g[g.module == service].module
        h["utilization"] = g[g.module == service]["service"]["sum"]*100 / time
        return h


