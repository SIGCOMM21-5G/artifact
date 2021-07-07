#!/usr/bin/python3
import os
from os import path
import pandas as pd
import numpy as np
import glob

'''
Merge logs for each run
1. 5GTracker Logs
2. Iperf Logs
3. Power Monitor Logs
'''

## Dataset Organization
proj_dir = path.abspath(path.join(path.dirname(__file__)))
data_dir = path.join(proj_dir, 'data')
data_processed_dir = path.join(proj_dir, 'data-processed')

##########  CONFIG #############
DEVICES = ['S20UPM']
EXPR_TYPE = 'Loc-A-Wild'
DATA_DIR = data_dir
OUTPUT_DIR = data_processed_dir
OUTPUT_LOGS_DIR = path.join(OUTPUT_DIR, 'merged-logs')
IPERF_SUMMARY_FILE = path.join(DATA_DIR, 'client', f"{DEVICES[0]}-iPerfSummary.csv")
MN_WALKING_SUMMARY = path.join(DATA_DIR, f"{EXPR_TYPE}-Summary.csv")
BASE_LINE_POWER = path.join(OUTPUT_DIR, 'baseline_power.csv')
USE_PM_ROLLING = True
PM_ROLLING_WINDOW = 10  # set to 0 if functionality not wanted
SW_ROLLING_WINDOW = 10
LOGS_GRANULARITY = 1
FORCE_REGENERATE_FLAG = 1  # set to 1 if you want to do everything from scratch
iperf_run_summary = pd.read_csv(IPERF_SUMMARY_FILE)
mn_walking_summary = pd.read_csv(MN_WALKING_SUMMARY)
summary = pd.merge(mn_walking_summary, iperf_run_summary, how='left',
                   left_on='Iperf run number', right_on='RunNumber')
summary_filtered = summary[summary['SessionID'].notna()].copy(deep=True)
summary_filtered['SessionID'] = summary_filtered['SessionID'].astype(int)
summary_filtered['Iperf run number'] = summary_filtered['Iperf run number'].astype(int)
summary_filtered.reset_index(drop=True, inplace=True)

## subtract baseline power
baseline_summary = pd.read_csv(BASE_LINE_POWER)
baseline_average = baseline_summary['base_power'].mean()
baseline_summary['base_power_new'] = np.where(baseline_summary.base_power.isnull(),
                                              baseline_average, baseline_summary['base_power'])
baseline_dict = pd.Series(baseline_summary.base_power_new.values, index=baseline_summary.run_number).to_dict()

########## run number, session ids and run numbers ###########
for idx, row in summary_filtered.iterrows():
    print('=======================================================================')
    print('  processing run: {}  ({}/{})'.format(row['Iperf run number'], idx + 1, summary_filtered.shape[0]))

    ## skip if run already processed
    if not os.path.exists(OUTPUT_LOGS_DIR):
        os.makedirs(OUTPUT_LOGS_DIR)
        print('Directory created: {}'.format(OUTPUT_LOGS_DIR))

    # skip if already processed
    out_name = '{}/{}-run{}.csv'.format(OUTPUT_LOGS_DIR, row['Device'], row['Iperf run number'])
    if os.path.exists(out_name) and FORCE_REGENERATE_FLAG == 0:
        print('    skipping run: {}. Already processed.\n\n'.format(row['Iperf run number']))
        continue

    ############ SESSION LOGS ################
    session_file = '{}/session-logs/{}-{}-01.csv'.format(OUTPUT_DIR, row['Device'], row['SessionID'])
    session_logs = pd.read_csv(session_file)
    session_logs = session_logs.iloc[2:]
    session_logs['downlink_mbps'] = session_logs['mobileRx'].diff()
    session_logs['downlink_mbps'] = (session_logs['downlink_mbps'] / 1000000) * 8
    session_logs['uplink_mbps'] = session_logs['mobileTx'].diff()
    session_logs['uplink_mbps'] = (session_logs['uplink_mbps'] / 1000000) * 8

    ## get SW power and change PM log units
    session_logs['sw_power'] = session_logs['currentNow'] * session_logs['voltageNow']
    session_logs['sw_power'] = session_logs['sw_power'].abs() / 1000000
    session_logs['sw_power_rolled'] = session_logs['sw_power'].rolling(SW_ROLLING_WINDOW, min_periods=1).mean()
    session_logs['sw_power_baseline'] = session_logs['sw_power_rolled'] - baseline_dict[row['Iperf run number']]

    ############ PM LOGS #####################

    ## Step 1. process PM Logs using rolling
    pm_file = glob.glob('{}/power/run{}*.csv'.format(DATA_DIR, row['Iperf run number']))[0]
    header_list = ["time", "avg_power"]
    pm_logs = pd.read_csv(pm_file, names=header_list, skiprows=1)
    pm_logs['avg_power'] = pm_logs['avg_power'] * 1000
    if USE_PM_ROLLING:
        pm_logs['avg_power_rolled'] = pm_logs['avg_power'].rolling(PM_ROLLING_WINDOW, min_periods=1).mean()
    pm_logs['avg_power_baseline'] = pm_logs['avg_power_rolled'] - baseline_dict[row['Iperf run number']]

    ## Step 2. bin power logs
    bins = range(int(pm_logs['time'].min()), int(pm_logs['time'].max()))
    pm_logs['r_time'] = pd.cut(pm_logs['time'], bins=bins, labels=bins[:-1], include_lowest=True)
    pm_grp = pm_logs.groupby('r_time').agg(avg_power=('avg_power', np.mean),
                                           avg_power_rolled=('avg_power_rolled', np.mean),
                                           avg_power_baseline=('avg_power_baseline', np.mean))
    pm_grp.reset_index(level=0, inplace=True)
    pm_grp = pm_grp.rename(columns={'r_time': 'time'})
    pm_grp['time'] = pm_grp['time'].astype(float)
    pm_grp.sort_values(by=['time'], inplace=True, ascending=True)
    pm_grp.index = pm_grp['time']

    ############ IPERF LOGS ##########################
    iperf_file = '{}/iperf-logs/{}-run{}-iPerf.csv'.format(OUTPUT_DIR, row['Device'], row['Iperf run number'])
    iperf_logs = pd.read_csv(iperf_file)

    ########### MERGE PROCESSED LOGS AND SAVE FILES ##########

    ## Step 1. Convert 5GTracker timestamps to datetime object
    session_logs['timestamp'] = pd.to_datetime(session_logs['timestamp'])
    session_logs.sort_values(by=['timestamp'], inplace=True, ascending=True)
    session_logs.index = session_logs['timestamp']

    ## Step 2. Convert Iperf timestamps to datetime object
    iperf_logs['Fixedtimestamp'] = pd.to_datetime(iperf_logs['Fixedtimestamp'])
    iperf_logs['timestamp'] = iperf_logs['Fixedtimestamp'].apply(lambda x: x.replace(microsecond=0)).astype(str).str[
                              :-6]
    iperf_logs['timestamp'] = pd.to_datetime(iperf_logs['timestamp'])
    del iperf_logs['time']
    iperf_logs.sort_values(by=['timestamp'], inplace=True, ascending=True)
    iperf_logs.index = iperf_logs['timestamp']

    ## Step 3. Merge 5GTracker and Iperf logs
    tol = pd.Timedelta('30 minutes')
    tracker_iperf_logs = pd.merge_asof(left=session_logs, right=iperf_logs, right_index=True,
                                       left_index=True, direction='backward', tolerance=tol)

    ## Step 4. Convert iperf + 5GTracker merged logs' time to seconds elapsed
    tracker_iperf_logs['time'] = (tracker_iperf_logs['timestamp_x'] - tracker_iperf_logs.iloc[0]['timestamp_x']).astype(
        'timedelta64[ms]') / 1000
    tracker_iperf_logs.sort_values(by=['time'], inplace=True, ascending=True)
    tracker_iperf_logs.index = tracker_iperf_logs['time']

    ## Step 5. Merge logs with power logs
    merged_logs = pd.merge_asof(left=tracker_iperf_logs, right=pm_grp, direction='backward', right_index=True,
                                left_index=True)

    ## Step 6. Filter columns
    merged_logs.rename(columns={'time_x': 'time_since_start', 'timestamp_x': 'timestamp'}, inplace=True)
    columns_to_delete = ['parent_file', 'protocol', 'length',
                         '_seconds', 'bits_per_second', 'rttvar', 'pmtu', '_omitted',
                         'iperf_did', 'exp_label', 'timestamp_y', 'time_y', '_socket',
                         '_bytes', 'rtt', 'snd_cwnd']
    for col in columns_to_delete:
        if col in merged_logs.columns.tolist():
            del merged_logs[col]

    ## Step 7. filter rows when iperf was not running
    merged_logs.dropna(subset=['iperf_type'], inplace=True)
    merged_logs.sort_values(by=['run_number', 'seq_no', 'Fixedtimestamp'], ascending=True, inplace=True)
    merged_logs.drop_duplicates(subset=['Fixedtimestamp', '_start', '_end'], keep='first', inplace=True)

    ## Step 8. Correct time_since_start after trimming starting point
    merged_logs['time_since_start'] = merged_logs['time_since_start'] - merged_logs.iloc[0]['time_since_start']
    merged_logs['provider'] = row['Provider']
    merged_logs['radio_type_used'] = row['Network Type']
    merged_logs['direction'] = row['Direction']

    # export results
    print('saving file: {}'.format(out_name))
    merged_logs.to_csv(out_name, header=True, index=False)
    print('file saved....')
    print('=======================================================================')
