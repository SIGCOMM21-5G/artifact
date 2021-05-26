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
import ipdb

                        

with open('WebSet.pickle', 'rb') as f:
    webSet = pickle.load(f)
with open('fileStatistics.pickle', 'rb') as f:
    fileStatistics = pickle.load(f)

webSetList = list(webSet)[0:60]
finalSet = set(webSetList)

finalFileStatistics = {}

for i in webSetList:
    if (not ((i, '4G') in fileStatistics.keys())) or (not ((i, '5G') in fileStatistics.keys())):
        continue
    finalFileStatistics[(i, "4G")] =fileStatistics[(i, "4G")]
    finalFileStatistics[(i, "5G")] =fileStatistics[(i, "5G")]

with open("./processed_dataset/WebSet.pickle", 'wb') as f:
    pickle.dump(finalSet, f)

with open("./processed_dataset/fileStatistics.pickle", 'wb') as f:
    pickle.dump(finalFileStatistics, f)

