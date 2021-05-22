#!/usr/bin/python3
import glob
import pandas as pd
import os
from set_paths import *

EXPR_TYPE = 'MN-Walking-Iperf'
DATA_FOLDER = '{}{}/merged-logs/'.format(OUTPUT_FOLDER, EXPR_TYPE)

# read all files names
files = glob.glob('{}*.csv'.format(DATA_FOLDER))

dfs = list()

for idx, file in enumerate(files):
    print('Processing {}/{}'.format(idx + 1, len(files)))
    dfs.append(pd.read_csv(file))
    basename = os.path.basename(file)
    dfs[idx]['mlogs_filename'] = basename

############################
# concat and export
merged_data = pd.concat(dfs)
merged_data.to_csv('{}{}_combined.csv'.format(OUTPUT_FOLDER, EXPR_TYPE), index=False, header=True)

############################
