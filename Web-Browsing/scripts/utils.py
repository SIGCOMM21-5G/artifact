import numpy as np
import pickle
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import StandardScaler

def mergeList(informationList):
    final_dict = {}
    final_dict["protocolNumber"] = 0.0
    final_dict["onContentLoad"] = 0.0
    final_dict["onLoad"] = 0.0
    final_dict["pageSize"] = 0.0
    final_dict["protocol"] = set()
    final_dict["objectNumber"] = 0.0
    final_dict["averageObjectSize"] = 0.0
    final_dict["protocolCounter"] = [0, 0, 0]
    final_dict["memeCounter"] = [0, 0]
    throughput_num = 0
    final_dict["throughput"] = 0
    tempInterSet = set(informationList[0]["urllist"])

    #identify the outlier
    onLoadList = []
    for i in informationList:
        onLoadList.append(i["onLoad"])
    
    range_length = np.quantile(onLoadList, 0.75) - np.quantile(onLoadList, 0.25)
    median = np.median(onLoadList)

    webnum = 0
    for i in informationList:

        if (i["onLoad"] > (median + (1.5* range_length)) or i["onLoad"] < (median - (1.5 * range_length))):
            continue
        webnum += 1
        tempInterSet = tempInterSet & set(i["urllist"])
        final_dict["title"] = i["title"]
        final_dict["protocolNumber"] += i["protocolNumber"]
        final_dict["onContentLoad"] += i["onContentLoad"]
        final_dict["onLoad"] += i["onLoad"]
        final_dict["pageSize"] += i["pageSize"]
        final_dict["protocol"] = final_dict["protocol"] | i["protocol"]
        final_dict["objectNumber"] += i["objectNumber"]
        final_dict["averageObjectSize"] += i["averageObjectSize"]
        final_dict["protocolCounter"] = [a + b for a, b in zip(final_dict["protocolCounter"], i["protocolCounter"])]
        final_dict["memeCounter"] = [a + b for a, b in zip(final_dict["memeCounter"], i["memeCounter"])]
        if ("throughput" in i.keys()):
            final_dict["throughput"] += i["throughput"]
            throughput_num += 1
    if (throughput_num > 0):
        final_dict["throughput"] = final_dict["throughput"] / throughput_num
    else:
        final_dict["throughput"] = 0

    staticObjSizeSum = 0
    for i in informationList:
        if (i["onLoad"] > (median + (1.5* range_length)) or i["onLoad"] < (median - (1.5 * range_length))):
            continue  
        for website in tempInterSet:
            staticObjSizeSum += i["urlDict"][website]

    final_dict["protocolNumber"] = final_dict["protocolNumber"]/webnum
    final_dict['staticObjSizeSum'] = staticObjSizeSum/webnum
    final_dict["onContentLoad"] = final_dict["onContentLoad"] / webnum
    final_dict["onLoad"] = final_dict["onLoad"] / webnum
    final_dict["pageSize"] = final_dict["pageSize"] / webnum
    final_dict["objectNumber"] = int(final_dict["objectNumber"] / webnum)
    final_dict["averageObjectSize"] = int(final_dict["averageObjectSize"] / webnum)
    final_dict["staticObjNum"] = len(tempInterSet)
    final_dict["dynamicObjNum"] = final_dict["objectNumber"] - len(tempInterSet)
    final_dict["staticObjratio"] = len(tempInterSet) / final_dict["objectNumber"]
    final_dict["dynamicObjratio"] = 1 - final_dict["staticObjratio"]
    request_sum = sum(final_dict["protocolCounter"])
    final_dict["protocolCounter"] = [i / request_sum for i in final_dict["protocolCounter"]]
    final_dict["dynamic-size-ratio"] = 1 - final_dict["staticObjSizeSum"] / final_dict["pageSize"]
    return final_dict


def picklePreprocessing(web_pickle_name, file_pickle_name, webset_threshold):
    with open(web_pickle_name, 'rb') as f:
        webSet = pickle.load(f)
    with open(file_pickle_name, 'rb') as f:
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

    plt_5g_energy_list = []
    plt_4g_energy_list = []
    plt_5g_plt_list = []
    plt_4g_plt_list = []


    power_all_list = []
    energy_all_list = []
    plt_all_list = []

    mn_power = MinMaxScaler()
    mn_energy = MinMaxScaler()
    mn_plt = MinMaxScaler()
    standard_power = StandardScaler()
    standard_energy = StandardScaler()
    standard_plt = StandardScaler()


    asset_number_plt_4g_dict = {}
    asset_number_plt_5g_dict = {}

    pagesize_plt_4g_dict = {}
    pagesize_plt_5g_dict = {}

    energy_plt_4g_dict = {}
    energy_plt_5g_dict = {}

    energy_pagesize_4g_dict = {}
    energy_pagesize_5g_dict = {}

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
        plt_all_list += [[dict_4g['onLoad']], [dict_5g['onLoad']]]
        power_all_list += [[dict_4g['power']], [dict_5g['power']]]
        energy_all_list += [[dict_4g['network_energy']], [dict_5g['network_energy']]]
        
        if (dict_4g['onLoad'] > dict_5g['onLoad']):
            time_percent_cost = int(int((dict_4g['onLoad'] - dict_5g['onLoad']) * 100/ dict_5g['onLoad'])/10)*10
            energy_reduction = int(dict_5g['network_energy'] - dict_4g['network_energy']) / dict_5g['network_energy']
            if not(time_percent_cost in energy_plt_dict.keys()):
                energy_plt_dict[time_percent_cost] = []
            energy_plt_dict[time_percent_cost].append(energy_reduction*100)


        total_num += 1
        plt_5g_energy_list.append(dict_5g['network_energy']*1e-6)
        plt_4g_energy_list.append(dict_4g['network_energy']*1e-6)
        plt_5g_plt_list.append(dict_5g['onLoad']*1e-3)
        plt_4g_plt_list.append(dict_4g['onLoad']*1e-3)


        merge_feature_dict = mergeList(fileStatistics[(i, '4G')] + fileStatistics[(i, '5G')])

        objNum = merge_feature_dict["objectNumber"]
        pageSize = merge_feature_dict["pageSize"]
        if not (objNum in asset_number_plt_4g_dict.keys()):
            asset_number_plt_4g_dict[objNum] = []
            asset_number_plt_5g_dict[objNum] = []
        if not (objNum in energy_plt_4g_dict.keys()):
            energy_plt_4g_dict[objNum] = []
            energy_plt_5g_dict[objNum] = []
        if not (pageSize in pagesize_plt_4g_dict.keys()):
            pagesize_plt_4g_dict[pageSize] = []
            pagesize_plt_5g_dict[pageSize] = []
        if not (pageSize in energy_pagesize_4g_dict.keys()):
            energy_pagesize_4g_dict[pageSize] = []
            energy_pagesize_5g_dict[pageSize] = []

        asset_number_plt_4g_dict[objNum].append(dict_4g['onLoad'])
        asset_number_plt_5g_dict[objNum].append(dict_5g['onLoad'])

        energy_plt_4g_dict[objNum].append(dict_4g['network_energy'])
        energy_plt_5g_dict[objNum].append(dict_5g['network_energy'])

        pagesize_plt_4g_dict[pageSize].append(dict_4g['onLoad'])
        pagesize_plt_5g_dict[pageSize].append(dict_5g['onLoad'])

        energy_pagesize_4g_dict[pageSize].append(dict_4g['network_energy'])
        energy_pagesize_5g_dict[pageSize].append(dict_5g['network_energy'])
        
    #get the normalizer and standard
    power_all_list = standard_power.fit_transform(power_all_list)
    plt_all_list = standard_plt.fit_transform(plt_all_list)
    energy_all_list = standard_energy.fit_transform(energy_all_list)
    mn_power.fit(power_all_list)
    mn_plt.fit(plt_all_list)
    mn_energy.fit(energy_all_list)

    preprocessed_data = {'filtered_webSet':filtered_webSet, 
    'fileStatistics': fileStatistics,
    'final_statistics': final_statistics,
    'energy_plt_dict':energy_plt_dict,
    'plt_5g_energy_list':plt_5g_energy_list, 
    'plt_4g_energy_list':plt_4g_energy_list,
    'plt_5g_plt_list':plt_5g_plt_list,
    'plt_4g_plt_list':plt_4g_plt_list,
    'power_all_list':power_all_list,
    'energy_all_list':energy_all_list,
    'plt_all_list':plt_all_list,
    'mn_power':mn_power,
    'mn_energy':mn_energy,
    'mn_plt':mn_plt,
    'standard_power':standard_power,
    'standard_energy':standard_energy,
    'standard_plt':standard_plt,
    'asset_number_plt_4g_dict':asset_number_plt_4g_dict, 
    'asset_number_plt_5g_dict':asset_number_plt_5g_dict,
    'pagesize_plt_4g_dict':pagesize_plt_4g_dict, 
    'pagesize_plt_5g_dict':pagesize_plt_5g_dict, 
    'energy_plt_4g_dict':energy_plt_4g_dict,
    'energy_plt_5g_dict':energy_plt_5g_dict,
    'energy_pagesize_4g_dict':energy_pagesize_4g_dict,
    'energy_pagesize_5g_dict':energy_pagesize_5g_dict,
    'total_num':total_num}
    
    return preprocessed_data


def treeFeatureGeneration(alpha, beta, dict_4g, dict_5g, standard_tuple, mn_tuple):
    standard_plt, standard_power, standard_energy = standard_tuple
    mn_plt, mn_power, mn_energy = mn_tuple
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

    return dict_4g, dict_5g