# -*- coding: utf-8 -*-
# Run the scenarios models and then transform to read in tableau
import os
import time
import shutil

def clear_directory(directory):
    """
    Delete all files in the given directory without removing subdirectories.
    """
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")

def copy_directory(src, dst):
    """
    Copy the entire directory from src to dst.
    """
    try:
        if os.path.exists(dst):
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        print(f"Directory {src} copied to {dst}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    # Measure time of execution
    start_time = time.time()

    # Load the file for scenarios
    os.system('python A2_Compiler.py')
    # Measure time of execution
    print('Wait for 5 seconds to run the next file')

    current_path = os.getcwd()
    source_directory = current_path + "/A2_Output_Params"
    destination_directory = current_path + '/B1_Output_Params'
    copy_directory(source_directory, destination_directory)
    final_time = time.time()
    print('Total time of execution: ' + str((final_time - start_time) / 60) + ' minutes')