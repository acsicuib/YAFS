.. _tutorial_example:

================
Tutorial Example
================

In this section, we explain the examples from Tutorial/ directory but you can see most sophisticated implemented cases:

* **Tutorial/main1.py** The most basic case: cloud allocation, and  minimum  path routing,
* **Tutorial/main2.py** Using first case, we scale the modules in the cloud and we use a round robin scheduler.
* **Tutorial/main3.py** Using second case, we show how to implement a dynamic control
* **VRGameFog-IFogSim-WL/main.py** This implemention have been used to compare YAFS simulator with iFogSim, implementing a close setup of the experiments.
* **FogCentrality/experiment1.py** In this case, we have analysed how the topology and the allocation of modules affects in the latency time.
* **FogCentrality/experiment2.py**
* **DynamicAllocation/.py** It is a demo of how to implement a dynamic allocation of modules according a customized distribution. We use a random euclidean network from a Graphml format, and several selection, population, and allocation implementations.
* **DynamicFailuresOnNodes/main.py** From a euclidean random network we dynamically remove nodes.
* **DynamicWorkload/main.py** In this case, we simulate the movement of users in the network. In each step of the customized distribution nodes are allocated in the next node of the path to reach the point on all modules are.


TODO Explain with detail the first three cases.