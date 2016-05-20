#!/usr/bin/env python
# -*- coding: utf-8 -*-

#    This file is a part of DARFI project (dna Damage And Repair Foci Imager)
#    Copyright (C) 2014  Ivan V. Ozerov
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License version 2 as·
#    published by the Free Software Foundation.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License v2 for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.



class setting:
    '''Class representing calculation setting'''

    def __init__(self, info_str, stype, default_val, min_val = None, max_val = None):
        '''Initialize setting'''

        self.info_str = info_str
        self.stype = stype
        self.default_val = default_val
        self.min_val = min_val
        self.max_val = max_val
        self.value = default_val

    def set_value(self, val):
        '''Set setting value to val'''

        if type(val) != self.stype:

            print 'Value type is wrong; setting ' +  self.info_str + ' to default'
            self.set_default()
            return False

        if self.stype == float or self.stype == int:
            if val > self.max_val or val < self.min_val:

                print 'Setting value is wrong; setting ' +  self.info_str + ' to default'
                self.set_default()
                return False

        self.value = val
        return True

    def set_to_default(self):
        '''Set setting to default value'''

        self.value = self.default_val


    def get_value(self):
        '''Get setting value'''

        return self.value


class settings():
    '''Class representing a full set of calculation settings'''

    def __init__(self, min_cell_size = 1500, cell_detect_sensitivity = 5, \
            peak_min_val_perc = 60, foci_min_val_perc = 90, foci_radius = 10,\
            foci_min_level_on_bg = 40, foci_rescale_min = 0.88,\
            foci_rescale_max = 1.875, nuclei_color = 0.66, foci_color = 0.33):
        '''Initialize settings for calculation'''

        min_cell_size_info = 'minimum cell size in pixels'
        min_cell_size_stype = int
        min_cell_size_default = 1500
        min_cell_size_min = 0
        min_cell_size_max = 4294967296


        cell_detect_sensitivity_info = 'sensitivity of the cell detection algorithm'
        cell_detect_sensitivity_stype = int
        cell_detect_sensitivity_default = 5
        cell_detect_sensitivity_min = 0
        cell_detect_sensitivity_max = 10


        peak_min_val_perc_info = 'minimum foci peak percentile'
        peak_min_val_perc_stype = float
        peak_min_val_perc_default = 60.
        peak_min_val_perc_min = 0.
        peak_min_val_perc_max = 100.


        foci_min_val_perc_info = 'foci value percentile'
        foci_min_val_perc_stype = float
        foci_min_val_perc_default = 90.
        foci_min_val_perc_min     = 0.
        foci_min_val_perc_max     = 100.


        foci_radius_info = 'foci search radius'
        foci_radius_stype = int
        foci_radius_default = 10
        foci_radius_min     = 0
        foci_radius_max     = 4294967296


        foci_min_level_on_bg_info = 'minimum level of foci on background'
        foci_min_level_on_bg_stype = int
        foci_min_level_on_bg_default = 40
        foci_min_level_on_bg_min = 0
        foci_min_level_on_bg_max = 255


        foci_rescale_min_info = 'foci rescale minimum value'
        foci_rescale_min_stype = float
        foci_rescale_min_default = 0.88
        foci_rescale_min_min    = 0.
        foci_rescale_min_max    = 255.


        foci_rescale_max_info = 'foci rescale maximum value'
        foci_rescale_max_stype = float
        foci_rescale_max_default = 1.875
        foci_rescale_max_min    = 0.
        foci_rescale_max_max    = 255.


        nuclei_color_info = 'nuclei color on the merged image'
        nuclei_color_stype = float
        nuclei_color_default = 0.66
        nuclei_color_min     = 0.
        nuclei_color_max     = 1.


        foci_color_info = 'foci color on the merged image'
        foci_color_stype = float
        foci_color_default = 0.33
        foci_color_min = 0.
        foci_color_max = 1.


        self.min_cell_size = setting(min_cell_size_info, min_cell_size_stype,\
                min_cell_size_default, min_cell_size_min, min_cell_size_max)
        self.cell_detect_sensitivity = setting(cell_detect_sensitivity_info, cell_detect_sensitivity_stype,\
                cell_detect_sensitivity_default, cell_detect_sensitivity_min, cell_detect_sensitivity_max)
        self.peak_min_val_perc = setting(peak_min_val_perc_info, peak_min_val_perc_stype,\
                peak_min_val_perc_default, peak_min_val_perc_min, peak_min_val_perc_max)
        self.foci_min_val_perc = setting(foci_min_val_perc_info, foci_min_val_perc_stype,\
                foci_min_val_perc_default, foci_min_val_perc_min, foci_min_val_perc_max)
        self.foci_radius = setting(foci_radius_info, foci_radius_stype,\
                foci_radius_default, foci_radius_min, foci_radius_max)
        self.foci_min_level_on_bg = setting(foci_min_level_on_bg_info, foci_min_level_on_bg_stype,\
                foci_min_level_on_bg_default, foci_min_level_on_bg_min, foci_min_level_on_bg_max)
        self.foci_rescale_min = setting(foci_rescale_min_info, foci_rescale_min_stype,\
                foci_rescale_min_default, foci_rescale_min_min, foci_rescale_min_max)
        self.foci_rescale_max = setting(foci_rescale_max_info, foci_rescale_max_stype,\
                foci_rescale_max_default, foci_rescale_max_min, foci_rescale_max_max)
        self.nuclei_color = setting(nuclei_color_info, nuclei_color_stype,\
                nuclei_color_default, nuclei_color_min, nuclei_color_max)
        self.foci_color = setting(foci_color_info, foci_color_stype,\
                foci_color_default, foci_color_min, foci_color_max)

        self.min_cell_size.set_value(min_cell_size)
        self.cell_detect_sensitivity.set_value(cell_detect_sensitivity)
        self.peak_min_val_perc.set_value(peak_min_val_perc)
        self.foci_min_val_perc.set_value(foci_min_val_perc)
        self.foci_radius.set_value(foci_radius)
        self.foci_min_level_on_bg.set_value(foci_min_level_on_bg)
        self.foci_rescale_min.set_value(foci_rescale_min)
        self.foci_rescale_max.set_value(foci_rescale_max)
        self.nuclei_color.set_value(nuclei_color)
        self.foci_color.set_value(foci_color)






