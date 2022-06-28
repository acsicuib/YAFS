from yafs.action import generic_action
import logging
class my_custom_action(generic_action):

    def __init__(self, *args, **kwargs):
        super(my_custom_action, self).__init__(*args, **kwargs)
        self.plates = {}
        self.fees = {}

    #mandatory function
    def action(self,ma): #mobile_entity
        # print "ACTION"
        # print ma
        # print ma.next_time
        # print ma.get_current_position()
        # print "-"*10
        logging.info(" Performing Action from VEHICLE: %i in: %i " % (ma.id, ma.get_current_position()))

        if ma.get_current_position() in self.sim.service_coverage.keys(): #sim is an instance of CORE.py
            if ma.plate in self.plates:
                self.fees[ma.plate]={"arrive":self.plates[ma.plate],"end":self.sim.env.now}
            else:
                self.plates[ma.plate]=self.sim.env.now
