#!/usr/bin/python3
# -*- coding: utf-8 -*-
""" run.py - Runs the toy model for optical part of a solar power tower plant. """

import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches

from plant import Plant
import utils

if __name__ == "__main__":
    ## initialize hypothetical plant with basic layout
    hypo_plant = utils.load("../data/plants/hypo-plant.json")
    basic_layout = utils.load("../data/layouts/theater-layout.json")['theater-layout']
    plant = Plant(hypo_plant, basic_layout)

    ## evaluate it
    energy = utils.get_energy(plant)
    print(energy)
