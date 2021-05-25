#!/usr/bin/python3

# Usage: python combine_dataset.py -p [data path] -s [save path]
# Example: python combine_dataset.py -t mi-vz-hb -s data/

import glob
import pandas as pd
import os
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("-t", "--type", help = "experiment type")
ap.add_argument("-s", "--save", help = "path to save the data")
args = vars(ap.parse_args())

EXPR_TYPE = args["type"]
OUTPUT_FOLDER = args["save"]
DATA_FOLDER = '{}/processed_{}/'.format(OUTPUT_FOLDER, EXPR_TYPE)


# read all files names
files = glob.glob('{}*.csv'.format(DATA_FOLDER))

dfs = list()

for idx, file in enumerate(files):
    print('Processing {}/{}'.format(idx + 1, len(files)))
    dfs.append(pd.read_csv(file,names=["Timestamp", "nrStatus", "LTE_RSRP", "nr_ssRsrp", "nr_ssSinr", "downlink_Mbps", "uplink_Mbps", "software_power", "hardware_power", "hardware_power_full"]))
    basename = os.path.basename(file)
    # dfs[idx]['mlogs_filename'] = basename

############################
# concat and export
merged_data = pd.concat(dfs)
merged_data.to_csv('{}{}_combined.csv'.format(OUTPUT_FOLDER, EXPR_TYPE), index=False, header=True)

############################
