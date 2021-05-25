#!/usr/bin/python3
import glob
import pandas as pd
from os import path

## Dataset Organization
proj_dir = path.abspath(path.join(path.dirname(__file__)))
data_dir = path.join(proj_dir, 'data')
data_processed_dir = path.join(proj_dir, 'data-processed')

## Config
EXPR_TYPE = 'MN-Power-Wild'
OUTPUT_FOLDER = data_processed_dir
DATA_FOLDER = path.join(OUTPUT_FOLDER, 'merged-logs')

# read all files names
files = glob.glob(path.join(DATA_FOLDER, '*.csv'))

dfs = list()

for idx, file in enumerate(files):
    print('Processing {}/{}'.format(idx + 1, len(files)))
    dfs.append(pd.read_csv(file))

############################
# concat and export
merged_data = pd.concat(dfs)
merged_data.to_csv(path.join(OUTPUT_FOLDER, f"{EXPR_TYPE}_combined.csv"), index=False, header=True)
print('Complete./')
