#!/usr/bin/python3
import os
from os import path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.mixture import GaussianMixture

## Dataset Organization
proj_dir = path.abspath(path.join(path.dirname(__file__)))
data_dir = path.join(proj_dir, 'data')
data_processed_dir = path.join(proj_dir, 'data-processed')

## Config
SHOW_PLOT = False
DEVICES = ['S20UPM']
EXPR_TYPE = 'Loc-A-Wild'
DATA_DIR = data_dir
OUTPUT_DIR = data_processed_dir
OUTPUT_LOGS_DIR = path.join(OUTPUT_DIR, 'cleaned-logs')
MN_WALKING_SUMMARY = path.join(DATA_DIR, f"{EXPR_TYPE}-Summary.csv")
MN_WALKING_COMBINE = path.join(OUTPUT_DIR, f"{EXPR_TYPE}_combined.csv")
FORCE_REGENERATE_FLAG = 0  # set to 1 if you want to do everything from scratch
THROUGHPUT_ROLLING_WINDOW = 3

mn_walking_summary = pd.read_csv(MN_WALKING_SUMMARY)
mn_walking_logs = pd.read_csv(MN_WALKING_COMBINE)
mn_walking_logs['run_number'] = mn_walking_logs['run_number'].astype(int)

## process throughput from 5GTracker logs
mn_walking_logs['downlink_rolled_mbps_2'] = mn_walking_logs['downlink_mbps'].rolling(2,
                                                                                     min_periods=1).mean()
mn_walking_logs['uplink_rolled_mbps_2'] = mn_walking_logs['uplink_mbps'].rolling(2,
                                                                                 min_periods=1).mean()
mn_walking_logs['downlink_rolled_mbps_3'] = mn_walking_logs['downlink_mbps'].rolling(THROUGHPUT_ROLLING_WINDOW,
                                                                                     min_periods=1).mean()
mn_walking_logs['uplink_rolled_mbps_3'] = mn_walking_logs['uplink_mbps'].rolling(THROUGHPUT_ROLLING_WINDOW,
                                                                                 min_periods=1).mean()
mn_walking_logs['downlink_rolled_mbps_4'] = mn_walking_logs['downlink_mbps'].rolling(4,
                                                                                     min_periods=1).mean()
mn_walking_logs['uplink_rolled_mbps_4'] = mn_walking_logs['uplink_mbps'].rolling(4,
                                                                                 min_periods=1).mean()

# create output folders if not present
if not os.path.exists(OUTPUT_LOGS_DIR):
    os.makedirs(OUTPUT_LOGS_DIR)
    print('Directory created: {}'.format(OUTPUT_LOGS_DIR))

df = mn_walking_logs[['timestamp', 'downlink_rolled_mbps_3', 'uplink_rolled_mbps_3',
                      'downlink_rolled_mbps_4', 'uplink_rolled_mbps_4',
                      'downlink_rolled_mbps_2', 'uplink_rolled_mbps_2',
                      'sw_power_baseline', 'avg_power_baseline', 'nr_ssRsrp_avg',
                      'rsrp', 'nr_ssRsrp', 'nr_ssSinr',
                      'rsrp_avg', 'nrStatus', 'nr_ssSinr_avg', 'provider', 'direction',
                      'network_type', 'sw_power_rolled', 'avg_power_rolled', 'avg_power',
                      'sw_power', 'downlink_mbps', 'uplink_mbps', 'Throughput']].copy(deep=True)

## T-Mobile Baseline Input Logs

# SA
print('processing t-mobile SA...')

t_mobile_sa_all = df[(df['provider'] == 'TMobile') &
                     (df['network_type'] == 'SA only')]
t_mobile_sa_all.to_csv('{}/s20_t-mobile_sa_all.csv'.format(OUTPUT_LOGS_DIR), index=False, header=True)

# NSA + LTE
print('processing t-mobile NSA...')

t_mobile_nsa_all = df[(df['provider'] == 'TMobile') &
                      (df['network_type'] == 'NSA+LTE')]
t_mobile_nsa_all.to_csv('{}/s20_t-mobile_nsa_all.csv'.format(OUTPUT_LOGS_DIR), index=False, header=True)

## Verizon Baseline Logs
print('processing Verizon...')
verizon_down = df[(df['provider'] == 'Verizon') &
                  (df['direction'] == 'downlink')]
verizon_down = verizon_down[verizon_down['nr_ssRsrp'].notnull()]
if SHOW_PLOT:
    sns.scatterplot(data=verizon_down, x='avg_power', y='nr_ssRsrp')
    plt.title('Downlink Data')
    plt.show()

## create gaussian mixture model to separate low band and high band
X = verizon_down[['avg_power', 'nr_ssRsrp']].values
gmm = GaussianMixture(n_components=2).fit(X)
labels = gmm.predict(X)
if SHOW_PLOT:
    plt.scatter(X[:, 0], X[:, 1], c=labels, s=20, cmap='viridis')
    plt.title('Downlink Gaussian Mixture')
    plt.show()
lowband_down_df = verizon_down[np.array(labels, dtype=bool)]
highband_down_df = verizon_down[~np.array(labels, dtype=bool)]
verizon_down['mmwave_flag'] = ~np.array(labels, dtype=bool)

verizon_up = df[(df['provider'] == 'Verizon') &
                (df['direction'] == 'uplink')]
verizon_up = verizon_up[verizon_up['nr_ssRsrp'].notnull()]
if SHOW_PLOT:
    sns.scatterplot(data=verizon_up, x='avg_power', y='nr_ssRsrp')
    plt.title('Uplink Data')
    plt.show()

## create gaussian mixture model to separate low band and high band
X = verizon_up[['avg_power', 'nr_ssRsrp']].values
gmm = GaussianMixture(n_components=2).fit(X)
labels = gmm.predict(X)
if SHOW_PLOT:
    plt.scatter(X[:, 0], X[:, 1], c=labels, s=20, cmap='viridis')
    plt.title('Uplink Gaussian Mixture')
    plt.show()
lowband_up_df = verizon_up[np.array(labels, dtype=bool)]
highband_up_df = verizon_up[~np.array(labels, dtype=bool)]
verizon_up['mmwave_flag'] = ~np.array(labels, dtype=bool)

verizon_lowband_all = lowband_down_df.append(lowband_up_df, ignore_index=True)
verizon_highband_all = highband_down_df.append(highband_up_df, ignore_index=True)

## Uncomment to generate these files: not needed for model
# verizon_highband_all.to_csv('{}/s20_verizon_nsahigh_all.csv'.format(OUTPUT_LOGS_DIR), index=False, header=True)
# verizon_lowband_all.to_csv('{}/s20_verizon_nsalow_all.csv'.format(OUTPUT_LOGS_DIR), index=False, header=True)


print('Complete../')
