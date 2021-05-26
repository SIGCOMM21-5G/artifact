#!/usr/bin/env python3
import os
import glob
import pandas as pd
import numpy as np
from os import path
from datetime import timedelta

from utils.IperfLogs import IperfLogs


def combine_timestamp(t1, t2):
    if not pd.isnull(t1):
        return t1
    elif not pd.isnull(t2):
        return t2
    else:
        return ''


## Dataset Organization
proj_dir = path.abspath(path.join(path.dirname(__file__)))
data_dir = path.join(proj_dir, 'data')
data_processed_dir = path.join(proj_dir, 'data-processed')

## Config
EXPR_NAME = 'TCP-Single-Conn-Perf'
DATA_DIR = data_dir
OUTPUT_LOGS_DIR = data_processed_dir
EXPR_SUMMARY_FILE = path.join(DATA_DIR, EXPR_NAME + '.csv')
IPERF_SUMMARY_FILE = path.join(DATA_DIR, 'client', 'HUCKLEBERRY_830-iPerfSummary.csv')

## Load summary files
expr_summary = pd.read_csv(EXPR_SUMMARY_FILE)
iperf_summary = pd.read_csv(IPERF_SUMMARY_FILE)

## Filter relevant runs from summary files
filtered_summary = expr_summary[(expr_summary['iperf run number'].notna()) &
                                (expr_summary['successful?'] == 'yes')].copy(deep=True)
filtered_summary = pd.merge(filtered_summary, iperf_summary, left_on='iperf run number', right_on='RunNumber',  how='left')
filtered_summary['iperf run number'] = filtered_summary['iperf run number'].astype(np.int)
filtered_summary.reset_index(inplace=True, drop=True)

## Process CC Logs and store processed files
if not os.path.exists(OUTPUT_LOGS_DIR):  # create output logs directory if not there
    os.makedirs(OUTPUT_LOGS_DIR)
    print('Directory created: {}'.format(OUTPUT_LOGS_DIR))

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
distance_df = pd.read_csv('{}/UE-Azure-Server-Distances.csv'.format(DATA_DIR))
distance_list = pd.Series(distance_df.distance.values, index=distance_df.server).to_dict()

rows_list = []
for idx, row in filtered_summary.iterrows():
    print('=======================================================================')
    print('[PROCESSING RUN]: {}  ({}/{})'.format(row['iperf run number'], idx + 1, filtered_summary.shape[0]))

    # skip if run already processed
    if row['month'] == 'dec':
        if row['iperf type'] in ['tcp1c', 'tcp1d', 'tcp8']:
            iperf_log_file = glob.glob('{}/{}*{}*.json'.format(DATA_DIR_COMBINED['client'],
                                                                   row['device id'], row['iperf run number']))[0]

            ## Iperf Logs
            iperf_log_df = IperfLogs.parseLogs(iperf_log_file)
            iperf_log_df['throughput_rolled3'] = iperf_log_df['throughput'].rolling(3, min_periods=1).mean()

            ## Make combined summary file
            df = {'server_location': row['server location'],
                  'latency_min': servers_rtt_min_dict[row['server location']],
                  'latency_avg': servers_rtt_avg_dict[row['server location']], 'type': row['iperf type'],
                  'iperf_run_number': row['iperf run number'], 'distance': distance_list[row['server location']],
                  'throughput_rolled3_avg': iperf_log_df['throughput_rolled3'].mean(),
                  'throughput_avg': iperf_log_df['throughput'].mean(),
                  'throughput_max': iperf_log_df['throughput'].max(),
                  'throughput_90tile': iperf_log_df['throughput'].quantile(0.9),
                  'throughput_95tile': iperf_log_df['throughput'].quantile(0.95),
                  'throughput_median': iperf_log_df['throughput'].quantile(0.5)}
            rows_list.append(df)
        else:
            iperf_log_file = glob.glob('{}/{}*{}*.json'.format(DATA_DIR_COMBINED['client'],
                                                                   row['device id'], row['iperf run number']))[0]

            ## Iperf Logs
            iperf_logs = IperfLogs.parseLogs(iperf_log_file)

            ############ SESSION LOGS ################
            session_file = path.join(DATA_DIR_CLIENT, f"{row['device id']}-{int(row['SessionID'])}-01.csv")
            session_logs = pd.read_csv(session_file)

            ## Step 1. Convert 5GTracker timestamps to datetime object
            session_logs['timestamp'] = pd.to_datetime(session_logs['timestamp'])
            delta = timedelta(hours=11)
            session_logs['timestamp'] = session_logs['timestamp'] + delta
            session_logs['timestamp'] = session_logs['timestamp'].dt.tz_localize(None)
            session_logs.sort_values(by=['timestamp'], inplace=True, ascending=True)
            session_logs['downlink_mbps'] = session_logs['mobileRx'].diff()
            session_logs['downlink_mbps'] = (session_logs['downlink_mbps'] / 1000000) * 8
            session_logs['throughput_rolled3'] = session_logs['downlink_mbps'].rolling(3, min_periods=1).mean()

            ## Step 3. Merge 5GTracker and Iperf logs
            tracker_iperf_logs = pd.merge(left=session_logs, right=iperf_logs, how='outer')

            ## Step 4. Convert iperf + 5GTracker merged logs' time to seconds elapsed
            tracker_iperf_logs['time'] = (tracker_iperf_logs['timestamp'] - tracker_iperf_logs.iloc[0][
                'timestamp']).astype(
                'timedelta64[ms]') / 1000
            tracker_iperf_logs.sort_values(by=['time'], inplace=True, ascending=True)

            ## Step 7. Filter rows when iperf was not running
            tracker_iperf_logs = tracker_iperf_logs[(tracker_iperf_logs['timestamp'] >= iperf_logs.iloc[0]['timestamp']) &
                                                    (tracker_iperf_logs['timestamp'] <= iperf_logs.iloc[-1]['timestamp'])]
            tracker_iperf_logs.reset_index(drop=True, inplace=True)

            ## Make combined summary file
            df = {'server_location': row['server location'],
                  'latency_min': servers_rtt_min_dict[row['server location']],
                  'latency_avg': servers_rtt_avg_dict[row['server location']], 'type': row['iperf type'],
                  'iperf_run_number': row['iperf run number'], 'distance': distance_list[row['server location']],
                  'throughput_rolled3_avg': tracker_iperf_logs['throughput_rolled3'].mean(),
                  'throughput_avg': tracker_iperf_logs['downlink_mbps'].mean(),
                  'throughput_max': tracker_iperf_logs['downlink_mbps'].max(),
                  'throughput_90tile': tracker_iperf_logs['downlink_mbps'].quantile(0.9),
                  'throughput_95tile': tracker_iperf_logs['downlink_mbps'].quantile(0.95),
                  'throughput_median': tracker_iperf_logs['downlink_mbps'].quantile(0.5)}
            rows_list.append(df)

    elif row['month'] == 'jan':

        ## Iperf Logs
        iperf_log_file = glob.glob('{}/{}*{}*.json'.format(DATA_DIR_COMBINED['client'],
                                                               row['device id'], row['iperf run number']))[0]
        iperf_log_df = IperfLogs.parseLogs(iperf_log_file)
        iperf_log_df['throughput_rolled3'] = iperf_log_df['throughput'].rolling(3, min_periods=1).mean()

        ## Make combined summary file
        df = {'server_location': row['server location'],
              'latency_min': servers_rtt_min_dict[row['server location']],
              'latency_avg': servers_rtt_avg_dict[row['server location']], 'type': row['iperf type'],
              'iperf_run_number': row['iperf run number'], 'distance': distance_list[row['server location']],
              'throughput_rolled3_avg': iperf_log_df['throughput_rolled3'].mean(),
              'throughput_avg': iperf_log_df['throughput'].mean(),
              'throughput_max': iperf_log_df['throughput'].max(),
              'throughput_90tile': iperf_log_df['throughput'].quantile(0.9),
              'throughput_95tile': iperf_log_df['throughput'].quantile(0.95),
              'throughput_median': iperf_log_df['throughput'].quantile(0.5)}
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
