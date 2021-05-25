#!/usr/bin/python3

import os
from os import path
import numpy as np
import pandas as pd
import re

## Dataset Organization
proj_dir = path.abspath(path.join(path.dirname(__file__)))
data_dir = path.join(proj_dir, 'data')
data_processed_dir = path.join(proj_dir, 'data-processed')

##  Config
DEVICES = ['S20UPM']
EXPR_TYPE = 'MN-Power-Wild'
DATA_DIR = data_dir
CLIENT_LOGS_DIR = path.join(DATA_DIR, 'client')
OUTPUT_DIR = data_processed_dir
IPERF_SUMMARY_FILE = path.join(CLIENT_LOGS_DIR, f"{DEVICES[0]}-iPerfSummary.csv")
MN_WALKING_SUMMARY = path.join(DATA_DIR, f"{EXPR_TYPE}-Summary.csv")
iperf_run_summary = pd.read_csv(IPERF_SUMMARY_FILE)
mn_walking_summary = pd.read_csv(MN_WALKING_SUMMARY)
FORCE_REGENERATE_FLAG = 0  # set to 1 if you want to do everything from scratch
summary = pd.merge(mn_walking_summary, iperf_run_summary, how='left',
                   left_on='Iperf run number', right_on='RunNumber')
summary_filtered = summary[summary['SessionID'].notna() &
                           (summary['Successful?'] == 'yes')].copy(deep=True)
del summary
summary_filtered['SessionID'] = summary_filtered['SessionID'].astype(int)
summary_filtered.reset_index(drop=True, inplace=True)

# create output folders if not present
OUTPUT_LOGS_DIR = path.join(OUTPUT_DIR, 'session-logs')
if not os.path.exists(OUTPUT_LOGS_DIR):
    os.makedirs(OUTPUT_LOGS_DIR)
    print('Directory created: {}'.format(OUTPUT_LOGS_DIR))


def mcidToTower(mcid):
    return mcid[:-2]


def getTextByIndex(originaltext, index, end=-1):
    parsedStr = ""
    if isinstance(originaltext, str) and originaltext:
        items = originaltext.split(" ")
        if index <= len(items):
            parsedStr = items[index]
        if end != -1:
            index += 1
            while index <= end:
                parsedStr += items[index]
                index += 1
    return parsedStr


def parseAllText(originaltext, label, regexpr):
    parsedStr = ""
    items = []
    if isinstance(originaltext, str) and label in originaltext:
        parsedStr_search = re.findall(regexpr, originaltext)
        if parsedStr_search:
            for item in parsedStr_search:
                item = item.replace(label, "").strip()
                item = item.replace(",", "").strip()
                item = item.replace("}", "").strip()
                items.append(item)
            parsedStr = '|'.join(items)
    return parsedStr


for idx, row in summary_filtered.iterrows():
    session_file = '{}/{}-{}-01.csv'.format(CLIENT_LOGS_DIR, row['Device'], row['SessionID'])
    print('============================== RUN: {} ================================='.format(row['Iperf run number']))
    print('processing file: {}   ({}/{})'.format(session_file, idx + 1, summary_filtered.shape[0]))

    # skip if already processed
    log_filename = '{}/{}'.format(OUTPUT_LOGS_DIR, os.path.basename(session_file))
    if os.path.exists(log_filename) and FORCE_REGENERATE_FLAG == 0:
        print('    skipping file: {}. Already processed.\n\n'.format(session_file))
        continue

    ## Process 5GTracker data
    session_logs = pd.read_csv(session_file)
    if row['Network Type'] == 'SA only' or 'NSA+LTE':
        session_logs['rsrp'] = session_logs['nr_ssRsrp']
    else:
        session_logs['rsrp'] = session_logs.apply(
            lambda x: parseAllText(x["RawSignalStrengths"], "rsrp=", r'(rsrp=.*?\s)'), axis=1).astype(int)

    session_logs = session_logs[~session_logs['mCid'].isna()]
    session_logs['towerid'] = session_logs.apply(lambda x: mcidToTower(str(x['mCid'])), axis=1).astype(int)
    session_logs['timestamp'] = pd.to_datetime(session_logs['timestamp'])
    session_logs['r_time'] = session_logs['timestamp'].apply(lambda x: x.replace(microsecond=0)).astype(str).str[:-6]
    session_grp = session_logs.groupby(['r_time']).agg(latitude=('latitude', np.mean),
                                                       longitude=('longitude', np.mean),
                                                       locationAccuracy=('locationAccuracy', np.mean),
                                                       movingSpeed=('movingSpeed', np.mean),
                                                       movingSpeedAccuracyMPS=('movingSpeedAccuracyMPS', np.mean),
                                                       compassDirection=('compassDirection', np.mean),
                                                       compassAccuracy=('compassAccuracy', np.mean),
                                                       nrStatus=('nrStatus', lambda x: list(x.unique())),
                                                       mCid=('mCid', lambda x: list(x.unique())),
                                                       towerid=('towerid', lambda x: list(x.unique())),
                                                       rsrp=('rsrp', np.max),
                                                       nr_ssRsrp=('nr_ssRsrp', np.max),
                                                       nr_ssSinr=('nr_ssSinr', np.max),
                                                       rsrp_avg=('rsrp', np.mean),
                                                       nr_ssRsrp_avg=('nr_ssRsrp', np.mean),
                                                       nr_ssSinr_avg=('nr_ssSinr', np.mean),
                                                       mobileRx=('mobileRx', np.max),
                                                       mobileTx=('mobileTx', np.max),
                                                       currentNow=('currentNow', np.mean),
                                                       voltageNow=('voltageNow', np.mean))
    session_grp.reset_index(level=0, inplace=True)
    session_grp.rename(columns={'r_time': 'timestamp'}, inplace=True)
    session_logs = session_grp.copy(deep=True)

    session_logs['compassDirection'] = session_logs['compassDirection'].astype(int)

    session_logs['num_mcids'] = session_logs['mCid'].apply(lambda x: len(x))
    session_logs['mCid'] = session_logs['mCid'].apply(lambda x: x[-1]).astype(int)
    session_logs['towerid'] = session_logs['towerid'].apply(lambda x: x[-1]).astype(int)

    session_logs['nrStatus_array'] = session_logs['nrStatus']
    session_logs['nrStatus'] = session_logs['nrStatus'].apply(lambda x: x[-1]).astype(str)

    # export results
    session_logs.to_csv(log_filename, index=False, header=True)
    print('file saved ({})..\n'.format(log_filename))
