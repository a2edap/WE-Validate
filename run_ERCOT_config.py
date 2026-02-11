import os
import pathlib
import sys 
import shutil
import matplotlib.pyplot as plt

sys.path.append(str(pathlib.Path(os.getcwd()).parent))

# main routine of we-validate
from wevalidate_csv import compare

YEAR = 2021
directory = f'config/ERCOT_config/ERCOT_{YEAR}'

yaml_files = [f for f in os.listdir(directory) if f.endswith('.yaml')]
yaml_files_sorted = sorted(yaml_files)

for yaml_file in yaml_files_sorted:

    plant_id = yaml_file.split('_')[0] 
    
    output_dir = f'output/{YEAR}/ERCOT_PLUSWIND_yearly_hsl/{plant_id}'
    os.makedirs(output_dir, exist_ok=True)
    config_path = f'ERCOT_config/ERCOT_{YEAR}/{yaml_file}'
    print(f"Processing: {yaml_file}")
    from pandas.plotting import register_matplotlib_converters
    register_matplotlib_converters()
    compare(config_path)


DATA_FOLDER = f"output/{YEAR}/ERCOT_PLUSWIND_yearly_hsl"
PDF_OUTPUT = f"output/{YEAR}/ERCOT_reports_{YEAR}_updated"
os.makedirs(PDF_OUTPUT, exist_ok=True)

for folder in os.listdir(DATA_FOLDER):
    folder_path = os.path.join(DATA_FOLDER, folder)
    if os.path.isdir(folder_path):
        for file in os.listdir(folder_path):
            if file.lower().endswith('.pdf'):
                source_file = os.path.join(folder_path, file)
                file_name = f"{file.replace('_average', '')}"
                dest_file = os.path.join(PDF_OUTPUT, file_name)

                shutil.copy2(source_file, dest_file)
                print(f"  Copied: {file}")