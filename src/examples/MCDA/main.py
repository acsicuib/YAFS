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

from yafs.core import Sim
from yafs.application import Application, Message
from yafs.topology import Topology
from yafs.distribution import *
from yafs.utils import fractional_selectivity

from yafs.placement import JSONPlacement
from MCDAPathSelectionNPlacement import MCDARoutingAndDeploying
from WAPathSelectionNPlacement import WARoutingAndDeploying
from jsonDynamicPopulation import DynamicPopulation
from placementOnlyCloud import JSONPlacementOnlyCloud
from jsonPopulation import JSONPopulation



def create_applications_from_json(data):
    applications = {}
    for app in data:
        a = Application(name=app["name"])
        modules = [{"None": {"Type": Application.TYPE_SOURCE}}]
        for module in app["module"]:
            modules.append({module["name"]: {"RAM": module["RAM"], "Type": Application.TYPE_MODULE}})
        a.set_modules(modules)

        ms = {}
        for message in app["message"]:
            # print "Creando mensaje: %s" %message["name"]
            ms[message["name"]] = Message(message["name"], message["s"], message["d"],
                                          instructions=message["instructions"], bytes=message["bytes"])
            if message["s"] == "None":
                a.add_source_messages(ms[message["name"]])

        # print "Total mensajes creados %i" %len(ms.keys())
        for idx, message in enumerate(app["transmission"]):
            if "message_out" in message.keys():
                a.add_service_module(message["module"], ms[message["message_in"]], ms[message["message_out"]],
                                     fractional_selectivity, threshold=1.0)
            else:
                a.add_service_module(message["module"], ms[message["message_in"]])

        applications[app["name"]] = a

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
        return DES, True
    else:
        return [], False


"""
It controls the elimination of a node
"""


def failureControl(sim, filelog, ids):
    global idxFControl  # WARNING! This global variable has to be reset in each simulation test

    nodes = list(sim.topology.G.nodes())
    if len(nodes) > 1:
        try:
            node_to_remove = ids[idxFControl]
            idxFControl += 1

            keys_DES, someModuleDeployed = getProcessFromThatNode(sim, node_to_remove)

            # print "\n\nRemoving node: %i, Total nodes: %i" % (node_to_remove, len(nodes))
            # print "\tStopping some DES processes: %s\n\n"%keys_DES
            filelog.write("%i,%s,%d\n" % (node_to_remove, someModuleDeployed, sim.env.now))

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
        sim.stop = True  ## We stop the simulation

# def loadTopology(pathGML):
#     t = Topology()
#     t.G = parser_ashiip.parse_ashiip(pathGML)
#
#     return t

def main(simulated_time, path,pathResults,case, failuresON, it,idcloud):
    """
    TOPOLOGY from a json
    """
    t = Topology()
    dataNetwork = json.load(open(path + 'networkDefinition.json'))
    t.load(dataNetwork)
    t.write(path +"network.gexf")
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
    placementJson = json.load(open(path + 'allocDefinition%s.json' % case))
    if case == "MCDA":
        # We modify this class to enable only cloud placement
        # Note: In this json, all service are assigned to the cloud device and other devices/nodes
        placement = JSONPlacementOnlyCloud(name="MCDA-Placement",idcloud=idcloud, json=placementJson)
    else:
        placement = JSONPlacement(name="Placement", json=placementJson)



    """
    SELECTOR and Deploying algorithm
    """
    if case == "MCDA":
        selectorPath = MCDARoutingAndDeploying(path=path,pathResults=pathResults,idcloud=idcloud)
    else:
        selectorPath = WARoutingAndDeploying(path=path, pathResults=pathResults,idcloud=idcloud)



    """
    SIMULATION ENGINE
    """

    stop_time = simulated_time
    s = Sim(t, default_results_path=pathResults + "Results_%s_%i_%i" % (case, stop_time, it))

    # """
    # Failure process
    # """
    # if failuresON:
    #     time_shift = 10000
    #     distribution = deterministicDistributionStartPoint(name="Deterministic", time=time_shift, start=100)
    #     failurefilelog = open(path + "Failure_%s_%i.csv" % (case, stop_time), "w")
    #     failurefilelog.write("node, module, time\n")
    #
    #     # idCloud = t.find_IDs({"type": "CLOUD"})[0] #[0] -> In this study there is only one CLOUD DEVICE
    #     # centrality = np.load(pathExperimento+"centrality.npy")
    #     # s.deploy_monitor("Failure Generation", failureControl, distribution,sim=s,filelog=failurefilelog,ids=centrality)
    #
    #     randomValues = np.load(path + "random.npy")
    #     s.deploy_monitor("Failure Generation", failureControl, distribution, sim=s, filelog=failurefilelog,
    #                      ids=randomValues)

    # For each deployment the user - population have to contain only its specific sources

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

        distribution = exponentialDistribution(name="Exp", lambd=random.randint(100,1000), seed= int(aName)*100+it)
        pop_app = DynamicPopulation(name="Dynamic_%s" % aName, data=data, iteration=it, activation_dist=distribution)
        s.deploy_app(apps[aName], placement, pop_app, selectorPath)

    logging.info(" Performing simulation: %s %i "%(case,it))
    s.run(stop_time, test_initial_deploy=False, show_progress_monitor=False)  # TEST to TRUE

    ## Enrouting information
    # print "Values"
    # print selectorPath.cache.values()

    # if failuresON:
    #     failurefilelog.close()
        # #CHECKS
        # print s.topology.G.nodes
    s.print_debug_assignaments()

    # Genera un fichero GEPHI donde se marcan los nodos con usuarios (userposition) y los nodos con servicios desplegados (services)
    print "----"
    l = s.get_alloc_entities()
    userposition = {}
    deploymentservices = {}
    for k in l:
        cu = 0
        cd = 0
        for item in l[k]:
            if "None" in item:
                cu += 1
            else:
                cd += 1

        deploymentservices[k] = cd
        userposition[k] = cu

    nx.set_node_attributes(s.topology.G, values =deploymentservices, name='services')
    nx.set_node_attributes(s.topology.G, values= userposition, name='userposition')
    # nx.write_gexf(s.topology.G, "network_assignments.gexf")

    print selectorPath.dname
    f = open(selectorPath.dname + "/file_alloc_entities_%s_%i_%i.pkl" % (case, stop_time, it), "wb")
    pickle.dump(l, f)
    f.close()

    print "----"
    controlServices = selectorPath.controlServices
    # print controlServices
    attEdges = collections.Counter()
    for k in controlServices:
        path = controlServices[k][0]
        for i in range(len(path)-1):
            edge = (path[i],path[i+1])
            attEdges[edge]+=1

    dl = {}
    for item in attEdges:
        dl[item] = {"W":attEdges[item]}
    nx.set_edge_attributes(s.topology.G, values=dl)

    nx.write_gexf(s.topology.G, selectorPath.dname+"/network_assignments_%s_%i_%i.gexf"% (case, stop_time, it))

    f = open(selectorPath.dname+"/file_assignments_%s_%i_%i.pkl" % (case, stop_time, it),"wb")
    pickle.dump(controlServices,f)
    f.close()

idxFControl = 0
logging.config.fileConfig(os.getcwd() + '/logging.ini')
if __name__ == '__main__':

    # NOTE: ABSOLUTE PATH TO JSON FILES ACCORDING TO THE EXECUTION-PLACE
    # We simplify the path update in our experimentation to external servers (it's a bit precarious but functional)
    runpath = os.getcwd()
    print runpath
    if "/home/uib/" in runpath :
        pathExperimento = "/home/uib/src/YAFS/src/examples/MCDA/exp1/"
    else:
        pathExperimento = "exp1/"
    #####

    print "PATH EXPERIMENTO: ",pathExperimento
    nSimulations = 1
    timeSimulation = 10000
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

        logging.info("Running MCDA - ELECTRE - %s" %pathExperimento)
        idxFControl = 0  # reset counter of failure nodes

        # Note: Some simulation parameters have to be defined inside of the main function
        # - Distribution lambdas
        # - Device id cloud
        # - Random seed for users
        main(simulated_time=timeSimulation, path=pathExperimento, pathResults=dname, case='MCDA', failuresON=False, it=i,idcloud = 153)

        random.seed(i)
        np.random.seed(i)

        logging.info("Running WA - %s" % pathExperimento)
        idxFControl = 0  # reset counter of failure nodes
        main(simulated_time=timeSimulation, path=pathExperimento,pathResults=dname, case='WA', failuresON=False, it=i, idcloud=153)

        print("\n--- %s seconds ---" % (time.time() - start_time))
        start_time = time.time()

    print "Simulation Done"

### NOTAS:
# Deberia de cambiar la posicion en cada simulation