#!/usr/bin/python3
# -*- coding: utf-8 -*-
""" annealing.py - Test of Dual Annealing. """

import numpy as np
from scipy import optimize
from plant import Plant
import utils

def f(x):
    plant.layout = x.reshape((5, 2))
    plant.set_layout()
    return -utils.get_energy(plant)

if __name__ == "__main__":
    ## Tiny plant, n=5 heliostats
    plant = Plant()
    n = 5

    ## box constraints
    bounds = []
    for i in range(n):
        bounds.append((plant.x_min, plant.x_max))
        bounds.append((plant.y_min, plant.y_max))

    ## initial guess - its possible to provide
    # x0 = utils.load("../data/layouts/random-layout.json")
    # x0 = np.array(x0)
    # x0 = x0.flatten()

    ## optimize
    result = optimize.dual_annealing(f, bounds, maxiter=500)
    print(result)
    #      fun: -66.85897919012248
    #  message: ['Maximum number of iteration reached']
    #     nfev: 11272
    #     nhev: 0
    #      nit: 200
    #     njev: 661
    #   status: 0
    #  success: True
    #        x: array([ 0.97988199,  8.15855357, 34.60034525,  9.60885119, 34.88693803,
    #         5.86200461, 23.98158401,  4.1000982 , 15.06607543,  3.24333255])
    # False
    # 66.82406254475265

    x = result['x'].reshape((n, 2))

    ## check the result
    plant.layout = x
    plant.set_layout()
    print(plant.valid_layout)
    print(utils.get_energy(plant))

    utils.save_layout(x[:, 0], x[:, 1], "annealing-layout")
