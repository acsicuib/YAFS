from yafs.placement import Placement

class NoPlacementOfModules(Placement):
    """
    This implementation locates the services of the application in the cheapest cluster regardless of where the sources or sinks are located.

    It only runs once, in the initialization.

    """
    def initial_allocation(self, sim, app_name):
        #The are not modules to be allocated
        None


