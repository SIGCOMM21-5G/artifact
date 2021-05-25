# !/usr/bin/python

# Plot time-power figure from a 5G Tracker log

# Usage: python plot_software_power.py /path/to/log.csv [sampling rate] [xrange start] [xrange end]
# Example: python plot_software_power.py data/5GTracker_iPerf/10Hz/APPLE-1607638238-01.csv 2 0 50


import numpy as np
import csv
import sys
import math
from matplotlib import pyplot as plt
import re
from ts_converter import extract_timestamp


def get_power_unit(headers):
	# print(headers[1])
	m = re.findall(r'\((.*?)\)', headers[1]) 
	return m[0]

def check_legal_interval(start, end):
	if start >= end:
		sys.exit("Left > Right !")

def set_inteval(idx1, idx2, SAMPLING_RATE):
	start_sec = float(sys.argv[idx1])
	end_sec = float(sys.argv[idx2])
	check_legal_interval(start_sec, end_sec)
	return int(start_sec * SAMPLING_RATE), int(end_sec * SAMPLING_RATE)


data_path = sys.argv[1]  # Path to the log file
data_name = data_path.split('.')[0].split('/')[-1]

if "10Hz" in data_path:
	SAMPLING_RATE = 10
else:
	SAMPLING_RATE = 2
NEW_SAMPLING_RATE = int(sys.argv[2])
STEP = int(SAMPLING_RATE / NEW_SAMPLING_RATE)

# Read results from the log
with open(data_path) as f:
	csv_reader = csv.reader(f, delimiter=',')
	headers = next(csv_reader)
	data = list(csv_reader)
	
	timestamps = extract_timestamp(np.array(data)[:,0])
	results = np.array(data)[:,50:52].astype("int")

timestamps = timestamps[::STEP] - timestamps[0]
results = abs(results[::STEP,0] * results[::STEP,1] / 1000000)

if len(sys.argv) >= 4:
	if len(sys.argv) == 4:
		sys.exit("Parameter not enough!")
	start, end = set_inteval(3, 4, NEW_SAMPLING_RATE)
else:
	start = 0
	end = results.shape[0] - 1

print(f"{results[start:end].mean()}\t{results[start:end].std()}")

plt.figure(figsize=(10, 3)).canvas.manager.set_window_title(data_name)
plt.xlabel("Time (s)")
plt.ylabel("Power (mW)")

x = timestamps[start:end]
y = results[start:end]
plt.plot(x, y)
plt.xlim(timestamps[start], timestamps[end])

plt.show()
