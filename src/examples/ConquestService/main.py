"""

    This example

    @author: Isaac Lera & Carlos Guerrero

"""
import os
import time
import json
import networkx as nx
import logging.config
import collections
import pickle
import random
import numpy as np
from collections import Counter

from yafs.core import Sim
from yafs.application import Application, Message
from yafs.topology import Topology
from yafs.distribution import *
from yafs.application import fractional_selectivity
from yafs.placement import JSONPlacement

from customStrategy import CustomStrategy
from jsonDynamicPopulation import DynamicPopulation
from selection_multipleDeploys import DeviceSpeedAwareRouting

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


def main(simulated_time, path,pathResults,case,it):
    """
    TOPOLOGY from a json
    """
    t = Topology()
    dataNetwork = json.load(open(path + 'networkDefinition.json'))
    t.load(dataNetwork)
    nx.write_gexf(t.G,path+"graph_main") # you can export the Graph in multiples format to view in tools like Gephi, and so on.
    # t = loadTopology(path + 'test_GLP.gml')

    """
    APPLICATION
    """
    dataApp = json.load(open(path + 'appDefinition.json'))
    apps = create_applications_from_json(dataApp)
    # for app in apps:
    #  print apps[app]

    """
    PLACEMENT algorithm
    """
    # In our model only initial cloud placements are enabled
    placementJson = json.load(open(path + 'allocDefinition.json'))
    placement = JSONPlacement(name="Placement", json=placementJson)

    """
    SELECTOR and Deploying algorithm
    """
    selectorPath =   DeviceSpeedAwareRouting()


    """
    SIMULATION ENGINE
    """
    stop_time = simulated_time
    s = Sim(t, default_results_path=pathResults + "Results_%s_%i_%i" % (case, stop_time, it))


    """
    POPULATION algorithm
    """
    dataPopulation = json.load(open(path + 'usersDefinition.json'))
    # Each application has an unique population politic
    # For the original json, we filter and create a sub-list for each app politic
    for aName in apps.keys():
        data = []
        for element in dataPopulation["sources"]:
            if element['app'] == aName:
                data.append(element)

        distribution = exponentialDistribution(name="Exp", lambd=random.randint(100,200), seed= int(aName)*100+it)
        pop_app = DynamicPopulation(name="Dynamic_%s" % aName, data=data, iteration=it, activation_dist=distribution)
        s.deploy_app2(apps[aName], placement, pop_app, selectorPath)


    """
    CUSTOM EVOLUTION
    """
    dStart = deterministicDistributionStartPoint(stop_time/2.,stop_time / 2.0 /10.0, name="Deterministic")
    evol = CustomStrategy(pathResults)
    s.deploy_monitor("EvolutionOfServices", evol, dStart, **{"sim": s, "routing": selectorPath,"case":case, "stop_time":stop_time, "it":it})

    """
    RUNNING
    """
    logging.info(" Performing simulation: %s %i "%(case,it))
    s.run(stop_time, test_initial_deploy=False, show_progress_monitor=False)  # TEST to TRUE




    """
    Storing results from other strategies
    """

    # Getting some info
    s.print_debug_assignaments()

    evol.summarize()

    print("----")
    entities = s.get_alloc_entities()
    src_entities,modules_entities = Counter(),Counter()
    for k, v in entities.iteritems():
        src_entities[k]=0
        modules_entities[k]=0
        for service in v:
            if "None" in service:
                src_entities[k]+=1
            elif "_" in service:
                modules_entities[k]+=1 #[u'3#3_22', u'2#2_19']


    nx.set_node_attributes(s.topology.G, values=src_entities,name="SRC")
    nx.set_node_attributes(s.topology.G, values=modules_entities,name="MOD")

    nx.write_gexf(s.topology.G, pathResults + "/network_assignments_%s_%i_%i.gexf" % (case, stop_time, it))


    # controlServices = selectorPath.controlServices
    # f = open(pathResults + "/file_assignments_%s_%i_%i.pkl" % (case, stop_time, it), "wb")
    # pickle.dump(controlServices, f)
    # f.close()



if __name__ == '__main__':
    import logging.config

    logging.config.fileConfig(os.getcwd() + '/logging.ini')

    # NOTE: ABSOLUTE PATH TO JSON FILES ACCORDING TO THE EXECUTION-PLACE
    # We simplify the path update in our experimentation to external servers (it's a bit precarious but functional)
    runpath = os.getcwd()
    print (runpath)
    if "/home/uib/" in runpath :
        pathExperimento = "/home/uib/src/YAFS/src/examples/ConquestService/exp/"
    else:
        pathExperimento = "exp1/"
    #####

    print("PATH EXPERIMENTO: ",pathExperimento)
    nSimulations = 1
    timeSimulation = 1000000#100000
    datestamp = time.strftime('%Y%m%d')
    dname = pathExperimento + "results_"+datestamp+"/"
    try:
        os.makedirs(dname)
    except OSError:
        None

    # Multiple simulations
    for i in range(nSimulations):
        start_time = time.time()

        random.seed(i)
        np.random.seed(i)

        logging.info("Running Conquest - %s" %pathExperimento)

        main(simulated_time=timeSimulation, path=pathExperimento, pathResults=dname, case='CQ',it=i)

        print("\n--- %s seconds ---" % (time.time() - start_time))
        start_time = time.time()

    print("Simulation Done")
