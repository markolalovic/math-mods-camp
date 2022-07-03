#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import utils

class Plant:
    ''' Constructs a plant given the plants specifications and heliostats layout.
    Args:
        * layout as a list of coordinates, for example: [[1, 2], [3, 4]]
        * plant_d as a dictionary, see ../data/plants/tiny-plant.json
    '''
    def __init__(self, layout=[[0, 0]], plant_d=None):
        self.dim = 2

        if plant_d is None:
            plant_d = utils.load("../data/plants/tiny-plant.json")

        self.name = plant_d["name"]

        ## field area bounds and diameter
        self.x_min = plant_d["field_area"]["x_min"]
        self.x_max = plant_d["field_area"]["x_max"]
        self.y_min = plant_d["field_area"]["y_min"]
        self.y_max = plant_d["field_area"]["y_max"]
        self.d_min = plant_d["field_area"]["d_min"]
        self.diameter = np.linalg.norm(
          np.array([self.x_min, self.y_min]) - np.array([self.x_max, self.y_max]))

        ## receiver position
        self.rec_height = plant_d["receiver"]["rec_height"]
        self.rec_angle = np.radians(plant_d["receiver"]["rec_angle"]) # in radians
        self.rec_size = plant_d["receiver"]["rec_size"]

        ## receiver center, tangent vector, edge points - fixed
        self.rec_c = np.array([0, self.rec_height])
        rec_tan_vec = np.array([np.cos(self.rec_angle), np.sin(self.rec_angle)])
        self.rec_a = self.rec_c + self.rec_size / 2 * rec_tan_vec
        self.rec_b = self.rec_c - self.rec_size / 2 * rec_tan_vec

        ## heliostats
        self.layout = np.array(layout) # centers of heliostats

        self.n = len(self.layout) # number of heliostats
        self.heli_size = plant_d["heliostats"]["heli_size"]
        self.heli_rays = plant_d["heliostats"]["heli_rays"] # number of rays per heliostat

        ## set reflected vectors, max_ij, valid_layout
        self.set_layout()

    def set_layout(self):
        ''' Checks that:
            * heliostats are in the field area
            * heliostats are minimum distance appart and minimum
        distance from the receiver. It also sets max_ij = maximum distance
        between heliostats for drawings.
        '''
        self.n = self.layout.shape[0]
        heli_refs = self.rec_c - self.layout
        heli_refs = heli_refs.astype("float128")
        self.ref_lengths = np.apply_along_axis(np.linalg.norm, 1, heli_refs)
        heli_refs = heli_refs / np.array([self.ref_lengths, self.ref_lengths]).T
        self.heli_refs = self.layout + heli_refs
        self.valid_layout = self.check_layout()
        if self.n == 1:
            self.max_ij = self.y_max
        else:
            self.max_ij = self.get_max_ij()

    def get_max_ij(self):
        max_ij = 0
        for i in range(self.n):
            for j in range(i + 1, self.n):
                dist_ij = np.linalg.norm(self.layout[i] - self.layout[j])
                if dist_ij > max_ij:
                    max_ij = dist_ij
        return max_ij/2

    def check_layout(self):
        eps = 1e-5
        if np.any(self.layout[:, 0] > self.x_max + eps):
            return False
        if np.any(self.layout[:, 0] < self.x_min - eps):
            return False
        if np.any(self.layout[:, 1] > self.y_max + eps):
            return False
        if np.any(self.layout[:, 1] < self.y_min - eps):
            return False

        for i in range(self.n):
            if np.linalg.norm(self.layout[i] - self.rec_c) < self.d_min:
                return False
            for j in range(i + 1, self.n):
                dist_ij = np.linalg.norm(self.layout[i] - self.layout[j])
                if dist_ij < self.d_min:
                    return False
        return True

    def __str__(self):
        out = ""
        if self.name:
            out += "{:s}: \n".format(self.name)
        else:
            out += "Plant: "
        out += "\n\t- field area:"
        out += "\n\t\t- [x_min, x_max] = [{:4.2f}, {:4.2f}]".format(self.x_min, self.x_max)
        out += "\n\t\t- [y_min, y_max] = [{:4.2f}, {:4.2f}]".format(self.y_min, self.y_max)
        out += "\n\t\t- diameter = {:4.2f}".format(self.diameter)
        out += "\n\t\t- max_ij = {:4.2f}\n".format(self.max_ij)

        out += "\n\t- receiver: "
        out += "\n\t\t- _height = {:4.2f}".format(self.rec_height)
        out += "\n\t\t- _angle = {:4.2f}".format(np.degrees(self.rec_angle))
        out += "\n\t\t- _size = {:4.2f}\n".format(self.rec_size)

        out += "\n\t- heliostats:"
        out += "\n\t\t- number of heliostats n = {:4.2f}".format(self.n)
        out += "\n\t\t- heli_size = {:4.2f}".format(self.heli_size)
        out += "\n\t\t- heli_rays = {:4.2f}".format(self.heli_rays)

        out += "\n\t\t- layout = [[{:4.2f}, {:4.2f}], ..., [{:4.2f}, {:4.2f}]]\n"\
            .format(self.layout[0, 0], self.layout[0, 1],\
                    self.layout[-1, 0], self.layout[-1, 1])
        return out

    def draw(self, name=None):
        fig, ax = plt.subplots()
        plt.axis('equal')
        x_margins = 2, 2 # for drawings
        y_margins = 2, 6

        ## coord sys
        ax.plot([self.x_min - x_margins[0],
                 self.x_max + x_margins[1]], [0, 0], color="black")

        ax.plot([0, 0],
          [self.y_min - y_margins[0],
           np.max([self.y_max, self.rec_height]) + y_margins[1]], color="black")

        ## field area
        rect = patches.Rectangle((self.x_min, self.y_min),
            self.x_max - self.x_min, self.y_max - self.y_min,
            linestyle='--', edgecolor='black', facecolor='none')
        ax.add_patch(rect)

        ## receiver
        ax.plot([self.rec_a[0], self.rec_b[0]],
                [self.rec_a[1], self.rec_b[1]], color="blue")
        rec_circle = plt.Circle(self.rec_c, self.rec_size / 2,
            edgecolor="black", fill=False, linestyle='--')
        ax.add_patch(rec_circle)

        ## heliostats
        ax.plot(self.layout[:, 0], self.layout[:, 1], "o", color="red")
        for heli_c in list(self.layout):
            heli_circle = plt.Circle(heli_c, self.heli_size / 2,
                edgecolor='black', fill=False, linestyle='--')
            ax.add_patch(heli_circle)

        if name:
            fig.tight_layout()
            fig.set_facecolor('white')
            fig.savefig('../figures/layouts/'+name+'.png',
                facecolor=fig.get_facecolor(), edgecolor='none', dpi=100)
        else:
            plt.show()
