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
from utils import mergeList, picklePreprocessing


webset_threshold = 3
manual_seed = 42
random.seed(manual_seed)

preprocessed_result = picklePreprocessing(web_pickle_name = './processed_dataset/WebSet.pickle',
                        file_pickle_name = './processed_dataset/fileStatistics.pickle', 
                        webset_threshold = webset_threshold)
asset_number_plt_5g_dict = preprocessed_result['asset_number_plt_5g_dict']
asset_number_plt_4g_dict = preprocessed_result['asset_number_plt_4g_dict']
energy_plt_5g_dict = preprocessed_result['energy_plt_5g_dict']
energy_plt_4g_dict = preprocessed_result['energy_plt_4g_dict']
  

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



