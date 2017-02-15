# -*- coding: utf-8 -*-
"""
Created on Wed Dec 21 08:51:33 2016

@author: RANN4896
"""

import pandas as pd
import numpy as np
import openpyxl as pxl
import datetime
import os
import sys
import tkinter as tk
import tkFileDialog

#==============================================================================
#                               Subroutines
#
#==============================================================================

# Specify file type
filetype = ".cog"

# list of files to cycle over
filelist = []

# Get current working directory (cwd)
cwd = os.getcwd()

# add all files andding in filetype to filelist
for file in os.listdir(cwd):
    if file.endswith(filetype):
        filelist.append(file)

#==============================================================================
#                                    Extraction
#
#==============================================================================

# Array for dfs to go into excel
summary_array = []


# Cylce through files
for files in range(len(filelist)):
    
    data_array = []
    vec_energy = []
    vec_photons = []
    vec_total = []
    vec_full = []
    
    filename = filelist[files]    
    
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

            #  Make Total spectrum file name
            o_filename  = filename.rsplit(".")[0] + "_TS.txt"

            # Open output file ('_TS')
            ofile = open(o_filename, 'w')
            
            # Write title to file
            ofile.write("C " + filename + '\n')
            
            # Write SI99 SP99, H, D
            ofile.write("#       SI99           SP99 \n")
            ofile.write("        H               D   \n")
            
            for i in range(len(vec_energy)):
                
                # Add photons and brem values together                
                vec_total.append(float(vec_photons[i]) + vec_brem[i])
            
            # Change to scientific %05E format
            for i in range(len(vec_total)):
                vec_total[i] = '%.5E' % float(vec_total[i])
            
            # Compile one two rowed array
            vec_full = np.column_stack((vec_energy, vec_total))

# !!!!!!!!!
#            print files, vec_full



            # Set float format to 5 dp scientific
            pd.set_option('display.float_format', '{:.5E}'.format)            
            
            # create dataframe
            df = pd.DataFrame(vec_full, dtype = float)
                       
            # Assign colunm names
            df.columns = [ 'Energy bin [MeV]', 'Ph/s/g']
                        
            # Add array to summary array
            summary_array.append(df)
            
#==============================================================================
#                       Extract to new file

            for i in range(len(vec_full)):
                ofile.write('      %.3e' % float(vec_full[i][0]))
                ofile.write('      %.3e' % float(vec_full[i][1]) + '\n')
            
            # Write total
            ofile.write('C Ph/s/g/:       ')
            ofile.write(str(sum(total)))
            
            # close ofile
            ofile.close()
        
# Single Dataframe of all full arrays            
RESULT = pd.concat((summary_array), keys=filelist, axis=1, copy=False)

#!!!!!!
print RESULT

# Excel summary file
xlfilename = "Summary--" + datetime.datetime.strftime(datetime.datetime.now(), '%H-%M-%S') + ".xlsx"

# opens excel
writer = pd.ExcelWriter(xlfilename)

# Write Dataframe to excel 
RESULT.to_excel(writer, "Cog_Data", float_format ='%E')

# Save new excel
writer.save()
