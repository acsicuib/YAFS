"""
This module is a generic class to introduce whatever kind of distribution in the simulator

"""
import random
import numpy as np
class Distribution(object):
    """
    Abstract class
    """
    def __init__(self,name):
        self.name=name

    def next(self):
        None

class deterministicDistribution(Distribution):
    def __init__(self,time, **kwargs):
        self.time = time
        super(deterministicDistribution, self).__init__(**kwargs)

    def next(self):
        return self.time

class deterministicDistributionStartPoint(Distribution):
    def __init__(self,start,time, **kwargs):
        self.start = start
        self.time = time
        self.started = False
        super(deterministicDistributionStartPoint, self).__init__(**kwargs)

    def next(self):
        if not self.started:
            self.started = True
            return self.start
        else:
            return self.time

class exponentialDistribution(Distribution):
    def __init__(self,lambd, **kwargs):
        self.lambd = lambd
        super(exponentialDistribution, self).__init__(**kwargs)

    def next(self):
        return int(np.random.exponential(self.lambd, size=1)[0])

class exponentialDistributionStartPoint(Distribution):
    def __init__(self,start,lambd, **kwargs):
        self.lambd = lambd
        self.start = start
        self.started = False
        super(exponentialDistributionStartPoint, self).__init__(**kwargs)

    def next(self):
        if not self.started:
            self.started = True
            return self.start
        else:
            return int(np.random.exponential(self.lambd, size=1)[0])

class uniformDistribution(Distribution):
    def __init__(self, min,max, **kwargs):
        self.min = min
        self.max = max
        super(uniformDistribution, self).__init__(**kwargs)
    def next(self):
        return random.randint(self.min, self.max)
