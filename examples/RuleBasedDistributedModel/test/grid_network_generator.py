import networkx as nx
import matplotlib.pyplot as plt 
import numpy as np
from matplotlib import colors
import matplotlib as mpl
import math
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
import json



dim = 10
G = nx.grid_graph([dim,dim])
pos = dict(zip(G.nodes(),G.nodes()))

for x in range(9,-1,-1):
    for y in range(9,0,-1):
        if x>0:
            G.add_edge((x,y),(x-1,y-1))
        if x<9:
            G.add_edge((x,y),(x+1,y-1))

services = 4

capacity = np.zeros(6)
capacity[0]=0.01
#print capacity.reshape((2,3))

#Defining capacity node (radial)
#par = dim%2.0==0
#dist_capacity=[2,4,]

mapCapacity={0:(1,2),1:(2,2),2:(3,3),3:(4,4),4:(5,5)}

#Desgrana el perimetro de una matrix por diferentes niveles para asignar una capacidad a cada nodo
nodeCapacity={}
currentOccupation={}

half=(dim/2)
levelR=0
for x in range(dim):
    if dim%2==0 and levelR==half: levelR-=1
    p = range(0,levelR,1)+range(dim-levelR,dim)
    levelC=0    
    for y in range(dim):
        if y in p:
            if y>half:
                levelC-=1
#            print x,y,levelC
            nodeCapacity[(x,y)]=mapCapacity[levelC]
            currentOccupation[(x,y)]=np.zeros(mapCapacity[levelC][0]*mapCapacity[levelC][1])
            if y<=half: 
                levelC+=1
        else:
#            print x,y,levelR
            nodeCapacity[(x,y)]=mapCapacity[levelR]
            currentOccupation[(x,y)]=np.zeros(mapCapacity[levelR][0]*mapCapacity[levelR][1])
    if x<half:
        levelR+=1
    else:
        levelR-=1
    
def getID(node):
    return dim*node[0]+node[1]

#writing topology -> networkDefinition.json
topology = dict({"entity":[],"link":[]})
for edge in G.edges():
    topology["link"].append({"s":getID(edge[0]),"d":getID(edge[1]),"BW":10,"PR":100})
for node in G.nodes():
    topology["entity"].append(({"id":getID(node),"capacity":str(nodeCapacity[node]),
                      "occupation":str(currentOccupation[node]).replace(".",","),"name":node,
                      "IPT": 1000, "RAM": 1, "COST": 1, "WATT": 1.0}))

with open("networkDefinition_grid_10.json","w") as f:
    json.dump(topology,f)




#Imshow size
piesize=.05
p2=piesize/2.

#Color map
#my_cmap = plt.cm.get_cmap('tab20')
#my_cmap.set_under('whitesmoke')
#
#tab20 = plt.cm.get_cmap('tab20', 256)
#newcolors = tab20(np.linspace(0, 1, 256))
#basecolor = np.array([250.0/256.0, 250./256., 250./256., 1])
#newcolors[:1, :] = basecolor
#newcmp = ListedColormap(newcolors)

tab20 = plt.cm.get_cmap('tab20', services)
bounds = range(services)
newcolors = tab20(np.linspace(0, 1, services))
newcolors[0]=np.array([250.0/256.0, 250./256., 250./256., 1])
newcmp = mpl.colors.ListedColormap(newcolors)
norm = mpl.colors.BoundaryNorm(bounds, newcmp.N)

fig, ax = plt.subplots(figsize=(9.0,6.0))
#Nodes + Egdes
nx.draw(G, pos, with_labels=False, node_size=200, node_color="#1260A0",edge_color="gray", node_shape="o",font_size=7,font_color="white",ax=ax)    

#Labels on nodes
for x in range(9,-1,-1):
    for y in range(9,-1,-1):
        ax.text(x+piesize*2.5,y+piesize*7.5,"%i-%i"%(x,y),fontsize=8)
#        ax.text(x+piesize*2.5,y+piesize*7.5,"%i-%i:(%s)"%(x,y,nodeCapacity[(x,y)]),fontsize=8)
  
def assignoccupation(node,service):
    try:
        pos = list(currentOccupation[node]).index(0.)
        currentOccupation[node][pos]=service        
        return True
    except ValueError:
        return False

def removeoccupation(node,service):
    try:
        pos = list(currentOccupation[node]).index(0.)
        currentOccupation[node][pos]=0.
        return True
    except ValueError:
        return False  
    
print assignoccupation((4,4),1)
print assignoccupation((4,4),2)
print assignoccupation((4,4),3)
print assignoccupation((4,4),4)
print assignoccupation((4,4),5)
print assignoccupation((4,4),6)
print assignoccupation((4,4),7)
print currentOccupation[(4,4)]


print assignoccupation((3,5),1)
print assignoccupation((3,5),2)
print assignoccupation((3,5),3)
print assignoccupation((3,5),4)
print assignoccupation((3,5),5)


print assignoccupation((1,5),1)
print assignoccupation((1,5),2)
print assignoccupation((1,5),3)


print assignoccupation((2,4),4)
print assignoccupation((2,4),4)
print assignoccupation((2,4),4)
print currentOccupation[(2,4)]

print assignoccupation((2,5),2)
print assignoccupation((2,5),3)
print assignoccupation((2,5),4)


print assignoccupation((0,4),3)
print assignoccupation((0,4),3)
print assignoccupation((0,4),3)
print currentOccupation[(0,4)]
data = currentOccupation[(0,4)].reshape(nodeCapacity[(0,4)])
print data

print assignoccupation((0,5),3)
print assignoccupation((0,5),2)


print assignoccupation((0,3),2)
print assignoccupation((0,3),2)


controlUser={}

def showUser(node,service):
    if node not in controlUser.keys():
        controlUser[node]=0

    total = controlUser[node]
    line = (total/4)+1
    duy=0.2*line
    dux=0.15*((total%4))
    controlUser[node]+=1
    
    print node,service,total,line,(total%5)+1
    
    if node[0]==0:#este
        dx=-piesize*10.-(dux*.8)
        dy= piesize*8.5-(duy*1.4)
    elif node[1]==0:#south
        dx=-piesize*9.5+duy
        dy=-piesize*10.-dux
    elif node[0]==9:#west
        dx=piesize*10.+dux
        dy= piesize*9.-duy
    elif node[1]==9:#north
        dx=-piesize*9+(duy*.8)
        dy=piesize*10.+(dux*1.4)
    ax.scatter(node[0]+dx,node[1]+dy,s=100.0, marker='o', color=newcolors[service])
    
def removeUser(node,service):
    if node not in controlUser.keys():
        return False
    else:
        controlUser[node]-=1
        return True
 
node = (0,4)
showUser(node,3)
showUser(node,3)
showUser(node,3)
showUser(node,3)
showUser(node,2)
showUser(node,2)
showUser(node,2)
showUser(node,1)
showUser(node,1)
node = (0,5)
showUser(node,2)

node = (3,0)
showUser(node,2)
showUser(node,2)
showUser(node,2)
showUser(node,2)
showUser(node,4)
showUser(node,4)
showUser(node,4)
showUser(node,4)
showUser(node,6)
showUser(node,7)
showUser(node,3)

node = (9,5)
showUser(node,2)
showUser(node,2)
showUser(node,2)
showUser(node,2)
showUser(node,3)



node = (4,9)
showUser(node,2)
showUser(node,2)
showUser(node,2)
showUser(node,2)
showUser(node,3)




#Displaying capacity, changing node shape        
trans=ax.transData.transform
trans2=fig.transFigure.inverted().transform
for n in G:
    xx,yy=trans(pos[n]) # figure coordinates
    xa,ya=trans2((xx,yy)) # axes coordinates
    
    a = plt.axes([xa-p2,ya-p2, piesize, piesize])
    a.set_aspect('equal')

    data = currentOccupation[n].reshape(nodeCapacity[n])
#    data=[[1.,3.,1.]]

    a.imshow(data,cmap=newcmp, interpolation='none',norm=norm)
    #    a.axis('off')
    a.axes.get_yaxis().set_visible(False)
    a.axes.get_xaxis().set_visible(False)


pos2 = {getID((x,y)):(x,y) for x in range(10) for y in range(10)}

np.linspace(0,10,10)*5