#!/usr/bin/env python2
# -*- coding: utf-8 -*-


import random
import Allocation
import experimentConfiguration




#****************************************************************************************************

#inizializations and set up

#****************************************************************************************************
random.seed(8)




ec = experimentConfiguration.experimentConfiguration()
ec.loadConfiguration()
ec.networkGeneration()
ec.appGeneration()
ec.userGeneration()

#########################
#    ILP OPTIMIZATION
#########################
ilp_ = Allocation.Allocation(ec)
service2DevicePlacementMatrixILP = ilp_.solve()


















    






