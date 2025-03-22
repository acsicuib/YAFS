from collections import defaultdict
from agent import PolicyManager
from yafs.distribution import *
import logging

import sys


class Mario():

    def __init__(self):
        self.active = True
        self.logger = logging.getLogger(__name__)

    def __call__(self, sim, routing,pathCSV):
        # The occupation of a node can be managed by the simulator but to easy integration with the visualization both structures are different
        if self.active:
            self.service_calls = defaultdict(list)
            print(sim.alloc_DES)
            print(sim.alloc_module)
            for app in sim.alloc_module:
                for service in sim.alloc_module[app]:
                    for des in sim.alloc_module[app][service]:
                        logging.info("Generating a new agent control from: %s with id: %i"%(service,des))

                        period = deterministicDistribution(100, name="Deterministic") #TODO fix the TIME
                        pm = PolicyManager(des,service,pathCSV)
                        sim.deploy_monitor("Policy Manager %i"%des, pm, period, **{"sim": sim, "routing": routing})


            self.active = False #only one time