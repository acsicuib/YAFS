
import numpy as np
import pandas as pd
# for size in [100,1000,10000,100000,1000000]:
time_loops = [["M.EGG", "M.Sensor", "M.Concentration"]]
import matplotlib.pyplot as plt
from yafs.stats import Stats

#### ANALYSE FILES YAFS

police = "cloud"

police = "edge"

# print depth
for idx1, depth in enumerate([4, 8, 12, 16]):
#for idx1, depth in enumerate([2]):
     # 1000, 10000,
     for idx2,size in enumerate([1000,10000,100000]):
     #     size = 100000
         print("DEPTH: %i | TIME: %s" %(depth , size))
         s = Stats(defaultPath="files/Results_%s_%s_%s"%(police,size,depth))

         #Network
         s.showResults2(size, time_loops=time_loops)

         print("\t Bytes transmitted: " ,s.bytes_transmitted())
         print("\t Messages transmitted: ",s.count_messages())
         print("\t- Network saturation -")
         print("\t\tAverage waiting messages : %i" % s.average_messages_not_transmitted())
         print("\t\tPeak of waiting messages : %i" % s.peak_messages_not_transmitted())
         print("\t\tTOTAL messages not transmitted: %i" % s.messages_not_transmitted())

         #LOOPS
         # res = s.showLoops(time_loops)
         # loopstime[depth][idx2]=res[0]
         #
         # #Print the execution delay
         # print s.times("time_total_response")
         #
         # print "Latency Acc: ", s.df_link["latency"].sum()
         print("*"*40)


police = "edge"
stop_time = 10000
dep = 8

path = "files/Results_%s_%s_%s.csv" % (police, stop_time, dep)
df = pd.read_csv(path)
df["time_latency"] = df["time_reception"] - df["time_emit"]

resp_msg = df.groupby("message").agg({"time_latency": ["mean","count"]}) #Its not necessary to have "count"
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
            
            

lat = df["time_latency"].describe()


df["time_latency"].plot()
df["date"]=df.time_in.astype('datetime64[s]')
df.index = df.date


#df = df.resample('1s').agg(dict(time_latency='mean'))

timeLatency = df.time_latency.values
ticks = range(len(timeLatency))

#OK
        ### Latency Time and Allocation replicas
fig = plt.figure()
ax1 = fig.add_subplot(111)
ax1.plot(lat, '-')
#ax1.set_ylim(timeLatency.min()-0.5,timeLatency.max()+0.5)
ax1.set_xlabel("Simulation time", fontsize=16)
ax1.set_ylabel("Latency time", fontsize=16)
