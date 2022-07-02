#!/usr/bin/python3
# -*- coding: utf-8 -*-
""" cobyla.py - Test of COBYLA method. """

import numpy as np
from scipy import optimize
from plant import Plant
import utils
import time

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

    ## construct the bounds in the form of constraints for COBYLA method
    # see: https://stackoverflow.com/a/41761740
    cons = []
    for factor in range(len(bounds)):
        lower, upper = bounds[factor]
        l = {'type': 'ineq',
             'fun': lambda x, lb=lower, i=factor: x[i] - lb}
        u = {'type': 'ineq',
             'fun': lambda x, ub=upper, i=factor: ub - x[i]}
        cons.append(l)
        cons.append(u)

    ## initial guess
    x0 = utils.load("../data/layouts/random-layout.json")
    x0 = np.array(x0)
    x0 = x0.flatten()

    ## optimize
    result = optimize.minimize(f, x0,
                               method="COBYLA",
                               constraints=cons,
                               options={
                                   'disp': True,
                                   'maxiter': 200})
    print(result)
    #    Normal return from subroutine COBYLA
    #
    #    NFVALS =  114   F =-6.103938E+01    MAXCV = 0.000000E+00
    #    X = 6.496684E+00   3.852641E-02   3.103694E+01   1.000000E+01   2.319267E+01
    #        2.089125E+00   1.406755E+01   8.977016E-01   3.407506E+01   4.696519E+00
    #      fun: -61.039380238959424
    #    maxcv: 0.0
    #  message: 'Optimization terminated successfully.'
    #     nfev: 114
    #   status: 1
    #
    #  success: True
    #        x: array([ 6.49668401,  0.03852641, 31.03694022, 10.        , 23.19266733,
    #         2.08912523, 14.06755327,  0.89770161, 34.07505779,  4.69651865])
    # True
    # 61.039380238959424
    x = result['x'].reshape((n, 2))

    ## check the result
    plant.layout = x
    plant.set_layout()
    print(plant.valid_layout)
    print(utils.get_energy(plant))

    utils.save_layout(x[:, 0], x[:, 1], "cobyla-layout")
