#!/usr/bin/python3
import os
import pandas as pd
import numpy as np
from os import path

## Dataset Organization
proj_dir = path.abspath(path.join(path.dirname(__file__)))
data_dir = path.join(proj_dir, 'data')
data_processed_dir = path.join(proj_dir, 'data-processed')

## Start of Config
DEVICES = ['S20UPM']
DATA_DIR = data_dir
OUTPUT_DIR = data_processed_dir

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
    print('Directory created: {}'.format(OUTPUT_DIR))

## runs and labels
run_list = ['112', '107', '108', '109', '110']
labels = ['NSA', 'SA+LTE', 'SA', 'LTE', 'ALL']

for i in range(len(run_list)):
    print('=======================================================================')
    print('  processing run: {}  ({}/{})'.format(run_list[i], i + 1, len(run_list)))

    handoff_file = '{}/{}-run{}-handoff.csv'.format(DATA_DIR, DEVICES[0], run_list[i])
    handoff_logs = pd.read_csv(handoff_file, dtype={'time': float, 'active interface': str, 'handover type': str})

    ## Process PM logs
    pm_file = '{}/{}-run{}_PM.csv'.format(DATA_DIR, DEVICES[0], run_list[i])
    header_list = ["time", "avg_power"]
    pm_logs = pd.read_csv(pm_file, names=header_list, skiprows=1)
    bins = range(int(pm_logs['time'].min()), int(pm_logs['time'].max()))
    pm_logs['r_time'] = pd.cut(pm_logs['time'], bins=bins, labels=bins[:-1], include_lowest=True)
    pm_grp = pm_logs.groupby('r_time').agg(avg_power=('avg_power', np.mean))
    pm_grp.reset_index(level=0, inplace=True)
    pm_grp = pm_grp.rename(columns={'r_time': 'time'})

    ## Merge 5GTracker and PM Logs and save logs
    mrg_logs = pd.merge(pm_grp, handoff_logs, on='time', how='outer')
    mrg_logs[mrg_logs['active interface'] == ""] = np.NaN
    mrg_logs[['active interface']] = mrg_logs[['active interface']].fillna(method='ffill')

    out_name = '{}/run{}.csv'.format(OUTPUT_DIR, run_list[i])
    mrg_logs.to_csv(out_name, header=True, index=False)
