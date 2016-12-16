# -*- coding: utf-8 -*-
"""
Created on Thu Dec 15 13:15:59 2016

@author: m_user
"""

import pandas as pd
import numpy as np
import sys
import os
import Tkinter
import tkFileDialog

# ==========================================================================

# ==========================================================================

data_array = []
vec_energy = []
vec_photons = []

# add initial 0.00 value to arrays
vec_photons.append(0.00)

# Tkinter.Tk().withdraw() # Close the root window
# filepath = tkFileDialog.askopenfilename()

filename = 'Cog_file.cog'

afile = open(filename, 'r')

# import cog file to an array 'Data_array'
for line in afile:
    data_array.append(line)
     
# Find the start of the spectra
for i in range(len(data_array)):
    if data_array[i] == '     DEFINE ENERGY =   1  PHOTON\n':
        
        # obatin number of photon bins
        # select Bin line
        holder = data_array[i+1]
        
        # split line by spaces
        holder = holder.rsplit(" ")
    
        # select number of Photon bins        
        num_ph = int(holder[-2])
        
        # move data_array to Bin line
        i += 1
        
        #
        for n in range(1, num_ph + 2):
            
            # move to first line of spectrum
            holder = data_array[i+n].rsplit(" ")
          
            # add energy bins to vector
            vec_energy.append(holder[2])
            # add photons to photon vector
            vec_photons.append(holder[-1])
            
        #     
        vec_brem = np.zeros(len(vec_energy))    
        
        # bring i back to Brem Bin number
        i = i + num_ph + 7
        
        # PRINT
#        print i, data_array[i]
        
        # obatin number of brem bins
        # select Bin line
        holder = data_array[i].rsplit(" ")
            
        # select number of Photon bins        
        num_br = int(holder[-2])
        
        # move to first energy bin value
        i += 1
        
        # add values for brem to vector
        for n in range(0,num_br):
            vec_brem[1+n] = data_array[i + n].rsplit(" ")[-1]
        
        # blank final array
        vec_output = np.zeros((len(vec_energy),2)) 

        # add values to array
        for n in range(len(vec_energy)):
            vec_output[n][0] = vec_energy[n] 
            vec_output[n][1] = float(vec_photons[n]) + vec_brem[n]
 
        # outpt filename       
        out_filename = filename.rsplit(".")[0] + "_TS.txt"
        
        # print summed spectra to txt file
        np.savetxt(out_filename, vec_output , fmt="%2e", delimiter=' ')