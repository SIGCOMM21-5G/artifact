import json
import os
import re
import pickle
from haralyzer import HarParser, HarPage
from collections import Counter
import scapy 
from scapy.all import *
from scapy.utils import PcapReader
import argparse

def parseTcpdump(fileName):

    packet_size = 0
    newfileName = fileName.replace("har-file", "tcpdump-file")
    newfileName = newfileName.replace(".har", ".pcap")
    if (os.path.exists(newfileName)): 
        packets = rdpcap(newfileName) 
        timeList = []
        for packet in packets:
            if packet.haslayer('IP'):
                timeList.append(packet.time)
                packet_size += packet.wirelen
        if (len(timeList) <= 1):
            return 0
        return packet_size*8/((timeList[len(timeList) - 1] - timeList[0])*1024*1024)
    else:
        return 0


def parseHarFile(fileName):
    flag = True
    informationDict = {}
    with open(fileName, 'r') as f:
        try:
            har_parser = HarParser(json.loads(f.read()))
        except:
            return (False, {})
    data = har_parser.har_data   

    #empty case
    if not(data["pages"]):
        flag = False
        return (flag, informationDict)
    informationDict["title"] = data["pages"][0]["title"]
    informationDict["onContentLoad"] = data["pages"][0]["pageTimings"]["onContentLoad"]
    informationDict["onLoad"] = data["pages"][0]["pageTimings"]["onLoad"]
    pageSize = 0
    #mimeType List to record the information 
    content_mimeType_list = []

    #urllist to record the url so as to calculate the static item number
    urllist = []
    urlDict = {}
    for i in data["entries"]:
        pageSize += i["response"]["content"]["size"]
        content_mimeType_list.append(i["response"]["content"]["mimeType"])
        urllist.append(i["request"]["url"])
        if not (i["request"]["url"] in urlDict.keys()):
            urlDict[i["request"]["url"]] = 0.0
        urlDict[i["request"]["url"]] += i["response"]["content"]["size"]/1024
    informationDict["pageSize"] = pageSize/1024 
    informationDict["averageObjectSize"] = pageSize/1024/len(data["entries"])  
    informationDict["urllist"] = urllist 
    informationDict["urlDict"] = urlDict
    
    page_id_set = set()
    protocol_list = []
    for i in data["entries"]:
        pageid = i['pageref']
        page_id_set.add(i['response']['httpVersion']) 
        protocol_list.append(i['response']['httpVersion'])
    informationDict["protocol"] = page_id_set
    protocol_dict = Counter(protocol_list)
    mime_dict = Counter(content_mimeType_list)
    #change the dict to the list

    counter_list = []
    protocol_num = 0
    #convert the dict to the list [h1 num, h2 num, h3 num]
    if ('http/1.1' in protocol_dict.keys()):
        counter_list.append(protocol_dict['http/1.1'])
        protocol_num += 1
    else:
        counter_list.append(0)

    if ('h2' in protocol_dict.keys()):
        counter_list.append(protocol_dict['h2'])
        protocol_num +=1
    else:
        counter_list.append(0)

    if ('h3-Q050' in protocol_dict.keys()):
        counter_list.append(protocol_dict['h3-Q050'])
        protocol_num += 1
    else:
        counter_list.append(0)

    #mime_list [static / dynamic /picture/ video]
    mime_list = [0, 0]

    if ("image/png" in mime_dict.keys()):
        mime_list[0] += mime_dict["image/png"]    
    if ("image/x-icon" in mime_dict.keys()):
        mime_list[0] += mime_dict["image/x-icon"]
    if ("image/svg+xml" in mime_dict.keys()):
        mime_list[0] += mime_dict["image/svg+xml"]
    if ("image/jpeg" in mime_dict.keys()):
        mime_list[0] += mime_dict["image/jpeg"]
    if ("video/mp4" in mime_dict.keys()):
        mime_list[1] += mime_dict["video/mp4"]     
    

    informationDict["memeCounter"] = mime_list
    informationDict["protocolCounter"] = counter_list
    informationDict["objectNumber"] = len(data["entries"])
    #deal with the throughput
    informationDict["throughput"] = 0
    informationDict["protocolNumber"] = protocol_num
    return (flag, informationDict)


parser = argparse.ArgumentParser(description='')
parser.add_argument('--data_path', type=str,  help='dataset directory path', required=True)
args = parser.parse_args()

parentPath = args.data_path+'/'
nameList = ["12-24-2020/har-file/20201224-010218", "12-24-2020/har-file/20201224-215611", "12-25-2020/har-file/20201225-082843", 
            "12-25-2020/har-file/20201225-233305", "12-26-2020/har-file/20201226-093530", "12-27-2020/har-file/20201227-214441", 
            "4g-12-28-2020/har-file/20201228-181445", "5g-12-30-2020/har-file/20201230-113119", 
            "4g-12-29-2020/har-file/20201229-181543", "4g-12-29-2020/har-file/20201229-183634", "4g-12-29-2020/har-file/20201229-231259",
            "5g-01-07-2021/har-file/20210107-220935", 
            "4g-01-08-2021/har-file/20210108-185323", "4g-01-08-2021/har-file/20210108-205258",
            "5g-01-08-2021/har-file/20210108-124615", "4g-01-09-2021/har-file/20210109-012342", "4g-01-09-2021/har-file/20210109-202810",
            "4g-01-10-2021/har-file/20210110-014751", "5g-01-10-2021/har-file/20210110-111032",
            "5g-01-10-2021/har-file/20210110-175244",
            "12-26-2020/har-file/20201226-173313", "4g-12-31-2020/har-file/20201231-230734", 
            "5g-01-11-2021/har-file/20210111-000558", "5g-01-11-2021/har-file/20210111-013015", "5g-01-11-2021/har-file/20210111-130042"
            ]
networkStatusList = ["5G", "4G", "5G", "4G", "5G", "5G", "4G", "5G", "4G", "4G", 
    "4G",  "5G", "4G", "4G", "5G", "4G", "4G",  "4G", "5G", "5G",
    "4G", "4G", "5G", "5G", "5G"]

fileStatistics = {}
fileSet = set()

for (i, foldername) in enumerate(nameList):
    fileList = os.listdir(parentPath + foldername)
    networkStatus = networkStatusList[i]
    for fileName in fileList:
        if (fileName == '.DS_Store'):
            continue
        print(fileName)
        fileName2 = fileName.split("_")[2]
        websiteName = fileName2.split("-")[0]
        timestampTemp = fileName2.split("-")[2] + fileName2.split("-")[3]    
        timestamp = timestampTemp.split(".")[0]
        print(websiteName)
        (flag, tempDict) = parseHarFile(parentPath + foldername + "/" + fileName)
        if (not flag):
            continue
        if (not (websiteName, networkStatus) in fileStatistics.keys()):
            fileStatistics[(websiteName, networkStatus)] = []
        if (flag):
            fileSet.add(websiteName)
            tempDict["throughput"] = parseTcpdump(parentPath + foldername + "/" + fileName)
            print(tempDict["throughput"])
            fileStatistics[(websiteName, networkStatus)].append(tempDict)

with open("WebSet.pickle", 'wb') as f:
    pickle.dump(fileSet, f)

with open("fileStatistics.pickle", 'wb') as f:
    pickle.dump(fileStatistics, f)


