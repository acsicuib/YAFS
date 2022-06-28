"""

    This example uses an external defintion of IoT domain based in a case study of FogTorchPI
    This domain definition is based on JSON files to illustrate how to include whatever policy in YAFS.

    The example used is the FogTorchPI implementation inspired on EGG_Game_Tractor application (IFogSim)

    Source: https://github.com/di-unipi-socc/FogTorchPI
    Branch: multithreaded
    Example folder is: FogTorchPI/src/main/java/di/unipi/socc/fogtorchpi/experiments/VR/
    with the following parameters:

    GATEWAYS =  2
    SMARTPHONES = 4
    Simulation time = 100000
    Tested: 02 May 2018


    Output running of FogTorchPI:

        java "-javaagent:/Applications/IntelliJ IDEA CE.app/Contents/lib/idea_rt.jar=50383:/Applications/IntelliJ IDEA CE.app/Contents/bin" -Dfile.encoding=UTF-8 -classpath main di.unipi.socc.fogtorchpi.experiments.VR.VRExample
        0 - [client_0_0->sp_0_0][client_0_1->sp_0_1][client_0_2->sp_0_2][client_0_3->sp_0_3][client_1_0->sp_1_0][client_1_1->sp_1_1][client_1_2->sp_1_2][client_1_3->sp_1_3][concentrator->isp][coordinator->gw_1]; 805.539; 2.5; 6.01
        1 - [client_0_0->sp_0_0][client_0_1->sp_0_1][client_0_2->sp_0_2][client_0_3->sp_0_3][client_1_0->sp_1_0][client_1_1->sp_1_1][client_1_2->sp_1_2][client_1_3->sp_1_3][concentrator->isp][coordinator->isp]; 807.534; 2.5; 6.01
        2 - [client_0_0->sp_0_0][client_0_1->sp_0_1][client_0_2->sp_0_2][client_0_3->sp_0_3][client_1_0->sp_1_0][client_1_1->sp_1_1][client_1_2->sp_1_2][client_1_3->sp_1_3][concentrator->gw_1][coordinator->gw_1]; 0.042; 2.5; 6.01
        3 - [client_0_0->sp_0_0][client_0_1->sp_0_1][client_0_2->sp_0_2][client_0_3->sp_0_3][client_1_0->sp_1_0][client_1_1->sp_1_1][client_1_2->sp_1_2][client_1_3->sp_1_3][concentrator->gw_1][coordinator->gw_0]; 0.042; 2.5; 6.01
        4 - [client_0_0->sp_0_0][client_0_1->sp_0_1][client_0_2->sp_0_2][client_0_3->sp_0_3][client_1_0->sp_1_0][client_1_1->sp_1_1][client_1_2->sp_1_2][client_1_3->sp_1_3][concentrator->isp][coordinator->gw_0]; 799.0185; 2.5; 6.01
        5 - [client_0_0->sp_0_0][client_0_1->sp_0_1][client_0_2->sp_0_2][client_0_3->sp_0_3][client_1_0->sp_1_0][client_1_1->sp_1_1][client_1_2->sp_1_2][client_1_3->sp_1_3][concentrator->gw_0][coordinator->isp]; 0.0735; 2.5; 6.01
        6 - [client_0_0->sp_0_0][client_0_1->sp_0_1][client_0_2->sp_0_2][client_0_3->sp_0_3][client_1_0->sp_1_0][client_1_1->sp_1_1][client_1_2->sp_1_2][client_1_3->sp_1_3][concentrator->gw_1][coordinator->isp]; 0.042; 2.5; 6.01
        7 - [client_0_0->sp_0_0][client_0_1->sp_0_1][client_0_2->sp_0_2][client_0_3->sp_0_3][client_1_0->sp_1_0][client_1_1->sp_1_1][client_1_2->sp_1_2][client_1_3->sp_1_3][concentrator->gw_0][coordinator->gw_0]; 0.0735; 2.5; 6.01
        8 - [client_0_0->sp_0_0][client_0_1->sp_0_1][client_0_2->sp_0_2][client_0_3->sp_0_3][client_1_0->sp_1_0][client_1_1->sp_1_1][client_1_2->sp_1_2][client_1_3->sp_1_3][concentrator->gw_0][coordinator->gw_1]; 0.0735; 2.5; 6.01
        ------------------
        ***Simulation ended in 11s!




    @author: isaac

"""
import json
from pprint import pprint


import argparse

from yafs.core import Sim
from yafs.application import Application,Message
from yafs.topology import Topology
from yafs.placement import JSONPlacement
from yafs.distribution import *

from selection_multipleDeploys import MinShortPath
from yafs.distribution import deterministicDistribution
from yafs.utils import fractional_selectivity
from jsonPopulation import *
import time

RANDOM_SEED = 1


def create_application():
    # APLICATION
    a = Application(name="EGG_GAME")

    a.set_modules([{"EGG":{"Type":Application.TYPE_SOURCE}},
                   {"Display": {"Type": Application.TYPE_SINK}},
                   {"Client": {"RAM": 10, "Type": Application.TYPE_MODULE}},
                   {"Calculator": {"RAM": 10, "Type": Application.TYPE_MODULE}},
                   {"Coordinator": {"RAM": 10, "Type": Application.TYPE_MODULE}}
                   ])
    """
    Messages among MODULES (AppEdge in iFogSim)
    """
    m_egg = Message("M.EGG", "EGG", "Client", instructions=2000*10**6, bytes=500)
    m_sensor = Message("M.Sensor", "Client", "Calculator", instructions=3500*10**6, bytes=500)
    m_player_game_state = Message("M.Player_Game_State", "Calculator", "Coordinator", instructions=1000*10**6, bytes=1000)
    m_concentration = Message("M.Concentration", "Calculator", "Client", instructions=14*10**6, bytes=500)           # This message is sent to all client modules
    m_global_game_state = Message("M.Global_Game_State", "Coordinator", "Client", instructions=28*10**6, bytes=1000, broadcasting=True) # This message is sent to all client modules
    m_global_state_update = Message("M.Global_State_Update", "Client", "Display",instructions=1000*10**6,bytes=500)
    m_self_state_update = Message("M.Self_State_Update", "Client", "Display",instructions=1000*10**6,bytes=500)

    """
    Defining which messages will be dynamically generated # the generation is controlled by Population algorithm
    """
    a.add_source_messages(m_egg)

    """
    MODULES/SERVICES: Definition of Generators and Consumers (AppEdges and TupleMappings in iFogSim)
    """
    # MODULE SOURCES: only periodic messages
    dDistribution = deterministicDistribution(name="Deterministic", time=100)

    a.add_service_source("Calculator", dDistribution, m_player_game_state) #According with the comments on VRGameFog.java, the period is 100ms
    a.add_service_source("Coordinator", dDistribution, m_global_game_state)
    # # MODULE SERVICES
    a.add_service_module("Client", m_egg, m_sensor, fractional_selectivity, threshold=0.9)
    a.add_service_module("Client", m_concentration, m_self_state_update, fractional_selectivity, threshold=1.0)
    a.add_service_module("Client", m_global_game_state, m_global_state_update, fractional_selectivity, threshold=1.0)
    a.add_service_module("Calculator", m_sensor, m_concentration, fractional_selectivity, threshold=1.0)
    a.add_service_module("Coordinator", m_player_game_state)

    return a

# @profile
def main(simulated_time):
    random.seed(RANDOM_SEED)

    """
    TOPOLOGY from a json
    """
    t = Topology()
    data = json.load(open('egg_infrastructure.json'))
    pprint(data["entity"])
    t.load(data)
    t.write("network.gexf")

    """
    APPLICATION
    """
    app = create_application()

    """
    PLACEMENT algorithm
    """
    #This adaptation can be done manually or automatically.
    # We make a simple manual allocation from the FogTorch output

    #8 - [client_0_0->sp_0_0][client_0_1->sp_0_1][client_0_2->sp_0_2][client_0_3->sp_0_3][client_1_0->sp_1_0][client_1_1->sp_1_1][client_1_2->sp_1_2]
    # [client_1_3->sp_1_3]
    # [concentrator->gw_0][coordinator->gw_1]; 0.105; 2.5; 6.01
    placementJson = {
        "initialAllocation": [
            {"app": "EGG_GAME",
             "module_name": "Calculator",
             "id_resource": 3},

            {"app": "EGG_GAME",
             "module_name": "Coordinator",
             "id_resource": 8},


            {"app": "EGG_GAME",
             "module_name": "Client",
             "id_resource": 4},
            {"app": "EGG_GAME",
             "module_name": "Client",
             "id_resource": 5},
            {"app": "EGG_GAME",
             "module_name": "Client",
             "id_resource": 6},
            {"app": "EGG_GAME",
             "module_name": "Client",
             "id_resource": 7},

            {"app": "EGG_GAME",
             "module_name": "Client",
             "id_resource": 9},
            {"app": "EGG_GAME",
             "module_name": "Client",
             "id_resource": 10},
            {"app": "EGG_GAME",
             "module_name": "Client",
             "id_resource": 11},
            {"app": "EGG_GAME",
             "module_name": "Client",
             "id_resource": 12},




        ]
    }


    placement = JSONPlacement(name="Places",json=placementJson)


    """
    POPULATION algorithm
    """

    populationJSON = {
          "sinks": [
            {"app": "EGG_GAME", "module_name": "Display", "id_resource": 4},
            {"app": "EGG_GAME", "module_name": "Display", "id_resource": 5},
            {"app": "EGG_GAME", "module_name": "Display", "id_resource": 6},
            {"app": "EGG_GAME", "module_name": "Display", "id_resource": 7},
            {"app": "EGG_GAME", "module_name": "Display", "id_resource": 9},
            {"app": "EGG_GAME", "module_name": "Display", "id_resource": 10},
            {"app": "EGG_GAME", "module_name": "Display", "id_resource": 11},
            {"app": "EGG_GAME", "module_name": "Display", "id_resource": 12}
        ],
        "sources":[
            {"app": "EGG_GAME", "message":"M.EGG", "lambda":100,"id_resource":4},
            {"app": "EGG_GAME", "message":"M.EGG", "lambda":100,"id_resource":5},
            {"app": "EGG_GAME", "message":"M.EGG", "lambda":100,"id_resource":6},
            {"app": "EGG_GAME", "message":"M.EGG", "lambda":100,"id_resource":7},
            {"app": "EGG_GAME", "message":"M.EGG", "lambda":100,"id_resource":9},
            {"app": "EGG_GAME", "message":"M.EGG", "lambda":100,"id_resource":10},
            {"app": "EGG_GAME", "message":"M.EGG", "lambda":100,"id_resource":11},
            {"app": "EGG_GAME", "message":"M.EGG", "lambda":100,"id_resource":12},
        ]

    }

    pop = JSONPopulation(name="Statical",json=populationJSON,iteration=0)

    """
    SELECTOR algorithm
    """
    selectorPath = MinShortPath()

    """
    SIMULATION ENGINE
    """

    stop_time = simulated_time
    s = Sim(t, default_results_path="Results_%i" % (stop_time))
    s.deploy_app(app, placement, pop, selectorPath)

    s.run(stop_time, test_initial_deploy=False, show_progress_monitor=False)
    s.print_debug_assignaments()


if __name__ == '__main__':
    import logging.config
    import os

    logging.config.fileConfig(os.getcwd()+'/logging.ini')

    start_time = time.time()

    main(simulated_time=100000)

    print("\n--- %s seconds ---" % (time.time() - start_time))
