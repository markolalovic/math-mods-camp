#!/usr/bin/python3
# -*- coding: utf-8 -*-
""" layouts.py - evaluates layouts for Tiny plant. """

import os
import numpy as np
import pandas as pd
from plant import Plant
import utils

if __name__ == "__main__":
    ## Plant=Tiny, n=5 heliostats
    plant = Plant()

    ## evaluate layouts
    d = {}
    for layout in os.listdir("../data/layouts/"):
        plant = Plant(utils.load("../data/layouts/"+layout))
        energy = utils.get_energy(plant, do_stats=False)
        d[layout.split(".")[0]] = np.round(energy, 2)
    df = pd.DataFrame.from_dict(d, orient='index', columns=['Energy'])
    df = df.sort_values(by=['Energy'], ascending=False)
    print(df)
