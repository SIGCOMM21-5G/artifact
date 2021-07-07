import json
import os
import re
import pickle
from haralyzer import HarParser, HarPage
import pickle
import matplotlib.pyplot as plt
from sklearn import tree
import graphviz
import seaborn as sns
import sklearn
from collections import Counter
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MaxAbsScaler
import random
from sklearn.ensemble import RandomForestClassifier
import numpy as np
from utils import mergeList, picklePreprocessing
from matplotlib.font_manager import FontProperties


webset_threshold = 3

manual_seed = 42
random.seed(manual_seed)


preprocessed_result = picklePreprocessing(web_pickle_name = './processed_dataset/WebSet.pickle',
                        file_pickle_name = './processed_dataset/fileStatistics.pickle', 
                        webset_threshold = webset_threshold)
                
plt_5g_energy_list = preprocessed_result['plt_5g_energy_list']
plt_4g_energy_list = preprocessed_result['plt_4g_energy_list']
plt_5g_plt_list = preprocessed_result['plt_5g_plt_list']
plt_4g_plt_list = preprocessed_result['plt_4g_plt_list']

"""
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



plt_5g_energy_list = []
plt_4g_energy_list = []
plt_5g_plt_list = []
plt_4g_plt_list = []


power_all_list = []
energy_all_list = []
plt_all_list = []

total_num = 0

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
    

    total_num += 1
    plt_5g_energy_list.append(dict_5g['network_energy']*1e-6)
    plt_4g_energy_list.append(dict_4g['network_energy']*1e-6)
    plt_5g_plt_list.append(dict_5g['onLoad']*1e-3)
    plt_4g_plt_list.append(dict_4g['onLoad']*1e-3)

"""

fig = plt.figure(figsize=(8, 4))
ax = fig.add_subplot(111)
ax.set_axisbelow(True)
ax.yaxis.grid(linestyle='dashed')
ax.xaxis.grid(linestyle='dashed')
original5g = sns.distplot(plt_5g_energy_list, color='blue', kde_kws={'cumulative': True, "lw": 5, 'linestyle':'--'}, hist = False, label='5G')
original4g = sns.distplot(plt_4g_energy_list, color='red', kde_kws={'cumulative': True, "lw": 5}, hist = False, label='4G')

plt.rcParams['pdf.fonttype'] = 42
plt.xticks(fontsize=50)
plt.yticks(fontsize=40)
plt.xlabel("Energy (J)", fontsize=50)
plt.ylabel("CDF", fontsize=50)

plt.legend(prop = {'size':40}, loc='lower right', bbox_to_anchor=(0.98,-0.05))
fig.tight_layout()
plt.savefig('./results/cdf-energy.pdf')

plt.cla()


fig2 = plt.figure(figsize=(8, 4))
ax = fig2.add_subplot(111)
ax.set_axisbelow(True)
ax.yaxis.grid(linestyle='dashed')
ax.xaxis.grid(linestyle='dashed')
original5g = sns.distplot(plt_5g_plt_list, color='blue', kde_kws={'cumulative': True, "lw": 5, 'linestyle':'--'}, hist = False, label='5G')
original4g = sns.distplot(plt_4g_plt_list, color='red', kde_kws={'cumulative': True, "lw": 5}, hist = False, label='4G')

plt.rcParams['pdf.fonttype'] = 42
plt.xticks(fontsize=50)
plt.yticks(fontsize=40)
plt.xlabel("PLT (s)", fontsize=50)
plt.ylabel("CDF", fontsize=30)
plt.legend(prop = {'size':40}, loc='lower right', bbox_to_anchor=(0.98,-0.05))
fig2.tight_layout()
plt.savefig('./results/cdf-plt.pdf')
