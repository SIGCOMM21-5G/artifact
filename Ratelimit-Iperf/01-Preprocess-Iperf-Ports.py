#!/usr/bin/env python3

import os
import glob
import json
import pandas as pd
import numpy as np
from os import path

import context

__author__ = "Ahmad Hassan"

## Config
FORCE_REGENERATE_FLAG = True
EXPR_NAME = 'Ratelimit-Iperf'
DATA_DIR = path.join(context.data_dir, EXPR_NAME)
SERVER_LOGS_DIR = path.join(DATA_DIR, 'server')
CLIENT_LOGS_DIR = path.join(DATA_DIR, 'client')
OUTPUT_LOGS_DIR = context.data_processed_dir
EXPR_SUMMARY_FILE = path.join(DATA_DIR, EXPR_NAME + '.csv')

## Load summary files
expr_summary = pd.read_csv(EXPR_SUMMARY_FILE)
filtered_summary = expr_summary[(expr_summary['iperf run number'].notna()) &
                                (expr_summary['successful?'] == 'yes')].copy(deep=True)
filtered_summary['iperf run number'] = filtered_summary['iperf run number'].astype(np.int)
filtered_summary.reset_index(inplace=True, drop=True)

## Get ports and save in a file
port_list = list()
for idx, row in filtered_summary.iterrows():
    if row['month'] == 'dec' and (row['iperf type'] == 'tcp1d' or row['iperf type'] == 'tcp1c'):
        print('[PROCESSING RUN]: {}  ({}/{})'.format(row['iperf run number'], idx + 1, filtered_summary.shape[0]))
        server_iperf_file = glob.glob('{}/*{}*.json'.format(SERVER_LOGS_DIR, row['iperf run number']))[0]
        with open(server_iperf_file) as fd:
            parsed_file = json.load(fd)
        server_port = parsed_file['start']['connected'][0]['remote_port']
        client_iperf_file = glob.glob('{}/*{}*.json'.format(CLIENT_LOGS_DIR, row['iperf run number']))[0]
        fd.close()
        with open(client_iperf_file) as fd:
            parsed_file = json.load(fd)
        client_port = parsed_file['start']['connected'][0]['local_port']
        fd.close()
        port_list.append([row['iperf run number'], server_port, client_port])

## If output directory doesn't exist
if not os.path.exists(OUTPUT_LOGS_DIR):
    os.makedirs(OUTPUT_LOGS_DIR)
    print('Directory created: {}'.format(OUTPUT_LOGS_DIR))

df = pd.DataFrame(port_list)
df.to_csv('{}/{}-Iperf-Ports.csv'.format(OUTPUT_LOGS_DIR, EXPR_NAME), index=False,
          header=['iperf run number', 'Server Port', 'Client Port'])
print('Complete./')
