#!/usr/bin/python3
# -*- coding: utf-8 -*-
""" random-layout.py - sample x,y uniformly at random. """

import json
import numpy as np
from plant import Plant
import utils

if __name__ == "__main__":
    ## Plant=Tiny, n=5 heliostats
    plant = Plant()
    n = 5

    ## random layout
    nruns = 10000
    max_energy = 0
    best_layout = []
    energies = []
    for i in range(nruns):
        ## we have to try until we get a valid layout
        xs = np.random.uniform(plant.x_min, plant.x_max, n)
        ys = np.random.uniform(plant.y_min, plant.y_max, n)
        plant.layout = np.stack((xs, ys)).T
        plant.set_layout()
        if plant.valid_layout:
            energy = utils.get_energy(plant, do_stats=False)
            energies.append(energy)
            if energy > max_energy:
                max_energy = energy
                best_layout = plant.layout

    print(max_energy, np.mean(energies), np.std(energies))
    # 54.059498031189726 34.36608182585655  6.971024042017483  # 1000 runs
    # 56.29071606490873  34.752847821956266 7.2430077703910385 # 3000 runs

    utils.save_layout(best_layout[:, 0], best_layout[:, 1], "random-layout")
