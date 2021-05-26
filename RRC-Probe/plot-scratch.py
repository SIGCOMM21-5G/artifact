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

df = pd.read_csv('data/TMob-SA-FULL-combined.csv')
df = df[df['KeepOrDrop'] == 'YEP']
df['RTT'] = (df['RTT1'] + df['RTT2']) / 2

### plotting

plt.figure()
dftemp = df[df['loop'] == 1]
fig = plt.figure(figsize=(11, 8))

# ROW 1

plt.scatter(dftemp['interval'], dftemp['RTT'])
plt.title('Verizon 5G NSA mmWave', fontsize=18)
plt.ylabel("RTT (ms)", fontsize=20)

plt.ylim(0, 1880)
plt.xlim(0, 19)

plt.show()