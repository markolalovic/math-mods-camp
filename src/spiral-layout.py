#!/usr/bin/python3
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from plant import Plant
import utils

def draw_points(plant, spiral_points, masked_points):
    fig, ax = plt.subplots()
    plt.axis('equal')
    x_margins = 2, 2
    y_margins = 2, 6

    ## coord sys
    ax.plot([plant.x_min - x_margins[0],
             plant.x_max + x_margins[1]], [0, 0], color="black")

    ax.plot([0, 0],
      [plant.y_min - y_margins[0],
       np.max([plant.y_max, plant.rec_height]) + y_margins[1]], color="black")

    ## receiver
    ax.plot([plant.rec_a[0], plant.rec_b[0]],
            [plant.rec_a[1], plant.rec_b[1]], color="blue")
    rec_circle = plt.Circle(plant.rec_c, plant.rec_size / 2,
        edgecolor="black", fill=False, linestyle='--')
    ax.add_patch(rec_circle)

    ## field area
    rect = patches.Rectangle((plant.x_min, plant.y_min),
        plant.x_max - plant.x_min, plant.y_max - plant.y_min,
        linestyle='--', edgecolor='black', facecolor='none')
    ax.add_patch(rect)

    ## draw points
    ax.plot(masked_points[:, 0], masked_points[:, 1], 'o')

    ## draw spiral
    ax.plot(spiral_points[:, 0], spiral_points[:, 1], '-', color='red')

    # plt.show()
    fig.tight_layout()
    fig.savefig('../figures/spiral/spiral_plot.png', dpi=100)

def filter_points(plant, point):
    if np.any(point[0] > plant.x_max):
        return False
    if np.any(point[0] < plant.x_min):
        return False
    if np.any(point[1] > plant.y_max):
        return False
    if np.any(point[1] < plant.y_min):
        return False

    if np.linalg.norm(point - plant.rec_c) < plant.d_min:
        return False

    return True

def spiral(t, scalex=1, scaley=0.33, shiftx=1, shifty=35):
    ''' Spiral curve: [t0, t1] -> R^2
        t \mapsto (scalex (shiftx + t cos(t)), scaley (shifty + t sin(t)))
    '''
    return scalex * (shiftx + t*np.cos(t)), scaley * (shifty + t*np.sin(t))

if __name__ == "__main__":
    plant = Plant()
    n = 5
    plant = Plant()
    ts = np.linspace(2, 50, 500)
    points = [spiral(t) for t in ts.tolist()]
    mask = [filter_points(plant, point) for point in points]
    spiral_points = np.array(points)
    masked_points = spiral_points[mask]
    print(masked_points.shape[0])
    draw_points(plant, spiral_points, masked_points)

    xs = masked_points[:, 0]
    ys = masked_points[:, 1]
    nruns = 100
    max_energy = 0
    best_layout = []
    energies = []
    for i in range(nruns):
        layout = []
        choices = np.random.choice(xs.shape[0], n, replace=False)
        for choice in choices:
            layout.append([xs[choice], ys[choice]])
        plant.layout = np.array(layout)
        plant.set_layout()
        if plant.valid_layout:
            energy = utils.get_energy(plant, do_stats=False)
            energies.append(energy)
            if energy > max_energy:
                max_energy = energy
                best_layout = plant.layout
    print(max_energy, np.mean(energies), np.std(energies))
    # 55.62450358372094 35.12028133879603 6.585674904294718 # 100 runs
    # 55.520676322352706 33.56358388126249 6.718791163821474 # 3000 runs
    utils.save_layout(best_layout[:, 0], best_layout[:, 1], "spiral-random-layout")
