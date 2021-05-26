import numpy as np

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