import random
import os

from playground_funcs import myConfig, environment_generation as eg


def placement_timer(iter=50, placement_alg='backtrack_placement'):
    exec_times = list()

    conf = myConfig.myConfig()
    exp = eg.ExperimentConfiguration(conf)

    while len(exec_times) != iter:
        exec_t = exp.config_generation_timer(placement_alg=placement_alg, seed=iter*100000)

        if exec_t != 0:
            exec_times.append(exec_t)

    print(f'Algoritmo: {placement_alg}')
    print(f'Tempo total: {sum(exec_times) * 1000 : .6f} ms')
    print(f'Tempo médio: {(sum(exec_times)/iter) * 1000 : .6f} ms')
    print(f'Tempo minimo: {min(exec_times) * 1000 : .6f} ms')
    print(f'Tempo máximo: {max(exec_times) * 1000 : .6f} ms')


algorithms = ['greedy_algorithm', 'near_GW_placement', 'randomPlacement', 'backtrack_placement', 'bt_min_mods']

for alg in algorithms:
    placement_timer(placement_alg=alg)
    print('\n')
