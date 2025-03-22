
#TODO Action de entrada y de salida? o solo una accion?

class generic_action(object):
    # service_coverage
    #   key   => street node network
    #   value => id. module SW

    def __init__(self, sim): #sim is an instance of CORE.py
        self.sim = sim

    def action(self,mobile_agent):
        None