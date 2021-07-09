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
plt.savefig('./plots/cdf-energy.pdf')

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
plt.savefig('./plots/cdf-plt.pdf')
