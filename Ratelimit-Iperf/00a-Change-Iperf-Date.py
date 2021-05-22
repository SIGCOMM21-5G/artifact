#!/usr/bin/env python3

import dateutil.relativedelta
from datetime import datetime
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
for idx, row in filtered_summary.iterrows():
    if row['month'] == 'dec':
        print('[PROCESSING RUN]: {}  ({}/{})'.format(row['iperf run number'], idx + 1, filtered_summary.shape[0]))

        ## Server File
        server_iperf_file = glob.glob('{}/*{}*.json'.format(SERVER_LOGS_DIR, row['iperf run number']))[0]
        server_out_file = path.join(context.data_processed_dir, 'server', path.basename(server_iperf_file))
        with open(server_iperf_file, 'r') as fd:
            parsed_file = json.load(fd)
            fd.close()
        timestamp = parsed_file['start']['timestamp']
        old_time = datetime.strptime(timestamp['time'], "%a, %d %b %Y %H:%M:%S %Z")
        new_time = old_time - dateutil.relativedelta.relativedelta(months=4)
        timestamp['time'] = new_time.strftime("%a, %d %b %Y %H:%M:%S %Z")
        old_time_utc = datetime.utcfromtimestamp(timestamp['timesecs'])
        new_time_utc = old_time_utc - dateutil.relativedelta.relativedelta(months=4)
        timestamp['timesecs'] = new_time_utc.timestamp()
        system_info = parsed_file['start']['system_info'].split()
        system_info[-2] = '2020'
        parsed_file['start']['system_info'] = " ".join(system_info)
        with open(server_out_file, 'w') as fd:
            json.dump(parsed_file, fd)
            fd.close()

        ## Client File
        client_iperf_file = glob.glob('{}/*{}*.json'.format(CLIENT_LOGS_DIR, row['iperf run number']))[0]
        client_out_file = path.join(context.data_processed_dir, 'client', path.basename(client_iperf_file))
        with open(client_iperf_file, 'r') as fd:
            parsed_file = json.load(fd)
            fd.close()
        timestamp = parsed_file['start']['timestamp']
        old_time = datetime.strptime(timestamp['time'], "%a, %d %b %Y %H:%M:%S %Z")
        new_time = old_time - dateutil.relativedelta.relativedelta(months=4)
        timestamp['time'] = new_time.strftime("%a, %d %b %Y %H:%M:%S %Z")
        old_time_utc = datetime.utcfromtimestamp(timestamp['timesecs'])
        new_time_utc = old_time_utc - dateutil.relativedelta.relativedelta(months=4)
        timestamp['timesecs'] = new_time_utc.timestamp()
        system_info = parsed_file['start']['system_info'].split()
        system_info[-2] = '2020'
        parsed_file['start']['system_info'] = " ".join(system_info)
        with open(client_out_file, 'w') as fd:
            json.dump(parsed_file, fd)
            fd.close()
    else:
        print('[COPYING RUN]: {}  ({}/{})'.format(row['iperf run number'], idx + 1, filtered_summary.shape[0]))

        ## Client File
        client_iperf_file = glob.glob('{}/*{}*.json'.format(CLIENT_LOGS_DIR, row['iperf run number']))[0]
        client_out_file = path.join(context.data_processed_dir, 'client', path.basename(client_iperf_file))
        with open(client_iperf_file, 'r') as fd:
            parsed_file = json.load(fd)
            fd.close()
        with open(client_out_file, 'w') as fd:
            json.dump(parsed_file, fd)
            fd.close()

print('Complete./')
