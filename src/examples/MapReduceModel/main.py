"""
    This example...
    @author: Isaac Lera & Carlos Guerrero

"""
import json
import argparse
from yafs.core import Sim
from yafs.application import Application,Message
from yafs.topology import Topology
from yafs.placement import JSONPlacement,JSONPlacementOnCloud
from yafs.distribution import *
import numpy as np
import logging.config
import os


from yafs.utils import fractional_selectivity

from selection_multipleDeploys import DeviceSpeedAwareRouting
from jsonPopulation import JSONPopulation

import time
import networkx as nx
RANDOM_SEED = 1

def create_applications_from_json(data):
    applications = {}
    for app in data:
        a = Application(name=app["name"])
        modules = [{"None":{"Type":Application.TYPE_SOURCE}}]
        for module in app["module"]:
            if "RAM" in module.keys():
                modules.append({module["name"]: {"RAM": module["RAM"], "Type": Application.TYPE_MODULE}})
            else:
                modules.append({module["name"]: {"RAM": 1, "Type": Application.TYPE_MODULE}})
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
                value_treshld = 1.0
                if "fractional" in message.keys():
                    value_treshld = message["fractional"]
                a.add_service_module(message["module"],ms[message["message_in"]], ms[message["message_out"]], fractional_selectivity, threshold=value_treshld)
            else:
                a.add_service_module(message["module"], ms[message["message_in"]])

        applications[app["name"]]=a

    #a.add_service_module("Client", m_egg, m_sensor, fractional_selectivity, threshold=0.9)
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
idxFControl = 0
def failureControl(sim,filelog,ids):
    global idxFControl
    nodes = list(sim.topology.G.nodes())
    if len(nodes)>1:
        node_to_remove = ids[idxFControl]
        idxFControl +=1

        keys_DES,someModuleDeployed = getProcessFromThatNode(sim, node_to_remove)

        print "\n\nRemoving node: %i, Total nodes: %i" % (node_to_remove, len(nodes))
        print "\tStopping some DES processes: %s\n\n"%keys_DES
        filelog.write("%i,%s,%d\n"%(node_to_remove, someModuleDeployed,sim.env.now))

        ##Print some information:
        for des in keys_DES:
            if des in sim.alloc_source.keys():
                print "Removing a Gtw/User entity\t"*4

        sim.remove_node(node_to_remove)
        for key in keys_DES:
            sim.stop_process(key)
    else:
        sim.stop = True ## We stop the simulation


def main(simulated_time,experimento,file,study,it):

    random.seed(it)
    np.random.seed(it)

    """
    TOPOLOGY from a json
    """
    t = Topology()


    dataNetwork = json.load(open(experimento+file+'-network.json'))
    t.load(dataNetwork)

    attNodes = {}
    for k in t.G.nodes():
        attNodes[k] = {"IPT": 1}
    nx.set_node_attributes(t.G, values=attNodes)

    # t.write("network.gexf")

    """
    APPLICATION
    """
    studyApp = study
    if study=="FstrRep":
        studyApp="Replica"
    elif study == "Cloud":
        studyApp="Single"

    dataApp = json.load(open(experimento+file+'-app%s.json'%studyApp))
    apps = create_applications_from_json(dataApp)
    #for app in apps:
    #  print apps[app]

    """
    PLACEMENT algorithm
    """
    placementJson = json.load(open(experimento+file+'-alloc%s.json'%study))
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

    studyUser = study
    if study == "FstrRep":
        studyUser = "Replica"
    elif study == "Cloud":
        studyUser = "Single"


    dataPopulation = json.load(open(experimento+file+'-users%s.json'%studyUser))
    pop = JSONPopulation(name="Statical",json=dataPopulation,it=it)


    """
    SELECTOR algorithm
    """
    selectorPath = DeviceSpeedAwareRouting()

    """
    SIMULATION ENGINE
    """

    stop_time = simulated_time
    s = Sim(t, default_results_path=experimento + "Results_%i_%s_%s_%i" % (it,file,study,stop_time))


    """
    Failure process
    """
    # time_shift = 10000
    # distribution = deterministicDistributionStartPoint(name="Deterministic", time=time_shift,start=10000)
    # failurefilelog = open(experimento+"Failure_%s_%i.csv" % (ilpPath,stop_time),"w")
    # failurefilelog.write("node, module, time\n")
    # idCloud = t.find_IDs({"type": "CLOUD"})[0] #[0] -> In this study there is only one CLOUD DEVICE
    # centrality = np.load(pathExperimento+"centrality.npy")
    # randomValues = np.load(pathExperimento+"random.npy")
    # # s.deploy_monitor("Failure Generation", failureControl, distribution,sim=s,filelog=failurefilelog,ids=centrality)
    # s.deploy_monitor("Failure Generation", failureControl, distribution,sim=s,filelog=failurefilelog,ids=randomValues)

    #For each deployment the user - population have to contain only its specific sources
    for aName in apps.keys():
        #print "Deploying app: ",aName
        pop_app = JSONPopulation(name="Statical_%s"%aName,json={},it=it)
        data = []
        for element in pop.data["sources"]:
            if element['app'] == aName:
                data.append(element)
        pop_app.data["sources"]=data

        s.deploy_app(apps[aName], placement, pop_app, selectorPath)


    s.run(stop_time, test_initial_deploy=False, show_progress_monitor=False) #TEST to TRUE


    ## Enrouting information
    # print "Values"
    # print selectorPath.cache.values()


    # failurefilelog.close()

    # #CHECKS
    #print s.topology.G.nodes
    # s.print_debug_assignaments()

if __name__ == '__main__':
    """Main function"""

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        '--work-dir',
        type=str,
        default="",
        help='Working directory')

    parser.add_argument(
        '--simulations',
        type=int,
        default=1,
        help='Number of simulations')

    parser.add_argument(
        '--duration',
        type=int,
        default=100000,
        help='Simulation time')

    args, pipeline_args = parser.parse_known_args()

    nSimulations = args.simulations
    pathExperimento = args.work_dir
    duration = args.duration



    study = ""

    #logging.config.fileConfig(os.getcwd()+'/logging.ini')

    for i in range(nSimulations):

        start_time = time.time()

        # for f in xrange(10, 110, 10):
        for f in xrange(100, 201, 10):
            # file = "f%in50" % f
            file = "f%in200" % f

            print file

            study = "Replica"
            print "\tRunning %s" % study
            main(simulated_time=duration, experimento=pathExperimento, file=file, study=study,it=i)

            study = "Single"
            print "\tRunning %s" % study
            main(simulated_time=duration, experimento=pathExperimento, file=file, study=study,it=i)

            study = "FstrRep"
            print "\tRunning %s" % study
            main(simulated_time=duration, experimento=pathExperimento, file=file, study=study,it=i)

          #  study = "Cloud"
          #  print "\tRunning %s" % study
          #  main(simulated_time=duration, experimento=pathExperimento, file=file, study=study,it=i)

        print "SEGUNDA PARTE"

        for n in xrange(100, 301, 20):
        # for n in xrange(20, 220, 20):
            file = "f100n%i" % n
            # file = "f100n%i" % n
            print file

            study = "Replica"
            print "\tRunning %s" % study
            main(simulated_time=duration, experimento=pathExperimento, file=file, study=study,it=i)

            study = "Single"
            print "\tRunning %s" % study
            main(simulated_time=duration, experimento=pathExperimento, file=file, study=study,it=i)

            study = "FstrRep"
            print "\tRunning %s" % study
            main(simulated_time=duration, experimento=pathExperimento, file=file, study=study,it=i)

           # study = "Cloud"
           # print "\tRunning %s" % study
           # main(simulated_time=duration, experimento=pathExperimento, file=file, study=study,it=i)

        print "Simulation Done"
        print("\n--- %s seconds ---" % (time.time() - start_time))


