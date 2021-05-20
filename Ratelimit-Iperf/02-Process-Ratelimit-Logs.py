#!/usr/bin/env python3
import os
import glob
import pandas as pd
import numpy as np
from os import path

import context
from utils.IperfLogs import IperfLogs

__author__ = "Ahmad Hassan"


def combine_timestamp(t1, t2):
    if not pd.isnull(t1):
        return t1
    elif not pd.isnull(t2):
        return t2
    else:
        return ''


## Config
IPERF_FORCE_REGENERATE_FLAG = True
FORCE_REGENERATE_FLAG = True  # To regenerate merged files
EXPR_NAME = 'Ratelimit-Iperf'
DATA_DIR = path.join(context.data_dir, EXPR_NAME)
OUTPUT_LOGS_DIR = context.data_processed_dir
OUTPUT_CC_LOGS_DIR = path.join(OUTPUT_LOGS_DIR, 'CC-Logs')
OUTPUT_MERGED_LOGS_DIR = path.join(OUTPUT_LOGS_DIR, 'Merged-Logs')
EXPR_SUMMARY_FILE = path.join(DATA_DIR, EXPR_NAME + '.csv')
IPERF_PORT_FILE = '{}/{}-Iperf-Ports.csv'.format(OUTPUT_LOGS_DIR, EXPR_NAME)

## Load summary files
expr_summary = pd.read_csv(EXPR_SUMMARY_FILE)
iperf_ports = pd.read_csv(IPERF_PORT_FILE)


## Filter relevant runs from summary files
filtered_summary = expr_summary[(expr_summary['iperf run number'].notna()) &
                                (expr_summary['successful?'] == 'yes')].copy(deep=True)
filtered_summary['iperf run number'] = filtered_summary['iperf run number'].astype(np.int)
filtered_summary = pd.merge(filtered_summary, iperf_ports, how='left')
filtered_summary.reset_index(inplace=True, drop=True)

## Process CC Logs and store processed files
if not os.path.exists(OUTPUT_LOGS_DIR):  # create output logs directory if not there
    os.makedirs(OUTPUT_LOGS_DIR)
    print('Directory created: {}'.format(OUTPUT_LOGS_DIR))

if not os.path.exists(OUTPUT_CC_LOGS_DIR):  # create output cc logs directory if not there
    os.makedirs(OUTPUT_CC_LOGS_DIR)
    print('Directory created: {}'.format(OUTPUT_CC_LOGS_DIR))

if not os.path.exists(OUTPUT_MERGED_LOGS_DIR):  # create merged logs directory if not there
    os.makedirs(OUTPUT_MERGED_LOGS_DIR)
    print('Directory created: {}'.format(OUTPUT_MERGED_LOGS_DIR))

DATA_DIR_SERVER = path.join(DATA_DIR, 'server')
DATA_DIR_CLIENT = path.join(DATA_DIR, 'client')
DATA_DIR_COMBINED = {'server': DATA_DIR_SERVER, 'client': DATA_DIR_CLIENT}

## Get min rtt for all servers
servers_rtt_min_dict = {}
servers_rtt_avg_dict = {}
server_list = filtered_summary['server location'].unique().tolist()
for server in server_list:
    ping_logs = pd.read_csv('{}/ping/az-{}.csv'.format(DATA_DIR, server))
    servers_rtt_min_dict[server] = ping_logs['RTT [ms]'].min()
    servers_rtt_avg_dict[server] = ping_logs['RTT [ms]'].mean()

## Get distances for each server
distance_df = pd.read_csv('{}/azure-distances.csv'.format(DATA_DIR))
distance_list = pd.Series(distance_df.distance.values, index=distance_df.server).to_dict()

rows_list = []
for idx, row in filtered_summary.iterrows():
    print('=======================================================================')
    print('[PROCESSING RUN]: {}  ({}/{})'.format(row['iperf run number'], idx + 1, filtered_summary.shape[0]))

    # skip if run already processed
    if row['month'] == 'dec':
        if row['iperf type'] in ['tcp1c', 'tcp1d', 'tcp8']:
            out_name = '{}/{}-run{}-{}.csv'.format(OUTPUT_MERGED_LOGS_DIR, row['device id'],
                                                   row['iperf run number'], 'server')
            cc_log_server_file = glob.glob('{}/{}*{}*.json'.format(DATA_DIR_COMBINED['server'],
                                                                   row['device id'], row['iperf run number']))[0]
            if os.path.exists(out_name) and not FORCE_REGENERATE_FLAG:
                print('    skipping file: {}. Already processed.\n\n'.format(out_name))
                continue

        else:
            out_name = '{}/{}-run{}-{}.csv'.format(OUTPUT_MERGED_LOGS_DIR, row['device id'],
                                                   row['iperf run number'], 'client')
            cc_log_server_file = glob.glob('{}/{}*{}*.json'.format(DATA_DIR_COMBINED['client'],
                                                                   row['device id'], row['iperf run number']))[0]
            if os.path.exists(out_name) and not FORCE_REGENERATE_FLAG:
                print('    skipping file: {}. Already processed.\n\n'.format(out_name))
                continue

        ## Iperf Logs
        cc_out_filename = '{}/run{}.csv'.format(OUTPUT_CC_LOGS_DIR, row['iperf run number'])
        if os.path.exists(cc_out_filename) and not IPERF_FORCE_REGENERATE_FLAG:
            cc_log_df = pd.read_csv(cc_out_filename)
            cc_log_df['timestamp'] = pd.to_datetime(cc_log_df['timestamp'])
        else:
            cc_log_df = IperfLogs.parseLogs(cc_log_server_file)
            cc_log_df['throughput_rolled3'] = cc_log_df['throughput'].rolling(3, min_periods=1).mean()
            cc_log_df.to_csv(cc_out_filename, index=False)

        ## Merge all logs
        merged_logs = cc_log_df.copy(deep=True)
        merged_logs['time_since_start'] = (merged_logs['timestamp'] -
                                           merged_logs.loc[0, 'timestamp']).dt.total_seconds()
        merged_logs.drop(columns=['timestamp'], inplace=True)

        ## Add Extra Columns and save logs
        merged_logs['run'] = row['iperf run number']
        merged_logs['month'] = row['month']
        merged_logs['type'] = row['iperf type']
        merged_logs['server location'] = row['server location']
        merged_logs.to_csv(out_name, index=False)

        ## Make combined summary file
        df = {'server location': row['server location'],
              'latency_min': servers_rtt_min_dict[row['server location']], 'month': row['month'],
              'latency_avg': servers_rtt_avg_dict[row['server location']], 'type': row['iperf type'],
              'iperf run number': row['iperf run number'], 'distance': distance_list[row['server location']],
              'throughput_rolled3': cc_log_df['throughput_rolled3'].mean(),
              'throughput_avg': cc_log_df['throughput'].mean(),
              'throughput_max': cc_log_df['throughput'].max(),
              'throughput_90tile': cc_log_df['throughput'].quantile(0.9),
              'throughput_95tile': cc_log_df['throughput'].quantile(0.95),
              'throughput_median': cc_log_df['throughput'].quantile(0.5)}
        if row['iperf type'] in ['tcp1c', 'tcp1d', 'tcp8']:
            df['retransmits'] = cc_log_df['retransmits'].sum()
        rows_list.append(df)

    elif row['month'] == 'jan':

        if row['iperf type'] in ['tcp1c', 'tcp1d', 'tcp8']:
            out_name = '{}/{}-run{}-{}.csv'.format(OUTPUT_MERGED_LOGS_DIR, row['device id'],
                                                   row['iperf run number'], 'server')
            if os.path.exists(out_name) and not FORCE_REGENERATE_FLAG:
                print('    skipping file: {}. Already processed.\n\n'.format(out_name))
                continue

            ## Iperf Logs
            cc_out_filename = '{}/run{}.csv'.format(OUTPUT_CC_LOGS_DIR, row['iperf run number'])
            if os.path.exists(cc_out_filename) and not IPERF_FORCE_REGENERATE_FLAG:
                cc_log_df = pd.read_csv(cc_out_filename)
                cc_log_df['timestamp'] = pd.to_datetime(cc_log_df['timestamp'])
            else:
                cc_log_server_file = glob.glob('{}/{}*{}*.json'.format(DATA_DIR_COMBINED['client'],
                                                                       row['device id'], row['iperf run number']))[0]
                cc_log_df = IperfLogs.parseLogs(cc_log_server_file)
                cc_log_df['throughput_rolled3'] = cc_log_df['throughput'].rolling(3, min_periods=1).mean()
                cc_log_df.to_csv(cc_out_filename, index=False)

            ## Merge all logs
            merged_logs = cc_log_df.copy(deep=True)
            merged_logs['time_since_start'] = (merged_logs['timestamp'] -
                                               merged_logs.loc[0, 'timestamp']).dt.total_seconds()
            merged_logs.drop(columns=['timestamp'], inplace=True)

            ## Add Extra Columns and save logs
            merged_logs['run'] = row['iperf run number']
            merged_logs['month'] = row['month']
            merged_logs['type'] = row['iperf type']
            merged_logs['server location'] = row['server location']
            merged_logs.to_csv(out_name, index=False)

            ## Make combined summary file
            df = {'server location': row['server location'],
                  'latency_min': servers_rtt_min_dict[row['server location']], 'month': row['month'],
                  'latency_avg': servers_rtt_avg_dict[row['server location']], 'type': row['iperf type'],
                  'iperf run number': row['iperf run number'], 'distance': distance_list[row['server location']],
                  'throughput_rolled3': cc_log_df['throughput_rolled3'].mean(),
                  'throughput_avg': cc_log_df['throughput'].mean(),
                  'throughput_max': cc_log_df['throughput'].max(),
                  'throughput_90tile': cc_log_df['throughput'].quantile(0.9),
                  'throughput_95tile': cc_log_df['throughput'].quantile(0.95),
                  'throughput_median': cc_log_df['throughput'].quantile(0.5)}
            rows_list.append(df)


dfs = pd.DataFrame(rows_list)
combined_filename = '{}/{}_combined.csv'.format(OUTPUT_LOGS_DIR, EXPR_NAME)
print('\nsaving combined file: {}'.format(combined_filename))
if os.path.isfile(combined_filename):
    # Delete the combined file if it exists
    os.remove(combined_filename)
    print('\t old rate-limiting-iperf combined file has been deleted')

# export
dfs.to_csv(combined_filename, index=False, header=True)
print('Complete./')
