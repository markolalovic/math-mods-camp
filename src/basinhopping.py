#!/usr/bin/python3
# -*- coding: utf-8 -*-
""" de.py - Test of Basin-hopping. """

import numpy as np
from scipy import optimize
from plant import Plant
import utils

class RandomDisplacementBounds(object):
    """Custom step-function using random displacement with bounds.
    See: https://stackoverflow.com/a/47058263
    """
    def __init__(self, xmin, xmax, stepsize=0.5):
        self.xmin = xmin
        self.xmax = xmax
        self.stepsize = stepsize

    def __call__(self, x):
        """ Takes a random step but ensure the new position is within the bounds. """
        min_step = np.maximum(self.xmin - x, -self.stepsize)
        max_step = np.minimum(self.xmax - x, self.stepsize)

        random_step = np.random.uniform(low=min_step, high=max_step, size=x.shape)
        xnew = x + random_step

        return xnew

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
    bounded_step = RandomDisplacementBounds(
        np.array([b[0] for b in bounds]), np.array([b[1] for b in bounds]))
    minimizer_kwargs = {"bounds": bounds}
    result = optimize.basinhopping(f,
                                   x0,
                                   minimizer_kwargs=minimizer_kwargs,
                                   niter=10,
                                   take_step=bounded_step)
    print(result)
    #  fun: -60.94709698636652
    #  lowest_optimization_result:       fun: -60.94709698636652
    #  hess_inv: <10x10 LbfgsInvHessProduct with dtype=float64>
    #       jac: array([0.31758134, 0.06922036, 0.        , 0.        , 0.        ,
    #        0.        , 0.        , 0.        , 0.        , 0.        ])
    #   message: 'ABNORMAL_TERMINATION_IN_LNSRCH'
    #      nfev: 1199
    #       nit: 5
    #      njev: 109
    #    status: 2
    #   success: False
    #         x: array([2.89380907e+00, 1.37591977e-02, 3.19591166e+01, 9.10438615e+00,
    #        2.32374986e+01, 2.83256643e+00, 1.40274824e+01, 1.03777259e+00,
    #        3.41491787e+01, 4.75483625e+00])
    #                     message: ['requested number of basinhopping iterations completed successfully']
    #       minimization_failures: 2
    #                        nfev: 2585
    #                         nit: 1
    #                        njev: 235
    #                     success: False
    #                           x: array([2.89380907e+00, 1.37591977e-02, 3.19591166e+01, 9.10438615e+00,
    #        2.32374986e+01, 2.83256643e+00, 1.40274824e+01, 1.03777259e+00,
    #        3.41491787e+01, 4.75483625e+00])
    # True
    # 61.343719655421474

    x = result['x'].reshape((n, 2))

    ## check the result
    plant.layout = x
    plant.set_layout()
    print(plant.valid_layout)
    print(utils.get_energy(plant))

    utils.save_layout(x[:, 0], x[:, 1], "basinhopping-layout")
