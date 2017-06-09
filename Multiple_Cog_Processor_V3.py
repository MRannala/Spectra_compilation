# -*- coding: utf-8 -*-
"""
Created on Tue Jun  6 10:51:32 2017

@author: RANN4896
"""

import pandas as pd
import numpy as np
import openpyxl as pxl
import datetime
import os
import sys
# import tkinter as tk
# import tkFileDialog

#==============================================================================
#                               Subroutines
#
#==============================================================================

def get_files(filetype):
    
    filelist = []
   
    # Get current working directory (cwd)
    cwd = os.getcwd()
    for file in os.listdir(cwd):
        if file.endswith(filetype):
            filelist.append(file)

    if len(filelist) == 0:
        print("No {0} type file found! \nScript terminated!".format(filetype))
        #Quit
    
    return filelist

def make_array(file_name):
    
    # open file
    afile = open(file_name, 'r')
    
    data = []

    for lines in afile:
        data.append(lines)
        
    return data
      
def find_X(data, var):
    
    v_index = False
    
    for i in range(len(data)):
        linetext = data[i].split()
        if len(linetext) > 0:
            if linetext[0].lower().startswith(var):
                v_index = i
                
    return v_index
    
def add_photon_info(data, start_ind):
    
    vec_energy = []
    vec_int    = []

     # Add first energy bin value
    vec_energy.append(data[start_ind].split()[0])
    
    # Add balnk for first bin
    vec_int.append(0.00)

    # Add first intensity value
    vec_int.append(data[start_ind].split()[1])
    
    i = start_ind + 1
    
    # do until line starts with a '$'
    while data[i].split()[0] != '$':
        vec_energy.append(data[i].split()[0])
 
        # if a corresponding intensity values available, add it
        if len(data[i].split()) > 1:
            vec_int.append(data[i].split()[1])
            
        i += 1
    
    return vec_energy, vec_int

def make_output_file(filename, df):
          
            # Provide only numeric sum from data frame
            total = df.sum(numeric_only=True).sum()
            
            #  Make Total spectrum file name
            o_filename  = filename.rsplit(".")[0] + ".spec"

            # Open output file ('_TS')
            ofile = open(o_filename, 'w')
            
            # Write title to file
            ofile.write("C " + filename + '\n')
            
            # Write SI99 SP99, H, D
            ofile.write("#       SI99           SP99 \n")
            ofile.write("        H               D   \n")
            
            # make the header a, b
            df.columns = ['b']

            # df of top row
            top = df[:1]

            # supress rows with zero
            df = df[df.b != 0]

            # concatonate the top row and filtered df
            df = pd.concat([top,df])
                        
            # add 5 spaces before text and remove header row
            df = " "*6 + df.to_string(header = True).replace("\n", "\n      ")
            
            # write to file
            ofile.write(df + '\n')
            
            # Write number of photons/s/g
            ofile.write('C Ph/s/g/:       {:.8E}'.format(total))
 
    
if __name__ == '__main__':
    
    # Record file
    infile = open('inert.txt', 'w')
    infile.write('Inert Materials\n')
    rfile = open('Record.txt','w')

    # Set pandas output default as % d.p. scientific with E
    pd.options.display.float_format = '{:.5E}'.format
        
    cog_files = get_files('.cog')
   
    # make iterable 
    cog_files = iter(cog_files)
    
    for i in cog_files:
        
        # file to record throughput
        rfile.write(i+'\n')
   
        data = make_array(i)
        
        # check if photo spectrum available 
        if find_X(data,'define') == False:
            
            print("No photon spectrum found, inert material.  " + i.split('.')[0])
            
            # write to inert register
            infile.write(i.split('.')[0]+'\n')
            
        else:
                                      
            # find 'DEFINE ENERGY' index
            ph_start = find_X(data,'define')
        
            # find number of direct photon bins
            ph_bin = data[ph_start + 1].split()[-2]

            # get direct photon spectrum
            ph_eng_bin, ph_int_bin = add_photon_info(data, ph_start+2)
                    
            # make data frame with index as energies
            ph_df = pd.DataFrame(ph_int_bin, dtype = float, index=ph_eng_bin)
           
            # Check for Bremmstrahlung spectrum            
            if find_X(data, 'sc') == False:
                
                # Set output to photon spectrum
                output_df = ph_df
                
                # Write output file
                make_output_file(i, output_df)
            
            # Check for Bremmstrahlung spectrum
            elif find_X(data, 'sc') != False:

                # find index of sc line
                brem_ind = find_X(data,'sc')
                
                # get direct photon spectrum
                br_eng_bin, br_int_bin = add_photon_info(data, brem_ind+1)
                
                # add 
                # make data frame with index as energies
                br_df = pd.DataFrame(br_int_bin, dtype = float, index=br_eng_bin)
               
                # combine total output
                holder = [ph_df, br_df]

                output_df = pd.concat(holder)

                output_df = output_df.groupby(output_df.index, sort=False).sum()

                # Write output file
                make_output_file(i, output_df)
                   
    rfile.close()
    infile.close()