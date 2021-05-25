import json
import os
import re
import pickle
import pickle
import matplotlib.pyplot as plt
from utils import mergeList
from sklearn import tree
import graphviz
import seaborn as sns
import sklearn
from collections import Counter
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import StandardScaler
import random
from sklearn.ensemble import RandomForestClassifier
import numpy as np


webset_threshold = 4
lambda_ratio = 2
lambda_power_ratio = 1
alpha = 0.6
beta = 0.4
manual_seed = 42
random.seed(manual_seed)



def treePredict():
    #build the decision tree model label, the label 0 means choose 4G and 1 means choose 5G
    label_list = []
    predict_label_list = []
    data_list = []
    total_num = 0

    for i in webSet_test:
        if (not ((i, '4G') in fileStatistics.keys())) or (not ((i, '5G') in fileStatistics.keys())):
            continue
        #ipdb.set_trace()
        if ((len(fileStatistics[(i, "4G")]) <= 1) or (len(fileStatistics[(i, "5G")]) <= 1)):
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


      
        #standarization part
        dict_4g['onLoad'] = standard_plt.transform([[dict_4g['onLoad']]])[0][0]
        dict_5g['onLoad'] = standard_plt.transform([[dict_5g['onLoad']]])[0][0]
        dict_4g['power'] = standard_power.transform([[dict_4g['power']]])[0][0]
        dict_5g['power'] = standard_power.transform([[dict_5g['power']]])[0][0]
        dict_4g['network_energy'] = standard_energy.transform([[dict_4g['network_energy']]])[0][0]
        dict_5g['network_energy'] = standard_energy.transform([[dict_5g['network_energy']]])[0][0]

        #normalization
        
        dict_4g['onLoad'] = mn_plt.transform([[dict_4g['onLoad']]])[0][0]
        dict_5g['onLoad'] = mn_plt.transform([[dict_5g['onLoad']]])[0][0]
        dict_4g['power'] = mn_power.transform([[dict_4g['power']]])[0][0]
        dict_5g['power'] = mn_power.transform([[dict_5g['power']]])[0][0]
        dict_4g['network_energy'] = mn_energy.transform([[dict_4g['network_energy']]])[0][0]
        dict_5g['network_energy'] = mn_energy.transform([[dict_5g['network_energy']]])[0][0]
  
       
        dict_4g['comparison_metric'] = dict_4g['network_energy'] * alpha + dict_4g['onLoad'] * beta
        dict_5g['comparison_metric'] = dict_5g['network_energy'] * alpha + dict_5g['onLoad'] * beta
        total_num += 1


        #construct the decision tree dataset
        if (dict_4g['comparison_metric'] < dict_5g['comparison_metric']):
            label_list.append(0)
        else:
            label_list.append(1)

        merge_feature_dict = mergeList(fileStatistics[(i, '4G')] + fileStatistics[(i, '5G')])
        feature_list = [merge_feature_dict["pageSize"], merge_feature_dict["objectNumber"], merge_feature_dict["averageObjectSize"],  
             merge_feature_dict["memeCounter"][0], merge_feature_dict["memeCounter"][1], 
            merge_feature_dict["dynamicObjratio"], merge_feature_dict["dynamic-size-ratio"]]
        data_list.append(feature_list)

        predict_label = clf.predict([feature_list])[0]
        predict_label_list.append(predict_label)
        
       
    #print('Counter2', Counter(predict_label_list))
    #print('accuracy', sklearn.metrics.accuracy_score(label_list, predict_label_list))
 




with open('WebSet.pickle', 'rb') as f:
    webSet = pickle.load(f)
with open('fileStatistics.pickle', 'rb') as f:
    fileStatistics = pickle.load(f)

webSet = list(webSet)
webSet.sort()

#filter the webset 
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


webSet_train, webSet_test = sklearn.model_selection.train_test_split(filtered_webSet, test_size = 0.3, random_state = manual_seed)

final_statistics = {}
#build the decision tree model label, the label 0 means choose 4G and 1 means choose 5G
label_list = []
data_list = []
total_num = 0
#list to record the long time website

power_all_list = []
energy_all_list = []
plt_all_list = []

mn_power = MinMaxScaler()
mn_energy = MinMaxScaler()
mn_plt = MinMaxScaler()
standard_power = StandardScaler()
standard_energy = StandardScaler()
standard_plt = StandardScaler()


#add the normalization part
for i in filtered_webSet:
    if (not ((i, '4G') in fileStatistics.keys())) or (not ((i, '5G') in fileStatistics.keys())):
        continue
    #ipdb.set_trace()
    if ((len(fileStatistics[(i, "4G")]) <= webset_threshold) or (len(fileStatistics[(i, "5G")]) <= webset_threshold)):
        continue
    dict_4g = mergeList(fileStatistics[(i, '4G')])
    dict_5g = mergeList(fileStatistics[(i, '5G')])

    dict_4g['power'] = 13.38 * float(dict_4g['throughput']) + 936.1
    dict_5g['power'] = 2.062 * float(dict_5g['throughput']) + 3352
    dict_4g['network_energy'] = dict_4g['power'] * dict_4g['onContentLoad']
    dict_5g['network_energy'] = dict_5g['power'] * dict_5g['onContentLoad']
    plt_all_list += [[dict_4g['onLoad']], [dict_5g['onLoad']]]
    power_all_list += [[dict_4g['power']], [dict_5g['power']]]
    energy_all_list += [[dict_4g['network_energy']], [dict_5g['network_energy']]]




power_all_list = standard_power.fit_transform(power_all_list)
plt_all_list = standard_plt.fit_transform(plt_all_list)
energy_all_list = standard_energy.fit_transform(energy_all_list)
mn_power.fit(power_all_list)
mn_plt.fit(plt_all_list)
mn_energy.fit(energy_all_list)
for i in webSet_train:
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
    
    #standarization part
    dict_4g['onLoad'] = standard_plt.transform([[dict_4g['onLoad']]])[0][0]
    dict_5g['onLoad'] = standard_plt.transform([[dict_5g['onLoad']]])[0][0]
    dict_4g['power'] = standard_power.transform([[dict_4g['power']]])[0][0]
    dict_5g['power'] = standard_power.transform([[dict_5g['power']]])[0][0]
    dict_4g['network_energy'] = standard_energy.transform([[dict_4g['network_energy']]])[0][0]
    dict_5g['network_energy'] = standard_energy.transform([[dict_5g['network_energy']]])[0][0]

    #normalization part
    dict_4g['onLoad'] = mn_plt.transform([[dict_4g['onLoad']]])[0][0]
    dict_5g['onLoad'] = mn_plt.transform([[dict_5g['onLoad']]])[0][0]
    dict_4g['power'] = mn_power.transform([[dict_4g['power']]])[0][0]
    dict_5g['power'] = mn_power.transform([[dict_5g['power']]])[0][0]
    dict_4g['network_energy'] = mn_energy.transform([[dict_4g['network_energy']]])[0][0]
    dict_5g['network_energy'] = mn_energy.transform([[dict_5g['network_energy']]])[0][0]
    

    dict_4g['comparison_metric'] = dict_4g['network_energy'] * alpha + dict_4g['onLoad'] * beta
    dict_5g['comparison_metric'] = dict_5g['network_energy'] * alpha + dict_5g['onLoad'] * beta

    total_num += 1
    #construct the decision tree dataset
    if (dict_4g['comparison_metric'] < dict_5g['comparison_metric']):
        label_list.append(0)
    else:
        label_list.append(1)

    merge_feature_dict = mergeList(fileStatistics[(i, '4G')] + fileStatistics[(i, '5G')])
    feature_list = [merge_feature_dict["pageSize"], merge_feature_dict["objectNumber"], merge_feature_dict["averageObjectSize"],  
             merge_feature_dict["memeCounter"][0], merge_feature_dict["memeCounter"][1], 
            merge_feature_dict["dynamicObjratio"], merge_feature_dict["dynamic-size-ratio"]]
    
    data_list.append(feature_list)


clf = tree.DecisionTreeClassifier(max_depth = 2, min_samples_leaf = 20, random_state = manual_seed)#, class_weight = "balanced")
clf.fit(data_list, label_list)
dot_data = tree.export_graphviz(clf, out_file='tree.dot', 
                         feature_names=["pageSize","objectNumber","averageObjectSize", 
                         "imageNum", "VideoNum", "dynamicObjRatio", "dynamicObjSizeRatio"],#, "ProtocolNumber"],
                         class_names=['4G','5G'],
                         filled=True, rounded=True,  
                         special_characters=True)  
graph = graphviz.Source(dot_data)  


treePredict()
os.system('dot -Tpng tree.dot -o tree-M4.png')