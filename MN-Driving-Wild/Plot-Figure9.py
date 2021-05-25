#!/usr/bin/python3
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from utils import *
from os import path
import matplotlib.lines as mlines

## Dataset Organization
proj_dir = path.abspath(path.join(path.dirname(__file__)))
data_dir = path.join(proj_dir, 'data')
data_processed_dir = path.join(proj_dir, 'data-processed')

## Start of Config
DEVICES = ['S20UPM']
DATA_DIR = data_processed_dir
PLOT_DIR = path.join(proj_dir, 'plots')
RANGE = 2
SHOW_PLOT_FLAG = False

handover_colors = {
    'unknown': colorlist10[7],
    '5t4': colorlist10[8],
    '4t5': colorlist10[8],
    '5t5': 'black',
    '4t4': 'black',
    'V': colorlist10[8],
    'H': 'black',
    'X': colorlist10[7],
}

handover_type = {
    'unknown': 'V',
    '5t4': 'V',
    '4t5': 'V',
    '5t5': 'H',
    '4t4': 'H',
}

radio_types = ['SA-5G only', 'NSA-5G + LTE', 'LTE only', 'SA-5G + LTE', 'All Bands']

y_value = {
    'SA-5G only': 5,
    'NSA-5G + LTE': 4,
    'LTE only': 3,
    'SA-5G + LTE': 2,
    'All Bands': 1,
}

run_numbers = {
    'SA-5G only': 108,
    'NSA-5G + LTE': 112,
    'LTE only': 109,
    'SA-5G + LTE': 107,
    'All Bands': 110,
}


def get_handoff_type(row):
    return handover_type[row['handover type']]


def get_handoff_color(row):
    return handover_colors[row['handover_vh']]


'''
plot 23
'''
plot_id = '23'
plot_name = 'pm-driving-handoff_plot'

plt.close('all')
plt.figure(figsize=(7.5, 2.5))
print('plotting {} - {} plot...'.format(plot_id, plot_name))

# get axis
ax = plt.gca()

for radio_idx, radio_type in enumerate(radio_types):
    ## Process PM Logs
    run_idx = 0
    pm_file = '{}/run{}.csv'.format(DATA_DIR, run_numbers[radio_type])
    pm_logs = pd.read_csv(pm_file)

    ## Extract handoff records
    handoff_logs = pm_logs[pm_logs['handover type'].notnull()].copy(deep=True)
    print(handoff_logs)
    handoff_logs['handover_vh'] = handoff_logs.apply(lambda x: get_handoff_type(x), axis=1)
    handoff_logs['handover_color'] = handoff_logs.apply(lambda x: get_handoff_color(x), axis=1)

    # identify sub groups
    pm_logs.sort_values(by=['time'], ascending=True, inplace=True)
    pm_logs['subgroup1'] = (pm_logs['active interface'] != pm_logs['active interface'].shift(1)).cumsum()
    blocks_nw = pm_logs.groupby('subgroup1').apply(
        lambda x: [x['active interface'].head(1).iloc[0], x['time'].min(), x['time'].max()])

    blk_list = blocks_nw.tolist()

    # fill up gaps in segments
    for idx, blk in enumerate(blk_list):
        if blk[1] == 0.0:
            pass
        if blk[2] == np.floor(pm_logs['time'].max()):
            pass
        pm_logs.loc[pm_logs['time'] == blk[1], 'time'] = blk[1] - 0.5
        pm_logs.loc[pm_logs['time'] == blk[2], 'time'] = blk[2] + 0.5
        blk_list[int(idx)][1] = blk_list[int(idx)][1] - 0.5
        blk_list[int(idx)][2] = blk_list[int(idx)][2] + 0.5

    # draw lines for handoff with alpha/transparency for row_idx in range(handoff_logs.shape[0]): ax.axvline(
    # x=handoff_logs.iloc[row_idx]['time'], linestyle='--', color=handover_colors[handoff_logs.iloc[row_idx][
    # 'handover type']], alpha=.4)

    # plot each segment of network type
    for idx, block in enumerate(blk_list):
        if block[0] == '4G':
            print(block)
            print
            lcolor = colorlist10[0]
        elif block[0] == 'NSA 5G':
            lcolor = colorlist10[1]
        elif block[0] == 'SA 5G':
            lcolor = colorlist10[2]
        elif block[0] == 'FLP':
            lcolor = colorlist10[3]

        dftemp = pm_logs[(block[1] <= pm_logs['time']) & (pm_logs['time'] <= block[2])]
        if dftemp.shape[0] > 0:
            plt.plot(dftemp['time'], dftemp['time'].shape[0] * [y_value[radio_type]], linewidth=6, color=lcolor,
                     label=block[0], zorder=2)
        plt.scatter(handoff_logs['time'], handoff_logs['time'].shape[0] * [y_value[radio_type]], s=200, marker='|',
                    linewidths=1.1, c=handoff_logs['handover_color'], zorder=3)

    del dftemp, pm_logs

# plt.ylabel('Avg. Power Util. (in W)', fontsize=14)
plt.xlabel('Timeline (in seconds)', fontsize=14)
plt.yticks(list(y_value.values()), list(y_value.keys()), fontsize=14)
plt.ylim(0.5, 5.5)
plt.xlim(0, 600)
# plt.ylim(0, 7.5 )
# plt.xlim(0, pm_logs['time'].max() + 1 )
# plt.xlim(313.98, 314.00)

# # draw fake lines (for each unique radio interface) and use them to create a legend
fourG, = plt.plot([-500, -500], '-', color=colorlist10[0])
nsa5G, = plt.plot([-500, -500], '-', color=colorlist10[1])
sa5G, = plt.plot([-500, -500], '-', color=colorlist10[2])
legend2 = ax.legend((fourG, nsa5G, sa5G), ('4G', 'NSA-5G', 'SA-5G'), loc='upper center', facecolor='whitesmoke',
                    handlelength=1, ncol=4, fontsize=14, bbox_to_anchor=(0.09, 1.43), title='Active Radio',
                    title_fontsize=15, borderpad=.3)
for text in legend2.get_texts():
    plt.setp(text, color='k')

# set the linewidth of each legend object
for legobj in legend2.legendHandles:
    legobj.set_linewidth(5)
ax.add_artist(legend2)

# # draw fake lines (for each unique handoff type) and use them to create a legend
# vh, = plt.plot([1, 1], marker='|',  markersize= 3, color=colorlist10[8])
# hh, = plt.plot([1, 1], marker='|',  markersize= 3, color=colorlist10[9])

vh = mlines.Line2D([], [], color=handover_colors['V'], marker='|', linestyle='None', markeredgewidth=2,
                   markersize=10, label='Vertical')
hh = mlines.Line2D([], [], color=handover_colors['H'], marker='|', linestyle='None', markeredgewidth=2,
                   markersize=10, label='Horizontal')

legend1 = ax.legend(handles=[vh, hh], loc='upper center', facecolor='whitesmoke', handlelength=1, ncol=4, fontsize=14,
                    bbox_to_anchor=(0.74, 1.43), title='Handoff Type', title_fontsize=15, borderpad=.3,
                    handletextpad=.2)
for text in legend1.get_texts():
    plt.setp(text, color='k')

# set the linewidth of each legend object
for legobj in legend1.legendHandles:
    legobj.set_linewidth(3)
ax.add_artist(legend1)

# enable grid
plt.grid(axis='y', linestyle='--', linewidth=.3, zorder=0)
plt.tight_layout()

if not os.path.exists(PLOT_DIR):
    os.makedirs(PLOT_DIR)
    print('Directory created: {}'.format(PLOT_DIR))

plotme(plt, plot_id, plot_name, PLOT_DIR, show_flag=SHOW_PLOT_FLAG, png_only=False, pad_inches=0.1)

######

print('Complete./')
