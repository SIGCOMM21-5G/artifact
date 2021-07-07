import json
import os
import re
import pickle
import pickle
import matplotlib.pyplot as plt
from utils import mergeList, picklePreprocessing, treeFeatureGeneration
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


webset_threshold = 3
lambda_ratio = 2
lambda_power_ratio = 1
alpha = 0.2
beta = 0.8
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

        dict_4g, dict_5g = treeFeatureGeneration(alpha, beta, dict_4g, dict_5g, standard_tuple, mn_tuple)
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
        
       

preprocessed_result = picklePreprocessing(web_pickle_name = './processed_dataset/WebSet.pickle',
                        file_pickle_name = './processed_dataset/fileStatistics.pickle', 
                        webset_threshold = webset_threshold)
filtered_webSet = preprocessed_result['filtered_webSet'] 
fileStatistics = preprocessed_result['fileStatistics']
final_statistics = preprocessed_result['final_statistics']
standard_power = preprocessed_result['standard_power']
standard_plt = preprocessed_result['standard_plt']
standard_energy = preprocessed_result['standard_energy']
mn_power = preprocessed_result['mn_power']
mn_plt = preprocessed_result['mn_plt']
mn_energy = preprocessed_result['mn_energy']
standard_tuple = (standard_plt, standard_power, standard_energy)
mn_tuple = (mn_plt, mn_power, mn_energy)
webSet_train, webSet_test = sklearn.model_selection.train_test_split(filtered_webSet, test_size = 0.3, random_state = manual_seed)


#build the decision tree model label, the label 0 means choose 4G and 1 means choose 5G
label_list = []
data_list = []
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

    dict_4g, dict_5g = treeFeatureGeneration(alpha, beta, dict_4g, dict_5g, standard_tuple, mn_tuple)

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



clf = tree.DecisionTreeClassifier(max_depth = 2, min_samples_leaf = 50, random_state = manual_seed)
clf.fit(data_list, label_list)


dot_data = tree.export_graphviz(clf, out_file='./results/tree.dot', 
                         feature_names=["pageSize","objectNumber","averageObjectSize", 
                         "imageNum", "VideoNum", "dynamicObjRatio", "dynamicObjSizeRatio"],
                         class_names=['4G','5G'],
                         filled=True, rounded=True,  
                         special_characters=True)  
graph = graphviz.Source(dot_data)  


treePredict()
os.system('dot -Tpng ./results/tree.dot -o ./results/tree-M1.png')