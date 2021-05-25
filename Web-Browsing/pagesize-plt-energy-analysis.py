#draw the pagesize-plt relation
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
random.seed(manual_seed)

with open('WebSet.pickle', 'rb') as f:
    webSet = pickle.load(f)
with open('fileStatistics.pickle', 'rb') as f:
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


    objNum = int(merge_feature_dict["objectNumber"]/100)
    pageSize = merge_feature_dict["pageSize"]
    

    if not (pageSize in pagesize_plt_4g_dict.keys()):
        pagesize_plt_4g_dict[pageSize] = []
        pagesize_plt_5g_dict[pageSize] = []
    if not (pageSize in energy_plt_4g_dict.keys()):
        energy_plt_4g_dict[pageSize] = []
        energy_plt_5g_dict[pageSize] = []

    pagesize_plt_4g_dict[pageSize].append(dict_4g['onLoad'])
    pagesize_plt_5g_dict[pageSize].append(dict_5g['onLoad'])

    energy_plt_4g_dict[pageSize].append(dict_4g['network_energy'])
    energy_plt_5g_dict[pageSize].append(dict_5g['network_energy'])

    feature_list = [merge_feature_dict["pageSize"], merge_feature_dict["objectNumber"], merge_feature_dict["averageObjectSize"], merge_feature_dict["protocolCounter"][0], 
        merge_feature_dict["protocolCounter"][1], merge_feature_dict["protocolCounter"][2], merge_feature_dict["memeCounter"][0], merge_feature_dict["memeCounter"][1], 
        merge_feature_dict["staticObjratio"], merge_feature_dict["dynamicObjratio"], merge_feature_dict["staticObjNum"], merge_feature_dict["dynamicObjNum"]]






labelList = []



#draw pagesize -plt relation graph
show_label_list = ["100KB", "1MB", "33MB"]
pageSize_plt_final_dict_4g = {}
pageSize_plt_final_dict_5g = {}
pageSize_energy_final_dict_5g = {}
pageSize_energy_final_dict_4g = {}

for label in show_label_list:
    pageSize_plt_final_dict_4g[label] = []
    pageSize_plt_final_dict_5g[label] = []
    pageSize_energy_final_dict_5g[label] = []
    pageSize_energy_final_dict_4g[label] = []

for key in pagesize_plt_4g_dict.keys():

    if (key < 1024):
        pageSize_plt_final_dict_4g["100KB"] += pagesize_plt_4g_dict[key]
        pageSize_plt_final_dict_5g["100KB"] += pagesize_plt_5g_dict[key]  
        pageSize_energy_final_dict_5g["100KB"] += energy_plt_5g_dict[key]
        pageSize_energy_final_dict_4g["100KB"] += energy_plt_4g_dict[key]
    elif (key < 10240):
        pageSize_plt_final_dict_4g["1MB"] += pagesize_plt_4g_dict[key]
        pageSize_plt_final_dict_5g["1MB"] += pagesize_plt_5g_dict[key]  
        pageSize_energy_final_dict_5g["1MB"] += energy_plt_5g_dict[key]
        pageSize_energy_final_dict_4g["1MB"] += energy_plt_4g_dict[key] 
    else:
        pageSize_plt_final_dict_4g["33MB"] += pagesize_plt_4g_dict[key]
        pageSize_plt_final_dict_5g["33MB"] += pagesize_plt_5g_dict[key] 
        pageSize_energy_final_dict_5g["33MB"] += energy_plt_5g_dict[key]
        pageSize_energy_final_dict_4g["33MB"] += energy_plt_4g_dict[key]         


Ylabel4g = []
Ylabel5g = []
energy5g = []
energy4g = []

for k in pageSize_plt_final_dict_4g.keys():
    labelList.append(k)
    mean4g = sum(pageSize_plt_final_dict_4g[k]) / len(pageSize_plt_final_dict_4g[k]) * 0.001
    Ylabel4g.append(mean4g)
    mean5g = sum(pageSize_plt_final_dict_5g[k]) / len(pageSize_plt_final_dict_5g[k]) * 0.001
    Ylabel5g.append(mean5g)
    energy5g.append(sum(pageSize_energy_final_dict_5g[k]) / len(pageSize_energy_final_dict_5g[k]) * 0.001 * 0.001)
    energy4g.append(sum(pageSize_energy_final_dict_4g[k]) / len(pageSize_energy_final_dict_4g[k]) * 0.001 * 0.001)
# ipdb.set_trace()

labelList = ['<1', '1-10', '>10']
print('keys', pageSize_plt_final_dict_5g.keys())

fig = plt.figure(figsize=(5.32, 5))
ax = fig.add_subplot(211) 
ax2 = fig.add_subplot(212, sharex = ax)
x4g = range(len(labelList))


rects1 = ax.bar(x4g, height = Ylabel4g, width=0.3, alpha=0.8, color='red', label="4G PLT")
rects2 = ax.bar([i + 0.3 for i in x4g], height=Ylabel5g, width=0.3, alpha = 0.8, color='white', ecolor='red', edgecolor='red', label="5G PLT", hatch='/')


rects3= ax2.bar([i for i in x4g], energy4g, width=0.3, alpha=0.8, color='blue', label='4G Energy')
rects4= ax2.bar([i + 0.3 for i in x4g], height=energy5g, width=0.3, alpha=0.8, color='white', ecolor='blue', edgecolor='blue', hatch='/', label='5G Energy')


ax2.set_xlabel("Total page Size (MB)", fontsize = 20)
ax.get_xaxis().set_visible(False)
ax2.set_xticks([index + 0.15 for index in x4g])
ax2.set_xticklabels(labelList, fontsize = 17, rotation=5)
ax.set_ylabel("PLT (Sec)", fontsize = 22)
ax2.set_ylabel('Energy (J)', fontsize = 22)
ax.set_ylim(0, 10.2)
ax.set_yticks(np.arange(0, 10.1, 2.0))
ax.tick_params(axis="y", labelsize = 20)
ax2.set_ylim(0, 10.2)
ax2.set_yticks(np.arange(0, 10.1, 2.0))
ax2.tick_params(axis="y", labelsize = 20)

ax.set_axisbelow(True)
ax.yaxis.grid(linestyle='dashed')
ax2.set_axisbelow(True)
ax2.yaxis.grid(linestyle='dashed')
ax.legend(fontsize=18)
ax2.legend(fontsize=16)
fig.tight_layout()
plt.subplots_adjust(hspace=.12)
plt.savefig('pagesize-plt-relation.pdf')
plt.close('all')
