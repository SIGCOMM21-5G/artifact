#!/usr/bin/python3
#
# Usage: python plots-figure-10.py
#

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import matplotlib.patches as patches
from utils import *

SHOW_PLOT_FLAG = True

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

df = pd.read_csv('dataset.csv')
df = df[(df['KeepOrDrop'] == 'YEP')]
df['RTT'] = (df['RTT1'] + df['RTT2']) / 2

grp = df.groupby(['enabled_radio_type', 'carrier', 'interval', 'active_radio_type']).agg(
  RTT_median=('RTT', np.median),
  RTT_mean=('RTT', np.mean),
  count=('timestamp', np.size)
)

grp.reset_index(level=0, inplace=True)
grp.reset_index(level=0, inplace=True)
grp.reset_index(level=0, inplace=True)
grp.reset_index(level=0, inplace=True)

grp.sort_values(by=['interval', 'count'], ascending=True, inplace=True)
grp.drop_duplicates(subset=['interval', 'enabled_radio_type'], keep='last', inplace=True)

grp['color'] = grp.apply(lambda x: determine_color_net_type(translate_network_type(str(x['active_radio_type']))), axis=1)


### plotting
plot_id = 10
plot_name = 'figure'

dfsatm = grp[(grp['carrier'] == 'TMobile') & (grp['enabled_radio_type'] == '5G-SA-Low-Band')]
fig = plt.figure(figsize=(13, 6))
ax0 = fig.add_subplot(221)
ax0.scatter(dfsatm['interval'], dfsatm['RTT_median'], c=dfsatm['color'])

dfnsatm = grp[(grp['carrier'] == 'TMobile') & (grp['enabled_radio_type'] == '5G-NSA-Low-Band')]
# dfnsatm = grp2[(grp2['carrier'] == 'T-Mobile') & (grp2['enabled_radio_type'] == '5G-NSA-Low-Band')]
ax1 = fig.add_subplot(222)
ax1.scatter(dfnsatm['interval'], dfnsatm['RTT_median'], c=dfnsatm['color'])

dfnsavz = grp[(grp['carrier'] == 'Verizon') & (grp['enabled_radio_type'] == '5G-NSA-Low-Band')]
ax2 = fig.add_subplot(223)
ax2.scatter(dfnsavz['interval'], dfnsavz['RTT_median'], c=dfnsavz['color'])

dfltetm = grp[(grp['carrier'] == 'TMobile') & (grp['enabled_radio_type'] == '4G-LTE')]
# dfltetm = grp2[(grp2['carrier'] == 'T-Mobile') & (grp2['enabled_radio_type'] == '4G-LTE')]
ax3 = fig.add_subplot(224)
ax3.scatter(dfltetm['interval'], dfltetm['RTT_median'], c=dfltetm['color'])

ax2.set_ylim(0, 1780)
ax2.set_yticks(np.arange(0, 1780, 500), minor=False)
ax2.set_xlim(7.8, 15.2)
nsa2_conn = patches.Rectangle((7.8, 1650), 10.2 - 7.8, 200, linewidth=1, edgecolor='forestgreen',
                              facecolor='forestgreen')
nsa2_idle = patches.Rectangle((10.2, 1650), 15.2 - 10.2, 200, linewidth=1, edgecolor='magenta', facecolor='magenta')
ax2.add_patch(nsa2_conn)
ax2.add_patch(nsa2_idle)

ax0.set_ylim(0, 1880)
ax0.set_yticks(np.arange(0, 1880, 500), minor=False)
ax0.set_xlim(7.8, 20.2)
sa_conn = patches.Rectangle((7.8, 1750), 10.2 - 7.8, 200, linewidth=1, edgecolor='forestgreen', facecolor='forestgreen',
                            label='RRC_CONNECTED')
sa_inac = patches.Rectangle((10.2, 1750), 15.0 - 10.2, 200, linewidth=1, edgecolor='crimson', facecolor='crimson',
                            label='RRC_INACTIVE')
sa_idle = patches.Rectangle((15.0, 1750), 20.2 - 15, 200, linewidth=1, edgecolor='magenta', facecolor='magenta',
                            label='RRC_IDLE')
ax0.add_patch(sa_conn)
ax0.add_patch(sa_inac)
ax0.add_patch(sa_idle)

ax1.set_ylim(0, 1880)
ax1.set_yticks(np.arange(0, 1880, 500), minor=False)
ax1.set_xlim(7.8, 19.0)
nsa1_conn = patches.Rectangle((7.8, 1750), 10.2 - 7.8, 200, linewidth=1, edgecolor='forestgreen',
                              facecolor='forestgreen', label='RRC_CONNECTED')
nsa1_idle = patches.Rectangle((10.2, 1750), 19.0 - 10.2, 200, linewidth=1, edgecolor='magenta', facecolor='magenta',
                              label='RRC_IDLE')
ax1.add_patch(nsa1_conn)
ax1.add_patch(nsa1_idle)

ax3.set_ylim(0, 1780)
ax3.set_yticks(np.arange(0, 1780, 500), minor=False)
ax3.set_xlim(7.8, 15.2)
# ax3.set_xlim(0, 15.2)
fourg_conn = patches.Rectangle((7.8, 1650), 10.2 - 7.8, 200, linewidth=1, edgecolor='forestgreen',
                               facecolor='forestgreen', label='RRC_CONNECTED')
fourg_idle = patches.Rectangle((10.1, 1650), 15.2 - 10.1, 200, linewidth=1, edgecolor='magenta', facecolor='magenta',
                               label='RRC_IDLE')
inac_label = patches.Rectangle((18.2, 1650), 15.0 - 10.2, 0, linewidth=1, edgecolor='crimson', facecolor='crimson',
                               label='RRC_INACTIVE')
ax3.add_patch(fourg_conn)
ax3.add_patch(fourg_idle)
ax3.add_patch(inac_label)

ax0.set_title('T-Mobile SA 5G', fontsize=18)
ax1.set_title('T-Mobile NSA 5G', fontsize=18)
ax2.set_title('Verizon NSA 5G', fontsize=18)
ax3.set_title('T-Mobile 4G', fontsize=18)
# ax2.legend(loc='lower center', fontsize=15, bbox_to_anchor=(0.4, -0.8), ncol=2, facecolor='whitesmoke')
lgd1 = plt.legend([fourg_conn, fourg_idle, inac_label], ['RRC_CONNECTED', 'RRC_IDLE', 'RRC_INACTIVE'], fontsize=15, ncol=3,
           loc='lower center', bbox_to_anchor=(0.2, -0.8), facecolor='whitesmoke')

fourG, = plt.plot([-500,-500],'-', color='#1f77b4')
fiveG, = plt.plot([-500,-500],'-', color='#ff7f0e')
# legend2 = ax2.legend((fourG, fiveG),('4G', '5G'), loc='lower center',
#                     facecolor='whitesmoke', handlelength=1, ncol=4, fontsize=14, bbox_to_anchor=(0.09, 1.43), title='Active Radio', title_fontsize=15, borderpad=.3)

ax2.set_xlabel("Idle Time between Packets (s)", fontsize=18)
ax3.set_xlabel("Idle Time between Packets (s)", fontsize=18)
ax2.set_ylabel("RTT (ms)", fontsize=20)
ax0.set_ylabel("RTT (ms)", fontsize=20)
ax0.tick_params(axis="both", labelsize=18)
ax3.tick_params(axis="both", labelsize=18)
ax1.tick_params(axis="both", labelsize=18)
ax2.tick_params(axis="both", labelsize=18)



plt.tight_layout()
plotme(plt, plot_id, plot_name, show_flag=SHOW_PLOT_FLAG, png_only=False, pad_inches=0.07)