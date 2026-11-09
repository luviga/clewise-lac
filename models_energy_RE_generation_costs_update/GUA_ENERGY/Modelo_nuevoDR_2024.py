# -*- coding: utf-8 -*-
# Run the scenarios models and then transform to read in tableau
import os
import time


if __name__ == '__main__':
    # Measure time of execution
    start_time = time.time()

    # Load the file for scenarios
    os.system('python B1_Energy_Base_Scenarios_Adj_Parallel_mac_DR.py')
    # Measure time of execution
    print('Wait for 5 seconds to run the next file')
    time.sleep(5)
    # Run the File: To transform the results to read in tableau
    os.system('python B2_Results_Creator_f0.py')
    # Measure time of execution
    final_time = time.time()
    print('Total time of execution: ' + str((final_time - start_time)/ 60) + ' minutes')