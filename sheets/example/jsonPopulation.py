from yafs.population import Population
from yafs.distribution import exponentialDistribution

class JSONPopulation(Population):
    def __init__(self, json, **kwargs):
        super(JSONPopulation, self).__init__(**kwargs)
        self.data = json

    def initial_allocation(self, sim, app_name):
            # for item in self.data["sinks"]:
            #     app_name = item["app"]
            #     module = item["module_name"]
            #     idtopo = item["id_resource"]
            #     sim.deploy_sink(app_name, node=idtopo, module=module)

            for item in self.data["sources"]:
                if item["app"]== app_name:
                    app_name = item["app"]
                    idtopo = item["id_resource"]
                    lambd = item["lambda"]
                    app = sim.apps[app_name]
                    msg = app.get_message(item["message"])

                    dDistribution = exponentialDistribution(name="Exp", lambd=lambd)

                    idsrc = sim.deploy_source(app_name, id_node=idtopo, msg=msg, distribution=dDistribution)

