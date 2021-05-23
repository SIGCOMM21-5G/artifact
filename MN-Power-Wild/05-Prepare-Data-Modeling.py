#!/usr/bin/python3
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.mixture import GaussianMixture
from set_paths import *

## Config
SHOW_PLOT = True
DEVICES = ['S20UPM']
EXPR_TYPE = 'MN-Power-Wild'
DATA_DIR = '{}{}'.format(DATA_FOLDER, EXPR_TYPE)
OUTPUT_DIR = '{}{}'.format(OUTPUT_FOLDER, EXPR_TYPE)
OUTPUT_LOGS_DIR = '{}/regression-input'.format(OUTPUT_DIR)
MN_WALKING_SUMMARY = '{}/{}-Summary.csv'.format(DATA_DIR, EXPR_TYPE)
MN_WALKING_COMBINE = '{}{}_combined.csv'.format(OUTPUT_FOLDER, EXPR_TYPE)
FORCE_REGENERATE_FLAG = 1  # set to 1 if you want to do everything from scratch
THROUGHPUT_ROLLING_WINDOW = 3

# ### Header Info ##### timestamp, nrStatus, lte_rsrp, nr_rsrp, nr_sinr, dl_thrpt, ul_thrpt, sw_power, power (baselin
# power subtracted), power_full

mn_walking_summary = pd.read_csv(MN_WALKING_SUMMARY)
mn_walking_logs = pd.read_csv(MN_WALKING_COMBINE)
mn_walking_logs['run_number'] = mn_walking_logs['run_number'].astype(int)
mn_walking_logs = mn_walking_logs[~mn_walking_logs['run_number'].isin(filter_run_list)]

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
t_mobile_sa_down = df[(df['provider'] == 'TMobile') &
                      (df['network_type'] == 'SA only') &
                      (df['direction'] == 'downlink')]
t_mobile_sa_down.to_csv('{}/t_mobile_sa_down.csv'.format(OUTPUT_LOGS_DIR), index=False, header=True)

t_mobile_sa_up = df[(df['provider'] == 'TMobile') &
                    (df['network_type'] == 'SA only') &
                    (df['direction'] == 'uplink')]
t_mobile_sa_up.to_csv('{}/t_mobile_sa_up.csv'.format(OUTPUT_LOGS_DIR), index=False, header=True)

t_mobile_sa_all = df[(df['provider'] == 'TMobile') &
                     (df['network_type'] == 'SA only')]
t_mobile_sa_all.to_csv('{}/t_mobile_sa_all.csv'.format(OUTPUT_LOGS_DIR), index=False, header=True)

# NSA + LTE
print('processing t-mobile NSA...')
t_mobile_nsa_down = df[(df['provider'] == 'TMobile') &
                       (df['network_type'] == 'NSA+LTE') &
                       (df['direction'] == 'downlink')]
t_mobile_nsa_down.to_csv('{}/t_mobile_nsa_down.csv'.format(OUTPUT_LOGS_DIR), index=False, header=True)

t_mobile_nsa_up = df[(df['provider'] == 'TMobile') &
                     (df['network_type'] == 'NSA+LTE') &
                     (df['direction'] == 'uplink')]
t_mobile_nsa_up.to_csv('{}/t_mobile_nsa_up.csv'.format(OUTPUT_LOGS_DIR), index=False, header=True)

t_mobile_nsa_all = df[(df['provider'] == 'TMobile') &
                      (df['network_type'] == 'NSA+LTE')]
t_mobile_nsa_all.to_csv('{}/t_mobile_nsa_all.csv'.format(OUTPUT_LOGS_DIR), index=False, header=True)

## Verizon Baseline Logs
print('processing Verizon...')
verizon_down = df[(df['provider'] == 'Verizon') &
                  (df['direction'] == 'downlink')]
verizon_down = verizon_down[verizon_down['nr_ssRsrp'].notnull()]
if SHOW_PLOT:
    sns.scatterplot(data=verizon_down, x='avg_power', y='nr_ssRsrp')
    plt.title('Combined Data')
    plt.show()

## create gaussian mixture model to separate low band and high band
X = verizon_down[['avg_power', 'nr_ssRsrp']].values
gmm = GaussianMixture(n_components=2).fit(X)
labels = gmm.predict(X)
if SHOW_PLOT:
    plt.scatter(X[:, 0], X[:, 1], c=labels, s=20, cmap='viridis')
    plt.title('Gaussian Mixture')
    plt.show()
lowband_df = verizon_down[np.array(labels, dtype=bool)]
highband_df = verizon_down[~np.array(labels, dtype=bool)]
lowband_df.to_csv('{}/verizon_lowband_down.csv'.format(OUTPUT_LOGS_DIR), index=False, header=True)
highband_df.to_csv('{}/verizon_highband_down.csv'.format(OUTPUT_LOGS_DIR), index=False, header=True)
verizon_down['mmwave_flag'] = ~np.array(labels, dtype=bool)
verizon_down.to_csv('{}/verizon_down.csv'.format(OUTPUT_LOGS_DIR), index=False, header=True)


verizon_up = df[(df['provider'] == 'Verizon') &
                (df['direction'] == 'uplink')]
verizon_up = verizon_up[verizon_up['nr_ssRsrp'].notnull()]
verizon_up.to_csv('{}/verizon_up.csv'.format(OUTPUT_LOGS_DIR), index=False, header=True)

verizon_all = df[(df['provider'] == 'Verizon')]
verizon_all.to_csv('{}/verizon_all.csv'.format(OUTPUT_LOGS_DIR), index=False, header=True)

print('Complete../')
