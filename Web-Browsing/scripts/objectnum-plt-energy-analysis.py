import json
import os
import re
import pickle
import pickle
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import random
import numpy as np
from utils import mergeList


webset_threshold = 3
manual_seed = 42
random.seed(manual_seed)


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


obj_num_plt_4g = {}
obj_num_plt_5g = {}


asset_number_plt_4g_dict = {}
asset_number_plt_5g_dict = {}

pagesize_plt_4g_dict = {}
pagesize_plt_5g_dict = {}

energy_plt_4g_dict = {}
energy_plt_5g_dict = {}

for i in filtered_webSet:
    if (not ((i, '4G') in fileStatistics.keys())) or (not ((i, '5G') in fileStatistics.keys())):
        continue
    #ipdb.set_trace()
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
    

    
    merge_feature_dict = mergeList(fileStatistics[(i, '4G')] + fileStatistics[(i, '5G')])


    objNum = merge_feature_dict["objectNumber"]
    pageSize = merge_feature_dict["pageSize"]
    if not (objNum in asset_number_plt_4g_dict.keys()):
        asset_number_plt_4g_dict[objNum] = []
        asset_number_plt_5g_dict[objNum] = []
    if not (objNum in energy_plt_4g_dict.keys()):
        energy_plt_4g_dict[objNum] = []
        energy_plt_5g_dict[objNum] = []
    
    asset_number_plt_4g_dict[objNum].append(dict_4g['onLoad'])
    asset_number_plt_5g_dict[objNum].append(dict_5g['onLoad'])

    energy_plt_4g_dict[objNum].append(dict_4g['network_energy'])
    energy_plt_5g_dict[objNum].append(dict_5g['network_energy'])

  

#deal with the asset_number_plt relationship drawing


labelList = []


show_label_list = ["0-10", "11-100", "100-1000"]
asset_number_plt_final_dict_4g = {}
asset_number_plt_final_dict_5g = {}
asset_number_energy_final_dict_5g = {}
asset_number_energy_final_dict_4g = {}
asset_number_energy_final_dict_5g = {}
asset_number_energy_final_dict_4g = {}
for label in show_label_list:
    asset_number_plt_final_dict_4g[label] = []
    asset_number_plt_final_dict_5g[label] = []
    asset_number_energy_final_dict_5g[label] = []
    asset_number_energy_final_dict_4g[label] = []
for key in asset_number_plt_4g_dict.keys():
    if (key < 10):
        asset_number_plt_final_dict_4g["0-10"] += asset_number_plt_4g_dict[key]
        asset_number_plt_final_dict_5g["0-10"] += asset_number_plt_5g_dict[key]
        asset_number_energy_final_dict_5g["0-10"] += energy_plt_5g_dict[key]
        asset_number_energy_final_dict_4g["0-10"] += energy_plt_4g_dict[key]
    elif (key < 100):
        asset_number_plt_final_dict_4g["11-100"] += asset_number_plt_4g_dict[key]
        asset_number_plt_final_dict_5g["11-100"] += asset_number_plt_5g_dict[key]    
        asset_number_energy_final_dict_5g["11-100"] += energy_plt_5g_dict[key]
        asset_number_energy_final_dict_4g["11-100"] += energy_plt_4g_dict[key]
    else:
        asset_number_plt_final_dict_4g["100-1000"] += asset_number_plt_4g_dict[key]
        asset_number_plt_final_dict_5g["100-1000"] += asset_number_plt_5g_dict[key]         
        asset_number_energy_final_dict_5g["100-1000"] += energy_plt_5g_dict[key]
        asset_number_energy_final_dict_4g["100-1000"] += energy_plt_4g_dict[key] 


Ylabel4g = []
Ylabel5g = []
energy5g = []
energy4g = []
for k in asset_number_plt_final_dict_4g.keys():
    if (len(asset_number_plt_final_dict_4g[k])) == 0:
        continue
    labelList.append(k)
    mean4g = sum(asset_number_plt_final_dict_4g[k]) / len(asset_number_plt_final_dict_5g[k]) * 0.001
    Ylabel4g.append(mean4g)
    mean5g = sum(asset_number_plt_final_dict_5g[k]) / len(asset_number_plt_final_dict_5g[k]) * 0.001
    Ylabel5g.append(mean5g)
    energy5g.append(sum(asset_number_energy_final_dict_5g[k]) / len(asset_number_energy_final_dict_5g[k]) * 0.001 * 0.001)
    energy4g.append(sum(asset_number_energy_final_dict_4g[k]) / len(asset_number_energy_final_dict_4g[k]) * 0.001 * 0.001)

if (len(labelList) == 2):
    show_label_list = ['11-100', '100-1000']

fig = plt.figure(figsize=(5.32, 5))
ax = fig.add_subplot(211) 
ax2 = fig.add_subplot(212, sharex = ax)
x4g = range(len(labelList))


rects1 = ax.bar(x4g, height = Ylabel4g, width=0.3, alpha=0.8, color='red', label="4G PLT")
rects2 = ax.bar([i + 0.3 for i in x4g], height=Ylabel5g, width=0.3, alpha = 0.8, color='white', ecolor='red', edgecolor='red', label="5G PLT", hatch='/')

# ax2=ax.twinx()
rects3= ax2.bar([i for i in x4g], energy4g, width=0.3, alpha=0.8, color='blue', label='4G Energy')
rects4= ax2.bar([i + 0.3 for i in x4g], height=energy5g, width=0.3, alpha=0.8, color='white', ecolor='blue', edgecolor='blue', hatch='/', label='5G Energy')


ax2.set_xlabel("Number of Objects", fontsize = 20)
ax.get_xaxis().set_visible(False)
ax2.set_xticks([index + 0.15 for index in x4g])
ax2.set_xticklabels(show_label_list, fontsize = 17)
ax.set_ylabel("PLT (Sec)", fontsize = 22)
ax2.set_ylabel('Energy (J)', fontsize = 22)
ax.set_ylim(0, 8.2)
ax.set_yticks(np.arange(0, 8.1, 2.0))
ax.tick_params(axis="y", labelsize = 20)
ax2.set_ylim(0, 8.2)
ax2.set_yticks(np.arange(0, 8.1, 2.0))
ax2.tick_params(axis="y", labelsize = 20)

ax.set_axisbelow(True)
ax.yaxis.grid(linestyle='dashed')
ax2.set_axisbelow(True)
ax2.yaxis.grid(linestyle='dashed')
ax.legend(fontsize=18)
ax2.legend(fontsize=16)
fig.tight_layout()
plt.subplots_adjust(hspace=.12)

plt.savefig('./results/objectnum-plt-energy-relation.pdf')
plt.close('all')



