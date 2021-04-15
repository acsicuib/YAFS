from yafs.stats import Stats
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


size = 10000
path = "examples/DynamicFailuresOnNodes/"
# THIS VALUE MUST BE UPDATED FROM YOUR EXECUTION (COPYPASTE)
failures = [{'id': 398, 'module': False, 'time': 0}, {'id': 343, 'module': False, 'time': 100}, {'id': 48, 'module': False, 'time': 200}, {'id': 133, 'module': True, 'time': 300}, {'id': 288, 'module': False, 'time': 400}, {'id': 283, 'module': False, 'time': 500}, {'id': 374, 'module': False, 'time': 600}, {'id': 168, 'module': False, 'time': 700}, {'id': 331, 'module': False, 'time': 800}, {'id': 265, 'module': False, 'time': 900}, {'id': 119, 'module': False, 'time': 1000}, {'id': 233, 'module': False, 'time': 1100}, {'id': 353, 'module': False, 'time': 1200}, {'id': 337, 'module': True, 'time': 1300}, {'id': 199, 'module': False, 'time': 1400}, {'id': 232, 'module': False, 'time': 1500}, {'id': 13, 'module': False, 'time': 1600}, {'id': 95, 'module': False, 'time': 1700}, {'id': 317, 'module': False, 'time': 1800}, {'id': 163, 'module': False, 'time': 1900}, {'id': 67, 'module': False, 'time': 2000}, {'id': 279, 'module': True, 'time': 2100}, {'id': 267, 'module': False, 'time': 2200}, {'id': 147, 'module': False, 'time': 2300}, {'id': 174, 'module': False, 'time': 2400}, {'id': 202, 'module': False, 'time': 2500}, {'id': 310, 'module': False, 'time': 2600}, {'id': 206, 'module': False, 'time': 2700}, {'id': 153, 'module': False, 'time': 2800}, {'id': 193, 'module': False, 'time': 2900}, {'id': 17, 'module': False, 'time': 3000}, {'id': 281, 'module': False, 'time': 3100}, {'id': 393, 'module': False, 'time': 3200}, {'id': 236, 'module': False, 'time': 3300}, {'id': 65, 'module': True, 'time': 3400}, {'id': 197, 'module': False, 'time': 3500}, {'id': 392, 'module': False, 'time': 3600}, {'id': 307, 'module': False, 'time': 3700}, {'id': 213, 'module': False, 'time': 3800}, {'id': 345, 'module': False, 'time': 3900}, {'id': 201, 'module': False, 'time': 4000}, {'id': 380, 'module': False, 'time': 4100}, {'id': 227, 'module': False, 'time': 4200}, {'id': 177, 'module': False, 'time': 4300}, {'id': 216, 'module': True, 'time': 4400}, {'id': 382, 'module': False, 'time': 4500}, {'id': 2, 'module': False, 'time': 4600}, {'id': 312, 'module': False, 'time': 4700}, {'id': 326, 'module': False, 'time': 4800}, {'id': 354, 'module': False, 'time': 4900}, {'id': 292, 'module': False, 'time': 5000}, {'id': 321, 'module': False, 'time': 5100}, {'id': 218, 'module': False, 'time': 5200}, {'id': 159, 'module': False, 'time': 5300}, {'id': 22, 'module': False, 'time': 5400}, {'id': 348, 'module': False, 'time': 5500}, {'id': 222, 'module': False, 'time': 5600}, {'id': 75, 'module': False, 'time': 5700}, {'id': 191, 'module': False, 'time': 5800}, {'id': 183, 'module': False, 'time': 5900}, {'id': 131, 'module': False, 'time': 6000}, {'id': 127, 'module': False, 'time': 6100}, {'id': 210, 'module': False, 'time': 6200}, {'id': 247, 'module': False, 'time': 6300}, {'id': 243, 'module': False, 'time': 6400}, {'id': 171, 'module': False, 'time': 6500}, {'id': 84, 'module': False, 'time': 6600}, {'id': 64, 'module': False, 'time': 6700}, {'id': 231, 'module': False, 'time': 6800}, {'id': 344, 'module': False, 'time': 6900}, {'id': 318, 'module': False, 'time': 7000}, {'id': 325, 'module': False, 'time': 7100}, {'id': 264, 'module': False, 'time': 7200}, {'id': 31, 'module': False, 'time': 7300}, {'id': 6, 'module': False, 'time': 7400}, {'id': 5, 'module': False, 'time': 7500}, {'id': 299, 'module': True, 'time': 7600}, {'id': 42, 'module': False, 'time': 7700}, {'id': 248, 'module': False, 'time': 7800}, {'id': 126, 'module': False, 'time': 7900}, {'id': 28, 'module': False, 'time': 8000}, {'id': 61, 'module': True, 'time': 8100}, {'id': 205, 'module': False, 'time': 8200}, {'id': 66, 'module': False, 'time': 8300}, {'id': 104, 'module': False, 'time': 8400}, {'id': 284, 'module': False, 'time': 8500}, {'id': 121, 'module': False, 'time': 8600}, {'id': 181, 'module': False, 'time': 8700}, {'id': 145, 'module': False, 'time': 8800}, {'id': 160, 'module': False, 'time': 8900}, {'id': 73, 'module': False, 'time': 9000}, {'id': 41, 'module': False, 'time': 9100}, {'id': 364, 'module': False, 'time': 9200}, {'id': 200, 'module': True, 'time': 9300}, {'id': 82, 'module': False, 'time': 9400}, {'id': 245, 'module': False, 'time': 9500}, {'id': 330, 'module': False, 'time': 9600}, {'id': 9, 'module': False, 'time': 9700}, {'id': 56, 'module': False, 'time': 9800}, {'id': 290, 'module': False, 'time': 9900}]
print("Number of nodes removed: ",len(failures))


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
ax1.set_ylim(timeLatency.min()-0.5,5)#timeLatency.max()+0.5)
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
#plt.savefig('figure9b.pdf', format='pdf', dpi=600)        

