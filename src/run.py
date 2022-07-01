#!/usr/bin/python3
# -*- coding: utf-8 -*-
""" run.py - how to evaluate a layout for Tiny plant. """

import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches

from plant import Plant
import utils

if __name__ == "__main__":
    ## create a layout, for example:
    layout = [[1, 1], [5, 2.5], [10, 5], [15, 8], [20, 10]]

    ## initialize Tiny plant with the layout
    plant = Plant(layout)

    ## check if it is valid layout
    print("Valid: " + str(plant.valid_layout))

    ## draw the layout
    plant.draw()

    ## evaluate the total energy output
    print("Energy: " + str(utils.get_energy(plant, do_stats=False)))
