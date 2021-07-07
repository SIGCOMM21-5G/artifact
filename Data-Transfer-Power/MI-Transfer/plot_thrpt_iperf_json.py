# !/usr/bin/python

# Plot the time-throughput figure from an iPerf json log
# Output the average throughput

# Usage: python plot_thrpt_iperf_json.py /path/to/log.json [xrange start] [xrange end]
# Example: python plot_thrpt_iperf_json.py data/5GTracker_iPerf/20201130/APPLE-run10045-udp-loc5-600m-1-iPerf.json 0 50

import numpy as np
import json
import sys
from matplotlib import pyplot as plt

data_path = sys.argv[1]  # Path to the json file
data_name = data_path.split('.')[0].split('/')[-1]

def find_close(num, target_list):
	i = 0
	while target_list[i] < num:
		i += 1
	# i = (np.abs(np.asarray(target_list) - num)).argmin()
	return i


with open(data_path) as f:
	data = json.load(f)

timestamp = []
throughput = []
for i in data['intervals']: 
    # print(i['sum']['bits_per_second'])
    timestamp.append(i['sum']['start'])
    throughput.append(i['sum']['bits_per_second'])

if len(sys.argv) >= 3: 
	if len(sys.argv) == 3:
		sys.exit("Parameter not enough!")
	start_sec = float(sys.argv[2])
	end_sec = float(sys.argv[3])
	if start_sec >= end_sec:
		sys.exit("Left > Right !")
	start = find_close(start_sec, timestamp)
	end = find_close(end_sec, timestamp) + 1
else:
	start = 0
	end = len(timestamp)

print(f'Average: {np.mean(throughput[start:end])/1000000}\t{np.std(throughput[start:end])/1000000}')
print(f'Max: {max(throughput[start:end])/1000000}')

x = timestamp[start:end]
y = [t/1000000 for t in throughput[start:end]]
plt.figure(figsize=(10, 2)).canvas.manager.set_window_title(data_name)
plt.xlabel("Time (s)")
plt.ylabel("Throughput (Mbps)")
plt.plot(x, y)
# plt.xlim(results[start,0], results[end,0])
# plt.ylim(0, 4000)
plt.show()
