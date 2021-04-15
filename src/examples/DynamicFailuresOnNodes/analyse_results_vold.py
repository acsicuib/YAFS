from yafs.stats import Stats
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pandas import Series, date_range

# for size in [100,1000,10000,100000,1000000]:
time_loops = [["M.Action"]]


#### ANALYSE FILES YAFS
size = 10000

path = "examples/DynamicFailuresOnNodes/"

s = Stats(defaultPath=path+"Results_%s_exp"%(size))
#Network
s.showResults2(size, time_loops=time_loops)

failures = [{'id': 398, 'module': False, 'time': 0}, {'id': 343, 'module': False, 'time': 100}, {'id': 48, 'module': False, 'time': 200}, {'id': 133, 'module': True, 'time': 300}, {'id': 288, 'module': False, 'time': 400}, {'id': 283, 'module': False, 'time': 500}, {'id': 374, 'module': False, 'time': 600}, {'id': 168, 'module': False, 'time': 700}, {'id': 331, 'module': False, 'time': 800}, {'id': 265, 'module': False, 'time': 900}, {'id': 119, 'module': False, 'time': 1000}, {'id': 233, 'module': False, 'time': 1100}, {'id': 353, 'module': False, 'time': 1200}, {'id': 337, 'module': True, 'time': 1300}, {'id': 199, 'module': False, 'time': 1400}, {'id': 232, 'module': False, 'time': 1500}, {'id': 13, 'module': False, 'time': 1600}, {'id': 95, 'module': False, 'time': 1700}, {'id': 317, 'module': False, 'time': 1800}, {'id': 163, 'module': False, 'time': 1900}, {'id': 67, 'module': False, 'time': 2000}, {'id': 279, 'module': True, 'time': 2100}, {'id': 267, 'module': False, 'time': 2200}, {'id': 147, 'module': False, 'time': 2300}, {'id': 174, 'module': False, 'time': 2400}, {'id': 202, 'module': False, 'time': 2500}, {'id': 310, 'module': False, 'time': 2600}, {'id': 206, 'module': False, 'time': 2700}, {'id': 153, 'module': False, 'time': 2800}, {'id': 193, 'module': False, 'time': 2900}, {'id': 17, 'module': False, 'time': 3000}, {'id': 281, 'module': False, 'time': 3100}, {'id': 393, 'module': False, 'time': 3200}, {'id': 236, 'module': False, 'time': 3300}, {'id': 65, 'module': True, 'time': 3400}, {'id': 197, 'module': False, 'time': 3500}, {'id': 392, 'module': False, 'time': 3600}, {'id': 307, 'module': False, 'time': 3700}, {'id': 213, 'module': False, 'time': 3800}, {'id': 345, 'module': False, 'time': 3900}, {'id': 201, 'module': False, 'time': 4000}, {'id': 380, 'module': False, 'time': 4100}, {'id': 227, 'module': False, 'time': 4200}, {'id': 177, 'module': False, 'time': 4300}, {'id': 216, 'module': True, 'time': 4400}, {'id': 382, 'module': False, 'time': 4500}, {'id': 2, 'module': False, 'time': 4600}, {'id': 312, 'module': False, 'time': 4700}, {'id': 326, 'module': False, 'time': 4800}, {'id': 354, 'module': False, 'time': 4900}, {'id': 292, 'module': False, 'time': 5000}, {'id': 321, 'module': False, 'time': 5100}, {'id': 218, 'module': False, 'time': 5200}, {'id': 159, 'module': False, 'time': 5300}, {'id': 22, 'module': False, 'time': 5400}, {'id': 348, 'module': False, 'time': 5500}, {'id': 222, 'module': False, 'time': 5600}, {'id': 75, 'module': False, 'time': 5700}, {'id': 191, 'module': False, 'time': 5800}, {'id': 183, 'module': False, 'time': 5900}, {'id': 131, 'module': False, 'time': 6000}, {'id': 127, 'module': False, 'time': 6100}, {'id': 210, 'module': False, 'time': 6200}, {'id': 247, 'module': False, 'time': 6300}, {'id': 243, 'module': False, 'time': 6400}, {'id': 171, 'module': False, 'time': 6500}, {'id': 84, 'module': False, 'time': 6600}, {'id': 64, 'module': False, 'time': 6700}, {'id': 231, 'module': False, 'time': 6800}, {'id': 344, 'module': False, 'time': 6900}, {'id': 318, 'module': False, 'time': 7000}, {'id': 325, 'module': False, 'time': 7100}, {'id': 264, 'module': False, 'time': 7200}, {'id': 31, 'module': False, 'time': 7300}, {'id': 6, 'module': False, 'time': 7400}, {'id': 5, 'module': False, 'time': 7500}, {'id': 299, 'module': True, 'time': 7600}, {'id': 42, 'module': False, 'time': 7700}, {'id': 248, 'module': False, 'time': 7800}, {'id': 126, 'module': False, 'time': 7900}, {'id': 28, 'module': False, 'time': 8000}, {'id': 61, 'module': True, 'time': 8100}, {'id': 205, 'module': False, 'time': 8200}, {'id': 66, 'module': False, 'time': 8300}, {'id': 104, 'module': False, 'time': 8400}, {'id': 284, 'module': False, 'time': 8500}, {'id': 121, 'module': False, 'time': 8600}, {'id': 181, 'module': False, 'time': 8700}, {'id': 145, 'module': False, 'time': 8800}, {'id': 160, 'module': False, 'time': 8900}, {'id': 73, 'module': False, 'time': 9000}, {'id': 41, 'module': False, 'time': 9100}, {'id': 364, 'module': False, 'time': 9200}, {'id': 200, 'module': True, 'time': 9300}, {'id': 82, 'module': False, 'time': 9400}, {'id': 245, 'module': False, 'time': 9500}, {'id': 330, 'module': False, 'time': 9600}, {'id': 9, 'module': False, 'time': 9700}, {'id': 56, 'module': False, 'time': 9800}, {'id': 290, 'module': False, 'time': 9900}]

failures_exp=[{'id': 398, 'module': False, 'time': 500}, {'id': 343, 'module': False, 'time': 694}, {'id': 48, 'module': False, 'time': 1070}, {'id': 133, 'module': True, 'time': 1072}, {'id': 288, 'module': False, 'time': 1136}, {'id': 283, 'module': False, 'time': 1323}, {'id': 374, 'module': False, 'time': 1451}, {'id': 168, 'module': False, 'time': 1471}, {'id': 331, 'module': False, 'time': 1493}, {'id': 265, 'module': False, 'time': 1691}, {'id': 119, 'module': False, 'time': 1694}, {'id': 233, 'module': False, 'time': 1722}, {'id': 353, 'module': False, 'time': 1837}, {'id': 337, 'module': True, 'time': 1838}, {'id': 199, 'module': False, 'time': 1858}, {'id': 232, 'module': False, 'time': 2393}, {'id': 13, 'module': False, 'time': 2419}, {'id': 95, 'module': False, 'time': 2723}, {'id': 317, 'module': False, 'time': 2814}, {'id': 163, 'module': False, 'time': 2919}, {'id': 67, 'module': False, 'time': 3012}, {'id': 279, 'module': True, 'time': 3077}, {'id': 267, 'module': False, 'time': 3112}, {'id': 147, 'module': False, 'time': 3296}, {'id': 174, 'module': False, 'time': 3353}, {'id': 202, 'module': False, 'time': 3489}, {'id': 310, 'module': False, 'time': 3579}, {'id': 206, 'module': False, 'time': 3647}, {'id': 153, 'module': False, 'time': 3752}, {'id': 193, 'module': False, 'time': 3804}, {'id': 17, 'module': False, 'time': 3825}, {'id': 281, 'module': False, 'time': 3928}, {'id': 393, 'module': False, 'time': 4107}, {'id': 236, 'module': False, 'time': 4173}, {'id': 65, 'module': True, 'time': 4372}, {'id': 197, 'module': False, 'time': 4642}, {'id': 392, 'module': False, 'time': 4737}, {'id': 307, 'module': False, 'time': 4832}, {'id': 213, 'module': False, 'time': 4950}, {'id': 345, 'module': False, 'time': 5128}, {'id': 201, 'module': False, 'time': 5312}, {'id': 380, 'module': False, 'time': 5323}, {'id': 227, 'module': False, 'time': 5366}, {'id': 177, 'module': False, 'time': 5413}, {'id': 216, 'module': True, 'time': 5740}, {'id': 382, 'module': False, 'time': 5789}, {'id': 2, 'module': False, 'time': 5840}, {'id': 312, 'module': False, 'time': 6326}, {'id': 326, 'module': False, 'time': 6338}, {'id': 354, 'module': False, 'time': 6344}, {'id': 292, 'module': False, 'time': 6395}, {'id': 321, 'module': False, 'time': 6529}, {'id': 218, 'module': False, 'time': 6539}, {'id': 159, 'module': False, 'time': 6566}, {'id': 22, 'module': False, 'time': 6830}, {'id': 348, 'module': False, 'time': 6847}, {'id': 222, 'module': False, 'time': 6999}, {'id': 75, 'module': False, 'time': 7053}, {'id': 191, 'module': False, 'time': 7315}, {'id': 183, 'module': False, 'time': 7370}, {'id': 131, 'module': False, 'time': 7440}, {'id': 127, 'module': False, 'time': 7466}, {'id': 210, 'module': False, 'time': 7584}, {'id': 247, 'module': False, 'time': 7706}, {'id': 243, 'module': False, 'time': 7748}, {'id': 171, 'module': False, 'time': 8281}, {'id': 84, 'module': False, 'time': 8343}, {'id': 64, 'module': False, 'time': 8366}, {'id': 231, 'module': False, 'time': 8389}, {'id': 344, 'module': False, 'time': 8447}, {'id': 318, 'module': False, 'time': 8616}, {'id': 325, 'module': False, 'time': 8970}, {'id': 264, 'module': False, 'time': 9031}, {'id': 31, 'module': False, 'time': 9125}, {'id': 6, 'module': False, 'time': 9424}, {'id': 5, 'module': False, 'time': 9526}, {'id': 299, 'module': True, 'time': 9572}, {'id': 42, 'module': False, 'time': 9701}, {'id': 248, 'module': False, 'time': 9867}, {'id': 126, 'module': False, 'time': 9891}, {'id': 28, 'module': False, 'time': 9916}, {'id': 61, 'module': True, 'time': 9928}]

              
print(len(failures_exp))
failures = failures_exp

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
    print(idx,item,len(item))
    #value = item == "True" ## OPTIONAL DESAAG. EVENTS
#    x = ticks[idx]
    x = idx
    if len(item)==4:    
        y = timeLatency[idx]+0.45
#        ax1.plot(ticks[idx], timeLatency[idx]+2, marker='o', c="green")
        ax1.arrow(x,4.7, 0, -0.35, head_width=15.0, head_length=0.15, fc='g', ec='g')
    elif len(item)==5:
        y = timeLatency[idx]+1
        ax1.arrow(x,4.7, 0, -0.1, head_width=0.5, head_length=0.1, fc='black', ec='black')
        #ax1.plot(x, y, marker='<', c="black")
        
#ax2 = ax1.twinx()
#ax2.set_ylabel("Number of allocation replicas", fontsize=16)
#ax2.set_yticks(ticks)
#ax2.set_xlim(0,35)
#ax2.plot(ticks, values, c="g",linestyle='-', marker="o",markersize=4)

#time_labels = []
#for t in ax1.get_xticks():
#   time_labels.append( "%3.0f"%(t*100))
#   ax1.set_xticklabels(time_labels)
#
#
#dfl["date"]=dfl.ctime.astype('datetime64[s]')
#dfl.index = dfl.date
#dfl1 = dfl.resample('100s').agg(dict(buffer='mean'))
#
#fig = plt.figure()
#ax1 = fig.add_subplot(111)
#ax1.plot(ticks, dfl1.buffer.values, '-')
#ax1.set_xlabel("Simulation time", fontsize=16)
#ax1.set_ylabel("Number of messages enqueued", fontsize=16)
#time_labels = []
#for t in ax2.get_xticks():
#    time_labels.append( "%3.0f"%(t*100))
#ax1.set_xticklabels(time_labels)



