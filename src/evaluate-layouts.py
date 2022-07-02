#!/usr/bin/python3
# -*- coding: utf-8 -*-
""" evaluate-layouts.py - evaluates layouts for Tiny plant. """

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
        valid = plant.check_layout()
        name = layout.split(".")[0]
        if not valid:
            print(name + ' is not valid')
        else:
            d[name] = np.round(energy, 2)
            plant.draw(name=name)
    d
    df = pd.DataFrame.from_dict(d, orient='index', columns=['Energy'])
    df = df.sort_values(by=['Energy'], ascending=False)
    print(df)
