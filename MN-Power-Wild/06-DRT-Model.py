# !/usr/bin/python
"""
Author: Xumiao
modified by: Ahmad
"""

# Decision Tree regression
from os import path
import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.tree import DecisionTreeRegressor

## Dataset Organization
proj_dir = path.abspath(path.join(path.dirname(__file__)))
data_dir = path.join(proj_dir, 'data')
data_processed_dir = path.join(proj_dir, 'data-processed')

## Config
VERBOSE = 0
EXPR_TYPE = 'MN-Power-Wild'
DATA_DIR = data_dir
OUTPUT_DIR = data_processed_dir
INPUT_LOGS_DIR = path.join(OUTPUT_DIR, 'cleaned-logs')

## Model Config
m_config = {
    'S20 T-Mobile NSA Lowband': 's20_t-mobile_nsa_all.csv',
    'S20 T-Mobile SA Lowband': 's20_t-mobile_sa_all.csv',
    'S20 Verizon NSA Lowband': 's20_verizon_nsalow_all.csv',
    'S20 Verizon NSA Highband': 's20_verizon_nsahigh_all.csv'
}

## possible features
# 'timestamp', 'downlink_rolled_mbps', 'uplink_rolled_mbps',
# 'sw_power_baseline', 'avg_power_baseline', 'nr_ssRsrp_avg',
# 'rsrp', 'nr_ssRsrp', 'nr_ssSinr', 'rsrp_avg', 'nrStatus',
# 'nr_ssSinr_avg', 'provider', 'direction', 'network_type',
# 'sw_power_rolled', 'avg_power_rolled', 'avg_power', 'sw_power'

for config, filename in m_config.items():

    print('=======================================================================')
    print(f"[PROCESSING CONFIG]: {config}")

    df = pd.read_csv(path.join(INPUT_LOGS_DIR, filename))

    df = df[df['nr_ssRsrp_avg'].notna()]

    df_train, df_test = train_test_split(df, train_size=0.7, test_size=0.3, random_state=5)

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
    MAPE_list = []

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

        scores = cross_val_score(model, X, Y, cv=10, scoring='neg_mean_absolute_percentage_error')
        MAPE_list.append(np.abs(scores.mean()))
        if VERBOSE:
            print(f"MAE: {mae}")
            print(f"RMSE: {rmse}")
            print(f"Score: {score}")
            print(f"{np.abs(scores.mean())}\t{scores.std()}")  # mae
            scores = cross_val_score(model, X, Y, cv=10, scoring='r2')
            print(f"{np.abs(scores.mean())}\t{scores.std()}\n")  # score
    best_depth = kernel_label[np.argmin(MAPE_list)].split('_')[-1]
    print("Minimum MAPE for DTR depth = {} : {:.3f}\n".format(best_depth, np.min(MAPE_list)))
