#!/usr/bin/python3

import pandas as pd
from datetime import datetime
import pytz
import os
from os import path
import re

## Config
DEVICES = ['S20UPM']
EXPR_TYPE = 'Loc-A-Wild'

## Dataset Organization
proj_dir = path.abspath(path.join(path.dirname(__file__)))
data_dir = path.join(proj_dir, 'data')
data_processed_dir = path.join(proj_dir, 'data-processed')

DATA_DIR = data_dir
CLIENT_LOGS_DIR = path.join(DATA_DIR, 'client')
OUTPUT_DIR = data_processed_dir
OUTPUT_LOGS_DIR = path.join(OUTPUT_DIR, 'iperf-logs')
MN_WALKING_SUMMARY = path.join(DATA_DIR, f"{EXPR_TYPE}-Summary.csv")
FORCE_REGENERATE_FLAG = 0  # set to 1 if you want to do everything from scratch


def get_run_num(exp_label):
    if len(exp_label.split('-')) < 3:
        print('Iperf Label Does not follow the standard format')
        return -1
    s = (exp_label.split('-')[1]).replace('run', '')
    if s.isdigit():
        return int(s)
    else:
        print('Iperf Run Number Not Found')
        return -1


def get_device(filename):
    iperf_filename = filename.split('/')[-1]
    iperf_device = iperf_filename.split('-')[0]
    return iperf_device.upper()


def process_timestamp_timezone(infilename, timestamp_str):
    origin_timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S %Z')

    # find origin timestamp of the file
    origin_timezone_str = timestamp_str.split(' ')[-1]
    origin_timezone = pytz.timezone(origin_timezone_str)
    timestamp_localized = origin_timezone.localize(origin_timestamp)

    # find the target timestamp of the iperf file
    if '-ATL' in infilename:
        target_timezone = pytz.timezone('US/Eastern')
    else:
        target_timezone = pytz.timezone('US/Central')

    if target_timezone is not origin_timezone:
        # convert origin timezone to target timezone if they are not the same
        corrected_timestamp = timestamp_localized.astimezone(target_timezone)
        corrected_timestamp_str = corrected_timestamp.strftime("%Y-%m-%d %H:%M:%S %Z")
    else:
        corrected_timestamp_str = timestamp_str

    return corrected_timestamp_str


def parseText(originaltext, label, regexpr):
    # print(originaltext, label, regexpr)
    parsedStr = ""
    if isinstance(originaltext, str) and label in originaltext:
        parsedStr_search = re.search(regexpr, originaltext)
        # print(parsedStr_search)
        if parsedStr_search:
            parsedStr = parsedStr_search.group(1)
            # print(parsedStr)
            parsedStr = parsedStr.replace(label, "").strip()
            parsedStr = parsedStr.replace(",", "").strip()
            parsedStr = parsedStr.replace("}", "").strip()
            # print('string found', parsedStr)
    return parsedStr


# read all files names
mn_walking_summary = pd.read_csv(MN_WALKING_SUMMARY)
mn_walking_summary = mn_walking_summary[mn_walking_summary['Successful?'] == 'yes']
mn_walking_summary.reset_index(inplace=True, drop=True)
iperf_run_list = mn_walking_summary['Iperf run number'].astype(int).tolist()

if not os.path.exists(OUTPUT_LOGS_DIR):
    os.makedirs(OUTPUT_LOGS_DIR)
    print('Directory created: {}'.format(OUTPUT_LOGS_DIR))

# For each txt file
for i in range(len(iperf_run_list)):
    infilename = '{}/{}-run{}-iPerf.txt'.format(CLIENT_LOGS_DIR, mn_walking_summary.loc[i, 'Device'], iperf_run_list[i])
    basename = os.path.basename(infilename)
    filenamewithoutext = basename.split('.')[0]

    output_filename = '{}/{}.csv'.format(OUTPUT_LOGS_DIR, filenamewithoutext)
    if os.path.isfile(output_filename) and FORCE_REGENERATE_FLAG == 0:
        print('skipping {} (already processed)'.format(infilename))
        continue

    print(infilename)
    isTCPFile = True
    intervalsStarted = False
    iperfdf = pd.DataFrame()
    streams = []
    length = 0
    streams_num = 0
    interval_index = -1
    with open(infilename, 'r') as f:
        for line in f:
            line = line.replace(os.path.splitext(os.path.basename(infilename))[0] + ":", "").strip()
            if "Time" in line:
                timestamp_str = line.replace('Time:', "")
                timestamp_str = timestamp_str.strip()
                corrected_timestamp_str = timestamp_str
            if "Starting Test" in line:
                protocol = parseText(line, 'protocol:', r'(protocol:.*?\,)')
                if protocol != "TCP":
                    print(' ignored not TCP\n')
                    isTCPFile = False
                    break
                parts = line.split(' ')
                streams_num = int(parts[4])
                if streams_num == 1:
                    iperf_type = "single"
                else:
                    iperf_type = "parallel"

            if 'Interval' in line:
                intervalsStarted = True
                continue

            if intervalsStarted and '[' in line:
                stream = {}
                line = re.sub(' +', ' ', line)
                line = re.sub('\[ ', '[', line)
                parts = line.split(' ')
                stream['socket'] = parts[0].replace('[', '').replace(']', '').strip()
                if stream['socket'] != 'SUM':
                    if len(parts) != 7:  # this is not the line which has the individual connection information, so skip
                        continue
                    sub_parts = parts[1].split('-')
                    try:
                        t = float(sub_parts[0])
                    except TypeError:
                        continue  # this is not the line which has the individual connection information, so skip
                    interval_index += 1
                    interval_index = interval_index % streams_num

                    stream['start'] = float(sub_parts[0])
                    stream['end'] = float(sub_parts[1])
                    if stream["end"] > length:
                        length = stream["end"]
                    stream['seconds'] = float(stream['end']) - float(stream['start'])
                    stream['bytes'] = ""
                    stream['bits_per_second'] = float(parts[5])  # bits/sec, Kbits/sec, Mbits/sec, Gbit/sec
                    mult_factor = 1
                    if parts[6] == 'Kbits/sec':
                        mult_factor = mult_factor * 1000
                    elif parts[6] == 'Mbits/sec':
                        mult_factor = mult_factor * 1000 * 1000
                    elif parts[6] == 'Gbits/sec':
                        mult_factor = mult_factor * 1000 * 1000 * 1000
                    stream['bits_per_second'] = mult_factor * stream['bits_per_second']
                    stream['rtt'] = -1
                    stream['rttvar'] = ""
                    stream['pmtu'] = ""
                    stream['omitted'] = ""
                    stream["session_num"] = 1
                    stream["conn_num"] = interval_index + 1
                    stream["iperf_type"] = iperf_type
                    streams.append(stream)
                else:  # Summary Interval
                    # # \todo removed as len(parts) was 7. We used another logic to check if this is sum. if len(
                    #  parts) != 8:  # this is not the line which has the individual connection information,
                    #  so skip
                    #  continue
                    if line[:5] != '[SUM]':
                        continue
                    sub_parts = parts[1].split('-')
                    try:
                        t = float(sub_parts[0])
                    except TypeError:
                        continue  # this is not the line which has the individual connection information, so skip
                    agg_stream = {}
                    agg_stream["socket"] = ""
                    agg_stream["start"] = float(sub_parts[0])
                    agg_stream["end"] = float(sub_parts[1])
                    agg_stream["seconds"] = float(agg_stream['end']) - float(agg_stream['start'])
                    agg_stream['bytes'] = ""
                    agg_stream['bits_per_second'] = float(parts[5])  # bits/sec, Kbits/sec, Mbits/sec, Gbit/sec
                    mult_factor = 1
                    if parts[6] == 'Kbits/sec':
                        mult_factor = mult_factor * 1000
                    elif parts[6] == 'Mbits/sec':
                        mult_factor = mult_factor * 1000 * 1000
                    elif parts[6] == 'Gbits/sec':
                        mult_factor = mult_factor * 1000 * 1000 * 1000
                    agg_stream['bits_per_second'] = mult_factor * agg_stream['bits_per_second']
                    agg_stream["rtt"] = -1
                    agg_stream[
                        "snd_cwnd"] = -1  # Can be updatd to calculate from the previous conn_num items in streams
                    agg_stream["session_num"] = 1
                    agg_stream["conn_num"] = ""
                    agg_stream["iperf_type"] = iperf_type + "-merged"
                    streams.append(agg_stream)
    if streams:
        streamsdf = pd.DataFrame.from_dict(streams)
        del streams
        print(infilename.split("/")[len(infilename.split("/")) - 1])
        streamsdf.insert(0, 'parent_file', infilename.split("/")[len(infilename.split("/")) - 1])
        basename = os.path.basename(infilename)
        exp_label = ""
        parts = basename.split("___")
        if len(parts) >= 2:
            exp_label = parts[1]
            exp_label = exp_label.split(".")
            exp_label = exp_label[0]
        if exp_label == "":
            exp_label = basename.split('.')[0]
        streamsdf.insert(1, 'exp_label', exp_label)
        streamsdf.insert(2, 'protocol', protocol)
        streamsdf.insert(3, 'length', length)
        streamsdf.insert(4, 'timestamp', corrected_timestamp_str)

        streamsdf.insert(5, 'Fixedtimestamp', streamsdf['timestamp'].astype(str))
        streamsdf['Fixedtimestamp'] = pd.to_datetime(streamsdf['Fixedtimestamp']) + pd.to_timedelta(
            streamsdf['end'], unit='s')

        streamsdf.insert(6, 'time', streamsdf['Fixedtimestamp'].astype(str))
        streamsdf['time'] = streamsdf['time'].str.split(' ').str.get(1).str.split('-').str.get(0)
        streamsdf.dropna(subset=['bits_per_second'], inplace=True)
        streamsdf['Throughput'] = streamsdf['bits_per_second'] / 1000000  # change bits/sec to Mbits/sec
        streamsdf['run_number'] = streamsdf.apply(lambda x: get_run_num(x['exp_label']), axis=1)
        streamsdf['iperf_did'] = streamsdf.apply(lambda x: get_device(x['exp_label']), axis=1)
        streamsdf['seq_no'] = streamsdf['start'].astype(int)

        # Calculating the average throughput for this run
        if iperf_type == 'single':
            tmp_df = streamsdf[streamsdf['iperf_type'] == 'single']
        else:
            # aggregate parallel records to get the aggregate throughput
            tmp_df = streamsdf[streamsdf['iperf_type'] == 'parallel-merged']
        if tmp_df.shape[0] > 1:
            average_throughput = int(tmp_df['Throughput'].mean())

            print('Run Number: {}, Duration: {}, Num of Connections: {}, Mean Throughput: {}'.format(
                get_run_num(exp_label), int(length), streams_num, average_throughput))

        # rename unused columns to start with _
        streamsdf.rename(columns={'bits_per_seconds': '_bits_per_seconds'}, inplace=True)
        streamsdf.rename(columns={'bytes': '_bytes'}, inplace=True)
        streamsdf.rename(columns={'start': '_start'}, inplace=True)
        streamsdf.rename(columns={'end': '_end'}, inplace=True)
        streamsdf.rename(columns={'omitted': '_omitted'}, inplace=True)
        streamsdf.rename(columns={'seconds': '_seconds'}, inplace=True)
        streamsdf.rename(columns={'socket': '_socket'}, inplace=True)

        # keep only parallel-merged and removed last 2 as they are summary of entire run
        dfexport = None
        if iperf_type == 'single':
            dfexport = streamsdf[(streamsdf['_seconds'] == 1) & (streamsdf['iperf_type'] == 'single')].copy(deep=True)
        else:
            dfexport = streamsdf[(streamsdf['_seconds'] == 1) & (streamsdf['iperf_type'] == 'parallel-merged')].copy(
                deep=True)

        # sort values
        dfexport.sort_values(by=['run_number', 'seq_no'], ascending=True, inplace=True)

        dfexport.to_csv(output_filename, index=False)
        del dfexport
        print('file processed')
    else:
        print('file is empty')
    print('=======================================================================')
