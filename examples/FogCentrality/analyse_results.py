from yafs.metrics import *
import pandas as pd
import glob
import networkx as nx
import matplotlib.pyplot as plt



community_size = [50,100,200,300]

topologies = {
    "BarabasiAlbert": "data/BarabasiAlbert2.graphml",
    "Grid": "data/grid200.graphml",
    "RandomEuclidean": "data/RandomEuclidean.graphml",
    "Lobster": "data/Lobster.graphml",

}
# functions =       ["Cluster","Eigenvector","Betweenness_centrality","Current_flow_betweenness_centrality"]
# labelsFunctions = ["Cloud","Eigenvector","Betweenness","Current Flow Betweenness"]


functions =       ["Cluster","Eigenvector"]
labelsFunctions = ["Cloud","Eigenvector"]

values = [[],[],[],[]]

m = Metrics()

for topo in topologies:
    print topo
    for size in community_size:
        print "\t",size
        vcluster = 0.0
        for idx, f in enumerate(functions):
            m.load_results("results_exp/results_exp_%s_%i_%s" % (topo,size,f))
            df,dl = m.get()
            print "\t\t%s :%i" %(labelsFunctions[idx], len(dl))
            if vcluster == 0.0:
                vcluster = len(dl)+0.0
            else:
                print "\t\tSpeedup %f" %(float(len(dl))/vcluster)
            values[idx].append(len(dl))
exit()

experiments = len(community_size)

fig, ax = plt.subplots(figsize=(8,4))
width = 0.18

colors = ["firebrick","yellowgreen","navy","darkorange","purple"]

index = np.arange(experiments)
p = range(0,5)
N = len(functions)

# patterns = ('x', ' ', ' ', 'o', 'O', '.')

for idx,f in enumerate(labelsFunctions):
    print idx
    print f
    p[idx] = plt.bar(index+(width*idx), values[idx], width, color=colors[idx], label=f) #hatch=patterns[idx])



plt.xticks(index + N*width/2.7, ("50","100","200","300"))
# plt.yticks(np.arange(0, 120, 20))
# plt.ylim(2000,8000)
ax.set_ylabel("Number of transmitted messages",fontsize=16)
ax.set_xlabel("Number of datatypes",fontsize=16)

# fig.savefig('test.jpg')
# ax.set_title("Lobster topology")
plt.legend((p[0],p[1],p[2],p[3]), labelsFunctions,fancybox=True,loc='upper left',framealpha=0.65,fontsize=14)
plt.gcf().subplots_adjust(bottom=0.15)

# fig.canvas.draw()
ax.grid(True)

plt.savefig('Grid.pdf', format='pdf', dpi=600)
plt.show()





