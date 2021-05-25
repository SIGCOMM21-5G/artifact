# !/usr/bin/python

# Extact downlink/uplink throughput, rsrp, and sinr from a 5G Tracker log
# Save them together with a power trace after alignment

# Usage: python generate_dataset.py -t /path/to/tracker.csv -p /path/to/power.csv -s [save path] -b [baseline power]

import numpy as np
import pandas as pd
import csv
import sys
import re
import argparse
from matplotlib import pyplot as plt
sys.path.append("../")
from fivegtracker.ts_converter import extract_timestamp
from power.utils import *

ap = argparse.ArgumentParser()
ap.add_argument("-t", "--tracker", help = "path to 5gtracker log file")
ap.add_argument("-p", "--power", help = "path to power log file")
ap.add_argument("-o", "--offset", help = "offset")
ap.add_argument("-s", "--save", help = "path to save the data")
ap.add_argument("-b", "--baseline", help = "baseline power")
ap.add_argument("-n", "--new", const=True, default=False, nargs='?', help = "new 5gtracker log format")
ap.add_argument("-a", "--sampling", const=True, default=False, nargs='?', help = "sampling instead of average of median")
args = vars(ap.parse_args())

SAMPLING_RATE = 1
POWER_SAMPLING_RATE = 5000
TRACK_SAMPLING_RATE = 10
POWER_STEP = int(POWER_SAMPLING_RATE / SAMPLING_RATE)
TRACK_STEP = int(TRACK_SAMPLING_RATE / SAMPLING_RATE)
tracker_data_path = args["tracker"] # Path to a 5G Tracker trace
power_data_path = args["power"]  # Path to the log file




# Power log
df = pd.read_csv(power_data_path, header=None)
power_unit = get_power_unit(df.to_numpy()[0])  # data header
results = df.to_numpy()[1:].astype("float")
results_full = df.to_numpy()[1:].astype("float")

if power_unit == 'W':  # Convert to mW
	results[:,1] *= 1000
	results_full[:,1] *= 1000
if args["baseline"]:
	results[:,1] -= float(args["baseline"])

range_l_pm = 0
range_r_pm = int(results.shape[0] / POWER_STEP)
offset = 0
if args["offset"]:
	offset = float(args["offset"])
	range_l_pm = int(max(range_l_pm + offset * SAMPLING_RATE, range_l_pm))
	range_r_pm = int(min(range_r_pm + offset * SAMPLING_RATE, range_r_pm))
p_ts = results[::POWER_STEP,0]
power = results[:int(len(results)/POWER_STEP)*POWER_STEP,1].reshape(-1, POWER_STEP).mean(axis=1)
power_full = results_full[:int(len(results_full)/POWER_STEP)*POWER_STEP,1].reshape(-1, POWER_STEP).mean(axis=1)
if len(results) % POWER_STEP != 0:
	power = np.append(power, results[int(len(results)/POWER_STEP)*POWER_STEP:,1].mean())
	power_full = np.append(power_full, results_full[int(len(results_full)/POWER_STEP)*POWER_STEP:,1].mean())
p_ts = p_ts[range_l_pm:range_r_pm] - offset
power = power[range_l_pm:range_r_pm]
power_full = power_full[range_l_pm:range_r_pm]


# 5GTracker log
df = pd.read_csv(tracker_data_path, header=None)

if args["new"]:  # new log format
	data = df.to_numpy()[1:,:62]  # 62
	nrStatus_raw = data[:,42]  # 42th column: nrStatus
	rawSignalStrengths = df.to_numpy()[1:,65]  # 65th column contains lte rsrp
	rsrp_values = data[:,43]  # 43th column: nr_ssRsrp
	sinr_values = data[:,45]  # 45th column: nr_ssSinr
	current_values = data[:,56].astype("int")  # 56th column: currentNow
	voltage_values = data[:,57].astype("int")  # 57th column: voltageNow
else:
	data = df.to_numpy()[1:,:56]  # 56
	nrStatus_raw = data[:,36]  # 36th column: nrStatus
	rawSignalStrengths = df.to_numpy()[2:,59]  # 59th column contains lte rsrp
	rsrp_values = data[:,37]  # 37th column: nr_ssRsrp
	sinr_values = data[:,39]  # 39th column: nr_ssSinr
	current_values = data[:,50].astype("int")  # 50th column: currentNow
	voltage_values = data[:,51].astype("int")  # 51th column: voltageNow

time = extract_timestamp(data[:,0])
recv_bytes = data[:,11].astype("int")  # 11th column: mobileRx
send_bytes = data[:,12].astype("int")  # 12th column: mobileTx

t_ts_raw = time[1:] - time[1:][0]
rsrp_raw = np.nan_to_num(rsrp_values.astype("float"))[1:].astype("int")
sinr_raw = np.nan_to_num(sinr_values.astype("float"))[1:].astype("int")
sw_power_raw = np.abs(current_values * voltage_values) / 1000000  # software-based power
recv_thrpt_raw = np.diff(recv_bytes) / np.diff(time) / 1000000 * 8
send_thrpt_raw = np.diff(send_bytes) / np.diff(time) / 1000000 * 8
ltersrp_raw = []
for i in range(len(rawSignalStrengths)):
	ltersrp_raw.append(re.findall(r'(rsrp=.*?\s)', rawSignalStrengths[i])[0][5:])
ltersrp_raw = np.array(ltersrp_raw).astype("int")

range_l_5g = 0  # range left and right ends for sampled data
range_r_5g = min(int(len(t_ts_raw) / TRACK_STEP), range_r_pm)
t_ts = t_ts_raw[::TRACK_STEP]
nrStatus = nrStatus_raw[::TRACK_STEP]
recv_thrpt = recv_thrpt_raw[:int(len(recv_thrpt_raw)/TRACK_STEP)*TRACK_STEP].reshape(-1, TRACK_STEP).mean(axis=1)
send_thrpt = send_thrpt_raw[:int(len(send_thrpt_raw)/TRACK_STEP)*TRACK_STEP].reshape(-1, TRACK_STEP).mean(axis=1)
if args["sampling"]:
	ltersrp = ltersrp_raw[::TRACK_STEP]
	rsrp = rsrp_raw[::TRACK_STEP]
	sinr = sinr_raw[::TRACK_STEP]
	sw_power = sw_power_raw[::TRACK_STEP]
else:
	ltersrp = np.median(ltersrp_raw[:int(len(ltersrp_raw)/TRACK_STEP)*TRACK_STEP].reshape(-1, TRACK_STEP), axis=1)
	rsrp = np.median(rsrp_raw[:int(len(rsrp_raw)/TRACK_STEP)*TRACK_STEP].reshape(-1, TRACK_STEP), axis=1)
	sinr = np.median(sinr_raw[:int(len(sinr_raw)/TRACK_STEP)*TRACK_STEP].reshape(-1, TRACK_STEP), axis=1)
	sw_power = sw_power_raw[:int(len(sw_power_raw)/TRACK_STEP)*TRACK_STEP].reshape(-1, TRACK_STEP).mean(axis=1)

if len(t_ts_raw) % TRACK_STEP != 0:
	# print(int(len(t_ts)/TRACK_STEP)*TRACK_STEP)
	# print(len(t_ts), len(rsrp), TRACK_STEP, int(len(t_ts)/TRACK_STEP)*TRACK_STEP)
	# sys.exit(0)
	if not args["sampling"]:
		ltersrp = np.append(ltersrp, np.median(ltersrp_raw[int(len(t_ts)/TRACK_STEP)*TRACK_STEP:]))
		rsrp = np.append(rsrp, np.median(rsrp_raw[int(len(t_ts)/TRACK_STEP)*TRACK_STEP:]))
		sinr = np.append(sinr, np.median(sinr_raw[int(len(t_ts)/TRACK_STEP)*TRACK_STEP:]))
		sw_power = np.append(sw_power, sw_power_raw[int(len(t_ts)/TRACK_STEP)*TRACK_STEP:].mean())
	recv_thrpt = np.append(recv_thrpt, recv_thrpt_raw[int(len(t_ts)/TRACK_STEP)*TRACK_STEP:].mean())
	send_thrpt = np.append(send_thrpt, send_thrpt_raw[int(len(t_ts)/TRACK_STEP)*TRACK_STEP:].mean())
t_ts = t_ts[range_l_5g:range_r_5g]
nrStatus = nrStatus[range_l_5g:range_r_5g]
ltersrp = ltersrp[range_l_5g:range_r_5g]
rsrp = rsrp[range_l_5g:range_r_5g]
sinr = sinr[range_l_5g:range_r_5g]
sw_power = sw_power[range_l_5g:range_r_5g]
recv_thrpt = recv_thrpt[range_l_5g:range_r_5g]
send_thrpt = send_thrpt[range_l_5g:range_r_5g]



# print(results[::POWER_STEP,0].shape, results[:int(len(results)/POWER_STEP)*POWER_STEP,1].reshape(-1, POWER_STEP).mean(axis=1).shape)
# print(p_ts.shape, power.shape)

idx = np.where(rsrp!=0)
idx_zero = np.where(rsrp==0)
idx_zero_neighbor = np.union1d(np.where(rsrp==0)[0]-1, np.where(rsrp==0)[0]+1)
to_delete = np.union1d(idx_zero, idx_zero_neighbor)
idx_ext = np.setdiff1d(np.arange(len(rsrp)),to_delete)

print(t_ts[idx].shape, t_ts[idx_ext].shape)
print(rsrp[idx].shape, rsrp[idx_ext].shape)
print(sinr[idx].shape, sinr[idx_ext].shape)
print(sw_power[idx].shape, sw_power[idx_ext].shape)
print(recv_thrpt[idx].shape, recv_thrpt[idx_ext].shape)
print(send_thrpt[idx].shape, send_thrpt[idx_ext].shape)
print(power[idx].shape, power[idx_ext].shape)


# fig, ax1 = plt.subplots()

# ax1.set_xlabel("Time (s)")
# ax1.set_ylabel("Thrpt (Mbps)")  # , color=color
# p1, = ax1.plot(t_ts[idx], recv_thrpt[idx], label='Downlink', color='tab:blue', zorder=0)  # , color=color
# p2, = ax1.plot(t_ts[idx], send_thrpt[idx], label='Uplink', color='tab:orange', zorder=1)  # , color=color
# ax1.tick_params(axis='y')

# ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
# ax2.set_ylabel("Power (mW)")
# p3, = ax1.plot(t_ts[idx], sw_power[idx], label='SW_Power', color='tab:olive', zorder=2)  # , color=color
# p4, = ax2.plot(p_ts[idx], power[idx], label='HW_Power', color='tab:green', zorder=3)
# ax2.tick_params(axis='y')

# fig.tight_layout()  # otherwise the right y-label is slightly clipped
# lines = [p1, p2, p3, p4]
# ax1.legend(lines, [l.get_label() for l in lines])
# plt.show()


if args["save"]:
	save_file = args["save"]
	trace = np.hstack((t_ts[idx].reshape(-1,1), nrStatus[idx].reshape(-1,1), ltersrp[idx].reshape(-1,1), 
		rsrp[idx].reshape(-1,1), sinr[idx].reshape(-1,1), recv_thrpt[idx].reshape(-1,1), send_thrpt[idx].reshape(-1,1), sw_power[idx].reshape(-1,1), 
		power[idx].reshape(-1,1), power_full[idx].reshape(-1,1)))
	print(trace.shape)
	np.savetxt(save_file, trace, delimiter=',', fmt='%f,%s,%d,%d,%d,%f,%f,%f,%f,%f')
