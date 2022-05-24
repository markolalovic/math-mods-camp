#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

class Plant:
    ''' Constructs a toy plant given the specifications and heliostats layout. '''
    def __init__(self, plant_file_name="", heli_layout_file_name="", heli_layout=[]):
        ''' Inputs:
            * Plant and layout descriptions in JSON format, for example:
                * plant_file_name="../data/plants/tiny-plant.json"
                * heli_layout_file_name="../data/layouts/tiny-layout.json"
            * For debugging also a list of coordinates, for example:
                heli_layout = [[8, 4], ..., [28, 4]]
        '''
        if plant_file_name:
            plant_d = self.load(plant_file_name) # loads the description in a dict
        else:
            raise ValueError("missing plant description")

        self.dim = 2 # dimensions fixed 2 for a start
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
        if heli_layout:
            self.heli_layout_name = ""
            self.heli_layout = np.array(heli_layout) # centers of heliostats
        elif heli_layout_file_name:
            layout_dict = self.load(heli_layout_file_name)
            self.heli_layout_name = list(layout_dict.keys())[0]
            self.heli_layout = np.array(layout_dict[self.heli_layout_name])
        else:
            raise ValueError("missing layout")

        self.n = len(self.heli_layout) # number of heliostats
        self.heli_size = plant_d["heliostats"]["heli_size"]
        self.heli_rays = plant_d["heliostats"]["heli_rays"] # number of rays per heliostat

        ## heliostats reflected vectors
        heli_refs = self.rec_c - self.heli_layout
        heli_refs = heli_refs.astype("float128")
        self.ref_lengths = np.apply_along_axis(np.linalg.norm, 1, heli_refs)
        heli_refs = heli_refs / np.array([self.ref_lengths, self.ref_lengths]).T
        self.heli_refs = self.heli_layout + heli_refs

        self.max_ij = 0
        self.valid_layout = self.check_layout()

    def save(self, d, file_name, indent=0):
        ''' Helper method to save the layout, or plant specs.
        Example:
            d = {"tiny-layout": [[8, 4], [16, 4], [22, 4], [28, 4]]}
            file_name = "../data/layouts/tiny-layout.json"
            plant.save(d, file_name) # saves it to ../data
        '''
        with open(file_name, 'w') as file:
            json.dump(d, file, indent=indent)

    def load(self, file_name):
        ''' Helper method to load the layout, or plant specs. '''
        with open(file_name) as file:
            d = json.load(file)
        return d

    def check_layout(self):
        ''' Checks that:
            * heliostats are in the field area
            * heliostats are minimum distance appart and minimum
        distance from the receiver.
        '''
        if np.any(self.heli_layout[:, 0] > self.x_max):
            return False
        if np.any(self.heli_layout[:, 0] < self.x_min):
            return False
        if np.any(self.heli_layout[:, 1] > self.y_max):
            return False
        if np.any(self.heli_layout[:, 1] < self.y_min):
            return False

        for i in range(self.n):
            if np.linalg.norm(self.heli_layout[i] - self.rec_c) < self.d_min:
                return False
            for j in range(i + 1, self.n):
                dist_ij = np.linalg.norm(self.heli_layout[i] - self.heli_layout[j])
                if dist_ij > self.max_ij:
                    self.max_ij = dist_ij
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
        if self.heli_layout_name:
            out += "\n\t\t- heli_layout = {:s} \n".format(self.heli_layout_name)
        else:
            out += "\n\t\t- heli_layout = [[{:4.2f}, {:4.2f}], ..., [{:4.2f}, {:4.2f}]]\n"\
                .format(self.heli_layout[0, 0], self.heli_layout[0, 1],\
                        self.heli_layout[-1, 0], self.heli_layout[-1, 1])
        return out

    def draw(self):
        fig, ax = plt.subplots()
        plt.axis('equal')
        x_margins = 2, 2 # for drawings
        y_margins = 2, 6

        ## coord sys
        ax.plot([self.x_min - x_margins[0],
                 self.x_max + x_margins[1]], [0, 0], color="black")

        ax.plot([0, 0],
          [self.y_min - y_margins[0],
           self.y_max + y_margins[1]], color="black")

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
        ax.plot(self.heli_layout[:, 0], self.heli_layout[:, 1], "o", color="red")
        for heli_c in list(self.heli_layout):
            heli_circle = plt.Circle(heli_c, self.d_min,
                edgecolor='black', fill=False, linestyle='--')
            ax.add_patch(heli_circle)

        plt.title(self.name)
        plt.show()

## tiny plant json creation:
# plant_d = {}
# plant_d["name"] = "Tiny Plant"
#
# field_area_d = {}
# field_area_d["x_min"] = 0
# field_area_d["x_max"] = 35
# field_area_d["y_min"] = 0
# field_area_d["y_max"] = 10
# field_area_d["d_min"] = 2
# plant_d["field_area"] = field_area_d
#
# rec_d = {}
# rec_d["rec_height"] = 12
# rec_d["rec_angle"] = 80
# rec_d["rec_size"] = 4
# plant_d["receiver"] = rec_d
#
# heli_d = {}
# heli_d["heli_size"] = 4
# heli_d["heli_rays"] = 5
# plant_d["heliostats"] = heli_d
#
# plant_file_name = "../data/plants/tiny-plant.json"
# plant.save(plant_d, plant_file_name, 4)
