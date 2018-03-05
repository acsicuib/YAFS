from yafs.stats import Stats
import numpy as np

# for size in [100,1000,10000,100000,1000000]:
time_loops = [["M.EGG", "M.Sensor", "M.Concentration"]]


#### ANALYSE FILES YAFS

police = "cloud"
police = "edge"

# print depth
# for idx1, depth in enumerate([4, 8, 12, 16]):
for idx1, depth in enumerate([2]):
    # 1000, 10000,
    for idx2,size in enumerate([1000,10000,100000]):
    #     size = 100000
        print "DEPTH: %i | TIME: %s" %(depth , size)
        s = Stats(defaultPath="Results_%s_%s_%s"%(police,size,depth))
        
        #Network
        s.showResults2(size, time_loops=time_loops)

        print "\t Bytes transmitted: " ,s.bytes_transmitted()
        print "\t Messages transmitted: ",s.count_messages()

        print "\t- Network saturation -"
        print "\t\tAverage waiting messages : %i" % s.average_messages_not_transmitted()
        print "\t\tPeak of waiting messages : %i" % s.peak_messages_not_transmitted()
        print "\t\tTOTAL messages not transmitted: %i" % s.messages_not_transmitted()

        #LOOPS
        # res = s.showLoops(time_loops)
        # loopstime[depth][idx2]=res[0]
        #
        # #Print the execution delay
        # print s.times("time_total_response")
        #
        # print "Latency Acc: ", s.df_link["latency"].sum()
        print "*"*40


