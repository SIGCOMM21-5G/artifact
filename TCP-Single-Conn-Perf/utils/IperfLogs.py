#!/usr/bin/env python3
"""Converts the iperf3 json logs to pandas dataframes.
See docs for detailed structure of iperf3 logs.
"""
import json
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

__author__ = "Ahmad Hassan"
__credits__ = ["Eman Ramadan"]


class IperfLogs:
    """Converts the iperf3 json/txt logs to pandas dataframes
    """
    @staticmethod
    def parseLogs(filename, verbose=False, include_streams=False):
        """
        Parse iperf3 logs to a dataframe
        :param verbose:
        :param include_streams:
        :param filename: location of logs file
        :return: dataframe
        """
        _, file_extension = os.path.splitext(filename)
        if file_extension == '.json':
            return IperfLogs.parseJsonLogs(filename, verbose, include_streams)
        # TODO: Add txt parsing as well

    @staticmethod
    def parseJsonLogs(filename, verbose=False, include_streams=False):
        """
        Parse json iperf3 logs
        :param include_streams:
        :param verbose:
        :param filename: location of logs file
        :return:
        """
        with open(filename, 'r') as fd:
            json_parsed = json.load(fd)
        if 'test_start' not in json_parsed['start'] or \
                'timestamp' not in json_parsed['start']:
            print('Incomplete Json Log File')
            return None
        protocol = json_parsed['start']['test_start']['protocol']
        downlink_flag = bool(json_parsed['start']['test_start']['reverse'])
        parallel_conns = len(json_parsed['start']['connected'])  # get total number of parallel connections
        unix_timestamp = json_parsed['start']['timestamp']['timesecs']
        start_timestamp = datetime.utcfromtimestamp(unix_timestamp)  # timestamps should be in utc
        stream_list = list()
        if protocol in ['TCP', 'UDP']:
            for idx, interval in enumerate(json_parsed['intervals']):
                rtt = list()
                snd_cwnd = list()
                for stream in interval['streams']:
                    if 'rtt' in stream:
                        rtt.append(stream['rtt'])
                    else:
                        rtt.append(np.nan)
                    if 'snd_cwnd' in stream:
                        snd_cwnd.append(stream['snd_cwnd'])
                    else:
                        snd_cwnd.append(np.nan)
                    if include_streams:
                        stream['type'] = 'single'
                        stream['interval'] = idx
                        stream['socket'] = int(stream['socket'])
                        stream['timestamp'] = start_timestamp + timedelta(seconds=stream['end'])
                        stream_list.append(stream)
                interval['sum']['interval'] = idx
                interval['sum']['type'] = 'summary'
                interval['sum']['rtt'] = np.mean(rtt)
                interval['sum']['snd_cwnd'] = np.mean(snd_cwnd)
                interval['sum']['timestamp'] = start_timestamp + timedelta(seconds=interval['sum']['end'])
                stream_list.append(interval['sum'])
        else:
            print('protocol not supported right now')
        df = pd.DataFrame(stream_list)
        df['throughput'] = df['bits_per_second'] / 1000000
        df['rtt'] = df['rtt'] / 1000
        df['snd_cwnd'] = df['snd_cwnd'] / 1000000
        df['protocol'] = protocol
        df['direction'] = 'downlink' if downlink_flag else 'uplink'
        df.downlink_flag = downlink_flag
        df.parallel_conns = parallel_conns
        if verbose:
            # TODO: add summary for iperf logs
            print('Summary: To be added later')
        return df
