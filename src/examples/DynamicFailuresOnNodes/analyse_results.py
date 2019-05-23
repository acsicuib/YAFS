from yafs.stats import Stats
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


size = 10000
path = "examples/DynamicFailuresOnNodes/"
# THIS VALUE MUST BE UPDATED FROM YOUR EXECUTION (COPYPASTE)
failures = [{'id': 398, 'module': False, 'time': 500}, {'id': 343, 'module': False, 'time': 553}, {'id': 48, 'module': False, 'time': 680}, {'id': 133, 'module': True, 'time': 680}, {'id': 288, 'module': False, 'time': 716}, {'id': 283, 'module': False, 'time': 731}, {'id': 374, 'module': False, 'time': 740}, {'id': 168, 'module': False, 'time': 760}, {'id': 331, 'module': False, 'time': 802}, {'id': 265, 'module': False, 'time': 852}, {'id': 119, 'module': False, 'time': 929}, {'id': 233, 'module': False, 'time': 983}, {'id': 353, 'module': False, 'time': 1098}, {'id': 337, 'module': True, 'time': 1120}, {'id': 199, 'module': False, 'time': 1330}, {'id': 232, 'module': False, 'time': 1332}, {'id': 13, 'module': False, 'time': 1443}, {'id': 95, 'module': False, 'time': 1497}, {'id': 317, 'module': False, 'time': 1578}, {'id': 163, 'module': False, 'time': 1593}, {'id': 67, 'module': False, 'time': 1615}, {'id': 279, 'module': True, 'time': 1776}, {'id': 267, 'module': False, 'time': 2121}, {'id': 147, 'module': False, 'time': 2158}, {'id': 174, 'module': False, 'time': 2275}, {'id': 202, 'module': False, 'time': 2484}, {'id': 310, 'module': False, 'time': 2709}, {'id': 206, 'module': False, 'time': 2717}, {'id': 153, 'module': False, 'time': 2720}, {'id': 193, 'module': False, 'time': 2738}, {'id': 17, 'module': False, 'time': 2948}, {'id': 281, 'module': False, 'time': 2958}, {'id': 393, 'module': False, 'time': 3012}, {'id': 236, 'module': False, 'time': 3328}, {'id': 65, 'module': True, 'time': 3404}, {'id': 197, 'module': False, 'time': 3521}, {'id': 392, 'module': False, 'time': 3558}, {'id': 307, 'module': False, 'time': 3673}, {'id': 213, 'module': False, 'time': 3852}, {'id': 345, 'module': False, 'time': 3853}, {'id': 201, 'module': False, 'time': 3991}, {'id': 380, 'module': False, 'time': 4440}, {'id': 227, 'module': False, 'time': 4577}, {'id': 177, 'module': False, 'time': 4609}, {'id': 216, 'module': True, 'time': 4764}, {'id': 382, 'module': False, 'time': 4774}, {'id': 2, 'module': False, 'time': 4833}, {'id': 312, 'module': False, 'time': 5072}, {'id': 326, 'module': False, 'time': 5106}, {'id': 354, 'module': False, 'time': 5139}, {'id': 292, 'module': False, 'time': 5152}, {'id': 321, 'module': False, 'time': 5153}, {'id': 218, 'module': False, 'time': 5266}, {'id': 159, 'module': False, 'time': 5289}, {'id': 22, 'module': False, 'time': 5319}, {'id': 348, 'module': False, 'time': 5386}, {'id': 222, 'module': False, 'time': 5391}, {'id': 75, 'module': False, 'time': 5476}, {'id': 191, 'module': False, 'time': 5491}, {'id': 183, 'module': False, 'time': 5579}, {'id': 131, 'module': False, 'time': 5699}, {'id': 127, 'module': False, 'time': 5709}, {'id': 210, 'module': False, 'time': 5762}, {'id': 247, 'module': False, 'time': 5880}, {'id': 243, 'module': False, 'time': 5933}, {'id': 171, 'module': False, 'time': 5938}, {'id': 84, 'module': False, 'time': 6014}, {'id': 64, 'module': False, 'time': 6123}, {'id': 231, 'module': False, 'time': 6195}, {'id': 344, 'module': False, 'time': 6484}, {'id': 318, 'module': False, 'time': 6572}, {'id': 325, 'module': False, 'time': 6805}, {'id': 264, 'module': False, 'time': 6819}, {'id': 31, 'module': False, 'time': 6833}, {'id': 6, 'module': False, 'time': 6997}, {'id': 5, 'module': False, 'time': 7047}, {'id': 299, 'module': True, 'time': 7065}, {'id': 42, 'module': False, 'time': 7327}, {'id': 248, 'module': False, 'time': 7369}, {'id': 126, 'module': False, 'time': 7507}, {'id': 28, 'module': False, 'time': 7636}, {'id': 61, 'module': True, 'time': 7850}, {'id': 205, 'module': False, 'time': 7947}, {'id': 66, 'module': False, 'time': 8086}, {'id': 104, 'module': False, 'time': 8128}, {'id': 284, 'module': False, 'time': 8159}, {'id': 121, 'module': False, 'time': 8385}, {'id': 181, 'module': False, 'time': 8440}, {'id': 145, 'module': False, 'time': 8774}, {'id': 160, 'module': False, 'time': 8882}, {'id': 73, 'module': False, 'time': 8979}, {'id': 41, 'module': False, 'time': 8991}, {'id': 364, 'module': False, 'time': 9289}, {'id': 200, 'module': True, 'time': 9348}, {'id': 82, 'module': False, 'time': 9434}, {'id': 245, 'module': False, 'time': 9486}, {'id': 330, 'module': False, 'time': 9513}, {'id': 9, 'module': False, 'time': 9746}, {'id': 56, 'module': False, 'time': 9831}, {'id': 290, 'module': False, 'time': 9831}, {'id': 62, 'module': False, 'time': 9927}, {'id': 282, 'module': False, 'time': 9966}]
print "Number of nodes removed: ",len(failures)


# Basic analysis
time_loops = [["M.Action"]]
s = Stats(defaultPath=path+"Results_%s_exp"%(size))
s.showResults2(size, time_loops=time_loops)

# Visualization of latency time series:

dfail = pd.DataFrame.from_dict(failures)
dfail["date"]=dfail.time.astype('datetime64[s]')
dfail.index = dfail.date
dfail['module'] = dfail.module.astype(str)
dfail = dfail.resample('10s').agg({"module": "-".join}) #OPTIONAL BE CAREFOUL: resampling -> agg events
#dict(module=''))['module'].apply(list)

df = s.df
dfl = s.df_link

#df[df.time_latency<0]
#df["date"]=df.time_in.astype('timedelta64[s]')
df["date"]=df.time_in.astype('datetime64[s]')
df.index = df.date
df = df.resample('10s').agg(dict(time_latency='mean'))

timeLatency = df.time_latency.values
ticks = range(len(timeLatency))

ticksV = np.array(ticks)*10


#OK
        ### Latency Time and Allocation replicas
fig = plt.figure()
ax1 = fig.add_subplot(111)
ax1.plot(ticks, timeLatency, '-')
ax1.set_ylim(timeLatency.min()-0.5,timeLatency.max()+0.5)
ax1.set_xlabel("Simulation time", fontsize=16)
ax1.set_ylabel("Latency time", fontsize=16)
for idx,item in enumerate(dfail.module):
#    print idx,item,len(item)
 #   value = item == "True" ## OPTIONAL DESAAG. EVENTS
    x = ticks[idx]
    if len(item)==4:    
        y = timeLatency[idx]+0.45
#        ax1.plot(ticks[idx], timeLatency[idx]+2, marker='o', c="green")
        ax1.arrow(x,4.7, 0, -0.35, head_width=15.0, head_length=0.15, fc='g', ec='g')
    elif len(item)==5:
        y = timeLatency[idx]+1
        ax1.arrow(x,4.7, 0, -0.1, head_width=0.5, head_length=0.1, fc='black', ec='black')
        #ax1.plot(x, y, marker='<', c="black")
        

