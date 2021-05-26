#!/usr/bin/python3
#
# Usage: python plot-section4-figure10.py
#

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import matplotlib.patches as patches
from utils import *
import glob

SHOW_PLOT_FLAG = False


def translate_network_type(net_type):
  if (net_type == '0'):
    return "Unknown"
  elif (net_type == '1'):
    return "WiFi"
  elif (net_type == '2'):
    return "2G"
  elif (net_type == '3'):
    return "3G"
  elif (net_type == '4'):
    return "4G"
  elif (net_type == '5'):
    return "5G"
  elif (net_type == '6'):
    return "5G"


def determine_color_net_type(net_type):
  if (net_type == 'Unknown'):
    return '#17becf'
  elif (net_type == 'WiFi'):
    return "#bcbd22"
  elif (net_type == '2G'):
    return "#7f7f7f"
  elif (net_type == '3G'):
    return "#e377c2"
  elif (net_type == '4G'):
    return "#1f77b4"
  elif (net_type == '5G'):
    return "#ff7f0e"
  elif (net_type == '5G'):
    return "#ff7f0e"

# load all files and merge them into single data frame
files = glob.glob('data/*.csv')
dfs = list()
for file in files:
  dfs.append(pd.read_csv(file))
df = pd.concat(dfs)

df = df[(df['KeepOrDrop'] == 'YEP')]
df['RTT'] = (df['RTT1'] + df['RTT2']) / 2

grp = df.groupby(['enabled_radio_type', 'carrier', 'interval', 'active_radio_type']).agg(
  RTT_median=('RTT', np.median),
  RTT_mean=('RTT', np.mean),
  count=('RTT', np.size)
)

grp.reset_index(level=0, inplace=True)
grp.reset_index(level=0, inplace=True)
grp.reset_index(level=0, inplace=True)
grp.reset_index(level=0, inplace=True)

grp.sort_values(by=['interval', 'count'], ascending=True, inplace=True)
# grp.drop_duplicates(subset=['interval', 'enabled_radio_type'], keep='last', inplace=True)

grp['color'] = grp.apply(lambda x: determine_color_net_type(translate_network_type(str(x['active_radio_type']))), axis=1)


### plotting
plot_id = 10
plot_name = 'figure'

dfnsammvz = grp[(grp['carrier'] == 'Verizon') & (grp['enabled_radio_type'] == '5G-NSA-mmWave')]
fig = plt.figure(figsize=(13, 6))

# ROW 1

dfsatm = grp[(grp['carrier'] == 'T-Mobile') & (grp['enabled_radio_type'] == '5G-SA-Low-Band')]
ax1 = fig.add_subplot(221)
ax1.scatter(dfsatm['interval'], dfsatm['RTT_median'], c=dfsatm['color'])
ax1.set_ylim(0, 1880)
ax1.set_yticks(np.arange(0, 1880, 500), minor=False)
ax1.set_xlim(0, 19.0)
nsa1_conn = patches.Rectangle((0.0, 1750), 10.2 - 0.0, 200, linewidth=1, edgecolor='forestgreen',
                              facecolor='forestgreen', label='RRC_CONNECTED')
sa_inac = patches.Rectangle((10.2, 1750), 15.0 - 10.2, 200, linewidth=1, edgecolor='crimson', facecolor='crimson',
                            label='RRC_INACTIVE')
nsa1_idle = patches.Rectangle((15.0, 1750), 19.0 - 15.0, 200, linewidth=1, edgecolor='magenta', facecolor='magenta',
                              label='RRC_IDLE')
ax1.add_patch(nsa1_conn)
ax1.add_patch(nsa1_idle)
ax1.add_patch(sa_inac)
ax1.set_ylabel("RTT (ms)", fontsize=20)
ax1.set_title('T-Mobile 5G SA Low-Band', fontsize=18)
ax1.tick_params(axis="both", labelsize=18)


dfnsalbtm = grp[(grp['carrier'] == 'T-Mobile') & (grp['enabled_radio_type'] == '5G-NSA-Low-Band')]
ax3 = fig.add_subplot(222)
ax3.scatter(dfnsalbtm['interval'], dfnsalbtm['RTT_median'], c=dfnsalbtm['color'])
ax3.set_ylim(0, 1780)
ax3.set_yticks(np.arange(0, 1780, 500), minor=False)
ax3.set_xlim(0, 19)
fourg_conn = patches.Rectangle((0, 1650), 10.2, 200, linewidth=1, edgecolor='forestgreen',
                               facecolor='forestgreen', label='RRC_CONNECTED')
fourg_idle = patches.Rectangle((10.2, 1650), 20 - 10.2, 200, linewidth=1, edgecolor='magenta', facecolor='magenta',
                               label='RRC_IDLE')
inac_label = patches.Rectangle((22, 1650), 23, 0, linewidth=1, edgecolor='crimson', facecolor='crimson',
                               label='RRC_INACTIVE')
ax3.add_patch(fourg_conn)
ax3.add_patch(fourg_idle)
ax3.add_patch(inac_label)
ax3.set_title('T-Mobile 5G NSA Low Band', fontsize=18)
ax3.tick_params(axis="both", labelsize=18)




## ROW 2

ax0 = fig.add_subplot(223)
ax0.scatter(dfnsammvz['interval'], dfnsammvz['RTT_median'], c=dfnsammvz['color'])
ax0.set_title('Verizon 5G NSA mmWave', fontsize=18)
ax0.set_ylabel("RTT (ms)", fontsize=20)
ax0.tick_params(axis="both", labelsize=18)
ax0.set_xlabel("Idle Time between Packets (s)", fontsize=18)
ax0.set_ylim(0, 1880)
ax0.set_yticks(np.arange(0, 1880, 500), minor=False)
ax0.set_xlim(0, 19)
sa_conn = patches.Rectangle((0.0, 1750), 11.2, 200, linewidth=1, edgecolor='forestgreen', facecolor='forestgreen',
                            label='RRC_CONNECTED')
sa_idle = patches.Rectangle((11.2, 1750), 20.2 - 11.2, 200, linewidth=1, edgecolor='magenta', facecolor='magenta',
                            label='RRC_IDLE')
ax0.add_patch(sa_conn)

ax0.add_patch(sa_idle)

df4gtm = grp[(grp['carrier'] == 'T-Mobile') & (grp['enabled_radio_type'] == '4G-LTE')]
ax5 = fig.add_subplot(224)
ax5.scatter(df4gtm['interval'], df4gtm['RTT_median'], c=df4gtm['color'])
ax5.set_xlabel("Idle Time between Packets (s)", fontsize=18)
ax5.set_ylim(0, 1780)
ax5.set_yticks(np.arange(0, 1780, 500), minor=False)
ax5.set_xlim(0, 19)
fourg_conn = patches.Rectangle((0, 1650), 5.0, 200, linewidth=1, edgecolor='forestgreen',
                               facecolor='forestgreen', label='RRC_CONNECTED')
fourg_idle = patches.Rectangle((5.0, 1650), 20 - 5.0, 200, linewidth=1, edgecolor='magenta', facecolor='magenta',
                               label='RRC_IDLE')
ax5.add_patch(fourg_conn)
ax5.add_patch(fourg_idle)
ax5.tick_params(axis="both", labelsize=18)
ax5.set_title('T-Mobile 4G', fontsize=18)






fig.legend([fourg_conn, fourg_idle, inac_label], ['RRC_CONNECTED', 'RRC_IDLE', 'RRC_INACTIVE'], fontsize=15, ncol=3,
           loc='lower center', bbox_to_anchor=(0.7, -0.05), facecolor='whitesmoke')

# # draw fake lines (for each unique radio interface) and use them to create a legend
fourG, = ax5.plot([-500,-500],'o', color='#1f77b4')
fiveG, = ax5.plot([-500,-500],'o', color='#ff7f0e')
ph, = ax5.plot([],'', ls='')
legend2 = fig.legend((ph, fourG, fiveG),('Radio type', '4G', '5G'), columnspacing=1.0, handletextpad=0.1, loc='lower center', facecolor='whitesmoke', ncol=3, fontsize=15, bbox_to_anchor=(0.2, -0.05), markerscale=2)
for text in legend2.get_texts():
    plt.setp(text, color = 'k')

fig.add_artist(legend2)

plt.tight_layout()
plotme(plt, plot_id, plot_name, show_flag=SHOW_PLOT_FLAG, png_only=False, pad_inches=0.07)

print('Complete./')