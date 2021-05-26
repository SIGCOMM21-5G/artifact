# !/usr/bin/python

# Date timestamp (e.g., from 5G Tracker) to unix timestamp

# Usage: python ts_converter.py /path/to/log.csv

import numpy as np
import csv
import sys
from datetime import datetime, tzinfo
from dateutil import tz


def extract_timestamp(dateTimes):
	epochTimes = []

	for dateTime in dateTimes:
		year = int(dateTime.split("-")[0])
		month = int(dateTime.split("-")[1])
		day = int(dateTime.split("-")[2].split(" ")[0])
		hour = int(dateTime.split(" ")[1].split(":")[0])
		minute = int(dateTime.split(" ")[1].split(":")[1])
		second = int(dateTime.split(" ")[1].split(":")[2].split(".")[0])
		millisecond = int(dateTime.split(" ")[1].split(":")[2].split(".")[1])
		tzone = dateTime.split(" ")[2]
		# print(year, month, day, hour, minute, second, millisecond, tzone)
		
		epochTime = datetime(year, month, day, hour, minute, second, millisecond*1000, tzinfo=tz.gettz(tzone)).timestamp()
		epochTimes.append(epochTime)
	return np.array(epochTimes)


if __name__ == '__main__':
	data_path = sys.argv[1]  # Path to a 5G Tracker trace
	dateTimes = []
	
	with open(data_path) as f:
		csv_reader = csv.reader(f, delimiter=',')
		for line in csv_reader:
			dateTimes.append(line[0])
	dateTimes = dateTimes[1:]
	
	epochTimes = extract_timestamp(dateTimes)
	
	for epochTime in epochTimes:
		print(epochTime)
