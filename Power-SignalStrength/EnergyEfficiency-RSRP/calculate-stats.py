#!/usr/bin/python3

# Usage: python combine_dataset.py -p [data path] -s [save path]
# Example: python combine_dataset.py -t mi-vz-hb -s data/

import glob
import numpy as np
import pandas as pd
import os
import argparse
import sys

ap = argparse.ArgumentParser()
ap.add_argument("-p", "--path", help = "data path")
ap.add_argument("-s", "--save", help = "path to save the data")
ap.add_argument('-k', '--keyword', help = "keyword of the files to be included")
args = vars(ap.parse_args())

DATA_FOLDER = args["path"]
OUTPUT_FOLDER = args["save"]


# read all files names
files = glob.glob('{}*.csv'.format(DATA_FOLDER))
if args["keyword"]:
    keyword = args["keyword"]
    ex_files = [x for x in files if not keyword in x and 'lock' not in x]
    for a in ex_files:
        files.remove(a)
print(len(files), files)


dfs = list()

for idx, file in enumerate(files):
    print('Processing {}/{}'.format(idx + 1, len(files)))
    df = pd.read_csv(file)
    df = df[["Timestamp", "nrStatus", "LTE_RSRP", "nr_ssRsrp", "nr_ssSinr", "downlink_Mbps", "uplink_Mbps", "software_power", "hardware_power", "hardware_power_full"]]
    dfs.append(df)
    # dfs.append(pd.read_csv(file, names=["Timestamp", "nrStatus", "LTE_RSRP", "nr_ssRsrp", "nr_ssSinr", "downlink_Mbps", "uplink_Mbps", "software_power", "hardware_power", "hardware_power_full"]))
    # dfs.append(pd.read_csv(file, names=["nr_ssRsrp", "hardware_power_full", "nrStatus", "downlink_Mbps", "LTE_RSRP", "nr_ssSinr", "hardware_power", "software_power", "Timestamp", "uplink_Mbps"]))
    # dfs.append(pd.read_csv(file,sep='\t', encoding='utf-16', names=["nr_ssRsrp", "hardware_power_full", "nrStatus", "downlink_Mbps", "LTE_RSRP", "nr_ssSinr", "hardware_power", "software_power", "Timestamp", "uplink_Mbps"]))

# print(dfs)
data = pd.concat(dfs).to_numpy()
# print(data.shape, data)

print(data.shape)
ids = np.where(data[:,5] >= 10)
# ids = np.where(np.logical_and(data[:,5] >= 300, data[:,5] < 800))
data = data[ids,:][0]

ranges = np.arange(-110, -75, 5)

print(data.shape)
i = 1
result_lines = ["11 \"\" \"\""]
for left in ranges:
    right = left + 5
    ids = np.where(np.logical_and(data[:,3] >= left, data[:,3] < right))

    if np.shape(ids)[1] > 50:
        mean = np.mean(data[ids,9]/data[ids,5])
        var = np.std(data[ids,9]/data[ids,5])
        percent_5 = np.percentile(data[ids,9]/data[ids,5], 5)
        percent_25 = np.percentile(data[ids,9]/data[ids,5], 25)
        percent_50 = np.percentile(data[ids,9]/data[ids,5], 50)
        percent_75 = np.percentile(data[ids,9]/data[ids,5], 75)
        percent_95 = np.percentile(data[ids,9]/data[ids,5], 95)

        # print(f'{left}\t{np.shape(ids)[1]}')
        # print(f"{left}\t{mean}\t{var}")
        # print(f"[{left},{left+5})\t{i}\t{percent_5}\t{percent_25}\t{percent_50}\t{percent_75}\t{percent_95}")
        result_lines.append(f"[{left},{left+5})\t{i}\t{percent_5}\t{percent_25}\t{percent_50}\t{percent_75}\t{percent_95}")
        i += 1

if args["save"]:
    result_str = '\n'.join(result_lines)
    with open(os.path.join(args["save"], args["keyword"] + '.txt'), 'w') as f:
        f.write(result_str)
# # concat and export
# merged_data = pd.concat(dfs)
# if args["nkeyword"]:
#     keyword = args["nkeyword"]
#     merged_data.to_csv('{}/combined_ex_{}.csv'.format(OUTPUT_FOLDER, keyword), index=False, header=True)
# else:
#     merged_data.to_csv('{}/combined_all.csv'.format(OUTPUT_FOLDER), index=False, header=True)

