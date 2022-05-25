#!/usr/bin/python3
# -*- coding: utf-8 -*-
""" run.py - Runs the toy model for optical part of a solar power tower plant. """

import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import pandas as pd

from plant import Plant
from sun import Sun
from state import State

def get_energy(plant, show_stats=True):
    ''' Returns the energy for a given plant initialized with a layout. '''
    sun = Sun()
    powers = np.zeros(sun.m, dtype="float128")
    etas_means_m = np.zeros((sun.m, 3), dtype="float128")
    sbms_props_m = np.zeros((sun.m, 3), dtype="float128")

    for t in sun.ts:
        sun_angle = sun.angles[t]
        state = State(plant, sun_angle)
        power, etas_means, sbms_props = get_power(plant, state)
        powers[t] = power
        etas_means_m[t] = etas_means
        sbms_props_m[t] = sbms_props

    powers_df = pd.DataFrame({'time': sun.times, 'power': powers})
    etas_means_df = pd.DataFrame(etas_means_m, columns=["mu_aa", "mu_cos", "mu_sbm"])
    sbms_props_df = pd.DataFrame(sbms_props_m, columns=["pi_sha", "pi_blo", "pi_mis"])
    stats_df = pd.concat([powers_df, etas_means_df, sbms_props_df], axis=1)

    energy = np.sum(powers)
    etas_means_means = list(np.apply_along_axis(np.mean, 0, etas_means_m))
    sbms_props_means = list(np.apply_along_axis(np.mean, 0, sbms_props_m))

    if show_stats:
        out = "{:s} with {:s}\n".format(plant.name, plant.heli_layout_name)
        out += "\n\t- energy = {:4.20f}\n".format(energy)
        out += "\n\t         {:6s}  {:6s}  {:6s}".format("mu_aa", "mu_cos", "mu_sbm")
        out += "\n\t- etas:  {:.4f}, {:.4f}, {:.4f}\n"\
            .format(etas_means_means[0], etas_means_means[1], etas_means_means[2])
        out += "\n\t         {:6s}  {:6s}  {:6s}".format("pi_sha", "pi_blo", "pi_mis")
        out += "\n\t- sbms:  {:.4f}, {:.4f}, {:.4f}\n"\
            .format(sbms_props_means[0], sbms_props_means[1], sbms_props_means[2])
        print(out)

    return energy, stats_df, powers

def draw(plant, powers):
    fig, ax = plt.subplots()
    sun = Sun()
    ax.plot(sun.times, powers)
    plt.xlabel('Time')
    plt.ylabel('Power')
    plt.title("{:s} with {:s}".format(plant.name, plant.heli_layout_name))
    plt.show()

def get_power(plant, state, do_stats=True):
    '''
    Returns agregates over all heliostats:
        * power = sum_i (eta_aa * eta_cos * eta_sbm)_i
        * etas_means = [mean_aa, mean_cos, mean_sbm]
        * sbms_props = [prop_sh, prop_blo, prop_mis]
    '''
    power = 0.0
    if do_stats:
        etas = np.zeros((plant.n, 3), dtype="float128")
        sbms = np.zeros((plant.n, 3), dtype="float128")

    for i in range(plant.n):
        eta_aa, eta_cos, eta_sbm, not_sbm = state.get_effects(i, verbose=False)
        power += eta_aa * eta_cos * eta_sbm
        if do_stats:
            etas[i] = eta_aa, eta_cos, eta_sbm
            sbms[i] = plant.heli_rays - not_sbm

    if do_stats:
        n_all_rays = plant.n * plant.heli_rays
        etas_means = np.apply_along_axis(np.mean, 0, etas)
        sbms_props = np.apply_along_axis(np.sum, 0, sbms) / n_all_rays
    else:
        etas_means, sbms_props = None, None

    return power, etas_means, sbms_props

if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise ValueError("missing layout file name")

    ## initialize hypothetical plant with provided layout
    plant = Plant(heli_layout_file_name=sys.argv[1])

    ## evaluate it
    energy, _, _ = get_energy(plant, show_stats=False)
    print(energy)
