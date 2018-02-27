import pandas as pd
from yafs.metrics import Metrics
from yafs.topology import *


# numOfDepts = 1
# numOfMobilesPerDept = 2
# t = Topology()
# t_json = create_json_topology(numOfDepts, numOfMobilesPerDept)
# t.load(t_json)

simulation_time = 10000

m = Metrics()
m.load_results("results") #Load both files with "results_*events*" and "results_*links*"

df,dl = m.get()


type(df)
print df.describe

time_loops = [["M.EGG","M.Sensor","M.Concentration"]]
m.showResults(100000,t,time_loops=time_loops)



