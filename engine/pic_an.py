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


import os, copy
import numpy as np

from skimage.exposure import rescale_intensity
from skimage import img_as_ubyte
from skimage.color import hsv2rgb

from skimage.measure import label as measure_label
from skimage.morphology import remove_small_objects
from skimage.filters import threshold_otsu as global_otsu

#from skimage.io import imsave
#from skimage.io import imread

from scipy.misc import imsave
from scipy.misc import imread

from pic_an_calc import find_nuclei
from pic_an_calc import split_label

#from pic_an_calc import foci_plm
#from pic_an_calc import foci_thres
from pic_an_calc import foci_log
from pic_an_calc import join_peaces
from pic_an_calc import join_peaces_3d
from pic_an_calc import peace

class cell:
    '''Class representing cell variables and methods'''

    def __init__(self, nucleus, pic_nucleus, pic_foci, coords = (0,0,0,0)):
        '''Construct cell from mask and channel pics'''

        self.nucleus           = nucleus
        self.pic_nucleus       = nucleus*pic_nucleus
        self.coords            = coords
        self.area              = np.sum(nucleus)
        self.nucleus_pic_mean  = np.sum(self.pic_nucleus)/np.float(self.area)
        self.is_active         = True
        self.touched           = False

        if pic_foci != None:
            self.pic_foci = nucleus*pic_foci
            self.foci_pic_mean = np.sum(self.pic_foci)/np.float(self.area)


    def calculate_foci(self, foci_det_sens = 70, foci_fill_perc = 30, \
            min_foci_radius = 3, max_foci_radius = 12, overlap = 100, \
            return_circles = True):
        '''Find foci and their parameters'''

        nucleus_new = (self.rescaled_nucleus_pic != 0)

        results = foci_log(self.rescaled_foci_pic, nucleus_new, foci_det_sens,\
                foci_fill_perc, min_foci_radius, max_foci_radius, overlap,
                return_circles)

        self.foci_number    = results[0]
        self.foci_soid      = results[1]
        self.foci_area      = results[2]
        self.foci_seeds     = results[3]
        self.foci_binary    = results[4]
        self.foci_intens    = results[5]


    def add_pic_foci(self, pic_foci):
        '''Add pic with foci to cell'''

        self.pic_foci     = self.nucleus*pic_foci
        self.foci_pic_mean = np.sum(self.pic_foci)/np.float(self.area)

#    def get_nucleus_mean_value(self):
#        '''Return mean value of the nucleus'''
#
#        if not hasattr(self, 'nucleus_mean_value'):
#
#            nucleus_values = np.extract(self.nucleus, self.pic_nucleus)
#
#            self.nucleus_mean_value = np.mean(nucleus_values, dtype = float)
#
#        return self.nucleus_mean_value



    def get_foci_bg_value(self):
        '''Return argmax of foci bg values'''

        if not hasattr(self, 'foci_bg_value'):

            foci_values = np.extract(self.nucleus, self.pic_foci)

#            self.foci_bg_value = np.percentile(foci_values, (20))

#            thres = global_otsu(foci_values)

            thres  =  np.percentile(foci_values, (20))

#            thres = np.median(foci_values)

#            bg_values = foci_values[foci_values <= thres]

#            value_count = np.bincount(bg_values)

#            self.foci_bg_value = np.float(np.argmax(value_count))

#            self.foci_bg_value = np.median(bg_values)

            self.foci_bg_value = thres

#            print np.min(foci_values), thres, np.round(100*bg_values.size/foci_values.size), self.foci_bg_value

        return self.foci_bg_value



class cell_set:
    '''Class representing set of cells'''

    def __init__(self, name = u'', cells = []):
        '''Construct set from the list of cells given'''

        self.cells = cells
        self.name  = name
        self.have_foci_params = False

    def reset_foci():
        '''Set have_foci_params to False'''

        self.have_foci_params = False

    def active_cells(self):
        '''Return a list of active cells only'''

        active = [cur_cell for cur_cell in self.cells if cur_cell.is_active]

        return active


    def rescale_nuclei(self):
        '''Rescale nuclei in the set'''

        if self.number_of_cells() == 0:
            return

        new_values = []

        for cur_cell in self.cells:

            nucleus_values = np.extract(cur_cell.nucleus, cur_cell.pic_nucleus)

            mean_value = np.mean(nucleus_values, dtype = float)

            new_values.append(nucleus_values/mean_value)

            cur_cell.nucleus_mean_value = mean_value

        p2,p98 = np.percentile(np.concatenate(new_values),(2,98))

        for cur_cell in self.cells:

            rescaled_norm_pic = rescale_intensity(cur_cell.pic_nucleus/cur_cell.nucleus_mean_value, in_range=(p2, p98))

            cur_cell.rescaled_nucleus_pic = np.floor(rescaled_norm_pic*200).astype(np.uint8)


    def get_foci_rescale_values(self, normalize = True):
        '''Return tuple with min and max values for foci rescale'''

        new_foci_values = []

        for cur_cell in self.active_cells():

            foci_values = np.extract(cur_cell.nucleus, cur_cell.pic_foci)

            if normalize:

                bg_value = cur_cell.get_foci_bg_value()

                new_foci_values.append(foci_values/bg_value)

            else:

                new_foci_values.append(foci_values/50.)

        return  tuple(np.percentile(np.concatenate(new_foci_values),(2,99)))


    def rescale_foci(self, foci_rescale_values=(None, None), normalize = True):
        '''Rescale foci in the set'''

        if foci_rescale_values == (None, None):

            foci_rescale_values = self.get_foci_rescale_values(normalize)

        for cur_cell in self.cells:

            if normalize:

                rescaled_norm_pic = rescale_intensity(cur_cell.pic_foci/cur_cell.get_foci_bg_value(), in_range=foci_rescale_values)

            else:

                rescaled_norm_pic = rescale_intensity(cur_cell.pic_foci/50., in_range=foci_rescale_values)

            cur_cell.rescaled_foci_pic = np.floor(rescaled_norm_pic*255).astype(np.uint8)


### Variable names should be replaced here

    def find_foci(self, peak_min_val_perc = 60, foci_min_val_perc = 90, \
            foci_radius = 10, foci_min_level_on_bg = 40, overlap = 100, \
            return_circles = True):
        '''Calculate foci_log for all cells'''

        remained = len(self.cells)

        name = self.name

#        print('Foci calculation has started for %s' % name)

        for cur_cell in self.cells:
            cur_cell.calculate_foci(peak_min_val_perc, foci_min_val_perc, \
                    foci_radius, foci_min_level_on_bg, overlap, return_circles)

            remained -= 1

#            if remained == 0:
#                print('Foci calculation has finished for %s' % name)


#            elif (remained == 1):
#                print('%d nucleus remained for %s' % (remained,name))

#            else:
#                print('%d nuclei remained for %s' % (remained,name))

###

    def calculate_foci(self, foci_det_sens = 70, foci_fill_perc = 30, \
            min_foci_radius = 3, max_foci_radius = 12, overlap=100, \
            return_circles = True, normalize = True, \
            foci_rescale_values = (None, None)):
        '''Rescale foci image and find foci'''

        self.rescale_foci(foci_rescale_values, normalize)
        self.find_foci(foci_det_sens, foci_fill_perc, min_foci_radius, \
                max_foci_radius, overlap, return_circles)
        self.have_foci_params = True



    def mean_cell_size(self):
        '''Return mean cell size'''

        cell_size_list = []

        for cur_cell in self.active_cells():

            cell_size_list.append(cur_cell.area)

        return np.mean(cell_size_list)


    def mean_nuclei_parameters(self):
        '''Return mean and MSE for cell area, mean intensity and mean cell
           intensity on nuclei image'''

        params = {}

        active_cells = self.active_cells()

        cell_areas     = []
        cell_ints_im1  = []
        cell_number    = len(active_cells)

        for cur_cell in active_cells:

            cell_areas.append(cur_cell.area)
            cell_ints_im1.append(cur_cell.nucleus_pic_mean)


        params['Cell number'] = {}
        params['Cell number']['Mean']  = cell_number
        params['Cell number']['MSE']   = ''

        params['Cell area']            = mean_and_MSE(cell_areas,0)
        params['Cell intensity im1']   = mean_and_MSE(cell_ints_im1)

        return params


    def mean_foci_parameters(self, mean_cell_size = 8100):
        '''Calculate absolute and relative foci number, area and soid in 10-90 percent interval'''

        params = {}

        abs_foci_nums  = []
        abs_foci_areas = []
        abs_foci_ints  = []
        abs_foci_soids = []

        rel_foci_nums  = []
        rel_foci_areas = []
#        rel_foci_ints  = []
        rel_foci_soids = []

        cell_ints_im2  = []


#        mean_cell_size = self.mean_cell_size()


        for cur_cell in self.active_cells():

            abs_foci_nums.append ( cur_cell.foci_number)
            abs_foci_areas.append( cur_cell.foci_area  )
            abs_foci_ints.append ( cur_cell.foci_intens)
            abs_foci_soids.append( cur_cell.foci_soid  )

            cell_ints_im2.append ( cur_cell.foci_pic_mean)

            if (cur_cell.area != 0):
                rel_foci_nums.append(  cur_cell.foci_number*mean_cell_size/np.float(cur_cell.area))
                rel_foci_areas.append( cur_cell.foci_area*  mean_cell_size/np.float(cur_cell.area))
#                rel_foci_ints.append(  cur_cell.foci_intens*mean_cell_size/np.float(cur_cell.area))
                rel_foci_soids.append( cur_cell.foci_soid*  mean_cell_size/np.float(cur_cell.area))


        params['Abs foci number']       = mean_and_MSE(abs_foci_nums)
        params['Abs foci area']         = mean_and_MSE(abs_foci_areas)
        params['Abs foci soid']         = mean_and_MSE(abs_foci_soids,0)
        params['Foci intensity']        = mean_and_MSE(abs_foci_ints)

        params['Rel foci number']       = mean_and_MSE(rel_foci_nums)
        params['Rel foci area']         = mean_and_MSE(rel_foci_areas)
        params['Rel foci soid']         = mean_and_MSE(rel_foci_soids,0)

        params['Cell intensity im2']    = mean_and_MSE(cell_ints_im2)

        abs_num ,  num_err = params['Abs foci number']['Mean'], params['Abs foci number']['MSE']
        abs_area, area_err = params['Abs foci area'  ]['Mean'], params['Abs foci area'  ]['MSE']

        params['Foci size'] = {}

        if abs_num != 0 or abs_area != 0:
            foci_size = np.round(abs_area/abs_num,2)
            size_err  = np.round((num_err/abs_num + area_err/abs_area)*foci_size,2)

            params['Foci size']['Mean'] = foci_size
            params['Foci size']['MSE']  = size_err
        else:
            params['Foci size']['Mean'] = 0.
            params['Foci size']['MSE']  = 0.

        self.have_foci_params = True

        return params


    def get_mean_parameters(self, mean_cell_size = 8100):
        '''Retrun dictionary with mean parameters'''

        params = {}

        params.update(self.mean_nuclei_parameters())

        if self.have_foci_params:

            params.update(self.mean_foci_parameters(mean_cell_size))

        return params


    def get_cell_parameters(self,mean_cell_size = 8100):
        '''Returns parameters for individual cells'''

        params = {}

        params['Cell number']            = {}
        params['Cell area']              = {}
        params['Cell intensity im1']     = {}

        if self.have_foci_params:

            params['Cell intensity im2'] = {}
            params['Abs foci number']    = {}
            params['Abs foci area']      = {}
            params['Abs foci soid']      = {}
            params['Rel foci number']    = {}
            params['Rel foci area']      = {}
            params['Rel foci soid']      = {}
            params['Foci intensity']     = {}
            params['Foci size']          = {}

        cell_num = len(self.cells)
        if cell_num != 0:
            zero_num = np.floor(np.log(cell_num)/np.log(10)).astype(int) + 1
        for cur_cell,cur_num in zip(self.cells,range(cell_num)):

#            if not cur_cell.is_active: continue

            name = 'cell_' + str(cur_num).zfill(zero_num)

            cell_int_im1    = np.round(cur_cell.nucleus_pic_mean,2)

            params['Cell number'][name]         = ''
            params['Cell area'][name]           = np.round(cur_cell.area,2)
            params['Cell intensity im1'][name]  = cell_int_im1

            if self.have_foci_params:

                rel_foci_number = np.round(cur_cell.foci_number*mean_cell_size/np.float(cur_cell.area),2)
                rel_foci_area   = np.round(cur_cell.foci_area*mean_cell_size/np.float(cur_cell.area),2)
                rel_foci_soid   = np.round(cur_cell.foci_soid*mean_cell_size/np.float(cur_cell.area),0).astype(int)
                cell_int_im2    = np.round(cur_cell.foci_pic_mean,2)
                if cur_cell.foci_number != 0:
                    foci_size       = np.round(cur_cell.foci_area/np.float(cur_cell.foci_number),2)
                else:
                    foci_size       = 0

                params['Cell intensity im2'][name]  = cell_int_im2
                params['Abs foci number'][name]     = cur_cell.foci_number
                params['Abs foci area'][name]       = cur_cell.foci_area
                params['Abs foci soid'][name]       = np.round(cur_cell.foci_soid,0).astype(int)
                params['Rel foci number'][name]     = rel_foci_number
                params['Rel foci area'][name]       = rel_foci_area
                params['Rel foci soid'][name]       = rel_foci_soid
                params['Foci intensity'][name]      = np.round(cur_cell.foci_intens,2)
                params['Foci size'][name]           = foci_size


        return params


    def get_parameters_dict(self, verbose = True, mean_cell_size = 8100):
        '''Returns final dictionary with all parameters'''

        self.mean_params = self.get_mean_parameters(mean_cell_size)

        if not verbose:
            self.last_dict_not_verbose = True
            return self.mean_params

        if not hasattr(self,'cell_params'):
            self.last_dict_not_verbose = True
            self.cell_params = self.get_cell_parameters(mean_cell_size)
            cell_names = []

            cell_num = len(self.cells)

            if cell_num != 0:
                zero_num = np.floor(np.log(cell_num)/np.log(10)).astype(int) + 1
            for cur_num in range(cell_num):
                cell_names.append('cell_' + str(cur_num).zfill(zero_num))

            self.cell_names = cell_names

        cell_params = self.cell_params

        param_names = cell_params.keys()

        cell_names = self.cell_names

        if self.last_dict_not_verbose:
            params = copy.deepcopy(cell_params)

            for cell_name, cur_cell in zip(cell_names,self.cells):
                if not cur_cell.is_active:
                    for key in param_names:
                        params[key].pop(cell_name)

            self.last_cell_params = params

        params = self.last_cell_params

        for key in param_names:
            params[key].update(self.mean_params[key])

        if not self.last_dict_not_verbose:
            for cell_name, cur_cell in zip(cell_names,self.cells):
                if cur_cell.touched:
                    if not cur_cell.is_active:
                        for key in param_names:
                            params[key].pop(cell_name)
                    else:
                        for key in param_names:
                            params[key][cell_name] = cell_params[key][cell_name]
                    break

        self.last_dict_not_verbose = False
        self.last_cell_params = params

        return params

    def untouch_cells(self):
        '''Untouch all cells in cell set'''

        for cur_cell in self.cells:
            cur_cell.touched = False


    def append(self,new_cell):
        '''Add a new cell to the set'''

        new_cell.touched = False
        self.cells.append(new_cell)

    def extend(self, other_cell_set):
        '''Add new cells from another cell set'''

        self.cells.extend(other_cell_set.cells)




class image_dir(cell_set):
    '''Class representing directory with images'''

    def __init__(self,dir_path, nuclei_name, foci_name = None):
        '''Constructor'''

        self.dir_path = dir_path
        self.cells = []
        self.nuclei_name = nuclei_name
        self.foci_name   = foci_name
        self.bg = 0
        self.all_pics = False


    def get_source_pic_nuclei(self):
        '''Return grey pic with nuclei'''

        nuclei_abspath = os.path.join(self.dir_path, self.nuclei_name)

        pic_nuclei = image_hsv_value(nuclei_abspath)

        return pic_nuclei


    def get_source_pic_foci(self):
        '''Return grey pic with foci'''

        foci_abspath   = os.path.join(self.dir_path,   self.foci_name)

        pic_foci   = image_hsv_value(  foci_abspath)

        return pic_foci


    def active_nuclei(self):
        '''Return binary image with active nuclei'''

        x_max, y_max = self.shape
        nuclei_peaces = []

        for cur_cell in self.active_cells():
            nuclei_peaces.append(peace(cur_cell.nucleus, cur_cell.coords))

        return join_peaces(nuclei_peaces, x_max, y_max)

    def reset_dir(self):
        '''Remove all cells from dir'''

        self.all_pics = False
        self.cells = []


    def detect_cells(self, sensitivity = 5., min_cell_size = 4000, \
            load_foci = True):
        '''Create cells and load image with foci'''

        if hasattr(self, 'cell_detect_params'):
            if (sensitivity, min_cell_size) == self.cell_detect_params:
                self.all_pics = load_foci
                return

        self.reset_dir()

        self.load_cell_image(sensitivity, min_cell_size)

        if load_foci:
            self.load_foci_image()
            self.all_pics = True



    def load_cell_image(self, sensitivity = 5., min_cell_size = 4000):
        '''Load cell image and add cells to self'''

        pic_nuclei = self.get_source_pic_nuclei()
        self.shape = pic_nuclei.shape

        nuclei = find_nuclei(pic_nuclei, sensitivity, min_cell_size)

        self.cell_detect_params = (sensitivity, min_cell_size)

        labels = measure_label(nuclei)

        labelcount = np.bincount(labels.ravel())

        bg = np.argmax(labelcount)

        labels += 1

        labels[labels == bg + 1] = 0

        labels = remove_small_objects(labels, min_cell_size)

        self.nuclei = labels

        self.create_cells_from_nuclei(pic_nuclei)

        self.rescale_nuclei()



    def create_cells_from_nuclei(self, pic_nuclei):
        '''Turns binary self.nuclei picture to cells'''

#        pic_foci   = self.get_source_pic_foci()
        min_size = self.cell_detect_params[1]

        labels = self.nuclei

        x_max, y_max = self.shape

        for label_num in np.unique(labels):

            if (label_num == 0):
                continue

            nucleus = (labels == label_num)
#            cell_pic_nucleus = nucleus*pic_nuclei
#            cell_pic_foci    = nucleus*pic_foci

            coords = find_cell_coords(nucleus)
            up,down,right,left = coords

            nucleus          =              nucleus[left:right,down:up]
            cell_pic_nucleus =           pic_nuclei[left:right,down:up]

            cell_pic_foci    =             None


            if split_required(coords, min_size, x_max, y_max):
                self.split_cell(nucleus, cell_pic_nucleus, cell_pic_foci, left, down)

            else:
                self.append(cell(nucleus, cell_pic_nucleus, cell_pic_foci, coords))


    def split_cell(self, nuclei, pic_nuclei, pic_foci, left_glob, down_glob):
        '''Split label using watershed algorithm'''

        x_max, y_max = self.shape
        min_size = self.cell_detect_params[1]
        labels = split_label(nuclei)

        for label_num in np.unique(labels):

            if (label_num == 0):
                continue

            nucleus = (labels == label_num)

            coords = find_cell_coords(nucleus)
            up,down,right,left = coords

            nucleus          =              nucleus[left:right,down:up]

            if np.sum(nucleus) < min_size:
                continue

            coords_glob = (up+down_glob, down+down_glob, right+left_glob, left+left_glob)

            if at_border(coords_glob, x_max, y_max):
                continue

            cell_pic_nucleus =           pic_nuclei[left:right,down:up]
            cell_pic_foci    =             None

            self.append(cell(nucleus, cell_pic_nucleus, cell_pic_foci, coords_glob))


    def load_foci_image(self, new_foci_name = None):
        '''Load image with foci'''

        if new_foci_name:
            self.foci_name = new_foci_name

        pic_foci = self.get_source_pic_foci()

        for cur_cell in self.cells:

            up,down,right,left = cur_cell.coords
            cur_cell.add_pic_foci(pic_foci[left:right,down:up])



    def get_pic_with_nuclei_colored(self):
        '''Return pic with colored nuclei'''

        pic_nuclei = self.get_source_pic_nuclei()

        x_max, y_max = self.shape

        cell_number = len(self.cells)

        if cell_number == 0:

            return np.dstack((pic_nuclei, pic_nuclei, pic_nuclei))

        hue_step = 0.29

        colored_nuclei_peaces = []

        for cur_cell, cur_num in zip(self.cells, range(cell_number)):

            if not cur_cell.is_active: continue

            pic_nucleus = cur_cell.pic_nucleus

            pic_nucleus_3d = np.dstack((pic_nucleus, pic_nucleus, pic_nucleus))

            rgb_koef = hsv2rgb(np.array([hue_step*cur_num, 0.5, 1.]).reshape((1,1,3))).reshape(3)

            colored_nuclei_peaces.append(peace(np.floor(pic_nucleus_3d*rgb_koef).astype(np.uint8),cur_cell.coords))

        pic_bg = pic_nuclei*(self.active_nuclei() == 0)

        pic_bg_3d = np.dstack((pic_bg, pic_bg, pic_bg))

        colored_nuclei_only = join_peaces_3d(colored_nuclei_peaces, x_max, y_max, dtype = np.uint8)

        colored_nuclei = pic_bg_3d + colored_nuclei_only

        return colored_nuclei


    def get_merged_pic(self, nuclei_color = 0.66, foci_color = 0.33, seeds = False):
        '''Return merged pic with foci and nuclei'''

        x_max, y_max = self.nuclei.shape

        active_cells = self.active_cells()

        cell_number = len(active_cells)

        if cell_number == 0:

            return np.zeros((x_max, y_max, 3), dtype = np.uint8)

        merged_pic_peaces = []

        nuclei_rgb_koef = hsv2rgb(np.array([nuclei_color, 1., 1.]).reshape((1,1,3))).reshape(3)

        foci_rgb_koef = hsv2rgb(np.array([foci_color, 1., 1.]).reshape((1,1,3))).reshape(3)

        for cur_cell in active_cells:

            if seeds:
                foci = cur_cell.foci_seeds
            else:
                foci = cur_cell.foci_binary

            nucleus_only = cur_cell.nucleus - foci

            pic_foci_enhanced = 255 - np.floor((255 - cur_cell.pic_foci)*0.6)

            pic_foci_enhanced = foci*pic_foci_enhanced

            pic_nucleus_only = cur_cell.pic_nucleus*nucleus_only

            pic_foci_enhanced_3d = np.dstack((pic_foci_enhanced, pic_foci_enhanced, pic_foci_enhanced))

            pic_nucleus_only_3d = np.dstack((pic_nucleus_only, pic_nucleus_only, pic_nucleus_only))

            pic_foci_rgb = pic_foci_enhanced_3d*foci_rgb_koef

            pic_nucleus_only_rgb = pic_nucleus_only_3d*nuclei_rgb_koef

            pic_merged_rgb = np.floor(pic_foci_rgb + pic_nucleus_only_rgb).astype(np.uint8)

            merged_pic_peaces.append(peace(pic_merged_rgb, cur_cell.coords))

        merged_pic = join_peaces_3d(merged_pic_peaces, x_max, y_max, dtype = np.uint8)

        return merged_pic




    def get_all_pics(self, nuclei_color = 0.66, foci_color = 0.33, seed_circles = False):
        '''Return all calculated pics'''

        if self.number_of_cells() == 0:
            print "No cells found in " + self.dir_path

#            return (None, None, None, None, None)

        rescaled_nuclei_peaces = []
        rescaled_foci_peaces   = []
        seed_peaces            = []
        foci_bin_peaces        = []

        pic_nuclei = self.get_source_pic_nuclei()

        x_max, y_max = self.nuclei.shape

        for cur_cell in self.active_cells():

            coords = cur_cell.coords

            rescaled_nuclei_peaces.append(peace(cur_cell.rescaled_nucleus_pic, coords))
            rescaled_foci_peaces.append(peace(cur_cell.rescaled_foci_pic, coords))
            seed_peaces.append(peace(cur_cell.foci_seeds, coords))
            foci_bin_peaces.append(peace(cur_cell.foci_binary, coords))


        rescaled_nuclei_pic = join_peaces(rescaled_nuclei_peaces, x_max, y_max, dtype = np.uint8)
        rescaled_foci_pic   = join_peaces(rescaled_foci_peaces, x_max, y_max, dtype = np.uint8)
        foci_binary         = join_peaces(foci_bin_peaces, x_max, y_max)

        seeds               = self.get_merged_pic(nuclei_color, foci_color, seeds = True)

        nuclei_colored = self.get_pic_with_nuclei_colored()
        merged = self.get_merged_pic(nuclei_color, foci_color)

        return (rescaled_nuclei_pic, nuclei_colored, rescaled_foci_pic, seeds, merged)


    def write_pic_with_nuclei_colored(self, pic_nuclei_colored = None):
        '''Write pic with colored nuclei to a file'''

        pic_nuclei_colored_path = os.path.join(self.dir_path, u'colored_nuclei.jpg')

        if (pic_nuclei_colored == None):
            pic_nuclei_colored = self.get_pic_with_nuclei_colored()

        imsave(pic_nuclei_colored_path, pic_nuclei_colored)


    def write_all_pic_files(self, nuclei_color = 0.66, foci_color = 0.33):
        '''Write all calculated pics to files'''

        if (self.number_of_cells() == 0):
            return

        if not self.all_pics:
            self.write_pic_with_nuclei_colored()
            return

        pic_colored_nuclei_path = os.path.join(self.dir_path,u'colored_nuclei.jpg')
        pic_merged_path         = os.path.join(self.dir_path,u'merged.jpg')
        pic_seeds_path          = os.path.join(self.dir_path,u'seeds_foci.jpg')
        pic_rescaled_foci_path  = os.path.join(self.dir_path,u'rescaled_foci.jpg')

        rescaled_nuclei_pic, nuclei_colored, rescaled_foci_pic, seeds, merged = \
                self.get_all_pics(nuclei_color, foci_color)

        imsave(pic_colored_nuclei_path, nuclei_colored)
        imsave(pic_merged_path, merged)
        imsave(pic_seeds_path, seeds)
        imsave(pic_rescaled_foci_path, rescaled_foci_pic)


    def touch_cell(self, coords):
        '''Enable or disable clicked cell'''

#        self.untouch_cells()

        y_touch, x_touch = coords

        touch = False

        for cur_cell in self.cells:
            up,down,right,left = cur_cell.coords

            if not (x_touch >= left and x_touch < right and y_touch >= down and y_touch < up):
                continue

            x_new, y_new = (x_touch - left).astype(int), (y_touch - down).astype(int)

            if not cur_cell.nucleus[x_new, y_new] == True:
                continue

            cur_cell.is_active = not cur_cell.is_active
            cur_cell.touched = True
            touch = True
            break

        return touch


    def number_of_cells(self):
        '''Return number of cells from this image_dir'''

        return len(self.cells)




def mean_and_MSE(value_list, precision = 2):
    '''Returns list with the mean value and MSE for value_list in 10-90 percentile'''

    if(len(value_list) == 0):
        if precision == 0: return [0,0]
        return [0.,0.]

    np_value_list = np.array(value_list)

    if(len(value_list) <= 4):

        new_values = np_value_list

    else:

        p10,p90 = np.percentile(np_value_list, (10,90))

        match_10_90 = np.logical_and(np_value_list >= p10, np_value_list <= p90)

        new_values = np.extract(match_10_90, np_value_list)

    mean = np.round(np.mean(new_values), precision)

    MSE = np.round(np.power(np.sum(np.power(new_values - mean, 2)/len(new_values)), 0.5), precision)

    if precision == 0:
        mean = mean.astype(np.int)
        MSE  =  MSE.astype(np.int)

    return {'Mean':mean, 'MSE':MSE}


def image_hsv_value(image_file):
    '''Returns HSV value as numpy array for image file given'''


    pic_source = img_as_ubyte(imread(image_file))

    if pic_source.ndim == 3:
        pic_grey = np.max(pic_source,2)
    else:
        pic_grey = pic_source

    return pic_grey


def find_cell_coords(nucleus):
    '''Find min and max coords = (up,down,right,left) of the cell area in the image'''

    x_sum = np.sum(nucleus,1).astype(bool)
    y_sum = np.sum(nucleus,0).astype(bool)

    x_ind = np.transpose(x_sum.nonzero())
    y_ind = np.transpose(y_sum.nonzero())

    left  = x_ind[0]
    right = x_ind[-1] + 1

    down  = y_ind[0]
    up    = y_ind[-1] + 1

    return (up, down, right, left)


def split_required(coords, min_size, x_max, y_max):
    '''Return true if cell should be split up'''

    up,down,right,left = coords
    koef = 3.5

    if at_border(coords, x_max, y_max):
        return True

    if ((up - down)*(right - left) > koef*min_size):
        return True

    return False


def at_border(coords, x_max, y_max):
    '''Return True if coords touch the border of the image'''

    up,down,right,left = coords

    if ((down == 0) or (left == 0) or (right == x_max) or (up == y_max)):
        return True

    return False

