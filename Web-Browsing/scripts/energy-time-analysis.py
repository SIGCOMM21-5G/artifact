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
from utils import mergeList, picklePreprocessing

webset_threshold = 3
manual_seed = 42

preprocessed_result = picklePreprocessing(web_pickle_name = './processed_dataset/WebSet.pickle',
                        file_pickle_name = './processed_dataset/fileStatistics.pickle', 
                        webset_threshold = webset_threshold)
energy_plt_dict = preprocessed_result['energy_plt_dict']   


key_list = list(energy_plt_dict.keys())
key_list.sort()
print(key_list)
box_list = []

x = []
y_min = []
y_max = []
y_average = []
for i in key_list:
    if (i < 50):
        x.append(i)
        temp_list = energy_plt_dict[i]
        box_list.append(energy_plt_dict[i])

fig = plt.figure(figsize=(8.5, 4.3))


if (len(x) < 5):
    #for toy demo
    final_labels = ["0-10",  "30-40", "40-50"]
else:
    final_labels = ["0-10", "10-20", "20-30", "30-40", "40-50"]
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
plt.savefig('./plots/energy-plt-relation.pdf')
