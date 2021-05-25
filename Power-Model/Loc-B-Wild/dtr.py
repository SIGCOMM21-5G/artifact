# !/usr/bin/python

# Decision Tree regression
# feature set index:
#	1: TH + SS
#	2: TH
#	3: SS

# Usage: python dtr.py -d [training data path] -k [keyword in filenames] -s [optional, save the improved model]
# Example: python dtr.py -d data/ -k MI-VZ-HB -f 1

import numpy as np
import pandas as pd
import sys
import os
import pickle
import argparse
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score, SCORERS
from sklearn.model_selection import train_test_split, cross_val_score, cross_val_predict
from sklearn.tree import DecisionTreeRegressor

ap = argparse.ArgumentParser()
ap.add_argument("-d", "--data", help = "path to the training data")
ap.add_argument("-k", "--keyword", help = "keyword in the log names")
ap.add_argument("-s", "--save", help = "save model to disk")
ap.add_argument("-f", "--feature", help = "index of the feature set")
args = vars(ap.parse_args())

path = args["data"]
files = [x for x in os.listdir(path) if 'csv' in x]
if args["keyword"]:
	keyword = args["keyword"]
	files = [x for x in files if keyword in x and 'lock' not in x]
print(files)

df_list = []
for file in files:
    tmp = pd.read_csv(path + '/' + file)
    df_list.append(tmp)
    # print(tmp.head(), tmp.size)
df = pd.concat(df_list, ignore_index=True)
df.columns = ["Timestamp", "nrStatus", "LTE_RSRP", "nr_ssRsrp", "nr_ssSinr", "downlink_Mbps", "uplink_Mbps", "software_power", "hardware_power", "hardware_power_full"]
# df = pd.read_csv(args["data"], header = None)
# print(df.head())
# print(f"Shape: {df.shape}")

df_train, df_test = train_test_split(df, train_size = 0.7, test_size = 0.3, random_state = 5)


feature_sets = [["nr_ssRsrp", "downlink_Mbps", "uplink_Mbps"],
				["downlink_Mbps", "uplink_Mbps"],
				["nr_ssRsrp"]]
# X_column = ["nr_ssRsrp", "downlink_Mbps", "uplink_Mbps", "software_power"]
# X_column = ["software_power"]
X_column = feature_sets[int(args["feature"])]
print(X_column)

Y_column = ["hardware_power_full"]

X = df[X_column].to_numpy()
Y = df[Y_column].to_numpy().reshape(-1)

X_train = df_train[X_column].to_numpy()
Y_train = df_train[Y_column].to_numpy().reshape(-1)


regr_dep2 = DecisionTreeRegressor(max_depth=2)
regr_dep3 = DecisionTreeRegressor(max_depth=3)
regr_dep4 = DecisionTreeRegressor(max_depth=4)
regr_dep5 = DecisionTreeRegressor(max_depth=5)
regr_dep6 = DecisionTreeRegressor(max_depth=6)
regr_dep7 = DecisionTreeRegressor(max_depth=7)
regr_dep8 = DecisionTreeRegressor(max_depth=8)
regr_dep9 = DecisionTreeRegressor(max_depth=9)
regr_dep10 = DecisionTreeRegressor(max_depth=10)
dtrs = [
		regr_dep2, 
		regr_dep3, 
		regr_dep4, 
		regr_dep5, 
		regr_dep6, 
		regr_dep7, 
		regr_dep8, 
		regr_dep9, 
		regr_dep10
		]
kernel_label = [
		'DTR_2', 
		'DTR_3', 
		'DTR_4', 
		'DTR_5',
		'DTR_6', 
		'DTR_7',
		'DTR_8', 
		'DTR_9', 
		'DTR_10'
		]

Y_mean = df[Y_column[0]].mean()
Y_max = df[Y_column[0]].max()
# print(f"Y_mean: {Y_mean}, Y_max: {Y_max}")

MAPEs = []

for i in range(len(dtrs)):
	dtr = dtrs[i]
	label = kernel_label[i]
	X_test = df_test[X_column]
	Y_test = df_test[Y_column]
	model = dtr.fit(X_train, Y_train)
	Y_pred = model.predict(X_test)

	if args["save"]:
		pkl_filename = args["save"]
		with open(pkl_filename, 'wb') as file:
			pickle.dump(model, file)

	mae = mean_absolute_error(Y_test, Y_pred)
	mse = mean_squared_error(Y_test, Y_pred)
	rmse = np.sqrt(mse)
	r2 = r2_score(Y_test, Y_pred)
	score = model.score(X_test, Y_test)
	Y_test = Y_test.to_numpy().reshape(-1)
	errors = np.abs(Y_test-Y_pred)/Y_test
	X_Y_errors = np.hstack((X_test, Y_test.reshape(-1,1), Y_pred.reshape(-1,1), errors.reshape(-1,1)))
	# print(errors.mean())
	# print(f"{mae}")
	# print(f"{rmse}")
	# print(f"{score}")

	scores = cross_val_score(model, X, Y, cv=10, scoring='neg_mean_absolute_percentage_error') #  
	MAPEs.append(np.abs(scores.mean()))

print(f"MAPE: {min(MAPEs)}")  # mae
