#!/usr/bin/python3
# -*- coding: utf-8 -*-
""" de.py - Test of Differential Evolution. """

import numpy as np
from scipy import optimize
from plant import Plant
import utils
import time

class MinimizeStopper(object):
    ''' Callback function to stop optimization after a time threshold, taken from:
    https://stackoverflow.com/a/60863988
    '''
    def __init__(self, max_sec=0.3):
        self.max_sec = max_sec
        self.start = time.time()

    def __call__(self, xk=None, convergence=None):
        elapsed = time.time() - self.start
        if elapsed > self.max_sec:
            print("Terminating optimization: time limit reached")
            return True
        else:
            print("Elapsed: %.3f sec" % elapsed)
            return False

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

    ## initial guess
    x0 = utils.load("../data/layouts/random-layout.json")
    x0 = np.array(x0)
    x0 = x0.flatten()

    ## optimize
    result = optimize.differential_evolution(
        f, bounds,
        # x0=x0,
        maxiter=150,
        # callback=MinimizeStopper(1E-3)
        )
    print(result)
    #      fun: -65.31960783563606
    #  message: ['Maximum number of iteration reached']
    #     nfev: 13208
    #     nhev: 0
    #      nit: 200
    #     njev: 837
    #   status: 0
    #  success: True
    #        x: array([ 2.61283822,  1.17755777, 27.05730546,  6.18566598, 10.41476582,
    #         2.9603552 , 18.32786566,  4.18708556, 34.90214481,  9.81592232])
    # True
    x = result['x'].reshape((n, 2))

    ## check the result
    plant.layout = x
    plant.set_layout()
    print(plant.valid_layout)
    print(utils.get_energy(plant))

    utils.save_layout(x[:, 0], x[:, 1], "de-layout")
