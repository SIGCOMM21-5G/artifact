#!/usr/bin/env python3

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from utils import *

plt.rc('font', family='sans-serif', serif='cm10')
plt.rc('text', usetex=True)
# plt.rcParams['text.latex.preamble'] = [r'\boldmath']


def get_intersect(a1, a2, b1, b2):
    """
    Returns the point of intersection of the lines passing through a2,a1 and b2,b1.
    a1: [x, y] a point on the first line
    a2: [x, y] another point on the first line
    b1: [x, y] a point on the second line
    b2: [x, y] another point on the second line
    """
    s = np.vstack([a1, a2, b1, b2])  # s for stacked
    h = np.hstack((s, np.ones((4, 1))))  # h for homogeneous
    l1 = np.cross(h[0], h[1])  # get first line
    l2 = np.cross(h[2], h[3])  # get second line
    x, y, z = np.cross(l1, l2)  # point of intersection
    if z == 0:  # lines are parallel
        return float('inf'), float('inf')
    return x / z, y / z


## Config
SHOW_PLOT_FLAG = False
EXPR_NAME = 'MN-Transfer'
COMBINED_DETAILED_FILE = 'data-processed/{}_combined.csv'.format(EXPR_NAME)

## Load combined file and add new columns
df_detailed = pd.read_csv(COMBINED_DETAILED_FILE)
df_detailed = df_detailed[df_detailed['provider'] == 'Verizon']
df_detailed['energy_efficiency'] = df_detailed['avg_power'] / df_detailed['throughput']  # get energy_efficiency

df_mmwave_dl_detailed = df_detailed[(df_detailed['network type'] == 'mmwave') &
                                    (df_detailed['direction'] == 'downlink')].copy(deep=True)
df_mmwave_ul_detailed = df_detailed[(df_detailed['network type'] == 'mmwave') &
                                    (df_detailed['direction'] == 'uplink')].copy(deep=True)
df_lte_dl_detailed = df_detailed[(df_detailed['network type'] == 'LTE') &
                                 (df_detailed['direction'] == 'downlink')].copy(deep=True)
df_lte_ul_detailed = df_detailed[(df_detailed['network type'] == 'LTE') &
                                 (df_detailed['direction'] == 'uplink')].copy(deep=True)
df_nsalow_dl_detailed = df_detailed[(df_detailed['network type'] == 'NSALow') &
                                    (df_detailed['direction'] == 'downlink')].copy(deep=True)
df_nsalow_ul_detailed = df_detailed[(df_detailed['network type'] == 'NSALow') &
                                    (df_detailed['direction'] == 'uplink')].copy(deep=True)

## Make bins for each band

# MMWAVE UL
mmwave_ul_interval = 1
mmwave_ul_bins = []
mmwave_ul_filter = []
mmwave_ul_target_bandwidth = df_mmwave_ul_detailed['target bandwidth'].unique()
for i in range(len(mmwave_ul_target_bandwidth)):
    mmwave_ul_bins.append(mmwave_ul_target_bandwidth[i] - mmwave_ul_interval)
    mmwave_ul_filter.append(True)
    mmwave_ul_bins.append(mmwave_ul_target_bandwidth[i] + mmwave_ul_interval)
    mmwave_ul_filter.append(False)
mmwave_ul_filter = mmwave_ul_filter[:-1]
df_mmwave_ul_detailed['bwd_filter'] = pd.cut(df_mmwave_ul_detailed['throughput'], bins=mmwave_ul_bins,
                                             include_lowest=True)
df_mmwave_ul_grp = df_mmwave_ul_detailed.groupby('bwd_filter').agg(
    avg_power=('avg_power', np.mean),
    throughput_mean=('throughput', np.mean),
    throughput_median=('throughput', np.median),
    throughput_std=('throughput', np.std),
    std_power=('avg_power', np.std),
    avg_energy_efficiency=('energy_efficiency', np.mean),
)
df_mmwave_ul_grp.reset_index(level=0, inplace=True)
df_mmwave_ul_grp = df_mmwave_ul_grp[mmwave_ul_filter]

# MMWAVE DL
mmwave_dl_interval = 4
mmwave_dl_interval_large = 20
mmwave_dl_bins = []
mmwave_dl_filter = []
# mmwave_dl_target_bandwidth = df_mmwave_dl_detailed['target bandwidth'].unique()
mmwave_dl_target_bandwidth = [1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190,
                              200, 400, 600, 800, 1000, 1200, 1400, 1600, 1800, 2000, 2200, 2400]
for i in range(len(mmwave_dl_target_bandwidth)):
    if mmwave_dl_target_bandwidth[i] <= 200:
        mmwave_dl_bins.append(mmwave_dl_target_bandwidth[i] - mmwave_dl_interval)
        mmwave_dl_filter.append(True)
        mmwave_dl_bins.append(mmwave_dl_target_bandwidth[i] + mmwave_dl_interval)
        mmwave_dl_filter.append(False)
    else:
        mmwave_dl_bins.append(mmwave_dl_target_bandwidth[i] - mmwave_dl_interval_large)
        mmwave_dl_filter.append(True)
        mmwave_dl_bins.append(mmwave_dl_target_bandwidth[i] + mmwave_dl_interval_large)
        mmwave_dl_filter.append(False)
mmwave_dl_filter = mmwave_dl_filter[:-1]
df_mmwave_dl_detailed['bwd_filter'] = pd.cut(df_mmwave_dl_detailed['throughput'], bins=mmwave_dl_bins,
                                             include_lowest=True)
df_mmwave_dl_grp = df_mmwave_dl_detailed.groupby('bwd_filter').agg(
    avg_power=('avg_power', np.mean),
    throughput_mean=('throughput', np.mean),
    throughput_median=('throughput', np.median),
    throughput_std=('throughput', np.std),
    std_power=('avg_power', np.std),
    avg_energy_efficiency=('energy_efficiency', np.mean)
)
df_mmwave_dl_grp.reset_index(level=0, inplace=True)
df_mmwave_dl_grp = df_mmwave_dl_grp[mmwave_dl_filter]

# LTE UL
lte_ul_interval = 1
lte_ul_bins = []
lte_ul_filter = []
lte_ul_target_bandwidth = [1., 5., 10., 15., 20., 25., 30., 35., 40.]
for i in range(len(lte_ul_target_bandwidth)):
    lte_ul_bins.append(lte_ul_target_bandwidth[i] - lte_ul_interval)
    lte_ul_filter.append(True)
    lte_ul_bins.append(lte_ul_target_bandwidth[i] + lte_ul_interval)
    lte_ul_filter.append(False)
lte_ul_filter = lte_ul_filter[:-1]
df_lte_ul_detailed['bwd_filter'] = pd.cut(df_lte_ul_detailed['throughput'], bins=lte_ul_bins,
                                          include_lowest=True)
df_lte_ul_grp = df_lte_ul_detailed.groupby('bwd_filter').agg(
    avg_power=('avg_power', np.mean),
    throughput_mean=('throughput', np.mean),
    throughput_median=('throughput', np.median),
    throughput_std=('throughput', np.std),
    std_power=('avg_power', np.std),
    avg_energy_efficiency=('energy_efficiency', np.mean)
)
df_lte_ul_grp.reset_index(level=0, inplace=True)
df_lte_ul_grp = df_lte_ul_grp[lte_ul_filter]

# LTE DL
lte_dl_interval = 1.5
lte_dl_bins = []
lte_dl_filter = []
lte_dl_target_bandwidth = df_lte_dl_detailed['target bandwidth'].unique()
for i in range(len(lte_dl_target_bandwidth)):
    lte_dl_bins.append(lte_dl_target_bandwidth[i] - lte_dl_interval)
    lte_dl_filter.append(True)
    lte_dl_bins.append(lte_dl_target_bandwidth[i] + lte_dl_interval)
    lte_dl_filter.append(False)
lte_dl_filter = lte_dl_filter[:-1]
df_lte_dl_detailed['bwd_filter'] = pd.cut(df_lte_dl_detailed['throughput'], bins=lte_dl_bins,
                                          include_lowest=True)
df_lte_dl_grp = df_lte_dl_detailed.groupby('bwd_filter').agg(
    avg_power=('avg_power', np.mean),
    throughput_mean=('throughput', np.mean),
    throughput_median=('throughput', np.median),
    throughput_std=('throughput', np.std),
    std_power=('avg_power', np.std),
    avg_energy_efficiency=('energy_efficiency', np.mean)
)
df_lte_dl_grp.reset_index(level=0, inplace=True)
df_lte_dl_grp = df_lte_dl_grp[lte_dl_filter]
df_lte_dl_grp.reset_index(inplace=True, drop=True)
df_lte_dl_grp = df_lte_dl_grp[:11]

# NSALow UL
nsalow_ul_interval = 0.5
nsalow_ul_bins = []
nsalow_ul_filter = []
nsalow_ul_target_bandwidth = [1., 10., 20., 30., 38., 40., 43., 46.]
for i in range(len(nsalow_ul_target_bandwidth)):
    nsalow_ul_bins.append(nsalow_ul_target_bandwidth[i] - nsalow_ul_interval)
    nsalow_ul_filter.append(True)
    nsalow_ul_bins.append(nsalow_ul_target_bandwidth[i] + nsalow_ul_interval)
    nsalow_ul_filter.append(False)
nsalow_ul_filter = nsalow_ul_filter[:-1]
df_nsalow_ul_detailed['bwd_filter'] = pd.cut(df_nsalow_ul_detailed['throughput'], bins=nsalow_ul_bins,
                                             include_lowest=True)
df_nsalow_ul_grp = df_nsalow_ul_detailed.groupby('bwd_filter').agg(
    avg_power=('avg_power', np.mean),
    throughput_mean=('throughput', np.mean),
    throughput_median=('throughput', np.median),
    throughput_std=('throughput', np.std),
    std_power=('avg_power', np.std),
    avg_energy_efficiency=('energy_efficiency', np.mean)
)
df_nsalow_ul_grp.reset_index(level=0, inplace=True)
df_nsalow_ul_grp = df_nsalow_ul_grp[nsalow_ul_filter]

# NSALow DL
nsalow_dl_interval = 1
nsalow_dl_bins = []
nsalow_dl_filter = []
nsalow_dl_target_bandwidth = [1., 10., 30., 40, 50., 60, 80, 90, 100.]
for i in range(len(nsalow_dl_target_bandwidth)):
    nsalow_dl_bins.append(nsalow_dl_target_bandwidth[i] - nsalow_dl_interval)
    nsalow_dl_filter.append(True)
    nsalow_dl_bins.append(nsalow_dl_target_bandwidth[i] + nsalow_dl_interval)
    nsalow_dl_filter.append(False)
nsalow_dl_filter = nsalow_dl_filter[:-1]
df_nsalow_dl_detailed['bwd_filter'] = pd.cut(df_nsalow_dl_detailed['throughput'], bins=nsalow_dl_bins,
                                             include_lowest=True)
df_nsalow_dl_grp = df_nsalow_dl_detailed.groupby('bwd_filter').agg(
    avg_power=('avg_power', np.mean),
    throughput_mean=('throughput', np.mean),
    throughput_median=('throughput', np.median),
    throughput_std=('throughput', np.std),
    std_power=('avg_power', np.std),
    avg_energy_efficiency=('energy_efficiency', np.mean)
)
df_nsalow_dl_grp.reset_index(level=0, inplace=True)
df_nsalow_dl_grp = df_nsalow_dl_grp[nsalow_dl_filter]


df_lte_dl_grp = df_lte_dl_grp[df_lte_dl_grp['throughput_mean'].notna()]
df_lte_ul_grp = df_lte_ul_grp[df_lte_ul_grp['throughput_mean'].notna()]
df_nsalow_dl_grp = df_nsalow_dl_grp[df_nsalow_dl_grp['throughput_mean'].notna()]
df_nsalow_ul_grp = df_nsalow_ul_grp[df_nsalow_ul_grp['throughput_mean'].notna()]
df_mmwave_dl_grp = df_mmwave_dl_grp[df_mmwave_dl_grp['throughput_mean'].notna()]
df_mmwave_ul_grp = df_mmwave_ul_grp[df_mmwave_ul_grp['throughput_mean'].notna()]

## plot graphs


#########################################################
## Verizon downlink + uplink MN
#########################################################
plot_id = '12'
plot_name = 'figure'
plt.close('all')
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.5, 2), sharey=True)
fig.tight_layout()
plt.subplots_adjust(bottom=0.15, wspace=0.05)

ax1.set_xscale('log')
ax1.set_yscale('log')
ax1.set_ylim(0, 1000)

x_lim_dl = ax1.get_xlim()


ax1.errorbar(df_mmwave_dl_grp['throughput_mean'], df_mmwave_dl_grp['avg_energy_efficiency'], color=colorlist10[0],
             fmt='o',
             label='5G NSA mmWave', markersize=6)
ax1.errorbar(df_nsalow_dl_grp['throughput_mean'], df_nsalow_dl_grp['avg_energy_efficiency'], color=colorlist10[1],
             fmt='o',
             label='5G NSA Low-Band', markersize=6)
ax1.errorbar(df_lte_dl_grp['throughput_mean'], df_lte_dl_grp['avg_energy_efficiency'], color=colorlist10[2], fmt='o',
             label='4G/LTE', markersize=6)

ax1.grid(True, which="both", ls="--", alpha=0.25)

legend1 = ax1.legend(loc='upper center', bbox_to_anchor=(0.9, 1.3),
                     ncol=3, fancybox=True, fontsize=16,
                     prop={'size': 16}, handletextpad=0.001, columnspacing=1.2, borderpad=0.1, markerscale=1.25)
ax1.set_ylabel('Energy Efficiency (uJ/bit)', fontsize=14)
ax1.set_xlabel('Downlink Throughput (Mbps)', fontsize=16)
ax1.tick_params(axis='both', labelsize=13)

ax2.set_ylim(0, 1000)
ax2.set_xscale('log')
ax2.set_yscale('log')

x_lim_ul = ax2.get_xlim()

ax2.errorbar(df_mmwave_ul_grp['throughput_mean'], df_mmwave_ul_grp['avg_energy_efficiency'], color=colorlist10[0],
             fmt='o',
             label='5G NSA-mmWave UL', markersize=6)

ax2.errorbar(df_nsalow_ul_grp['throughput_mean'], df_nsalow_ul_grp['avg_energy_efficiency'], color=colorlist10[1],
             fmt='o',
             label='5G NSA-LB UL', markersize=6)

ax2.errorbar(df_lte_ul_grp['throughput_mean'], df_lte_ul_grp['avg_energy_efficiency'], color=colorlist10[2], fmt='o',
             label='4G/LTE UL', markersize=6)

ax2.set_xlabel('Uplink Throughput (Mbps)', fontsize=16)
ax2.grid(True, which="both", ls="--", alpha=0.25)
ax2.tick_params(axis='both', labelsize=12)

plotme(plt, plot_id, plot_name, show_flag=SHOW_PLOT_FLAG, png_only=False, pad_inches=0.07)

print('Complete./')
