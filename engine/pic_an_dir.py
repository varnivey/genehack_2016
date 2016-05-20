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


import os
import pic_an

def calc_multiple_dirs(dir_path, nuclei_name=u'3DAPI.TIF', foci_name=u'3FITС.TIF'):
    '''Separately calculates foci for all subdirs'''

    subdirs = [os.path.join(dir_path, directory) for directory in os.listdir(dir_path) \
            if os.path.isdir(os.path.join(dir_path, directory))]

    for subdir in subdirs:

        print 'Calculation has STARTED in', os.path.split(subdir)[0]

        calc_foci_in_dir(subdir, nuclei_name, foci_name)

        print 'Calculation has FINISHED in', os.path.split(subdir)[0]

def calc_foci_in_dir(dir_path, nuclei_name=u'3DAPI.TIF', foci_name=u'3FITС.TIF', outfile = u'result.txt',\
        sensitivity = 4., min_cell_size = 4000, peak_min_val_perc = 60, foci_min_val_perc = 90,\
        foci_radius = 10, foci_min_level_on_bg = 40, foci_rescale_min = None, foci_rescale_max = None,\
        nuclei_color = 0.66, foci_color = 0.33):
    '''Calculates foci from dir list'''

    dirs_with_images = [os.path.join(dir_path, directory) for directory in os.listdir(dir_path)]

    calc_foci_in_dirlist(dir_path, dirs_with_images, nuclei_name, foci_name, outfile,\
        sensitivity, min_cell_size, peak_min_val_perc, foci_min_val_perc,\
        foci_radius, foci_min_level_on_bg, foci_rescale_min, foci_rescale_max,\
        nuclei_color, foci_color)

#THE lasiest way to do the job =D
def calc_foci_in_dirlist(dir_path, dir_list, nuclei_name=u'3DAPI.TIF', foci_name=u'3FITС.TIF', outfile = u'result.txt',\
        sensitivity = 8., min_cell_size = 1500, peak_min_val_perc = 60, foci_min_val_perc = 90,\
        foci_radius = 10, foci_min_level_on_bg = 40, foci_rescale_min = None, foci_rescale_max = None,\
        nuclei_color = 0.66, foci_color = 0.33):
    '''Calculates foci from dir'''

    dirs_with_images = dir_list

    pre_image_dirs = [image_dir for image_dir in dirs_with_images if \
            (os.path.isfile(os.path.join(image_dir,nuclei_name)) and os.path.isfile(os.path.join(image_dir, foci_name)))]

    image_dirs = [pic_an.image_dir(image_dir, nuclei_name, foci_name) for image_dir in pre_image_dirs]

    path1,name2 = os.path.split(dir_path)
    name1       = os.path.split(path1)[1]
    print name1, name2, path1
    name = name1 + '_' + name2
    absoutfile = os.path.join(dir_path,outfile)
    print name
    cell_set = pic_an.cell_set(name=name, cells=[])

    remained = len(image_dirs)

    print "We have", remained, 'images to load for', name

    print "Image loading have started for", name

    for image_dir in image_dirs:
        image_dir.load_separate_images(sensitivity, min_cell_size)

        remained -= 1

        if remained == 0:
            print "Image loading have finished for", name
        else:
            print remained, 'images remained to load for', name

        image_dir.write_pic_with_nuclei_colored()

        cell_set.extend(image_dir)

'''
    if len(cell_set.cells) == 0:
        print "There are no cells in the images from ", dir_path
        return

    print "We have", len(cell_set.cells), "cells to analyze for", name

    cell_set.rescale_nuclei()
    cell_set.rescale_foci((foci_rescale_min, foci_rescale_max))

    cell_set.calculate_foci(peak_min_val_perc, foci_min_val_perc, foci_radius, foci_min_level_on_bg)
    cell_set.calculate_foci_parameters()
    cell_set.write_parameters(absoutfile)

    for image_dir in image_dirs:
        image_dir.write_all_pic_files(nuclei_color, foci_color)
'''



