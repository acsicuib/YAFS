#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 18 13:39:00 2019

@author: isaaclera
"""

import simpy
import osmnx as ox
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import random
from matplotlib import colors
from shapely.ops import transform
from functools import partial
import pyproj
import scipy.spatial
from collections import OrderedDict


random.seed(0)


# =============================================================================
# Triggered actions when a mobile agent is under the coverage of a IoT device (edge/sensor)
# =============================================================================

class generic_action(object):
    # service_coverage
    #   key   => street node network
    #   value => id. module SW

    def __init__(self, service_coverage, env):
        self.service_coverage = service_coverage
        self.env = env

    def action(self,mobile_agent):
        None


class my_custom_action(generic_action):

    def __init__(self, *args, **kwargs):
        super(my_custom_action, self).__init__(*args, **kwargs)
        self.plates = {}
        self.fees = {}

    #mandatory function
    def action(self,ma): #mobile_entity
        # print "ACTION"
        # print ma
        # print ma.next_time
        # print ma.get_current_position()
        # print "-"*10
        if ma.get_current_position() in service_coverage.keys():
            if ma.plate in self.plates:
                self.fees[ma.plate]={"arrive":self.plates[ma.plate],"end":self.env.now}
            else:
                self.plates[ma.plate]=self.env.now

        
# =============================================================================
#  Generic definition of a mobile agent
# =============================================================================
# In this example, I thought in vehicles (cars)
        
#More constructs are necessaries: random paths, 
# A speed is necessary? or/and use of mov. distributions?
class generic_mobile_entity(object): #GME
    
    def __init__(self, _id, path, speed, action=None, start=0):
        self.__default_speed = 10.0    
        self._id=_id
        self.path = path
        self.speed = speed
        self.next_time = None

        self.do = action
        self.start = start

        self.current_position = 0 #path index

        if speed==0.0:
            self.speed = self.__default_speed
   

    def __str__(self):
        return "Agent (%i) in node: %i[%i/%i]"%(self._id,self.path[self.current_position],self.current_position,len(self.path)-1)

    def get_current_position(self):
        return self.path[self.current_position]

class car_agent(generic_mobile_entity):

    def __init__(self, *args, **kwargs):
        super(car_agent, self).__init__(*args, **kwargs)
        self.plate = "EU"+str(self._id)


    def __str__(self):   
        return "Car: %s {%s}"%(self.plate,super(car_agent,self).__str__())
    
        
#def actionFunction(mobileAgent, nextTime):
#    # print "%i \t Arrived! %s \t NEXT TIME: %i"%(env.now,mobileAgent,nextTime)
#    nodeid = mobileAgent.path[mobileAgent.current_position]
#    x,y = G.nodes[nodeid]['x'],G.nodes[nodeid]['y']
#    if (x,y) in service_coverage.keys():
#        print (x,y)
#        if ma.idx in plates:
#            print "REGISTRADO"
#            
#        else:
#            plates.append(ma.idx)
#            print plates
#        

# =============================================================================
# UTILS FUNCTIONS
# =============================================================================
def create_pos(G,scale):
    x = nx.get_node_attributes(G,'x')
    y = nx.get_node_attributes(G,'y')
    pos = {}
    for k in x.keys():
        lat = x[k]*scale
        lng = y[k]*scale
        pos[k]=np.array([lat,lng])
    return pos

def create_points(G):
    x = nx.get_node_attributes(G,'x')
    y = nx.get_node_attributes(G,'y')
    pos = OrderedDict()
    for k in x.keys():
        lat = x[k]
        lng = y[k]
        pos[k]=[lat,lng]
    return pos

def toMeters(geometry):
    project = partial(
    pyproj.transform,
    pyproj.Proj(init='EPSG:4326'),
    pyproj.Proj(init='EPSG:32633'))
    return transform(project,geometry).length

def get_random_node(G):
    return list(G.nodes())[random.randint(0,len(G.nodes())-1)]   

# =============================================================================
# INTERNAL FUNCTION OF YAFS-CORE
# =============================================================================
def __add_mobile_agent(idDES,gme,G):
    yield env.timeout(gme.start)
    while (len(gme.path)-1 > gme.current_position):
        e = (gme.path[gme.current_position], gme.path[ gme.current_position+1])
        data = G.get_edge_data(*e)
        try:
            nextTime = int(toMeters(data[0]["geometry"])/gme.speed)
        except KeyError:
            nextTime = 1 #default time by roundabout or other Spatial THINGS
            
        #take an action?
        gme.next_time = nextTime
        gme.do.action(gme)

        gme.current_position += 1
        yield env.timeout(nextTime)
 
    #Last movement
    gme.do.action(gme)
    print "Mobile agent: %s ends "%gme.plate


# =============================================================================
# ## Street network 
# =============================================================================
G = ox.graph_from_point((39.637759,  2.646532), distance=750, network_type='drive')


# =============================================================================
# ## Fog topology (based on the current YAFS version)
# =============================================================================
topology_json = {}
topology_json["entity"] = []
topology_json["link"] = []

cloud_dev    = {"id": 0, "model": "cloud","mytag":"cloud", "IPT": 5000 * 10 ** 6, "RAM": 40000,"COST": 3,"WATT":20.0, 'x': 2.6484887, 'y': 39.6580786}
sensor_dev   = {"id": 1, "model": "radar-device1", "IPT": 100* 10 ** 6, "RAM": 4000,"COST": 3,"WATT":40.0, 'x': 2.645623, 'y': 39.6426471}
sensor_dev2  = {"id": 2, "model": "radar-device2", "IPT": 100 * 10 ** 6, "RAM": 4000,"COST": 3, "WATT": 40.0,'x': 2.6507741, 'y': 39.6362394}

link1 = {"s": 0, "d": 1, "BW": 1, "PR": 10}
link2 = {"s": 0, "d": 2, "BW": 1, "PR": 1}

topology_json["entity"].append(cloud_dev)
topology_json["entity"].append(sensor_dev)
topology_json["entity"].append(sensor_dev2)
topology_json["link"].append(link1)
topology_json["link"].append(link2)

G2 = nx.Graph()
for edge in topology_json["link"]:
    G2.add_edge(edge["s"], edge["d"])
attNodes = {}
for entity in topology_json["entity"]:
    attNodes[entity['id']] = entity
nx.set_node_attributes(G2, values=attNodes)        
      

# =============================================================================
# # Plot both structures
# =============================================================================
posG = create_pos(G,100)
posG2 = create_pos(G2,100)
nx.draw(G,posG,node_size=50)
nx.draw(G2,posG2,node_size=20,node_color="yellow",edge_color='pink',width=2)


# =============================================================================
# #Creating links among g1:nodes - g2:nodes
# The coverage of fog entities and street structures
# YAFS INTERNAL FUNCTION
# =============================================================================
tolerance = 0.0001
pG = create_points(G)
pG2 = create_points(G2)
tree = scipy.spatial.KDTree(pG.values())
points_within_tolerance = tree.query_ball_point(pG2.values(),tolerance)

# key = node network
# value = id - module SW
service_coverage = {}

for idx,pt in enumerate(points_within_tolerance):
    ## MODULE SW
    key2 = pG2.keys()[idx]
    nG2 = G2.nodes[key2]
    print "%s is close to "%nG2["model"]
    ## Street coverage
    for p in pt:
        key = pG.keys()[p]
        print G.nodes[key]
        # service_coverage[(G.nodes[key]['x'],G.nodes[key]['y'])]=nG2["model"]
        service_coverage[key] = nG2["id"]

print "SERVICE COVERAGE"        
print service_coverage

 
# =============================================================================
# Simulation execution
# =============================================================================

env = simpy.Environment()
counter  =0

action = my_custom_action(service_coverage,env)

for i in range(10000):
    try:
        src = get_random_node(G)
        dst = get_random_node(G)
        path = nx.shortest_path(G,src,dst)
        
        paths = list(nx.all_simple_paths(G, source=src, target=dst,cutoff=5))
        
#        if len(path)==0:
#            continue
        speed = random.randint(2,20)
        start = random.randint(0,2000)
        ma = car_agent(i,path,speed,action,start)
        env.process(__add_mobile_agent(i, ma, G))
    except nx.NetworkXNoPath:
        counter+=1 #oneway edges by random choice

env.run(until=1000000)
print "COCHES REGISTRADOS EN ESE MOVIMIENTO: %i"%len(action.fees)
