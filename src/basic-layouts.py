#!/usr/bin/python3
# -*- coding: utf-8 -*-
""" layouts.py - some simple layouts for Tiny plant. """

import json
import numpy as np
from plant import Plant
import utils

if __name__ == "__main__":
    ## Plant=Tiny, n=5 heliostats
    plant = Plant()
    n = 5

    ## tiny layout
    xs = np.round(np.linspace(plant.x_min, plant.x_max, n + 2))[1:-1]
    ys = np.ones(n) * (plant.y_max / 2)
    utils.save_layout(xs, ys, "tiny-layout")

    ## theater layout
    xs = np.round(np.linspace(plant.x_min, plant.x_max, n + 1))[1:]
    ys = list(map(lambda x: (plant.y_max / plant.x_max)*x, xs))
    utils.save_layout(xs, ys, "theater-layout")

    ## on parabola through the boundary points
    xs = np.round(np.linspace(plant.x_min, plant.x_max, n + 1))[1:]
    ys = list(map(lambda x: np.round( (plant.y_max / plant.x_max**2) * x**2 ), xs))
    utils.save_layout(xs, ys, "parabolic-layout")

    ## grid layout
    xs = np.linspace(plant.x_min, plant.x_max, 3)
    ys = np.linspace(plant.y_min, plant.y_max, 2)
    pr = [(x, y) for x in xs for y in ys]
    del pr[1]
    pr = np.array(pr)
    utils.save_layout(pr[:, 0], pr[:, 1], "grid-layout")
