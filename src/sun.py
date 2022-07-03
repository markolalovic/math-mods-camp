#!/usr/bin/python3
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

class Sun:
    ''' Models the sun positions, parameters are m = number of time steps,
    and times of sunrise and sunset. For example m = 17 hours from sunrise
    at 5:00 to sunset at 21:00.
    '''
    def __init__(self, m=17, sunrise=5, sunset=21):
        self.m = m
        self.angles = np.linspace(0, np.pi, self.m)
        self.angles_deg = np.degrees(self.angles)
        self.ts = list(range(self.m))
        self.times = [str(int(time))+":00" for\
            time in list(np.linspace(sunrise, sunset, self.m))]

    def __str__(self):
        out = "Sun: "
        out += "\n\t- angles_deg = " + str([int(angle) for angle in self.angles_deg])
        out += "\n\t- ts = " + str(self.ts)
        out += "\n\t- times = " + str(self.times)
        return out

    def draw(self, name=None):
        fig, ax = plt.subplots()
        plt.axis('equal')

        for t in self.ts:
            angle = self.angles[t]
            sun_vec = np.array([np.cos(angle), np.sin(angle)])
            sun_circle = plt.Circle(sun_vec, 0.08, edgecolor="black", fill=False, linestyle='-')
            ax.add_patch(sun_circle)
            ax.text(sun_vec[0], sun_vec[1], self.times[t], fontsize=12)
            ax.plot([0, sun_vec[0]],[0, sun_vec[1]], color="orange", linewidth=2)

        if name:
            fig.tight_layout()
            fig.set_facecolor('white')
            fig.savefig('../figures/models/'+name+'.png',
                facecolor=fig.get_facecolor(), edgecolor='none', dpi=100)
        else:
            plt.show()
