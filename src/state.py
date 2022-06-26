#!/usr/bin/python3
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

class State:
    ''' '''
    def __init__(self, plant, sun_angle):
        '''
        Inputs:
            * object plant of class Plant: description of a plant
            * sun_angle: angle between 0 and \pi in radians
        '''
        self.plant = plant
        self.sun_angle = sun_angle
        self.d_factor = 1.5 # rays multiplier to ensure it hits

        ## sun tangent vector
        sun_vec = np.array([np.cos(self.sun_angle), np.sin(self.sun_angle)])
        self.heli_suns = self.plant.layout + sun_vec

        ## heliostats normals
        heli_normals = self.plant.heli_refs + self.heli_suns - 2 * self.plant.layout
        normal_lengths = np.apply_along_axis(np.linalg.norm, 1, heli_normals)
        heli_normals = heli_normals / np.array([normal_lengths, normal_lengths]).T
        self.heli_normals = self.plant.layout + heli_normals

        ## heliostats tangent vectors and edge points
        heli_tans = self.heli_normals - self.plant.layout
        self.heli_tans = np.array([-heli_tans[:, 1], heli_tans[:, 0]]).T
        self.heli_as = self.plant.layout + self.plant.heli_size / 2 * self.heli_tans
        self.heli_bs = self.plant.layout - self.plant.heli_size / 2 * self.heli_tans

        ## ray points
        self.surf_points = np.zeros((self.plant.n, self.plant.heli_rays, self.plant.dim), dtype="float128")
        self.ref_ends = np.zeros((self.plant.n, self.plant.heli_rays, self.plant.dim), dtype="float128")
        self.sun_ends = np.zeros((self.plant.n, self.plant.heli_rays, self.plant.dim), dtype="float128")
        for i in range(self.plant.n):
            self.surf_points[i], self.ref_ends[i], self.sun_ends[i] = self.get_ray_points(i)

    def __str__(self):
        out = "State: \n"
        out += "\n - sun_angle = {:4.2f}\n".format(np.degrees(self.sun_angle))
        return out

    def get_effects(self, i, verbose=False):
        ''' For heliostat i returns the effects of:
            * eta_aa = atmospheric attenuation
            * eta_cos = cosine effect
            * eta_sbm = shading, blocking and rays missing the receiver
        '''
        received_rays, not_sbm = self.get_received_rays(i)
        all_rays = self.plant.heli_rays

        eta_aa = self.get_atmospheric_attenuation(0)
        eta_cos = self.get_cosine_effect(0)
        eta_sbm = np.array(received_rays / all_rays)

        if verbose:
            out = "Effects on heliostat {:d}: \n".format(i)
            out += "\n\t* eta_aa = {:f}".format(eta_aa)
            out += "\n\t* eta_cos = {:f}".format(eta_cos)
            out += "\n\t* eta_sbm = {:f}".format(eta_sbm)
            out += "\n\t* received_rays / all_rays = {:d} / {:d}".format(received_rays, all_rays)
            out += "\n\t* [not-shaded, not-blocked, not-missed] / all_rays = "
            out += str(not_sbm) + " / " + str(all_rays) + "\n"
            print(out)

        return eta_aa, eta_cos, eta_sbm, not_sbm

    def get_cosine_effect(self, i):
        heli_normal = self.heli_normals[i] - self.plant.layout[i]
        heli_sun = self.heli_suns[i] - self.plant.layout[i]
        return np.inner(heli_normal, heli_sun)

    def get_received_rays(self, i):
        ''' Returns for heliostat i:
        * received_prop = prortion of received rays that are not shaded,
        not blocked and do not miss the receiver,
        * not_sbm_props = proportions of not shaded, not blocked and
        not missed rays. '''
        not_shaded = self.get_not_sb(i, self.sun_ends)
        not_blocked = self.get_not_sb(i, self.ref_ends)
        not_missed = self.get_not_missed(i)
        received = np.sum(not_shaded & not_blocked & not_missed)

        ## not shaded, not blocked and not missed rays
        rays_matrix = np.concatenate(
          ([not_shaded], [not_blocked], [not_missed]), axis=0)
        not_sbm = np.apply_along_axis(np.sum, 1, rays_matrix)

        return received, not_sbm

    def get_not_sb(self, i, end_points):
        ''' Returns a vector of not shaded or not blocked rays for heliostat i
        if end_points are sun_ends or ref_ends respectively.
        e.g. [0, 0, 1, 1, 1] where:
            * rays j = 0, 1 are shaded or blocked
            * rays j = 2, 3, 4 are not shaded or blocked
        by any other heliostat.
        '''
        not_sb = np.ones(self.plant.heli_rays, dtype=int)
        for j in range(self.plant.heli_rays):
            for k in range(self.plant.n):
                if k != i:
                    a, b = self.heli_as[k, :], self.heli_bs[k, :]
                    c, d = self.surf_points[i, j, :], end_points[i, j, :]
                    if self.intersect(a, b, c, d):
                        not_sb[j] = 0
                        break
        return not_sb

    def get_not_missed(self, i):
        ''' Returns which rays do not miss the receiver. '''
        not_missed = np.zeros(self.plant.heli_rays, dtype=int)
        for j in range(self.plant.heli_rays):
            a, b = self.plant.rec_a, self.plant.rec_b
            c, d = self.surf_points[i, j, :], self.ref_ends[i, j, :]
            if self.intersect(a, b, c, d):
                not_missed[j] = 1
        return not_missed

    def get_atmospheric_attenuation(self, i):
        di = self.plant.ref_lengths[i]
        if di <= 1000:
            return 0.99321 - 0.0001176 * di + 1.97 * 10**(-8) * di**2
        else:
            return np.exp(-0.0001106 * di)

    def get_ray_points(self, i):
        ''' Returns the points on the rays for heliostat i:
            * surface points on the heliostat
            * reflected rays ends towards the receiver
            * sun rays ends towards the sun
        '''
        heli_a = np.array([self.heli_as[i, 0], self.heli_as[i, 1]])
        heli_b = np.array([self.heli_bs[i, 0], self.heli_bs[i, 1]])
        heli_tan = self.heli_tans[i]

        # the surface points
        surf_coefs = np.linspace(0.1, 0.9, self.plant.heli_rays)
        mat_coefs = np.tile(surf_coefs, (2, 1))
        mat_heli_b = np.tile(heli_b, (self.plant.heli_rays, 1)).T
        mat_heli_tan = np.tile(heli_tan, (self.plant.heli_rays, 1)).T
        surf_points = mat_heli_b + mat_coefs * mat_heli_tan * self.plant.heli_size
        surf_points = surf_points.T

        ref_ends = np.zeros((self.plant.heli_rays, self.plant.dim), dtype="float128")
        sun_ends = np.zeros((self.plant.heli_rays, self.plant.dim), dtype="float128")
        for j in range(self.plant.heli_rays):
            surf_point = surf_points[j, :].T

            # ray ends towards the receiver
            ref_vec = self.plant.heli_refs[i] - self.plant.layout[i]
            ref_ends[j] = surf_point + ref_vec * self.plant.ref_lengths[i] * self.d_factor

            # draw the rays towards the sun
            sun_vec = self.heli_suns[i] - self.plant.layout[i]
            sun_ends[j] = surf_point + sun_vec * self.plant.max_ij * self.d_factor

        return surf_points, ref_ends, sun_ends

    def intersect(self, a, b, c, d):
        ''' Checks if line segment ab intersects cd.
        From: https://gist.github.com/kylemcdonald/6132fc1c29fd3767691442ba4bc84018
        '''
        x1, y1 = a
        x2, y2 = b
        x3, y3 = c
        x4, y4 = d

        denom = (y4 - y3)*(x2 - x1) - (x4 - x3)*(y2 - y1)
        if denom == 0: # parallel
            return False

        ua = ((x4 - x3)*(y1 - y3) - (y4 - y3)*(x1 - x3)) / denom
        if ua < 0 or ua > 1: # out of range
            return False

        ub = ((x2 - x1)*(y1 - y3) - (y2 - y1)*(x1 - x3)) / denom
        if ub < 0 or ub > 1: # out of range
            return False

        x = x1 + ua * (x2-x1)
        y = y1 + ua * (y2-y1)

        return True

    def draw(self, i):
        fig, ax = plt.subplots()
        plt.axis('equal')
        x_margins = 2, 2 # for drawings
        y_margins = 2, 6

        ## coord sys
        ax.plot([self.plant.x_min - x_margins[0],
                 self.plant.x_max + x_margins[1]], [0, 0], color="black")

        ax.plot([0, 0],
          [self.plant.y_min - y_margins[0],
           self.plant.y_max + y_margins[1]], color="black")

        ## receiver
        ax.plot([self.plant.rec_a[0], self.plant.rec_b[0]],
                [self.plant.rec_a[1], self.plant.rec_b[1]],
                color="blue", linewidth=2)

        ## heliostats
        ax.plot(self.plant.layout[:, 0], self.plant.layout[:, 1],
          "o", color="red")

        ## heliostats, sun vectors, reflected vectors, normals
        ax.plot([self.heli_as[:, 0], self.heli_bs[:, 0]],
                [self.heli_as[:, 1], self.heli_bs[:, 1]],
                color="blue", linewidth=2)

        ax.plot([self.plant.layout[:, 0], self.heli_suns[:, 0]],
                [self.plant.layout[:, 1], self.heli_suns[:, 1]],
                color="red")

        ax.plot([self.plant.layout[:, 0], self.plant.heli_refs[:, 0]],
                [self.plant.layout[:, 1], self.plant.heli_refs[:, 1]],
                color="red")

        ax.plot([self.plant.layout[:, 0], self.heli_normals[:, 0]],
                [self.plant.layout[:, 1], self.heli_normals[:, 1]],
                color="black")

        ## draw the surface points for heliostat i
        ax.plot(self.surf_points[i, :, 0], self.surf_points[i, :, 1], "o", color="red")

        ## draw the rays towards the receiver
        ax.plot([self.surf_points[i, :, 0], self.ref_ends[i, :, 0]],
                [self.surf_points[i, :, 1], self.ref_ends[i, :, 1]], color="green")

        ## draw the rays towards the sun
        ax.plot([self.surf_points[i, :, 0], self.sun_ends[i, :, 0]],
                [self.surf_points[i, :, 1], self.sun_ends[i, :, 1]], color="orange")

        plt.title("State at sun angle "
          + str(np.round(np.degrees(self.sun_angle))))

        plt.show()
