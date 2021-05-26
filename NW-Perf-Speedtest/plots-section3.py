#!/usr/bin/python3
#
# Usage: python plots-section3.py
#

import pandas as pd
import matplotlib.pyplot as plt
from utils import *

df = pd.read_csv('speedtest_ookla.csv')
SHOW_PLOT_FLAG = False

##########################################
# Figure 2 # Verizon (mmWave, 4G/NSA-5G)
#########################################

df_f2 = df[(df['type'] == 'latency') & (df['carrier'] == 'Verizon')]

MARKERS = ['*', 'd', '>', '<', '^', 'v']
CONN_LINE_STYLE = {
  'multi' : '-',
  'single' : '--'
}

# remove Alaska
df_f2 = df_f2[df_f2['Server_state'] != 'AK']

plot_id = '3'
plot_name = 'figure'

plt.close('all')
plt.figure(figsize=(5, 3))
# plt.figure(figsize=(10, 3))
print('plotting {} - {} plot...'.format(plot_id, plot_name))

F3_MARKERS = {
  '5G-NSA-mmWave' : '<',
  '4G-LTE' : 'v',
  '5G-NSA-Low-Band' : '^'
}

F3_COLORS = {
  '5G-NSA-mmWave' : colorlist10[3],
  '4G-LTE' : colorlist10[5],
  '5G-NSA-Low-Band' : colorlist10[4]
}

for radio_idx, radio_type in enumerate(df_f2.radio_type.unique().tolist()): #enumerate(['NSAUW', 'NSAlow', 'LTE']):
  dftemp = df_f2[(df_f2['radio_type'] == radio_type)].copy(deep=True)
  dftemp.sort_values(by=['UE_Server_distance_km'], ascending=True, inplace=True)
  plt.plot(dftemp['UE_Server_distance_km'], dftemp['latency_ms'], linestyle='-', ms=5.5, marker=F3_MARKERS[radio_type], c=F3_COLORS[radio_type],
           alpha=.8)
  del dftemp


plt.grid()
plt.ylabel('RTT (in ms)', fontsize=14)
plt.xlabel('Distance (in km)', fontsize=14)

ax = plt.gca()
# We change the fontsize of minor ticks label
ax.tick_params(axis='both', which='major', labelsize=11)
ax.tick_params(axis='both', which='minor', labelsize=12)

# draw temporary lines and use them to create a legend
h1, = plt.plot([1, 1], linestyle='-',  marker=MARKERS[0], markersize= 3, color=colorlist10[3])
h2, = plt.plot([1, 1], linestyle='-',  marker=MARKERS[1],  markersize= 3, color=colorlist10[4])
h3, = plt.plot([1, 1], linestyle='-',  marker=MARKERS[2],  markersize= 3, color=colorlist10[5])
legend1 = ax.legend((h1, h2, h3), ('mmWave', 'Low-Band', 'LTE/4G'), loc='upper center', ncol=3,
                    bbox_to_anchor=(0.44, 1.18), facecolor='#dddddd', handlelength=1.5, framealpha=.7, fontsize = 12, markerscale=3)
for text in legend1.get_texts():
    plt.setp(text, color='k')
ax.add_artist(legend1)
h1.set_visible(False)
h2.set_visible(False)
h3.set_visible(False)

plotme(plt, plot_id, plot_name, show_flag=SHOW_PLOT_FLAG, png_only=False, pad_inches=0.07)

del df_f2


##########################################
# Figure 3 # Verizon (mmWave throughput downlink)
#########################################

plot_id = '3'
plot_name = 'figure'

# remove Alaska
df_f3 = df[df['Server_state'] != 'AK']

# filter data for different line plots
df_fig3_s = df_f3[(df_f3['type'] == 'downlink') & (df_f3['carrier'] == 'Verizon') & (df_f3['connection_mode'] == 'single') & (df_f3['radio_type'] == '5G-NSA-mmWave')]
df_fig3_m = df_f3[(df_f3['type'] == 'downlink') & (df_f3['carrier'] == 'Verizon') & (df_f3['connection_mode'] == 'multi') & (df_f3['radio_type'] == '5G-NSA-mmWave')]
df_fig3_latency = df_f3[(df_f3['type'] == 'latency') & (df_f3['carrier'] == 'Verizon') & (df_f3['radio_type'] == '5G-NSA-mmWave')]

plt.close('all')
plt.figure(figsize=(4.5, 3.1))
print('plotting {} - {} plot...'.format(plot_id, plot_name))

# plot downlink throughput
plt.plot(df_fig3_m['UE_Server_distance_km'], df_fig3_m['downlink_Mbps'], linestyle='-', ms=7.5, marker='*', c=colorlist10[3], label='multiple conn.')
plt.plot(df_fig3_s['UE_Server_distance_km'], df_fig3_s['downlink_Mbps'], linestyle='--', ms=6.5, marker='>', c=colorlist10[3], label='single conn.')
plt.grid()
plt.ylabel('Downlink\nThroughput (in Mbps)', fontsize=14, color=colorlist10[3])
plt.xlabel('Distance (in km)', fontsize=14)
plt.ylim(0, 3500)

plt.text(1700, 2550, 'mmWave', color='black', fontsize=15,
        bbox=dict(facecolor='lightgray', edgecolor='lightgray', boxstyle='round,pad=.5'))
ax1 = plt.gca()

# We change the fontsize of minor ticks label
ax1.tick_params(axis='both', which='major', labelsize=11)
ax1.tick_params(axis='both', which='minor', labelsize=12)
ax1.tick_params(axis='y', labelcolor=colorlist10[3])

# plot the RTT
ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
ax2.invert_yaxis()
ax2.plot(df_fig3_latency['UE_Server_distance_km'], df_fig3_latency['latency_ms'], linestyle=':', ms=2.5, marker='o', c=colorlist10[7], label='RTT', alpha=.8)
ax2.tick_params(axis='y', labelcolor=colorlist10[7])
ax2.set_ylabel('RTT in ms (inverted axis)', color=colorlist10[7], rotation=270, labelpad=15, fontsize=14)

lines_labels = [ax.get_legend_handles_labels() for ax in [ax1, ax2]]
lines, labels = [sum(lol, []) for lol in zip(*lines_labels)]

leg = plt.legend(lines, labels, loc='upper center', bbox_to_anchor=(0.45, 1.18), fontsize=13, markerscale=1.5, handletextpad=.2, handlelength=3,columnspacing=.5, borderpad=.3, labelspacing=.2, ncol=3)
leg._legend_box.align = "left"

plotme(plt, plot_id, plot_name, show_flag=SHOW_PLOT_FLAG, png_only=False, pad_inches=0.07)

del df_f3, df_fig3_m, df_fig3_s, df_fig3_latency

##########################################
# Figure 4 # Verizon (mmWave throughput uplink)
#########################################

# remove Alaska
df_f4 = df[(df['Server_state'] != 'AK') & (df['Server_city'] != 'Cleveland')]

# filter data for different line plots
df_fig4_s = df_f4[(df_f4['type'] == 'uplink') & (df_f4['carrier'] == 'Verizon') & (df_f4['connection_mode'] == 'single') & (df_f4['radio_type'] == '5G-NSA-mmWave')]
df_fig4_m = df_f4[(df_f4['type'] == 'uplink') & (df_f4['carrier'] == 'Verizon') & (df_f4['connection_mode'] == 'multi') & (df_f4['radio_type'] == '5G-NSA-mmWave')]


plot_id = '4'
plot_name = 'figure'

plt.close('all')
plt.figure(figsize=(5, 3))
print('plotting {} - {} plot...'.format(plot_id, plot_name))

plt.plot(df_fig4_m['UE_Server_distance_km'], df_fig4_m['uplink_Mbps'], linestyle='-', ms=7.5, marker='*', c='forestgreen', label='multiple conn.')
plt.plot(df_fig4_s['UE_Server_distance_km'], df_fig4_s['uplink_Mbps'], linestyle='--', ms=6.5, marker='>', c='firebrick', label='single conn.')

plt.grid()
plt.ylabel('Uplink\nThroughput (in Mbps)', fontsize=14)
plt.xlabel('Distance (in km)', fontsize=14)
plt.ylim(0, 250)

plt.text(1700, 50, 'mmWave', color='black', fontsize=15,
        bbox=dict(facecolor='lightgray', edgecolor='lightgray', boxstyle='round,pad=.5'))
ax1 = plt.gca()
# We change the fontsize of minor ticks label
ax1.tick_params(axis='both', which='major', labelsize=11)
ax1.tick_params(axis='both', which='minor', labelsize=12)

plt.legend(loc='upper center', bbox_to_anchor=(0.45, 1.18), fontsize=13, markerscale=1.5, handletextpad=.2, handlelength=3,columnspacing=.5, borderpad=.3, labelspacing=.2, ncol=3)

plotme(plt, plot_id, plot_name, show_flag=SHOW_PLOT_FLAG, png_only=False, pad_inches=0.07)

del df_f4, df_fig4_s, df_fig4_m


##########################################
# Figure 5 # T-Mobile (Latency)
#########################################

plot_id = '5'
plot_name = 'figure'

F5_MARKERS = {
  '5G-SA-Low-Band': '*',
  '5G-NSA-Low-Band' : 'd'
}

F5_COLORS = {
  '5G-SA-Low-Band': 'mediumvioletred',
  '5G-NSA-Low-Band' : 'blueviolet'
}


df_f5 = df[(df['type'] == 'latency') & (df['carrier'] == 'TMobile')]

plt.close('all')
plt.figure(figsize=(5, 3.1))
print('plotting {} - {} plot...'.format(plot_id, plot_name))

colors_list = ['mediumvioletred', 'blueviolet']
for radio_idx, radio_type in enumerate(['5G-SA-Low-Band', '5G-NSA-Low-Band']):
  dftemp = df_f5[(df_f5['radio_type'] == radio_type)].copy(deep=True)
  dftemp.sort_values(by=['UE_Server_distance_km'], ascending=True, inplace=True)
  plt.plot(dftemp['UE_Server_distance_km'], dftemp['latency_ms'], linestyle='-', ms=5.5, marker=F5_MARKERS[radio_type], c=F5_COLORS[radio_type],
           alpha=.8)
  del dftemp

plt.grid()
plt.ylabel('RTT (in ms)', fontsize=14)
plt.xlabel('Distance (in km)', fontsize=14)
plt.ylim(0, 110)

ax = plt.gca()
# We change the fontsize of minor ticks label
ax.tick_params(axis='both', which='major', labelsize=11)
ax.tick_params(axis='both', which='minor', labelsize=12)

# draw temporary lines and use them to create a legend
h1, = plt.plot([1, 1], linestyle='-',  marker=F5_MARKERS['5G-SA-Low-Band'], markersize= 3, color=F5_COLORS['5G-SA-Low-Band'])
h2, = plt.plot([1, 1], linestyle='-',  marker=F5_MARKERS['5G-NSA-Low-Band'],  markersize= 3, color=F5_COLORS['5G-NSA-Low-Band'])
legend1 = ax.legend((h1, h2), ('SA Low-Band (T-Mobile)', 'NSA Low-Band (T-Mobile)'), loc='upper left', ncol=1, facecolor='#dddddd', handlelength=1.5, handletextpad=.2, framealpha=.7, fontsize = 12, markerscale=3, columnspacing=.5)

for text in legend1.get_texts():
    plt.setp(text, color='k')
ax.add_artist(legend1)
h1.set_visible(False)
h2.set_visible(False)

plotme(plt, plot_id, plot_name, show_flag=SHOW_PLOT_FLAG, png_only=False, pad_inches=0.07)


##########################################
# Figure 6 # T-Mobile (Downlink)
#########################################

MARKERS = ['*', 'd', '>', '<', '^', 'v']

OP_COLOR = {
  'Verizon' : '*',
  'single' : 'P'
}
CONN_LINE_STYLE = {
  'multi' : '-',
  'single' : '--'
}


plot_id = '6'
plot_name = 'figure'

F6_MARKERS = {
  '5G-SA-Low-Band': '*',
  '5G-NSA-Low-Band' : 'd'
}

F6_COLORS = {
  '5G-SA-Low-Band': 'mediumvioletred',
  '5G-NSA-Low-Band' : 'blueviolet'
}

df_f6 = df[(df['type'] == 'downlink') & (df['carrier'] == 'TMobile')]

plt.close('all')
plt.figure(figsize=(5, 2.5))
print('plotting {} - {} plot...'.format(plot_id, plot_name))


for radio_idx, radio_type in enumerate(df_f6['radio_type'].unique()):
  for conn_idx, conn in enumerate(df_f6['connection_mode'].unique()):
    dftemp = df_f6[(df_f6['radio_type'] == radio_type) & (df_f6['connection_mode'] == conn)].copy(deep=True)
    dftemp.sort_values(by=['UE_Server_distance_km'], ascending=True, inplace=True)
    plt.plot(dftemp['UE_Server_distance_km'], dftemp['downlink_Mbps'], linestyle=CONN_LINE_STYLE[conn], ms=5.5, marker=F6_MARKERS[radio_type], c=F6_COLORS[radio_type],
             alpha=.8)
    del dftemp


plt.grid()
plt.ylabel('Downlink\nThroughput (in Mbps)', fontsize=14)
plt.xlabel('Distance (in km)', fontsize=14)

ax = plt.gca()
# We change the fontsize of minor ticks label
ax.tick_params(axis='both', which='major', labelsize=11)
ax.tick_params(axis='both', which='minor', labelsize=12)

# draw temporary lines and use them to create a legend
h1, = plt.plot([1, 1], linestyle='-',  marker=F6_MARKERS[df_f6['radio_type'].unique()[0]], markersize= 3, color=F6_COLORS[df_f6['radio_type'].unique()[0]])
h2, = plt.plot([1, 1], linestyle='-',  marker=F6_MARKERS[df_f6['radio_type'].unique()[1]],  markersize= 3, color=F6_COLORS[df_f6['radio_type'].unique()[1]])
legend1 = ax.legend((h1, h2), ('SA Low Band (T-Mobile)', 'NSA Low Band (T-Mobile)'), loc='upper center',
                    bbox_to_anchor=(0.22, 1.34), facecolor='#dddddd', handlelength=1.5, framealpha=.7, fontsize = 12, markerscale=3, handletextpad=.2)
for text in legend1.get_texts():
    plt.setp(text, color='k')
ax.add_artist(legend1)
h1.set_visible(False)
h2.set_visible(False)

# draw temporary lines and use them to create a legend
h4, = plt.plot([1, 1], linestyle='-',  markersize= 3, color='black')
h5, = plt.plot([1, 1], linestyle='--',  markersize= 3, color='black')
legend2 = ax.legend((h4, h5), ('Multiple conn.', 'Single conn.'), loc='upper center',
                    bbox_to_anchor=(0.78, 1.34), facecolor='#dddddd', handlelength=2, framealpha=.7, fontsize = 12, markerscale=3, handletextpad=.2)
for text in legend2.get_texts():
    plt.setp(text, color='k')
ax.add_artist(legend2)
h4.set_visible(False)
h5.set_visible(False)

plotme(plt, plot_id, plot_name, show_flag=SHOW_PLOT_FLAG, png_only=False, pad_inches=0.07)

del df_f6

##########################################
# Figure 7 # T-Mobile (Uplink)
#########################################

CONN_LINE_STYLE = {
  'multi' : '-',
  'single' : '--'
}


plot_id = '7'
plot_name = 'figure'

F7_MARKERS = {
  '5G-SA-Low-Band': '*',
  '5G-NSA-Low-Band' : 'd'
}

F7_COLORS = {
  '5G-SA-Low-Band': 'mediumvioletred',
  '5G-NSA-Low-Band' : 'blueviolet'
}

df_f7 = df[(df['type'] == 'uplink') & (df['carrier'] == 'TMobile')]

plt.close('all')
plt.figure(figsize=(5, 2.5))
print('plotting {} - {} plot...'.format(plot_id, plot_name))


for radio_idx, radio_type in enumerate(df_f7['radio_type'].unique()):
  for conn_idx, conn in enumerate(df_f7['connection_mode'].unique()):
    dftemp = df_f7[(df_f7['radio_type'] == radio_type) & (df_f7['connection_mode'] == conn)].copy(deep=True)
    dftemp.sort_values(by=['UE_Server_distance_km'], ascending=True, inplace=True)
    plt.plot(dftemp['UE_Server_distance_km'], dftemp['uplink_Mbps'], linestyle=CONN_LINE_STYLE[conn], ms=5.5, marker=F7_MARKERS[radio_type], c=F7_COLORS[radio_type],
             alpha=.8)
    del dftemp

plt.grid()
plt.ylabel('Uplink\nThroughput (in Mbps)', fontsize=14)
plt.xlabel('Distance (in km)', fontsize=14)

ax = plt.gca()

# We change the fontsize of minor ticks label
ax.tick_params(axis='both', which='major', labelsize=11)
ax.tick_params(axis='both', which='minor', labelsize=12)

# draw temporary lines and use them to create a legend
h1, = plt.plot([1, 1], linestyle='-',  marker=F7_MARKERS[df_f7['radio_type'].unique()[0]], markersize= 3, color=F7_COLORS[df_f7['radio_type'].unique()[0]])
h2, = plt.plot([1, 1], linestyle='-',  marker=F7_MARKERS[df_f7['radio_type'].unique()[1]],  markersize= 3, color=F7_COLORS[df_f7['radio_type'].unique()[1]])
legend1 = ax.legend((h1, h2), ('SA Low Band (T-Mobile)', 'NSA Low Band (T-Mobile)'), loc='upper center',
                    bbox_to_anchor=(0.22, 1.34), facecolor='#dddddd', handlelength=1.5, framealpha=.7, fontsize = 12, markerscale=3, handletextpad=.2)
for text in legend1.get_texts():
    plt.setp(text, color='k')
ax.add_artist(legend1)
h1.set_visible(False)
h2.set_visible(False)

# draw temporary lines and use them to create a legend
h4, = plt.plot([1, 1], linestyle='-',  markersize= 3, color='black')
h5, = plt.plot([1, 1], linestyle='--',  markersize= 3, color='black')
legend2 = ax.legend((h4, h5), ('Multiple conn.', 'Single conn.'), loc='upper center',
                    bbox_to_anchor=(0.78, 1.34), facecolor='#dddddd', handlelength=2, framealpha=.7, fontsize = 12, markerscale=3, handletextpad=.2)
for text in legend2.get_texts():
    plt.setp(text, color='k')
ax.add_artist(legend2)
h4.set_visible(False)
h5.set_visible(False)

plotme(plt, plot_id, plot_name, show_flag=SHOW_PLOT_FLAG, png_only=False, pad_inches=0.07)

del df_f7

###################################################################

print('Complete./')