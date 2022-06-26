#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
import numpy as np
import pandas as pd
from plant import Plant
from sun import Sun
from state import State
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def save(d, file_name, indent=0):
    ''' Helper method to save the layout, or plant specs.
    Example:
        d = {"tiny-layout": [[8, 4], [16, 4], [22, 4], [28, 4]]}
        file_name = "../data/layouts/tiny-layout.json"
        plant.save(d, file_name) # saves it to ../data
    '''
    with open(file_name, 'w') as file:
        json.dump(d, file, indent=indent)


def load(file_name):
    ''' Helper method to load the layout, or plant specs. '''
    with open(file_name) as file:
        d = json.load(file)
    return d

def get_energy(plant, do_stats=False):
    ''' Returns the energy for a given plant initialized with a layout. '''
    sun = Sun()
    powers = np.zeros(sun.m, dtype="float128")
    if do_stats:
        etas_means_m = np.zeros((sun.m, 3), dtype="float128")
        sbms_props_m = np.zeros((sun.m, 3), dtype="float128")

    for t in sun.ts:
        sun_angle = sun.angles[t]
        state = State(plant, sun_angle)
        power, etas_means, sbms_props = get_power(plant, state)
        powers[t] = power
        if do_stats:
            etas_means_m[t] = etas_means
            sbms_props_m[t] = sbms_props

    if do_stats:
        powers_df = pd.DataFrame({'time': sun.times, 'power': powers})
        etas_means_df = pd.DataFrame(etas_means_m, columns=["mu_aa", "mu_cos", "mu_sbm"])
        sbms_props_df = pd.DataFrame(sbms_props_m, columns=["pi_sha", "pi_blo", "pi_mis"])
        stats_df = pd.concat([powers_df, etas_means_df, sbms_props_df], axis=1)
        etas_means_means = list(np.apply_along_axis(np.mean, 0, etas_means_m))
        sbms_props_means = list(np.apply_along_axis(np.mean, 0, sbms_props_m))

    energy = np.sum(powers)

    if do_stats:
        out = ""
        out += "\n\t- energy = {:4.20f}\n".format(energy)
        out += "\n\t         {:6s}  {:6s}  {:6s}".format("mu_aa", "mu_cos", "mu_sbm")
        out += "\n\t- etas:  {:.4f}, {:.4f}, {:.4f}\n"\
            .format(etas_means_means[0], etas_means_means[1], etas_means_means[2])
        out += "\n\t         {:6s}  {:6s}  {:6s}".format("pi_sha", "pi_blo", "pi_mis")
        out += "\n\t- sbms:  {:.4f}, {:.4f}, {:.4f}\n"\
            .format(sbms_props_means[0], sbms_props_means[1], sbms_props_means[2])
        print(out)

    if do_stats:
        return energy, stats_df, powers
    else:
        return energy

def draw(plant, powers):
    fig, ax = plt.subplots()
    sun = Sun()
    ax.plot(sun.times, powers)
    plt.xlabel('Time')
    plt.ylabel('Power')
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
