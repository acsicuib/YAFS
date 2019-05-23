class generic_mobile_entity(object): #GME

    def __init__(self, id, path, speed, action=None, start=0):
        self.__default_speed = 10.0
        self.id=id
        self.path = path
        self.speed = speed
        self.next_time = None

        self.do = action
        self.start = start

        self.current_position = 0 #path index

        if speed==0.0:
            self.speed = self.__default_speed


    def __str__(self):
        return "Agent (%i) in node: %i[%i/%i]"%(self.id,self.path[self.current_position],self.current_position,len(self.path)-1)

    def get_current_position(self):
        return self.path[self.current_position]