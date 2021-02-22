#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
@author: Qun Yang
@license: (C) Copyright 2021, University of Auckland
@contact: qyan327@aucklanduni.ac.nz
@date: 18/02/21 4:05 PM
@description:  
@version: 1.0
"""


import numpy as np
import matplotlib.pyplot as plt
import argparse


data_path = '../data/data_processed'
info_path = '../data/info'


class Map:

    def __init__(self, args):
        self.data = np.load('{0}/{1}/{2}/{3}_{1}.npy'.
                            format(data_path, args.data_source, args.len_seg, args.dataset)
                            )
        self.sensors = np.load('{}/sensors.npy'.format(info_path))
        self.num_sensors = self.data.shape[0]
        self.num_channels = self.data.shape[1]
        self.num_segs = self.data.shape[2]
        self.font = {'family': 'Arial',
                     'style': 'normal',
                     'weight': 'bold',
                     'size': 8,
                     'color': 'k',
                     }

    def plot_map(self):
        data = self.data.reshape(self.num_sensors * self.num_channels, self.num_segs, -1)
        sensors = self.sensors.ravel()
        fig, axs = plt.subplots(6, 6, figsize=(8, 5))
        for idx, ax in enumerate(axs.flat):
            ax.imshow(data[idx], interpolation='gaussian', cmap='viridis')
            ax.set_title(sensors[idx].item().strip('A-'), fontdict=self.font, pad=3)
            ax.axis('off')
        plt.tight_layout()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', default='W-1', type=str)
    parser.add_argument('--data_source', default='FFT', type=str)
    parser.add_argument('--len_seg', default=500, type=int)
    args = parser.parse_args()
    plt.rcParams['font.family'] = 'Arial'
    m = Map(args)
    m.plot_map()
    plt.show()
