"""
This module is a generic class to introduce whatever kind of distribution in the simulator

"""
import random
import numpy as np
import warnings


class Distribution(object):
    """
    Abstract class
    """
    def __init__(self,name):
        self.name=name

    def next(self):
        None


class deterministic_distribution(Distribution):
    def __init__(self, time, **kwargs):
        super(deterministic_distribution, self).__init__(**kwargs)
        self.time = time

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
    def __init__(self,lambd,seed=1, **kwargs):
        warnings.warn("The exponentialDistribution class is deprecated and "
                      "will be removed in version 2.0.0. "
                      "Use the exponential_distribution function instead.",
                      FutureWarning,
                      stacklevel=8
                     )
        super(exponentialDistribution, self).__init__(**kwargs)
        self.l = lambd
        self.rnd = np.random.RandomState(seed)

    def next(self):
        value = int(self.rnd.exponential(self.l, size=1)[0])
        if value==0: return 1
        return value


class exponential_distribution(Distribution):
    def __init__(self,lambd,seed=1, **kwargs):
        super(exponential_distribution, self).__init__(**kwargs)
        self.l = lambd
        self.rnd = np.random.RandomState(seed)

    def next(self):
        value = int(self.rnd.exponential(self.l, size=1)[0])
        if value==0: return 1
        return value


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
