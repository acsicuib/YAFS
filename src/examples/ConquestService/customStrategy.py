from collections import defaultdict
import random
import pickle

class CustomStrategy():

    def __init__(self,pathResults):
        self.activations = 0
        self.pathResults = pathResults

    def summarize(self):
        print("Number of evolutions %i" % self.activations)

    def deploy_module(self,sim,service,idtopo):
        app_name = service[0:service.index("_")]
        app = sim.apps[app_name]
        services = app.services
        idDES = sim.deploy_module(app_name, service, services[service], [idtopo])

    ### FUNCTION MOVED TO core.py

    # def remove_module(self, sim, service_name, idtopo):
    #
    #     sim.print_debug_assignaments()
    #
    #     app_name = service_name[0:service_name.index("_")]
    #     # Stopping related processes deployed in the module and clearing main structure: alloc_DES
    #     all_des = []
    #     for k, v in sim.alloc_DES.items():
    #         if v == idtopo:
    #             all_des.append(k)
    #
    #     # Clearing other related structures
    #     for des in sim.alloc_module[app_name][service_name]:
    #         if des in all_des:
    #               print "REMOVE PROCESS ", des
    #               sim.alloc_module[app_name][service_name].remove(des)
    #               sim.stop_process(des)
    #               del sim.alloc_DES[des]

    def is_already_deployed(self,sim,service_name,idtopo):
        app_name = service_name[0:service_name.index("_")]

        all_des = []
        for k, v in sim.alloc_DES.items():
            if v == idtopo:
                all_des.append(k)

        # Clearing other related structures
        for des in sim.alloc_module[app_name][service_name]:
            if des in all_des:
                return True


    def get_current_services(self,sim):
        """ returns a dictionary with name_service and a list of node where they are deployed
        example: defaultdict(<type 'list'>, {u'2_19': [15], u'3_22': [5]})
        """
        current_services = sim.get_alloc_entities()
        current_services = dict((k, v) for k, v in current_services.items() if len(v)>0)
        deployed_services = defaultdict(list)
        for k,v  in current_services.items():
            for service_name in v:
                if not "None" in service_name: #[u'2#2_19']
                    deployed_services[service_name[service_name.index("#")+1:]].append(k)
        return deployed_services


    def __call__(self, sim, routing,case, stop_time, it):

        self.activations  +=1
        routing.invalid_cache_value = True

        # sim.print_debug_assignaments()
        # routing.invalid_cache_value = True

        # Current utilization of services
        services = defaultdict(list)
        for k,v in routing.controlServices.items():
            # print k[1]
            services[k[1]].append(v[0])
            # print v #[(node_src, service)] = (path, des)
        print("Current utilization of services")
        print(services)
        print("-" * 30)

        # Current deployed services
        print("Current deployed services")
        current_services = self.get_current_services(sim)
        print(current_services)
        print("-" * 30)

        # Deployed services not used
        services_not_used = defaultdict(list)
        for k in current_services:
            if not k in services.keys():
                #This service is not used
                None
            else:
               for service in current_services[k]:
                    found = False
                    for path in services[k]:
                        if path[-1] == service:
                            found = True
                            break
                    #endfor
                    if not found:
                        services_not_used[k].append(service)


        print("-- Servicios no usados")
        print(services_not_used)
        print("-"*30)

        # We remove all the services not used but they have been called in a previous step
        for service_name,nodes in services_not_used.items():
            for node in nodes:
                app_name = service_name[0:service_name.index("_")]
                print(" + Removing module: %s from node: %i"%(service_name,node))
                exit()
                sim.undeploy_module(app_name,service_name,node)

        # por cada servicio se toma una decision:
        # clonarse
        for service in services:
            #TODO other type of operation
            if random.random()<1.0:
                #clonning
                clones = len(services[service]) # numero de veces que se solicita
                for clon in range(clones):
                    path = services[service][clon]
                    # path[-1] is the current location of the service
                    if len(path)>2:
                        nextLocation = path[-2]
                        #TODO capacity control
                        if not self.is_already_deployed(sim,service,nextLocation):
                            print(service)
                            print(nextLocation)

                            self.deploy_module(sim,service,nextLocation)

        # entities = sim.get_alloc_entities()
        # f = open(self.pathResults + "/file_alloc_entities_%s_%i_%i_%i.pkl" % (case, stop_time, it,self.activations), "wb")
        # pickle.dump(entities, f)
        # f.close()

        # if self.activations==2:
        #     sim.print_debug_assignaments()
        #     print "ESTOOOO "
        #
        #     exit()

