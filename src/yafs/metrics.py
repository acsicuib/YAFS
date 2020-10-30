import csv

class Metrics:

    TIME_LATENCY = "time_latency"
    TIME_WAIT =  "time_wait"
    TIME_RESPONSE = "time_response"
    TIME_SERVICE = "time_service"
    TIME_TOTAL_RESPONSE = "time_total_response"

    WATT_SERVICE = "byService"
    WATT_UPTIME = "byUptime"


    def __init__(self, default_results_path=None):
        columns_event = ["id","type", "app", "module", "message","DES.src","DES.dst","TOPO.src","TOPO.dst","module.src","service", "time_in","time_out",
                         "time_emit","time_reception"]
        columns_link = ["id","type", "src", "dst", "app", "latency", "message", "ctime", "size","buffer"]

        path = "result"
        if  default_results_path is not None:
            path = default_results_path

        self.__filef = open("%s.csv" % path, "w")
        self.__filel = open("%s_link.csv"%path, "w")
        self.__ff = csv.writer(self.__filef)
        self.__ff_link = csv.writer(self.__filel)
        self.__ff.writerow(columns_event)
        self.__ff_link.writerow(columns_link)

    def flush(self):
        self.__filef.flush()
        self.__filel.flush()

    def insert(self,value):

        self.__ff.writerow([value["id"],value["type"],
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

    def insert_link(self, value):
        self.__ff_link.writerow([value["id"],value["type"],
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
