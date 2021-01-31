#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
@author: Qun Yang
@license: (C) Copyright 2021, University of Auckland
@contact: qyan327@aucklanduni.ac.nz
@date: 31/01/21 11:29 AM
@description:  
@version: 1.0
"""

import json

folders = {'W-1': '7_W-1',
           'W-2': '11_W-2',
           'W-3': '12_W-3',
           'W-5': '14_W-5',
           'W-6': '16_W-6',
           'W-7': '19_W-7',
           'W-8': '20_W-8',
           'W-9': '22_W-9',
           'W-10': '23_W-10',
           'W-11': '25_W-11',
           'W-12': '27_W-12',
           'W-13': '29_W-13',
           'W-14': '30_W-14',
           'W-15': '34_W-15',
           'W-16': '35_W-16',
           'W-17': '37_W-17',
           'W-18': '38_W-18',
           'W-19': '40_W-19',
           'W-21': '42_W-21',
           'W-22': '43_W-22',
           'W-23': '45_W-23'
           }

folders = json.dumps(folders, indent=2)
with open('./folders.json', 'w') as f:
    f.write(folders)
