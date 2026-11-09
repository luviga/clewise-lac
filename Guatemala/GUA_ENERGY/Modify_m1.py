import subprocess
from tqdm import tqdm
import os
#

def models():

    """It Worked"""

    # BAU model
    current_path = os.getcwd()
    model_file = current_path + "/OSeMOSYS_Model.txt"
    data_file_1 = current_path + "/Executables/BAU_0/BAU_0.txt"
    output_file_1 = current_path + "/Executables/BAU_0/BAU_0_output.txt"


    # Define the glpsol command as a list of strings
    glpsol_command_1 = ["glpsol", "-m", model_file, "-d", data_file_1, "-o", output_file_1]

    # NDP model 2
    data_file_2 = current_path + "/Executables/NDP_0/NDP_0.txt"
    output_file_2 = current_path + "/Executables/NDP_0/NDP_0_output.txt"

    # Define the glpsol command as a list of strings
    glpsol_command_2 = ["glpsol", "-m", model_file, "-d", data_file_2, "-o", output_file_2]

    # Use subprocess to run both glpsol commands with tqdm progress tracking
    with tqdm(total=200) as pbar:
        # Run the first glpsol command
        process_1 = subprocess.Popen(glpsol_command_1, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        while True:
            output = process_1.stdout.readline().decode().strip()
            if output == '' and process_1.poll() is not None:
                break
            if output:
                pbar.update(1)
                print(output)

        if process_1.returncode != 0:
            print(process_1.stderr.read().decode())

        # Run the second glpsol command
        process_2 = subprocess.Popen(glpsol_command_2, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        while True:
            output = process_2.stdout.readline().decode().strip()
            if output == '' and process_2.poll() is not None:
                break
            if output:
                pbar.update(1)
                print(output)

        if process_2.returncode != 0:
            print(process_2.stderr.read().decode())
