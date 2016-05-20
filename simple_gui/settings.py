# -*- coding: utf-8 -*-
"""
Created on Tue Dec 16 22:08:01 2014

@author: satary
you can fin info about settings in engine/README file ;)
"""

class Settings(object):      
    def __init__(self):
        self.nuclei_name='' # type 'unicode'
        self.foci_name='' # type 'unicode'
        self.sensitivity=5 # type 'int' range: 0 to 10
        self.min_cell_size=4000 # type 'int' range: 0 to 4294967296
        self.foci_lookup_sensivity=70 # type 'int' range: 0 to 100
        self.foci_area_fill_percent=30 # type 'int' range: 0 to 100
        self.min_foci_radius=3 # type 'int' range: 0 to 4294967296
        self.max_foci_radius=12 # type 'int' range: 0 to 4294967296
        self.allowed_foci_overlap=100 # type 'int' range: 0 to 100
        self.normalize_intensity=True # type 'bool' 
        self.foci_rescale_min=None # type 'float' range: 0 to 255.
        self.foci_rescale_max=None # type 'float' range: 0 to 255.
        self.return_circles=True # type 'bool' 
        self.nuclei_color=0.66 # type 'float' range: 0 to 1.0
        self.foci_color=0.33 # type 'float' range: 0 to 1.0
        self.rowOrder=['Cell number',
                    'Cell area',
                    'Mean intensity im1',
                    'Mean intensity im2',
                    'Abs foci number',
                    'Abs foci area',
                    'Abs foci soid',
                    'Rel foci number',
                    'Rel foci area',
                    'Rel foci soid',
                    'Foci intensity',
                    'Foci size']
        self.columnOrder=['Mean', 'MSE']
    def __getitem__(self, item):
         return self.__dict__[item]
