# !/usr/bin/python

# Plot time-power figure from a Monsoon Power Tool log
# Support processing two intervals

# Usage: python plot_hardware_power.py /path/to/log.csv [new sampling rate] [xrange start] [xrange end] [xrange start2] [xrange end2]
# Example: python plot_hardware_power.py data/PowerMonitor/10Hz/screenmax-5g-dl-udp-loc5-50m-2-10hz.csv 2 0 50

import numpy as np
import csv
import sys
import math
from matplotlib import pyplot as plt
import re


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


SAMPLING_RATE = 5000
NEW_SAMPLING_RATE = int(sys.argv[2])
STEP = int(SAMPLING_RATE / NEW_SAMPLING_RATE)
data_path = sys.argv[1]  # Path to the log file
data_name = data_path.split('.')[0].split('/')[-1]
isTwoInterval = (len(sys.argv) == 7)  # two intervals

# Read results from the log
with open(data_path) as f:
	csv_reader = csv.reader(f, delimiter=',')
	headers = next(csv_reader)
	power_unit = get_power_unit(headers)
	
	results = np.array(list(csv_reader)).astype("float")

# Check the unit
if power_unit == 'W':  # Convert to mW
	results[:,1] *= 1000

# Get ranges
if len(sys.argv) >= 4: 
	if len(sys.argv) == 4:
		sys.exit("Parameter not enough!")
	start, end = set_inteval(3, 4, NEW_SAMPLING_RATE)
	if isTwoInterval:
		start2, end2 = set_inteval(5, 6, NEW_SAMPLING_RATE)
else:
	start = 0
	end = int((results.shape[0] - 1)*NEW_SAMPLING_RATE/SAMPLING_RATE)

# Sample the raw results
time = results[::STEP,0]
power = results[:int(len(results)/STEP)*STEP,1].reshape(-1, STEP).mean(axis=1)


if isTwoInterval:
	print(f"{np.hstack((power[start:end], power[start2:end2])).mean()}\t{np.hstack((power[start:end], power[start2:end2])).std()}")
else:
	print(f"{power[start:end].mean()}\t{power[start:end].std()}")


plt.figure(figsize=(10, 3)).canvas.manager.set_window_title(data_name)
plt.xlabel("Time (s)")
plt.ylabel("Power (mW)")

if isTwoInterval:
	plt.subplot(211)
x = time[start:end]
y = power[start:end]
plt.plot(x, y)
plt.xlim(time[start], time[end])

if isTwoInterval:
	plt.subplot(212)
	x = time[start2:end2]
	y = power[start2:end2]
	plt.plot(x, y)
	plt.xlim(time[start2], time[end2])

plt.show()

# print(power)
# np.savetxt('/home/harry/5g/TCP-scripts/results/raw/1231-realapp-ratelimit-cpu/traces-S10/APPLE-1609479849-01-POWER.txt',power)