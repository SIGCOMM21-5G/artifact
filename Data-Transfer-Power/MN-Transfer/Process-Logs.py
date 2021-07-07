#!/usr/bin/env python3

import glob
import pandas as pd

## Config
FORCE_REGENERATE_FLAG = True
EXPR_NAME = 'MN-Transfer'
LOGS_DIR = 'data'

## Read all files to combine
files = glob.glob('{}/*run*.csv'.format(LOGS_DIR))

dfs = list()

for idx, file in enumerate(files):
    print('Processing {}/{}'.format(idx + 1, len(files)))
    dfs.append(pd.read_csv(file))

## concat and export
merged_data = pd.concat(dfs)
columns_to_select = ['throughput', 'time_since_start', 'avg_power',
                     'target bandwidth', 'direction', 'network type', 'provider']
merged_data = merged_data[columns_to_select]
merged_data.sort_values(by=['network type', 'direction', 'target bandwidth'], inplace=True)
merged_data.to_csv('{}/{}_combined.csv'.format('data-processed', EXPR_NAME), index=False, header=True)

print('Complete./')
