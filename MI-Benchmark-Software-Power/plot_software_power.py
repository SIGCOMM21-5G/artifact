# !/usr/bin/python

# Plot time-power figure from a 5G Tracker log

# Usage: python plot_software_power.py /path/to/log.csv [sampling rate] [xrange start] [xrange end]

import numpy as np
import csv
import sys
import math
from matplotlib import pyplot as plt
from utils import *
sys.path.append("../")
from fivegtracker.ts_converter import extract_timestamp


data_path = sys.argv[1]  # Path to the log file
data_name = data_path.split('.')[0].split('/')[-1]
SAMPLING_RATE = int(sys.argv[2])


with open(data_path) as f:
	csv_reader = csv.reader(f, delimiter=',')
	headers = next(csv_reader)
	data = list(csv_reader)
	
	timestamps = extract_timestamp(np.array(data)[:,0])
	results = np.array(data)[:,50:52].astype("int")

timestamps = timestamps - timestamps[0]
results = abs(results[:,0] * results[:,1] / 1000000)

if len(sys.argv) >= 4:
	if len(sys.argv) == 4:
		sys.exit("Parameter not enough!")
	start, end = set_inteval(3, 4, SAMPLING_RATE)
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
