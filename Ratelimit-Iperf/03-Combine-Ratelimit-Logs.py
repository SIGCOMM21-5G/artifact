#!/usr/bin/env python3

import glob
import pandas as pd
from os import path

import context

__author__ = "Ahmad Hassan"

## Config
FORCE_REGENERATE_FLAG = True
EXPR_NAME = 'Ratelimit-Iperf'
OUTPUT_LOGS_DIR = context.data_processed_dir
OUTPUT_CC_LOGS_DIR = path.join(OUTPUT_LOGS_DIR, 'Merged-Logs')

## Read all files to combine
files = glob.glob('{}/*.csv'.format(OUTPUT_CC_LOGS_DIR))  # just combining server files

dfs = list()

for idx, file in enumerate(files):
    print('Processing {}/{}'.format(idx + 1, len(files)))
    dfs.append(pd.read_csv(file))

## concat and export
merged_data = pd.concat(dfs)
merged_data.sort_values(by='run', inplace=True)
merged_data.to_csv('{}/{}_detail-combined.csv'.format(OUTPUT_LOGS_DIR, EXPR_NAME), index=False, header=True)

print('Complete./')
