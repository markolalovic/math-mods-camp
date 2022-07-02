#!/usr/bin/python3
# -*- coding: utf-8 -*-
""" landscape.py - starting from some basic layout, try to optimize
    on position of a single heliostat to be able to draw some figures. """

from plant import Plant
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from mpl_toolkits.mplot3d import Axes3D
import utils

def get_points(xs, ys, zs):
    # to be able to add constraints
    grid_points = []
    for i in range(len(xs)):
        for j in range(len(ys)):
            grid_points.append([xs[i], ys[j]])

    xpts = [grid_points[i][0] for i in range(len(grid_points))]
    ypts = [grid_points[i][1] for i in range(len(grid_points))]
    zpts = list(zs)
    return xpts, ypts, zpts

def get_XYZ(points, nx, ny):
    xpts, ypts, zpts = points
    xs1 = np.array(xpts).astype(float)
    ys1 = np.array(ypts).astype(float)
    zs1 = np.array(zpts).astype(float)
    X = xs1.reshape(nx, ny)
    Y = ys1.reshape(nx, ny)
    Z = zs1.reshape(nx, ny)
    return X, Y, Z

def surface_plot(points):
    ## 3d surface plot
    xpts, ypts, zpts = points
    fig = plt.figure(figsize = (15, 10))
    ax = fig.add_subplot(111, projection='3d')
    ax.set_xlabel('x-position')
    ax.set_ylabel('y-position')
    ax.set_zlabel('Energy')

    surf = ax.plot_trisurf(xpts, ypts, zpts, cmap=cm.jet, linewidth=0, alpha=.6)
    fig.colorbar(surf)

    # to add (argmax, max) to the plot:
    argmax_i = np.argmax(zpts)
    ax.scatter3D(xpts[argmax_i], ypts[argmax_i], zpts[argmax_i], s=200);

    fig.tight_layout()
    fig.savefig('../figures/landscape/surface_plot.png', dpi=100)
    plt.show()

def contour_plot(XYZ):
    fig, ax = plt.subplots(1, 1, figsize=(20, 10))
    X, Y, Z = XYZ
    ax.contour(X, Y, Z, 25)
    plt.show()

def grad(plant, x):
    ''' Estimates the gradient.
        TODO: could try central difference and different step size h. '''
    h = 0.1
    e1 = np.array([1, 0])
    e2 = np.array([0, 1])
    return np.array([(f(plant, x + h*e1) - f(plant, x))/h,
                     (f(plant, x + h*e2) - f(plant, x))/h])

def f(plant, x, i=2):
    ''' Returns plants energy as a function of ith heliostat position.'''
    plant.layout[i] = [x[0], x[1]]
    plant.set_layout()
    return utils.get_energy(plant)

def evaluate_grid(xs, ys, f, plant, recompute=False):
    nx, ny = len(xs), len(ys)
    if recompute:
        zs = []
        for i in range(nx):
            for j in range(ny):
                zs.append( f(plant, [xs[i], ys[j]]) )
        with open("../data/results/zs.npy", "wb") as f:
            np.save(f, zs)
    else:
        with open("../data/results/zs.npy", "rb") as f:
            zs = np.load(f)
    return zs

def gradient_ascent(plant, x, grad, sigma, max_iter=10):
    xs = np.zeros((1 + max_iter, x.shape[0]))
    xs[0] = x
    for i in range(max_iter):
        g = grad(plant, x)
        norm_g = np.linalg.norm(g)
        if norm_g > 0:
            g = g / norm_g
        x = x + sigma * g
        xs[i+1] = x
    return xs

def gradient_plot(plant, xs, XYZ, name):
    ## draw contour
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(20, 10))
    X, Y, Z = XYZ
    ax.contour(X, Y, Z, 25)

    ## constraints
    plant.layout[2] = plant.layout[0]
    for heli_c in list(plant.layout):
        heli_circle = plt.Circle(heli_c, plant.heli_size / 2,
            edgecolor='black', fill=False, linestyle='--')
        ax.add_patch(heli_circle)

    ## gradient ascent steps
    for i in range(1, xs.shape[0]):
        ax.annotate('', xy=xs[i], xytext=xs[i-1],
                    arrowprops={'arrowstyle': '->', 'color': 'r', 'lw': 1},
                    va='center', ha='center')
    for i in range(xs.shape[0]):
        ax.text(xs[i][0] - .03, xs[i][1] + 0.03, str(i), fontsize=12)

    # plt.show()
    fig.savefig('../figures/landscape/gradient_ascent_'+ name +'.png', dpi=100)

if __name__ == "__main__":
    ## Tiny plant, n=5 heliostats, pick parabolic-layout
    n = 5
    plant = Plant(utils.load("../data/layouts/parabolic-layout.json"))
    ## check result:
    # print(plant.valid_layout)
    # print(utils.get_energy(plant))
    # plant.draw()

    ## optimize on only the middle heliostat position
    ## so we can draw the figures
    ## so we have a function of two variables x1, x2
    # f(plant, [21, 4]) # = 63.13903716835735

    ## evaluate f on a grid
    nx = 70
    ny = int(10/35*nx)
    print(nx, ny)
    xs = np.linspace(plant.x_min, plant.x_max, nx)
    ys = np.linspace(plant.y_min, plant.y_max, ny)
    zs = evaluate_grid(xs, ys, f, plant, recompute=False)
    points = get_points(xs, ys, zs)
    XYZ = get_XYZ(points, nx, ny)

    # plots
    surface_plot(points)
    # contour_plot(XYZ)

    ## test gradient ascent with x0 close to max
    x0 = np.array([20, 5])
    sigma = 1
    xs = gradient_ascent(plant, x0, grad, sigma, max_iter=5)
    gradient_plot(plant, xs, XYZ, 'close')

    ## test gradient ascent with x0 far from max
    x0 = np.array([2, 2])
    sigma = 1
    xs = gradient_ascent(plant, x0, grad, sigma, max_iter=5)
    gradient_plot(plant, xs, XYZ, 'far')
