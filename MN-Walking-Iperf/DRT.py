# !/usr/bin/python
"""
Author: Xumiao
modified by: Ahmad
"""


# Decision Tree regression

import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.tree import DecisionTreeRegressor
from set_paths import *

## Config
EXPR_TYPE = 'MN-Walking-Iperf'
DATA_DIR = '{}{}'.format(DATA_FOLDER, EXPR_TYPE)
OUTPUT_DIR = '{}{}'.format(OUTPUT_FOLDER, EXPR_TYPE)
INPUT_LOGS_DIR = '{}/regression-input'.format(OUTPUT_DIR)

## Model to train
# df = pd.read_csv('{}/t_mobile_sa_down.csv'.format(INPUT_LOGS_DIR))
# df = pd.read_csv('{}/t_mobile_sa_up.csv'.format(INPUT_LOGS_DIR))
# df = pd.read_csv('{}/t_mobile_sa_all.csv'.format(INPUT_LOGS_DIR))
# df = pd.read_csv('{}/t_mobile_nsa_down.csv'.format(INPUT_LOGS_DIR))
# df = pd.read_csv('{}/t_mobile_nsa_up.csv'.format(INPUT_LOGS_DIR))
df = pd.read_csv('{}/t_mobile_nsa_all.csv'.format(INPUT_LOGS_DIR))
# df = pd.read_csv('{}/verizon_down.csv'.format(INPUT_LOGS_DIR))
# df = pd.read_csv('{}/verizon_lowband_down.csv'.format(INPUT_LOGS_DIR))
# df = pd.read_csv('{}/verizon_highband_down.csv'.format(INPUT_LOGS_DIR))
# df = pd.read_csv('{}/verizon_up.csv'.format(INPUT_LOGS_DIR))
# df = pd.read_csv('{}/verizon_all.csv'.format(INPUT_LOGS_DIR))

df = df[df['nr_ssRsrp_avg'].notna()]

df_train, df_test = train_test_split(df, train_size=0.7, test_size=0.3, random_state=5)

## possible column list
# ['timestamp', 'downlink_rolled_mbps', 'uplink_rolled_mbps',
# 'sw_power_baseline', 'avg_power_baseline', 'nr_ssRsrp_avg',
# 'rsrp', 'nr_ssRsrp', 'nr_ssSinr',
# 'rsrp_avg', 'nrStatus', 'nr_ssSinr_avg', 'provider', 'direction',
# 'network_type', 'sw_power_rolled', 'avg_power_rolled', 'avg_power',
# 'sw_power']
# X_column = ['sw_power_baseline']
X_column = ['nr_ssRsrp_avg', 'downlink_rolled_mbps_3', 'uplink_rolled_mbps_3']
Y_column = ['avg_power_rolled']


X = df[X_column].to_numpy()
Y = df[Y_column].to_numpy().reshape(-1)


X_train = df_train[X_column].to_numpy()
Y_train = df_train[Y_column].to_numpy().reshape(-1)

regr_dep5 = DecisionTreeRegressor(max_depth=5)
regr_dep6 = DecisionTreeRegressor(max_depth=6)
regr_dep7 = DecisionTreeRegressor(max_depth=7)
regr_dep8 = DecisionTreeRegressor(max_depth=8)
dtrs = [
    regr_dep5,
    regr_dep6,
    regr_dep7,
    regr_dep8,
]
kernel_label = [
    'DTR_5',
    'DTR_6',
    'DTR_7',
    'DTR_8',
]

Y_mean = df[Y_column[0]].mean()
Y_max = df[Y_column[0]].max()
print(f"Y_mean: {Y_mean}, Y_max: {Y_max}")

for i in range(len(dtrs)):
    dtr = dtrs[i]
    label = kernel_label[i]
    X_test = df_test[X_column]
    Y_test = df_test[Y_column]
    model = dtr.fit(X_train, Y_train)
    Y_pred = model.predict(X_test)

    mae = mean_absolute_error(Y_test, Y_pred)
    mse = mean_squared_error(Y_test, Y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(Y_test, Y_pred)
    score = model.score(X_test, Y_test)

    print(f"{mae}")
    print(f"{rmse}")
    print(f"{score}")

    scores = cross_val_score(model, X, Y, cv=10, scoring='neg_mean_absolute_percentage_error')
    print(f"{np.abs(scores.mean())}\t{scores.std()}")  # mae
    scores = cross_val_score(model, X, Y, cv=10, scoring='r2')
    print(f"{np.abs(scores.mean())}\t{scores.std()}\n")  # score
