from yafs.population import Population
import yafs.distribution

class JSONPopulation(Population):
    def __init__(self, json, it, **kwargs):
        super(JSONPopulation, self).__init__(**kwargs)
        self.data = json
        self.it =  it

    def initial_allocation(self, sim, app_name):
        for idx, behaviour in enumerate(self.data["sources"]):
            # Creating the type of the distribution
            # behaviour["args"] should have the same attributes of the used distribution
            class_ = getattr(yafs.distribution, behaviour["distribution"])
            if "seed" not in behaviour["args"].keys():
                seed = idx + self.it
                instance_distribution = class_(name="h%i" % idx, seed=seed, **behaviour["args"])
            else:
                instance_distribution = class_(name="h%i" % idx, **behaviour["args"])

            # Getting information from the APP
            app_name = behaviour["app"]
            app = sim.apps[app_name]
            msg = app.get_message(behaviour["message"])

            # TODO Include a more flexible constructor
            # if behaviour["entity"] == "all":
            #     for entity in sim.mobile_fog_entities:
            #         print entity
            #         idsrc = sim.deploy_source(app_name, id_node=int(entity), msg=msg, distribution=instance_distribution)
            # else:

            idsrc = sim.deploy_source(app_name, id_node=behaviour["entity"], msg=msg,distribution=instance_distribution)
