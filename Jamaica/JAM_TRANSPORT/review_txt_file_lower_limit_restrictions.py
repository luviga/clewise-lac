# -*- coding: utf-8 -*-
"""
Created on Tue May 28 14:28:39 2024

@author: luisfernando
"""

import os
import pandas as pd
import sys
from copy import deepcopy
import re
import pickle


def read_parameters(file_path, parameter_name):
    data = {}  # This dictionary will store the extracted data
    years = []  # This list will store the years

    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Search for the parameter definition
    start_index = -1
    for i, line in enumerate(lines):
        if f"param {parameter_name} default" in line:
            # Find the line containing the years, assumed to be two lines after the definition
            years_line = lines[i + 2]
            # Clean the years line and convert to a list of integers
            years = [int(year) for year in re.findall(r'\d{4}', years_line)]
            start_index = i + 3
            break
    
    if start_index == -1:
        print(f"The restriction {parameter_name} was not found.")
        return pd.DataFrame()

    # Search and capture values for technologies until a ';' is found
    for line in lines[start_index:]:
        if line.strip() == ';':
            break
        elements = line.split()
        technology = elements[0]
        values = list(map(float, elements[1:]))  # Convert the values to float
        data[technology] = values

    # Convert the dictionary to a pandas DataFrame for easier manipulation
    return pd.DataFrame(data, index=years).T  # Transpose so that technologies are rows and years are columns

##
# Let us iterate across scenarios for the debugging

# scenarios = ['BAU', 'NDP']
scenarios = ['NDP']

for scen in scenarios:
    print('\n###################')
    print(scen)
    print('\n')

    future = '0'
    file_path = f'Executables\{scen}_{future}\{scen}_{future}.txt'
    file_names = ['TotalTechnologyAnnualActivityUpperLimit', 'TotalTechnologyAnnualActivityLowerLimit', 'TotalAnnualMaxCapacity','ResidualCapacity']

    for i in range(len(file_names)):
        # Take techs defined for the parameter
        result = read_parameters(file_path, file_names[i])  # Make sure parameter is defined

        # Only to check the technologies have this parameter
        if file_names[i] == 'ResidualCapacity' and scen == 'NDP' and future == 1:
            df_residual_capacity = deepcopy(result)
        if file_names[i] == 'TotalTechnologyAnnualActivityUpperLimit':
            df_upper_techs = deepcopy(result)
        elif file_names[i] == 'TotalTechnologyAnnualActivityLowerLimit':
            df_lower_techs = deepcopy(result)
        elif file_names[i] == 'TotalAnnualMaxCapacity':
            df_maxcapa_techs = deepcopy(result)
        elif file_names[i] == 'ResidualCapacity':
            df_resicapa_techs = deepcopy(result)

    # Perform tests here - TEST 1:
    common_techs = df_maxcapa_techs.index.intersection(df_lower_techs.index)
    common_techs_tr = [tech for tech in common_techs if 'PP' not in tech[:2]] 
    for tech in common_techs_tr:
        # for year in parameter.columns:
        param_maxcap = df_maxcapa_techs.loc[tech].tolist()
        param_lowerlimit = df_lower_techs.loc[tech].tolist()
       
        diff_list = [a - b for a, b in zip(param_maxcap, param_lowerlimit)]
        # Check if there are any negative values in the list
        has_negative = any(diff < 0 for diff in diff_list)
        
        print(tech, has_negative)
        if has_negative:
            print(param_maxcap)
            print(param_lowerlimit)
            print(diff_list)
            print('\n')

    # Perform tests here - TEST 2:
    # Open A-O Fleet Gorups
    aofleet_path = f'A1_Outputs\A-O_Fleet_Groups.pickle'

    # Open the pickle file
    with open(aofleet_path, 'rb') as file:
        data_aofleet = pickle.load(file)
        
        # Test 2a
        # For every key of the dictionary, get the lower limit
        # Then, sum the max capacity of the daughters
        list_momtechs = list(data_aofleet.keys())
        
        for momtech in list(data_aofleet.keys()):
            daughter_techs = data_aofleet[momtech]
            '''
            row_lowlim_mom = df_lower_techs.loc[df_lower_techs.index.str.contains(momtech)]



            list_maxcap_ds = [0]*len(row_lowlim_mom)            
            for d in daughter_techs:
                row_maxcap_d = df_maxcapa_techs.loc[df_maxcapa_techs.index.str.contains(d)].tolist()
                list_maxcap_ds = [a + b for a, b in zip(list_maxcap_ds, row_maxcap_d)]

            diff_list_2a = [a - b for a, b in zip(row_lowlim_mom, list_maxcap_ds)]
            '''

            # Test 2b
            # For every key of the dictionary, get the max capacity
            # Then, sum the lower limit of the daughters
            row_maxcap_mom = df_maxcapa_techs.loc[df_maxcapa_techs.index.str.contains(momtech)].values.tolist()[0]

            list_lowlim_ds = [0]*len(row_maxcap_mom)      
            d_without_ll = []
            for d in daughter_techs:
                try:
                    row_lowlim_d = df_lower_techs.loc[df_lower_techs.index.str.contains(d)].values.tolist()[0]
                    list_lowlim_ds = [a + b for a, b in zip(list_lowlim_ds, row_lowlim_d)]
                except Exception:
                    print('No lower limit', d)
                    d_without_ll.append(d)

            diff_list_2b = [a - b for a, b in zip(row_maxcap_mom, list_lowlim_ds)]
            has_negative = any(diff < 0 for diff in diff_list_2b)

            print('\n')
            print(momtech)
            if has_negative:
                print(diff_list_2b)


            # Test 2c: check if anyone has a max capacity greater than the lower limit
            for d in daughter_techs:
                if d not in d_without_ll:
                    try:
                        row_maxcap_d = df_maxcapa_techs.loc[df_maxcapa_techs.index.str.contains(d)].values.tolist()[0]
                        row_lowlim_d = df_lower_techs.loc[df_lower_techs.index.str.contains(d)].values.tolist()[0]
                        diff_list_2c = [a - b for a, b in zip(row_maxcap_d, row_lowlim_d)]
                        has_negative = any(diff < 0 for diff in diff_list_2c)
                        print('-', d)
                        if has_negative:
                            print(diff_list_2c)
                    except Exception:
                        print('No max capacity', d)

            # print('check up until here')
            # sys.exit()

    # print('check up until here 2')
    # sys.exit()
