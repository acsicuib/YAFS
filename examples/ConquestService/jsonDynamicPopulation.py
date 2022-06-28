from yafs.population import Population
from yafs.distribution import exponentialDistribution
import random
import logging


class DynamicPopulation(Population):
    """
    We launch one user by invocation
    """
    def __init__(self, data, iteration,logger=None,**kwargs):
        super(DynamicPopulation, self).__init__(**kwargs)
        self.data = data
        self.it = iteration
        self.userOrderInputByInvocation = []

        self.logger = logger or logging.getLogger(__name__)

        self.logger.info(" Initializating dynamic population: %s"%self.name)

    """
    In userOrderInputByInvocation, we create the user apparition sequence
    """
    def initial_allocation(self, sim, app_name):
            size = len(self.data)
            self.userOrderInputByInvocation = random.sample(range(size), size)

    """
    In each invocation, we launch one user
    """
    def run(self, sim):
        if len(self.userOrderInputByInvocation)>0:
            idx = self.userOrderInputByInvocation.pop(0)
            item = self.data[idx]

            app_name = item["app"]
            idtopo = item["id_resource"]
            lambd = item["lambda"]

            self.logger.info("Launching user %i (app: %s), in node: %i, at time: %i " % (item["id_resource"],app_name, idtopo,sim.env.now))

            app = sim.apps[app_name]
            msg = app.get_message(item["message"])

            # A basic creation of the seed: unique for each user and different in each simulation repetition
            seed = item["id_resource"] * 1000 + item["lambda"] + self.it

            dDistribution = exponentialDistribution(name="Exp", lambd=lambd, seed=seed)
            idsrc = sim.deploy_source(app_name, id_node=idtopo, msg=msg, distribution=dDistribution)



