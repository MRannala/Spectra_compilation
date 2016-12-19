# -*- coding: utf-8 -*-
"""
Created on Thu Dec 15 13:15:59 2016
This script will combine the photon spectra due to direct and bremsstrahlung photons from a .COG file to produce a single spectrum 
that can be used within an MCNP input file.

@author: Magnus Rannala
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

# user inputs filename
print "Please Select .Cog File: "

# Open interactive window
filepath = tkFileDialog.askopenfilename()
filename = filepath.split('/')
filename = filename[-1]

# Test if file name exists and exit if not
if os.path.isfile(filename) == False:
    print " "
    print "No Such File in Directory! "    
    print " "
    sys.exit()
else:
    pass

# filename = 'Cog_file.cog'

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

        # For sum of photons
        total = []

        # add values to array
        for n in range(len(vec_energy)):
            vec_output[n][0] = vec_energy[n] 
            vec_output[n][1] = float(vec_photons[n]) + vec_brem[n]
            total.append(float(vec_photons[n]) + vec_brem[n])
                           
        Last = "Ph/s/g:       " + str(int(round(sum(total))))
        
        # outpt filename       
        out_filename = filename.rsplit(".")[0] + "_TS.txt"
        
        # print summed spectra to txt file
        np.savetxt(out_filename, vec_output , fmt="%2e", header = "Energy Bin [MeV]    Photon Intensity", footer = Last, delimiter=' ')
