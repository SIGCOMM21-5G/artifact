#draw the graph between plt saving and energy saving
import json
import os
import re
import pickle
import pickle
import matplotlib.pyplot as plt
from sklearn import tree
import seaborn as sns
from collections import Counter
import random
import numpy as np
from utils import mergeList

webset_threshold = 4
manual_seed = 42
                        

with open('./processed_dataset/WebSet.pickle', 'rb') as f:
    webSet = pickle.load(f)
with open('./processed_dataset/fileStatistics.pickle', 'rb') as f:
    fileStatistics = pickle.load(f)

webSet = list(webSet)
webSet.sort()

filtered_webSet = []
for i in webSet:
    if (not ((i, '4G') in fileStatistics.keys())) or (not ((i, '5G') in fileStatistics.keys())):
        continue
    if ((len(fileStatistics[(i, "4G")]) <= webset_threshold) or (len(fileStatistics[(i, "5G")]) <= webset_threshold)):
        continue
    dict_4g = mergeList(fileStatistics[(i, '4G')])
    dict_5g = mergeList(fileStatistics[(i, '5G')])
    #filter the website which have a really long loading time
    if (dict_4g['onLoad'] > 15000 and dict_5g['onLoad'] > 15000):
        continue
    filtered_webSet.append(i)




final_statistics = {}
energy_plt_dict = {}


for i in filtered_webSet:
    if (not ((i, '4G') in fileStatistics.keys())) or (not ((i, '5G') in fileStatistics.keys())):
        continue

    if ((len(fileStatistics[(i, "4G")]) <= webset_threshold) or (len(fileStatistics[(i, "5G")]) <= webset_threshold)):
        continue
    final_statistics[(i, "4G")] = mergeList(fileStatistics[(i, '4G')])
    final_statistics[(i, "5G")] = mergeList(fileStatistics[(i, '5G')])
    dict_4g = final_statistics[(i, "4G")]
    dict_5g = final_statistics[(i, "5G")]

    #add the energy consumption calculated from the throughput
    dict_4g['power'] = 13.38 * float(dict_4g['throughput']) + 936.1
    dict_5g['power'] = 2.062 * float(dict_5g['throughput']) + 3352
    dict_4g['network_energy'] = dict_4g['power'] * dict_4g['onContentLoad']
    dict_5g['network_energy'] = dict_5g['power'] * dict_5g['onContentLoad']
    
    if (dict_4g['onLoad'] > dict_5g['onLoad']):
        time_percent_cost = int(int((dict_4g['onLoad'] - dict_5g['onLoad']) * 100/ dict_5g['onLoad'])/10)*10
        energy_reduction = int(dict_5g['network_energy'] - dict_4g['network_energy']) / dict_5g['network_energy']
        if not(time_percent_cost in energy_plt_dict.keys()):
            energy_plt_dict[time_percent_cost] = []
        energy_plt_dict[time_percent_cost].append(energy_reduction*100)


key_list = list(energy_plt_dict.keys())
key_list.sort()

box_list = []

x = []
y_min = []
y_max = []
y_average = []
for i in key_list:
    if (i < 60):
        x.append(i)
        temp_list = energy_plt_dict[i]
        box_list.append(energy_plt_dict[i])

fig = plt.figure(figsize=(8.5, 4.3))
final_labels = ["0-10", "10-20", "20-30", "30-40", "40-50", "50-60"]#, "60-70"]
b = plt.boxplot(box_list, labels = final_labels, showfliers=False, patch_artist=True)
for box in b['boxes']:
    box.set(color='lightblue')
    box.set(edgecolor='black')
    box.set(linewidth=1.5)
    # box.set(hatch='/')
for med in b['medians']:
    med.set(color='darkblue', linewidth=1.5)

plt.xticks()
plt.yticks()
plt.xlabel("Penalty of additional PLT (%)")
plt.ylabel("% of energy saving over\nthe penalised PLT")
plt.rcParams['pdf.fonttype'] = 42
fig.tight_layout()
# Show the plot
plt.savefig('./generated_figure/energy-plt-relation.pdf')
