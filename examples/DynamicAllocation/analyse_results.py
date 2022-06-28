from yafs.stats import Stats
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pandas import Series, date_range
from matplotlib.ticker import FormatStrFormatter
# for size in [100,1000,10000,100000,1000000]:
time_loops = [["M.Action"]]


#### ANALYSE FILES YAFS

app1 = "app1"
app2 = "app2"

size = 12000

path = "examples/DynamicAllocation/"

#s = Stats(defaultPath=path+"Results_%s"%(size))
s1 = Stats(defaultPath=path+"Results_%s_singleApp1" % (size))
#s2 = Stats(defaultPath=path+"Results_%s_singleApp2" % (size))
#Network
#s.showResults2(size, time_loops=time_loops)
#app1 based on dinamic Edge
s1.showResults2(size, time_loops=time_loops)
#app2 based on static Cloud
#s2.showResults2(size, time_loops=time_loops)


df = s1.df
dfl = s1.df_link

#df["date"]=df.time_in.astype('timedelta64[s]')
df["date"]=df.time_in.astype('datetime64[s]')
df.index = df.date


dfap1 = df[df["app"]=="app1"]
dfap1 = dfap1.resample('300s').agg(dict(time_latency='mean'))

timeLatency = dfap1.time_latency.values

ticks = range(len(timeLatency))
ticksV = np.array(ticks)*300

#index = dfap1.index
#rng = pd.date_range('01/01/1970',periods=20,freq="300s")

values = range(len(ticks))

for x in range(len(ticks)):
    if x<10:
        values[x]=1
    elif x>28:
        values[x]=20
    else:
        values[x]=values[x-1]+1

#OK
        ### Latency Time and Allocation replicas
fig = plt.figure()
ax1 = fig.add_subplot(111)
ax1.plot(ticks, timeLatency, '-')
ax1.set_xlabel("Simulation time", fontsize=16)
ax1.set_ylabel("Latency time", fontsize=16)
ax2 = ax1.twinx()
ax2.set_ylabel("Number of allocation replicas", fontsize=16)
ax2.set_yticks(ticks)
ax2.set_xlim(0,35)
ax2.plot(ticks, values, c="g",linestyle='-', marker="o",markersize=4)

time_labels = []
for t in ax2.get_xticks():
    time_labels.append( "%3.0f"%(t*300))
ax1.set_xticklabels(time_labels)
plt.savefig('figure8b.pdf', format='pdf', dpi=600)
 
#dfl["date"]=dfl.ctime.astype('datetime64[s]')
#dfl.index = dfl.date
#dfl1 = dfl.resample('300s').agg(dict(buffer='mean'))
#
#fig = plt.figure()
#ax1 = fig.add_subplot(111)
#ax1.plot(ticks, dfl1.buffer.values, '-')
#ax1.set_xlabel("Simulation time", fontsize=16)
#ax1.set_ylabel("Number of messages enqueued", fontsize=16)
#
#time_labels = []
#for t in ax1.get_xticks():
#    time_labels.append( "%3.0f"%(t*300))
#ax1.set_xticklabels(time_labels)



