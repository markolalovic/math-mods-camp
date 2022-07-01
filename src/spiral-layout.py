#!/usr/bin/python3
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from plant import Plant

def draw_points(plant, points_np, symbol):
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
    ax.plot(points_np[:, 0], points_np[:, 1], symbol)

    plt.show()

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

if __name__ == "__main__":
    plant = Plant()

    ## spiral: t \mapsto scalex (shiftx + t cos(t)), scaley (shifty + t sin(t)), for t in [2, 50]
    ts = np.linspace(2, 50, 400)
    def spiral(t, scalex=2, scaley=0.33, shiftx=1, shifty=34):
        return scalex * (shiftx + t*np.cos(t)), scaley * (shifty + t*np.sin(t))

    points = [spiral(t) for t in ts.tolist()]
    mask = [filter_points(plant, point) for point in points]

    points_np = np.array(points)
    draw_points(plant, points_np, '-')

    points_np = points_np[mask]
    draw_points(plant, points_np, 'o')

    print(points_np.shape[0])
