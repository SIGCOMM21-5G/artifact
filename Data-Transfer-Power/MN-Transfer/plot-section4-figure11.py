#!/usr/bin/env python3

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from utils import *
from mpl_toolkits.axes_grid1.inset_locator import zoomed_inset_axes
from mpl_toolkits.axes_grid1.inset_locator import mark_inset

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
df_detailed['avg_power'] = df_detailed['avg_power'] / 1000  # convert mW to W

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
    std_power=('avg_power', np.std)
)
df_mmwave_ul_grp.reset_index(level=0, inplace=True)
df_mmwave_ul_grp = df_mmwave_ul_grp[mmwave_ul_filter]

# MMWAVE DL
mmwave_dl_interval = 4
mmwave_dl_interval_large = 20
mmwave_dl_bins = []
mmwave_dl_filter = []
mmwave_dl_target_bandwidth = [1, 50, 100, 130, 200, 400, 600, 800, 1000, 1200, 1400, 1600,
                              1800, 2000, 2200, 2400]
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
    std_power=('avg_power', np.std)
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
    std_power=('avg_power', np.std)
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
    std_power=('avg_power', np.std)
)
df_lte_dl_grp.reset_index(level=0, inplace=True)
df_lte_dl_grp = df_lte_dl_grp[lte_dl_filter]
df_lte_dl_grp.reset_index(inplace=True, drop=True)
df_lte_dl_grp = df_lte_dl_grp[:11]

# NSALow UL
nsalow_ul_interval = 0.5
nsalow_ul_bins = []
nsalow_ul_filter = []
nsalow_ul_target_bandwidth = df_nsalow_ul_detailed['target bandwidth'].unique()
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
    std_power=('avg_power', np.std)
)
df_nsalow_ul_grp.reset_index(level=0, inplace=True)
df_nsalow_ul_grp = df_nsalow_ul_grp[nsalow_ul_filter]

# NSALow DL
nsalow_dl_interval = 1
nsalow_dl_bins = []
nsalow_dl_filter = []
nsalow_dl_target_bandwidth = df_nsalow_dl_detailed['target bandwidth'].unique()
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
    std_power=('avg_power', np.std)
)
df_nsalow_dl_grp.reset_index(level=0, inplace=True)
df_nsalow_dl_grp = df_nsalow_dl_grp[nsalow_dl_filter]

df_lte_dl_grp = df_lte_dl_grp[df_lte_dl_grp['throughput_mean'].notna()]
df_lte_ul_grp = df_lte_ul_grp[df_lte_ul_grp['throughput_mean'].notna()]
df_nsalow_dl_grp = df_nsalow_dl_grp[df_nsalow_dl_grp['throughput_mean'].notna()]
df_nsalow_ul_grp = df_nsalow_ul_grp[df_nsalow_ul_grp['throughput_mean'].notna()]
df_mmwave_dl_grp = df_mmwave_dl_grp[df_mmwave_dl_grp['throughput_mean'].notna()]
df_mmwave_ul_grp = df_mmwave_ul_grp[df_mmwave_ul_grp['throughput_mean'].notna()]

dl_mmwave_m, dl_mmwave_b = np.polyfit(df_mmwave_dl_grp['throughput_mean'], df_mmwave_dl_grp['avg_power'], 1)

ul_mmwave_m, ul_mmwave_b = np.polyfit(df_mmwave_ul_grp['throughput_mean'], df_mmwave_ul_grp['avg_power'], 1)

dl_lte_m, dl_lte_b = np.polyfit(df_lte_dl_grp['throughput_mean'], df_lte_dl_grp['avg_power'], 1)

ul_lte_m, ul_lte_b = np.polyfit(df_lte_ul_grp['throughput_mean'], df_lte_ul_grp['avg_power'], 1)

dl_nsalow_m, dl_nsalow_b = np.polyfit(df_nsalow_dl_grp['throughput_mean'], df_nsalow_dl_grp['avg_power'], 1)

ul_nsalow_m, ul_nsalow_b = np.polyfit(df_nsalow_ul_grp['throughput_mean'], df_nsalow_ul_grp['avg_power'], 1)

## plot graph

#########################################################
## Verizon downlink + uplink MN
#########################################################
plot_id = '11'
plot_name = 'figure'
plt.close('all')
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.5, 2.5), sharey=True)
fig.tight_layout()
plt.subplots_adjust(bottom=0.15, wspace=0.05)

ax1.set_xlim(0, 2400)
ax1.set_ylim(0, 10)

x_lim_dl = ax1.get_xlim()
regress_range_dl = np.arange(x_lim_dl[0], x_lim_dl[1])

# Compute Intersection of Lines
mmwave_dl1 = [regress_range_dl[0], dl_mmwave_m * regress_range_dl[0] + dl_mmwave_b]
mmwave_dl2 = [regress_range_dl[-1], dl_mmwave_m * regress_range_dl[-1] + dl_mmwave_b]
lte_dl1 = [regress_range_dl[0], dl_lte_m * regress_range_dl[0] + dl_lte_b]
lte_dl2 = [regress_range_dl[-1], dl_lte_m * regress_range_dl[-1] + dl_lte_b]
nsalow_dl1 = [regress_range_dl[0], dl_nsalow_m * regress_range_dl[0] + dl_nsalow_b]
nsalow_dl2 = [regress_range_dl[-1], dl_nsalow_m * regress_range_dl[-1] + dl_nsalow_b]

mmwave_lte_intersect_dl = get_intersect(mmwave_dl1, mmwave_dl2, lte_dl1, lte_dl2)
mmwave_nsalow_intersect_dl = get_intersect(mmwave_dl1, mmwave_dl2, nsalow_dl1, nsalow_dl2)

ax1.errorbar(df_mmwave_dl_grp['throughput_mean'], df_mmwave_dl_grp['avg_power'], color=colorlist10[0], fmt='o',
             label='5G NSA mmWave', markersize=8)
ax1.plot(regress_range_dl, dl_mmwave_m * regress_range_dl + dl_mmwave_b, color=colorlist10[0], linestyle='--')

ax1.errorbar(df_nsalow_dl_grp['throughput_mean'], df_nsalow_dl_grp['avg_power'], color=colorlist10[1], fmt='s',
             label='5G NSA Low-Band', markersize=8)
ax1.plot(regress_range_dl, dl_nsalow_m * regress_range_dl + dl_nsalow_b,
         color=colorlist10[1], linestyle='--')

ax1.errorbar(df_lte_dl_grp['throughput_mean'], df_lte_dl_grp['avg_power'], color=colorlist10[2], fmt='<',
             label='4G/LTE', markersize=8)
ax1.plot(regress_range_dl, dl_lte_m * regress_range_dl + dl_lte_b, color=colorlist10[2], linestyle='--')

x1_zoom = 70
x2_zoom = 325
y1_zoom = 5
y2_zoom = 6

# Make the zoom-in plot:
axins = zoomed_inset_axes(ax1, 5.5, loc=4)
axins.errorbar(df_mmwave_dl_grp['throughput_mean'], df_mmwave_dl_grp['avg_power'], color=colorlist10[0], fmt='o',
               label='5G NSA-mmWave', markersize=8)
axins.plot(regress_range_dl, dl_mmwave_m * regress_range_dl + dl_mmwave_b, color=colorlist10[0], linestyle='--')

axins.errorbar(df_nsalow_dl_grp['throughput_mean'], df_nsalow_dl_grp['avg_power'], color=colorlist10[1], fmt='s',
               label='5G NSA-LB', markersize=8)
axins.plot(regress_range_dl, dl_nsalow_m * regress_range_dl + dl_nsalow_b,
           color=colorlist10[1], linestyle='--')

axins.errorbar(df_lte_dl_grp['throughput_mean'], df_lte_dl_grp['avg_power'], color=colorlist10[2], fmt='<',
               label='4G/LTE', markersize=8)
axins.plot(regress_range_dl, dl_lte_m * regress_range_dl + dl_lte_b, color=colorlist10[2], linestyle='--')

axins.set_xlim(x1_zoom, x2_zoom)
axins.set_ylim(y1_zoom, y2_zoom)
axins.set_xticks([])
axins.set_yticks([])
pp, p1, p2 = mark_inset(ax1, axins, loc1=1, loc2=3, fc="none", ec="black", zorder=2)
pp.set_fill(True)
pp.set_facecolor("gainsboro")

axins.annotate('{:.2f}\nMbps'.format(mmwave_lte_intersect_dl[0]),
               ha='center', fontsize=14,
               xy=(mmwave_lte_intersect_dl[0] - 0.25, mmwave_lte_intersect_dl[1] + 0.03),
               xycoords='data',
               xytext=(mmwave_lte_intersect_dl[0] - 72, mmwave_lte_intersect_dl[1] + 0.16),
               textcoords='data',
               arrowprops=dict(arrowstyle='-|>, head_width=0.35', color='black', lw=1.5),
               # bbox=dict(boxstyle="round", alpha=0.1)
               )
axins.annotate('{:.2f}\nMbps'.format(mmwave_nsalow_intersect_dl[0]),
               ha='center', fontsize=14,
               xy=(mmwave_nsalow_intersect_dl[0] + 1, mmwave_nsalow_intersect_dl[1] + 0.010),
               xycoords='data',
               xytext=(mmwave_nsalow_intersect_dl[0] + 80, mmwave_nsalow_intersect_dl[1] - 0.4),
               textcoords='data',
               arrowprops=dict(arrowstyle='-|>, head_width=0.35', color='black', lw=1.5),
               # bbox=dict(boxstyle="round", alpha=0.1)
               )

# draw temporary lines and use them to create a legend
h4, = ax1.plot([1, 1], linestyle='', markersize=3, color='black')
h5, = ax1.plot([1, 1], linestyle='--', markersize=3, color='black')
legend2 = ax1.legend((h4, h5), ('', 'Regression Line'), loc='upper center', title_fontsize=18, ncol=2,
                     bbox_to_anchor=(1.675, 1.27), facecolor='#dddddd', handlelength=2, framealpha=0, fontsize=16,
                     markerscale=3, handletextpad=.2)
for text in legend2.get_texts():
    plt.setp(text, color='k')
ax1.add_artist(legend2)
h4.set_visible(False)

legend1 = ax1.legend(loc='upper center', bbox_to_anchor=(0.59, 1.25),
                     ncol=3, fancybox=True, fontsize=16, handletextpad=0.2, columnspacing=0.3, borderpad=0.1, markerscale=1.25)
ax1.set_ylabel('Power (W)', fontsize=17)
ax1.set_xlabel('Downlink Throughput (Mbps)', fontsize=16)

axins.grid(True, linestyle='--')
ax1.grid(True, linestyle='--', zorder=0)
ax1.tick_params(axis='both', labelsize=12)
axins.set_facecolor("gainsboro")

####

ax2.set_xlim(0, 200)

x_lim_ul = ax2.get_xlim()
regress_range_ul = np.arange(x_lim_ul[0], x_lim_ul[1])

# Compute Intersection of Lines
mmwave_ul1 = [regress_range_ul[0], ul_mmwave_m * regress_range_ul[0] + ul_mmwave_b]
mmwave_ul2 = [regress_range_ul[-1], ul_mmwave_m * regress_range_ul[-1] + ul_mmwave_b]
lte_ul1 = [regress_range_ul[0], ul_lte_m * regress_range_ul[0] + ul_lte_b]
lte_ul2 = [regress_range_ul[-1], ul_lte_m * regress_range_ul[-1] + ul_lte_b]
nsalow_ul1 = [regress_range_ul[0], ul_nsalow_m * regress_range_ul[0] + ul_nsalow_b]
nsalow_ul2 = [regress_range_ul[-1], ul_nsalow_m * regress_range_ul[-1] + ul_nsalow_b]

mmwave_lte_intersect_ul = get_intersect(mmwave_ul1, mmwave_ul2, lte_ul1, lte_ul2)
mmwave_nsalow_intersect_ul = get_intersect(mmwave_ul1, mmwave_ul2, nsalow_ul1, nsalow_ul2)

ax2.errorbar(df_mmwave_ul_grp['throughput_mean'], df_mmwave_ul_grp['avg_power'], color=colorlist10[0], fmt='o',
             label='NSA mmWave UL', markersize=8)
ax2.plot(regress_range_ul, ul_mmwave_m * regress_range_ul + ul_mmwave_b,
         color=colorlist10[0], linestyle='--')

ax2.errorbar(df_nsalow_ul_grp['throughput_mean'], df_nsalow_ul_grp['avg_power'], color=colorlist10[1], fmt='s',
             label='NSA Low-Band UL', markersize=8)
ax2.plot(regress_range_ul, ul_nsalow_m * regress_range_ul + ul_nsalow_b,
         color=colorlist10[1], linestyle='--')

ax2.errorbar(df_lte_ul_grp['throughput_mean'], df_lte_ul_grp['avg_power'], color=colorlist10[2], fmt='<',
             label='4G/LTE UL', markersize=8)
ax2.plot(regress_range_ul, ul_lte_m * regress_range_ul + ul_lte_b, color=colorlist10[2], linestyle='--')

ax2.annotate('{:.2f}\nMbps'.format(mmwave_lte_intersect_ul[0]),
             ha='center', fontsize=14,
             xy=(mmwave_lte_intersect_ul[0] + 5, mmwave_lte_intersect_ul[1] + 0.150),
             xycoords='data',
             xytext=(mmwave_lte_intersect_ul[0] + 60, mmwave_lte_intersect_ul[1] + 1.400),
             textcoords='data',
             arrowprops=dict(arrowstyle='-|>, head_width=0.35', color='black', lw=1.5),
             # bbox=dict(boxstyle="round", alpha=0.1)
             )
ax2.annotate('{:.2f}\nMbps'.format(mmwave_nsalow_intersect_ul[0]),
             ha='center', fontsize=14,
             xy=(mmwave_nsalow_intersect_ul[0] + 2, mmwave_nsalow_intersect_ul[1] - 0.06),
             xycoords='data',
             xytext=(mmwave_nsalow_intersect_ul[0] + 15, mmwave_nsalow_intersect_ul[1] - 3.5),
             textcoords='data',
             arrowprops=dict(arrowstyle='-|>, head_width=0.35', color='black', lw=1.5),
             # bbox=dict(boxstyle="round", alpha=0.1)
             )

ax2.set_xlabel('Uplink Throughput (Mbps)', fontsize=16)
ax2.grid(True, linestyle='--')
ax2.tick_params(axis='both', labelsize=12)

plotme(plt, plot_id, plot_name, show_flag=SHOW_PLOT_FLAG, png_only=False, pad_inches=0.07)

print('Complete./')
