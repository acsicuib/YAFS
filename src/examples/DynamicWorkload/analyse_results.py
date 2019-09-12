from yafs.stats import Stats
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pandas import Series, date_range

# for size in [100,1000,10000,100000,1000000]:
time_loops = [["M.Action"]]


#### ANALYSE FILES YAFS
size = 10000

path = "examples/DynamicWorkload/"

s = Stats(defaultPath=path+"Results_%s"%(size))
#Network
s.showResults2(size, time_loops=time_loops)


df = s.df
dfl = s.df_link

df["date"]=df.time_in.astype('datetime64[s]')
df.index = df.date
df = df.resample('100s').agg(dict(time_latency='mean'))

timeLatency = df.time_latency.values
ticks = range(len(timeLatency))

#OK
        ### Latency Time and Allocation replicas
fig = plt.figure()
ax1 = fig.add_subplot(111)
ax1.plot(ticks, timeLatency, '-')
ax1.set_ylim(timeLatency.min()-0.5,timeLatency.max()+0.5)
ax1.set_xlabel("Simulation time", fontsize=16)
ax1.set_ylabel("Latency time", fontsize=16)
plt.savefig('figure10c.pdf', format='pdf', dpi=600)