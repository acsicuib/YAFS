"""

    This example

    @author: Isaac Lera & Carlos Guerrero

"""
import json
import random
import networkx as nx
import argparse
from pathlib import Path
import time
import numpy as np

from selection_multipleDeploys import DeviceSpeedAwareRouting
from jsonPopulation import JSONPopulation

from yafs.core import Sim
from yafs.application import Application,Message,fractional_selectivity
from yafs.topology import Topology
from yafs.placement import JSONPlacement,JSONPlacementOnCloud
from yafs.distribution import *


def create_applications_from_json(data):
    applications = {}
    for app in data:
        a = Application(name=app["name"])
        modules = [{"None":{"Type":Application.TYPE_SOURCE}}]
        for module in app["module"]:
            modules.append({module["name"]: {"RAM": module["RAM"], "Type": Application.TYPE_MODULE}})
        a.set_modules(modules)

        ms = {}
        for message in app["message"]:
            #print "Creando mensaje: %s" %message["name"]
            ms[message["name"]] = Message(message["name"],message["s"],message["d"],instructions=message["instructions"],bytes=message["bytes"])
            if message["s"] == "None":
                a.add_source_messages(ms[message["name"]])

        #print "Total mensajes creados %i" %len(ms.keys())
        for idx, message in enumerate(app["transmission"]):
            if "message_out" in message.keys():
                a.add_service_module(message["module"],ms[message["message_in"]], ms[message["message_out"]], fractional_selectivity, threshold=1.0)
            else:
                a.add_service_module(message["module"], ms[message["message_in"]])

        applications[app["name"]]=a

    return applications


###
# Thanks to this function, the user can control about the elemination of the nodes according with the modules deployed (see also DynamicFailuresOnNodes example)
###
"""
It returns the software modules (a list of identifiers of DES process) deployed on this node
"""
def getProcessFromThatNode(sim, node_to_remove):
    if node_to_remove in sim.alloc_DES.values():
        DES = []
        # This node can have multiples DES processes on itself
        for k, v in sim.alloc_DES.items():
            if v == node_to_remove:
                DES.append(k)
        return DES,True
    else:
        return [],False



"""
It controls the elimination of a node
"""

def failureControl(sim,filelog,ids):
    global idxFControl # WARNING! This global variable has to be reset in each simulation test

    nodes = list(sim.topology.G.nodes())
    if len(nodes)>1:
        try:
            node_to_remove = ids[idxFControl]
            idxFControl +=1

            keys_DES,someModuleDeployed = getProcessFromThatNode(sim, node_to_remove)

            # print "\n\nRemoving node: %i, Total nodes: %i" % (node_to_remove, len(nodes))
            # print "\tStopping some DES processes: %s\n\n"%keys_DES
            filelog.write("%i,%s,%d\n"%(node_to_remove, someModuleDeployed,sim.env.now))

            ##Print some information:
            # for des in keys_DES:
            #     if des in sim.alloc_source.keys():
            #         print "Removing a Gtw/User entity\t"*4

            sim.remove_node(node_to_remove)
            for key in keys_DES:
                sim.stop_process(key)
        except IndexError:
            None

    else:
        sim.stop = True ## We stop the simulation


def main(simulated_time,experimento,ilpPath,it):
    """
    TOPOLOGY from a json
    """
    t = Topology()
    dataNetwork = json.load(open(experimento+'network.json'))
    t.load(dataNetwork)
    nx.write_gexf(t.G,"graph_main") # you can export the Graph in multiples format to view in tools like Gephi, and so on.

    """
    APPLICATION
    """
    dataApp = json.load(open(experimento+'appDefinition.json'))
    apps = create_applications_from_json(dataApp)
    for app in apps:
        print(apps[app])

    """
    PLACEMENT algorithm
    """
    placementJson = json.load(open(experimento+'allocDefinition%s.json'%ilpPath))
    placement = JSONPlacement(name="Placement",json=placementJson)

    ### Placement histogram

    # listDevices =[]
    # for item in placementJson["initialAllocation"]:
    #     listDevices.append(item["id_resource"])
    # import matplotlib.pyplot as plt
    # print listDevices
    # print np.histogram(listDevices,bins=range(101))
    # plt.hist(listDevices, bins=100)  # arguments are passed to np.histogram
    # plt.title("Placement Histogram")
    # plt.show()
    ## exit()
    """
    POPULATION algorithm
    """
    dataPopulation = json.load(open(experimento+'usersDefinition.json'))
    pop = JSONPopulation(name="Statical",json=dataPopulation,iteration=it)


    """
    SELECTOR algorithm
    """
    selectorPath = DeviceSpeedAwareRouting()

    """
    SIMULATION ENGINE
    """

    stop_time = simulated_time
    s = Sim(t, default_results_path=experimento + "Results_%s_%i_%i" % (ilpPath, stop_time,it))

    """
    Failure process
    """
    # time_shift = 10000
    # # distribution = deterministicDistributionStartPoint(name="Deterministic", time=time_shift,start=10000)
    # distribution = deterministicDistributionStartPoint(name="Deterministic", time=time_shift, start=1)
    # failurefilelog = open(experimento+"Failure_%s_%i.csv" % (ilpPath,stop_time),"w")
    # failurefilelog.write("node, module, time\n")
    # idCloud = t.find_IDs({"type": "CLOUD"})[0] #[0] -> In this study there is only one CLOUD DEVICE
    # centrality = np.load(pathExperimento+"centrality.npy")
    # s.deploy_monitor("Failure Generation", failureControl, distribution,sim=s,filelog=failurefilelog,ids=centrality)

    # randomValues = np.load(pathExperimento+"random.npy")
    # s.deploy_monitor("Failure Generation", failureControl, distribution,sim=s,filelog=failurefilelog,ids=randomValues)

    #For each deployment the user - population have to contain only its specific sources
    for aName in apps.keys():
        print("Deploying app: ",aName)
        pop_app = JSONPopulation(name="Statical_%s"%aName,json={},iteration=it)
        data = []
        for element in pop.data["sources"]:
            if element['app'] == aName:
                data.append(element)
        pop_app.data["sources"]=data

        s.deploy_app2(apps[aName], placement, pop_app, selectorPath)


    s.run(stop_time, test_initial_deploy=False, show_progress_monitor=False) #TEST to TRUE


    ## Enrouting information
    # print "Values"
    # print selectorPath.cache.values()


    #failurefilelog.close()

    # #CHECKS
    #print s.topology.G.nodes
    #s.print_debug_assignaments()

idxFControl = 0
if __name__ == '__main__':
    import os
    pathExperimento = "testjsons/"

    timeSimulation = 100
    print(os.getcwd())
    # logging.config.fileConfig(os.getcwd()+'/logging.ini')
    for i in range(50):
    #for i in  [0]:
        start_time = time.time()
        random.seed(i)
        np.random.seed(i)

        print("Running Partition")
        main(simulated_time=timeSimulation,  experimento=pathExperimento,ilpPath='',it=i)
        print("\n--- %s seconds ---" % (time.time() - start_time))
        start_time = time.time()

    print("Simulation Done")


