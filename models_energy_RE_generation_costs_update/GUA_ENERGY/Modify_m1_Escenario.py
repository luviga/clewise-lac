import subprocess
from tqdm import tqdm
import os
#

def run_model(scenario_name):

    """Run the OseMOSYS modelo for a given scenario"""

    current_path = os.getcwd()
    model_file = current_path + "/OSeMOSYS_Model.txt"
    data_file = current_path + f"/Executables/{scenario_name}_0/{scenario_name}_0.txt"
    output_file = current_path + f"/Executables/{scenario_name}_0/{scenario_name}_0_output.txt"


    # Define the glpsol command as a list of strings

    glpsol_command = ["glpsol", "-m", model_file, "-d", data_file, "-o", output_file]

    # Use subprocess to run both glpsol commands with tqdm progress tracking
    with tqdm(total=100) as pbar:
        process = subprocess.Popen(glpsol_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        while True:
            output = process.stdout.readline().decode().strip()
            if output == '' and process.poll() is not None:
                break
            if output:
                pbar.update(1)
                print(output)

        if process.returncode != 0:
            print(process.stderr.read().decode())