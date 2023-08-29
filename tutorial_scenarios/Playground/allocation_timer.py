import random
import os

from playground_funcs import myConfig, environment_generation as eg


conf = myConfig.myConfig()

random.seed(15612357)
exp_conf = eg.ExperimentConfiguration(conf, lpath=os.path.dirname(__file__))

random.seed(15612357)
exp_conf.app_generation(app_struct='simple')
random.seed(15612357)
exp_conf.networkGeneration(n=10, file_name_network='network.json')
random.seed(15612357)
exp_conf.user_generation()

# Algoritmo de alloc
# exp_conf.randomPlacement(file_name_network='network.json')
# plot_name = 'randomPlacement'

exp_conf.bt_min_mods()
plot_name = 'bt_min_mods'

# exp_conf.near_GW_placement()
# plot_name = 'near_GW_placement'

exp_conf.greedy_algorithm()
plot_name = 'greedy_algorithm'