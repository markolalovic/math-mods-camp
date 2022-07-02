#!/usr/bin/python3
# -*- coding: utf-8 -*-
""" sqp.py - Test of SQP. """

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

    ## initial guess
    x0 = utils.load("../data/layouts/random-layout.json")
    x0 = np.array(x0)
    x0 = x0.flatten()

    ## optimize
    result = optimize.minimize(f, x0,
                               method="SLSQP",
                               bounds=bounds,
                               options={
                                   'disp': True,
                                   'maxiter': 100})
    print(result)
    # Optimization terminated successfully    (Exit mode 0)
    #             Current function value: -61.34496963130124
    #             Iterations: 25
    #             Function evaluations: 336
    #             Gradient evaluations: 25
    #      fun: -61.34496963130124
    #      jac: array([0.32207108, 0.07030439, 0.        , 0.        , 0.        ,
    #        0.        , 0.        , 0.        , 0.        , 0.        ])
    #  message: 'Optimization terminated successfully'
    #     nfev: 336
    #      nit: 25
    #     njev: 25
    #   status: 0
    #
    #  success: True
    #        x: array([ 2.85331564,  0.18148341, 31.95911663,  9.10438615, 23.23749862,
    #         2.83256643, 14.0274824 ,  1.03777259, 34.14917873,  4.75483625])
    # True
    # 61.34496963130124
    x = result['x'].reshape((n, 2))

    ## check the result
    plant.layout = x
    plant.set_layout()
    print(plant.valid_layout)
    print(utils.get_energy(plant))

    utils.save_layout(x[:, 0], x[:, 1], "sqp-layout")
