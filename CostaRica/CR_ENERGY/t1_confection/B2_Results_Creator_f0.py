# -*- coding: utf-8 -*-
# Suggested Citation:
# Victor-Gallardo, L. (2022). Robust Energy System Planning for Decarbonization under Technological Uncertainty.
# Retrieved from https://www.kerwa.ucr.ac.cr/handle/10669/87273

"""
Modified version with:
1. Flexible config path detection
2. Scenario selection capability
"""

from datetime import date
import sys
import pandas as pd
import os
from copy import deepcopy
import csv
import numpy as np
import yaml
import platform

sys.path.insert(0, 'Executables')
import local_dataset_creator_0

# =============================================================================
# USER CONFIGURATION - MODIFY THESE AS NEEDED
# =============================================================================

# Specify scenarios to process (leave empty to process all)
# Example: SELECTED_SCENARIOS = ['BAU', 'NZE', 'LTS']
SELECTED_SCENARIOS = []  # Empty list = process all scenarios

# Set to False if you've already run the dataset creator and just want to process existing results
RUN_FOR_FIRST_TIME = True

# =============================================================================
# PATH FUNCTIONS
# =============================================================================

def get_config_main_path(full_path, base_folder='config_main_files'):
    """
    Find the config_main_files folder. 
    Strategy: Look for the folder one level up from the current script location.
    """
    # First, try the parent directory approach (config_main_files is just outside script location)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    
    # Check if config_main_files exists in parent directory
    config_in_parent = os.path.join(parent_dir, base_folder)
    if os.path.exists(config_in_parent):
        print(f"[INFO] Found config folder at: {config_in_parent}")
        return config_in_parent
    
    # Check if config_main_files exists in same directory as script
    config_in_same = os.path.join(script_dir, base_folder)
    if os.path.exists(config_in_same):
        print(f"[INFO] Found config folder at: {config_in_same}")
        return config_in_same
    
    # Fallback: Try the original approach with path splitting
    parts = full_path.split(os.sep)
    
    # Try to find common project folder names
    common_names = ['ndc_cr_30', 'MODELS_LAC', 'OSeMOSYS', 'model', 'project']
    target_index = None
    
    for name in common_names:
        if name in parts:
            target_index = parts.index(name)
            break
    
    if target_index is not None:
        base_path = os.sep.join(parts[:target_index + 1])
        appended_path = os.path.join(base_path, base_folder)
        if os.path.exists(appended_path):
            print(f"[INFO] Found config folder at: {appended_path}")
            return appended_path
    
    # Last resort: use provided path
    print(f"[WARNING] Could not find {base_folder}. Using: {os.path.join(full_path, base_folder)}")
    return os.path.join(full_path, base_folder)


def load_and_process_yaml(path):
    """
    Load a YAML file and replace the specific placeholder '${year_apply_discount_rate}' 
    with the year specified in the file.
    """
    with open(path, 'r') as file:
        params = yaml.safe_load(file)

    reference_year = str(params['year_apply_discount_rate'])

    def update_strings(obj):
        if isinstance(obj, dict):
            return {k: update_strings(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [update_strings(element) for element in obj]
        elif isinstance(obj, str):
            return obj.replace('${year_apply_discount_rate}', reference_year)
        else:
            return obj

    updated_params = update_strings(params)
    return updated_params


# =============================================================================
# SCENARIO FILTERING FUNCTION
# =============================================================================

def filter_dataframe_by_scenarios(df, scenarios, scenario_column='Strategy'):
    """
    Filter a dataframe to only include specified scenarios.
    Tries common column names for scenario identification.
    """
    if not scenarios:
        return df
    
    # Try common scenario column names
    possible_columns = ['Strategy', 'Scenario', 'Future.ID', 'SCENARIO', 'STRATEGY']
    
    for col in possible_columns:
        if col in df.columns:
            # Check if any scenarios match values in this column
            matching = df[df[col].astype(str).isin(scenarios)]
            if len(matching) > 0:
                print(f"[INFO] Filtered by column '{col}': {len(matching)} rows from {len(df)}")
                return matching
    
    print(f"[WARNING] Could not filter by scenarios. Returning full dataset.")
    return df


# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    
    # Read yaml file with parameterization
    file_config_address = get_config_main_path(os.path.abspath('../'))
    
    yaml_path = os.path.join(file_config_address, 'MOMF_B1_exp_manager.yaml')
    if os.path.exists(yaml_path):
        params = load_and_process_yaml(yaml_path)
    else:
        print(f"[ERROR] Config file not found: {yaml_path}")
        print("[INFO] Using default parameters...")
        params = {'solver': 'cbc', 'glpk_option': 'new'}
    
    # For macOS system delete a hidden folder
    if platform.system() == 'Darwin':
        ds_store = os.path.join('Executables', '.DS_Store')
        if os.path.exists(ds_store):
            os.remove(ds_store)
    
    # Get region from model structure
    if os.path.exists('B1_Model_Structure.xlsx'):
        df_structure = pd.read_excel('B1_Model_Structure.xlsx')
        region_str = df_structure['REGION'].dropna().iloc[-1]
    else:
        print("[WARNING] B1_Model_Structure.xlsx not found. Using default region 'REGION'")
        region_str = 'REGION'
    
    file_name_suffix = 'f0_OSMOSYS_' + region_str + '_'
    
    # Show selected scenarios
    if SELECTED_SCENARIOS:
        print(f"\n[INFO] Processing selected scenarios: {SELECTED_SCENARIOS}")
    else:
        print("\n[INFO] Processing ALL scenarios (no filter applied)")
    
    # Run dataset creator if needed
    if RUN_FOR_FIRST_TIME:
        print("\n[INFO] Running local_dataset_creator_0...")
        local_dataset_creator_0.execute_local_dataset_creator_0_outputs()
        local_dataset_creator_0.execute_local_dataset_creator_0_inputs()
    
    # Process outputs
    print("\n[INFO] Processing output data...")
    path_output_0 = os.path.join('Executables', 'output_dataset_0.csv')
    
    if os.path.exists(path_output_0):
        df_0_output = pd.read_csv(path_output_0, index_col=None, header=0, low_memory=False)
        li_output = [df_0_output]
        df_output = pd.concat(li_output, axis=0, ignore_index=True)
        
        # Sort based on solver configuration
        if params.get('solver') == 'glpk' and params.get('glpk_option') == 'old':
            df_output.sort_values(by=['Future.ID', 'Fuel', 'Technology', 'Emission', 'Year'], inplace=True)
        else:
            sort_cols = [c for c in ['FUEL', 'TECHNOLOGY', 'EMISSION', 'YEAR'] if c in df_output.columns]
            if sort_cols:
                df_output.sort_values(by=sort_cols, inplace=True)
        
        # Filter by selected scenarios
        if SELECTED_SCENARIOS:
            df_output = filter_dataframe_by_scenarios(df_output, SELECTED_SCENARIOS)
    else:
        print(f"[ERROR] Output file not found: {path_output_0}")
        df_output = pd.DataFrame()
    
    # Process inputs
    print("[INFO] Processing input data...")
    path_input_0 = os.path.join('Executables', 'input_dataset_0.csv')
    
    if os.path.exists(path_input_0):
        df_0_input = pd.read_csv(path_input_0, index_col=None, header=0, low_memory=False)
        li_input = [df_0_input]
        df_input = pd.concat(li_input, axis=0, ignore_index=True)
        
        sort_cols = [c for c in ['Future.ID', 'Strategy.ID', 'Strategy', 'Fuel', 'Technology', 
                                  'Emission', 'Season', 'Year'] if c in df_input.columns]
        if sort_cols:
            df_input.sort_values(by=sort_cols, inplace=True)
        
        # Filter by selected scenarios
        if SELECTED_SCENARIOS:
            df_input = filter_dataframe_by_scenarios(df_input, SELECTED_SCENARIOS)
    else:
        print(f"[ERROR] Input file not found: {path_input_0}")
        df_input = pd.DataFrame()
    
    # Save results
    print("\n[INFO] Saving results...")
    today = date.today()
    
    if not df_output.empty:
        output_file = f'{region_str}Output.csv'
        output_file_dated = f'{region_str}Output_{str(today).replace("-", "_")}.csv'
        df_output.to_csv(output_file, index=None, header=True)
        df_output.to_csv(output_file_dated, index=None, header=True)
        print(f"  Saved: {output_file} ({len(df_output)} rows)")
    
    if not df_input.empty:
        input_file = f'{region_str}Input.csv'
        input_file_dated = f'{region_str}Input_{str(today).replace("-", "_")}.csv'
        df_input.to_csv(input_file, index=None, header=True)
        df_input.to_csv(input_file_dated, index=None, header=True)
        print(f"  Saved: {input_file} ({len(df_input)} rows)")
    
    print("\n[DONE] Results processing complete!")
