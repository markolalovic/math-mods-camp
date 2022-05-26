#!/usr/bin/python3
# -*- coding: utf-8 -*-
""" layouts.py - some simple layouts for hypothetical plant. """

import json
import numpy as np

## some helper functions
## TODO: collect the helper functions into one file, and remove them from classes
def save_layout(xs, ys, layout_name, indent=4):
    d = {}
    d[layout_name] = np.column_stack((xs,ys)).tolist()
    file_name = "../data/layouts/{:s}.json".format(layout_name)
    with open(file_name, 'w') as file:
        json.dump(d, file, indent=indent)

def valid_layout(heli_layout):
    n = heli_layout.shape[0]
    d_min = 3
    for i in range(n):
        for j in range(i + 1, n):
            dist_ij = np.linalg.norm(heli_layout[i] - heli_layout[j])
            if dist_ij < d_min:
                return False
    return True

## theater layout
xs = np.linspace(0, 100, 20)
ys = list(map(lambda x: x/5, xs))
save_layout(xs, ys, "theater-layout")

## put heliostats on parabola trough boundary points = parabolic layout
xs = np.linspace(0, 100, 20)
ys = list(map(lambda x: 1/125*(x - 50)**2, xs))
save_layout(xs, ys, "parabolic-layout")

## lets try flipping the previous parabola
xs = np.linspace(0, 100, 20)
ys = list(map(lambda x: -1/125*(x - 50)**2 + 20, xs))
save_layout(xs, ys, "parabolic-layout-flipped")

## grid layout
xs = np.linspace(0, 100, 5)
ys = np.linspace(0, 20, 4)
pr = np.array([(x, y) for x in xs for y in ys])
save_layout(pr[:, 0], pr[:, 1], "grid-layout")

## second grid layout
pr = np.array([[x, 0] for x in np.linspace(5,  90, 10)]+\
              [[x, 20] for x in np.linspace(10,  100, 10)])
save_layout(pr[:, 0], pr[:, 1], "grid-layout-2")


## uniform random layout
while True:
    ## we have to try until we get a valid layout
    xs = np.random.uniform(0, 100, 20)
    ys = np.random.uniform(0, 20, 20)
    heli_layout = np.stack((xs, ys)).T

    if valid_layout(heli_layout):
        break

save_layout(xs, ys, "uniform-random-layout")
