#!/usr/bin/python3
"""
authors: Rishabh, Xinyue Hu, Eman
modified by: Ahmad
modified on 17 January, 2021
"""

import math
import os
from operator import itemgetter
import numpy as np
import pandas as pd
from set_paths import *
import re

'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
Process 5GTracker Logs
1a. Zoom Level and Geo-coordinates to pixel coordinates
1b. Use tower info to get panel angles etc.
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

##  Config
MAX_NUM_PANELS = 9
MAX_NUM_TOWERS = 3
DEVICES = ['S20UPM']
EXPR_TYPE = 'MN-Power-Wild'
DATA_DIR = '{}{}'.format(DATA_FOLDER, EXPR_TYPE)
CLIENT_LOGS_DIR = '{}/Client'.format(DATA_DIR)
OUTPUT_DIR = '{}{}'.format(OUTPUT_FOLDER, EXPR_TYPE)
IPERF_SUMMARY_FILE = '{}/Client/{}-iPerfSummary.csv'.format(DATA_DIR, DEVICES[0])  # for Verizon and T-Mobile
MN_WALKING_SUMMARY = '{}/{}-Summary.csv'.format(DATA_DIR, EXPR_TYPE)
iperf_run_summary = pd.read_csv(IPERF_SUMMARY_FILE)
mn_walking_summary = pd.read_csv(MN_WALKING_SUMMARY)
FORCE_REGENERATE_FLAG = 0  # set to 1 if you want to do everything from scratch
summary = pd.merge(mn_walking_summary, iperf_run_summary, how='left', left_on='Iperf run number',
                   right_on='RunNumber')
summary_filtered = summary[summary['SessionID'].notna() & (summary['Successful?'] == 'yes')].copy(deep=True)
del summary
summary_filtered['SessionID'] = summary_filtered['SessionID'].astype(int)
summary_filtered.reset_index(drop=True, inplace=True)

# create output folders if not present
OUTPUT_LOGS_DIR = '{}/session-logs'.format(OUTPUT_DIR)
if not os.path.exists(OUTPUT_LOGS_DIR):
    os.makedirs(OUTPUT_LOGS_DIR)
    print('Directory created: {}'.format(OUTPUT_LOGS_DIR))


def mcidToTower(mcid):
    return mcid[:-2]


def getTextByIndex(originaltext, index, end=-1):
    parsedStr = ""
    if isinstance(originaltext, str) and originaltext:
        items = originaltext.split(" ")
        if index <= len(items):
            parsedStr = items[index]
        if end != -1:
            index += 1
            while index <= end:
                parsedStr += items[index]
                index += 1
    return parsedStr


def parseAllText(originaltext, label, regexpr):
    parsedStr = ""
    items = []
    if isinstance(originaltext, str) and label in originaltext:
        parsedStr_search = re.findall(regexpr, originaltext)
        if parsedStr_search:
            for item in parsedStr_search:
                item = item.replace(label, "").strip()
                item = item.replace(",", "").strip()
                item = item.replace("}", "").strip()
                items.append(item)
            parsedStr = '|'.join(items)
    return parsedStr


for idx, row in summary_filtered.iterrows():
    session_file = '{}/{}-{}-01.csv'.format(CLIENT_LOGS_DIR, row['Device'], row['SessionID'])
    print('============================== RUN: {} ================================='.format(row['Iperf run number']))
    print('processing file: {}   ({}/{})'.format(session_file, idx + 1, summary_filtered.shape[0]))

    # skip if already processed
    log_filename = '{}/{}'.format(OUTPUT_LOGS_DIR, os.path.basename(session_file))
    if os.path.exists(log_filename) and FORCE_REGENERATE_FLAG == 0:
        print('    skipping file: {}. Already processed.\n\n'.format(session_file))
        continue

    ## Process 5GTracker data
    session_logs = pd.read_csv(session_file)
    if row['Network Type'] == 'SA only' or 'NSA+LTE':
        session_logs['rsrp'] = session_logs['nr_ssRsrp']
    else:
        session_logs['rsrp'] = session_logs.apply(
            lambda x: parseAllText(x["RawSignalStrengths"], "rsrp=", r'(rsrp=.*?\s)'), axis=1).astype(int)

    session_logs = session_logs[~session_logs['mCid'].isna()]
    session_logs['towerid'] = session_logs.apply(lambda x: mcidToTower(str(x['mCid'])), axis=1).astype(int)
    session_logs['timestamp'] = pd.to_datetime(session_logs['timestamp'])
    session_logs['r_time'] = session_logs['timestamp'].apply(lambda x: x.replace(microsecond=0)).astype(str).str[:-6]
    session_grp = session_logs.groupby(['r_time']).agg(latitude=('latitude', np.mean),
                                                       longitude=('longitude', np.mean),
                                                       locationAccuracy=('locationAccuracy', np.mean),
                                                       movingSpeed=('movingSpeed', np.mean),
                                                       movingSpeedAccuracyMPS=('movingSpeedAccuracyMPS', np.mean),
                                                       compassDirection=('compassDirection', np.mean),
                                                       compassAccuracy=('compassAccuracy', np.mean),
                                                       nrStatus=('nrStatus', lambda x: list(x.unique())),
                                                       mCid=('mCid', lambda x: list(x.unique())),
                                                       towerid=('towerid', lambda x: list(x.unique())),
                                                       rsrp=('rsrp', np.max),
                                                       nr_ssRsrp=('nr_ssRsrp', np.max),
                                                       nr_ssSinr=('nr_ssSinr', np.max),
                                                       rsrp_avg=('rsrp', np.mean),
                                                       nr_ssRsrp_avg=('nr_ssRsrp', np.mean),
                                                       nr_ssSinr_avg=('nr_ssSinr', np.mean),
                                                       mobileRx=('mobileRx', np.max),
                                                       mobileTx=('mobileTx', np.max),
                                                       currentNow=('currentNow', np.mean),
                                                       voltageNow=('voltageNow', np.mean))
    session_grp.reset_index(level=0, inplace=True)
    session_grp.rename(columns={'r_time': 'timestamp'}, inplace=True)
    session_logs = session_grp.copy(deep=True)


    ## 1. Convert geolocation to pixel coordinates

    # latitude = 44.88286883
    # longitude = -93.21207125
    # convertGeoLocationToPixelCoordinates(latitude, longitude)
    #
    # Output:
    # Pixel Coordinates: 8089221, 12085793
    # Tile Coordinates: 31598, 47210
    def convertGeoLocationToPixelCoordinates(latitude, longitude, ZOOM_LEVEL):
        def get_world_coords(latitude_val, longitude_val):
            siny = min(max(np.sin(float(latitude_val) * np.pi / 180), -.9999), .9999)
            world_lat_256 = 256 * (0.5 - np.log((1 + siny) / (1 - siny)) / (4 * np.pi))
            world_long_256 = 256 * (0.5 + float(longitude_val) / 360)
            return world_lat_256, world_long_256

        # the following can be used to test the correctness of calculations using
        # https://developers-dot-devsite-v2-prod.appspot.com/maps/documentation/javascript/examples/map-coordinates
        world_lat_256, world_long_256 = get_world_coords(latitude, longitude)
        TILE_SIZE = 256
        scale = 1 << ZOOM_LEVEL
        pixel_256_z_x = int(np.floor(world_long_256 * scale))
        pixel_256_z_y = int(np.floor(world_lat_256 * scale).astype(int))
        tile_id_256_z_x = int(np.floor(world_long_256 * scale / TILE_SIZE))
        tile_id_256_z_y = int(np.floor(world_lat_256 * scale / TILE_SIZE))
        return pixel_256_z_x, pixel_256_z_y, tile_id_256_z_x, tile_id_256_z_y


    session_logs['pixel_x_y_17'] = session_logs.apply(
        lambda x: convertGeoLocationToPixelCoordinates(x['latitude'], x['longitude'], 17), axis=1)
    session_logs[['pixel_256_z17_x', 'pixel_256_z17_y', 'tile_id_256_z17_x', 'tile_id_256_z17_y']] = pd.DataFrame(
        session_logs['pixel_x_y_17'].tolist(),
        index=session_logs.index)
    session_logs['pixel_x_y_15'] = session_logs.apply(
        lambda x: convertGeoLocationToPixelCoordinates(x['latitude'], x['longitude'], 15), axis=1)
    session_logs[['pixel_256_z15_x', 'pixel_256_z15_y', 'tile_id_256_z15_x', 'tile_id_256_z15_y']] = pd.DataFrame(
        session_logs['pixel_x_y_15'].tolist(),
        index=session_logs.index)


    ## 2. Get panel angles

    def getDistancePixelInMeters(tower_x, tower_y, user_x, user_y, current_latitude):
        distance = math.sqrt((user_x - tower_x) ** 2 + (user_y - tower_y) ** 2) * 1.193 * math.cos(
            math.radians(current_latitude))
        return distance


    def getDistanceGeoInMeters(tower_lon, tower_lat, user_lon, user_lat):
        tower_lon, tower_lat, user_lon, user_lat = map(math.radians, [tower_lon, tower_lat, user_lon, user_lat])
        dlon = user_lon - tower_lon
        dlat = user_lat - tower_lat
        a = math.sin(dlat / 2) ** 2 + math.cos(tower_lat) * math.cos(user_lat) * math.sin(dlon / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))
        r = 6378137
        return c * r


    """
    Author: Xinyue Hu 
    This function calculates the user panel angle from 0 to 360 using the user and tower locations and panel angle
    Usage: 
      tower_x = np.array([2, 2, 2, 2, 2, 2]*2)
      tower_y = np.array([2, 2, 2, 2, 2, 2]*2)
      user_x = np.array([3, 3, 3, 3, 1, 1]*2)
      user_y = np.array([1, 1.5, 0.5, 3, 4, 0.5]*2)
      panel_angle = np.array([45, 45, 45, 45, 45, 45] + [120]*6)
      print('tower_x', tower_x)
      print('tower_y', tower_y)
      print('user_x', user_x)
      print('user_y', user_y)
      print('input panel_angle', panel_angle)
      print('theta2', getUserPanelAnglePixel(tower_x, tower_y, user_x, user_y, panel_angle))
    """


    def getUserPanelAnglePixel(tower_x, tower_y, user_x, user_y, panel_angle):
        # panel_angle: the angle between panel facing direction and the north direction (-y axis)
        # Step 1: Shifting the origin of coordinates to tower, the user coordinate becomes:
        user_x = user_x - tower_x
        user_y = user_y - tower_y
        # step 2: calculate the angle between the tower_user vector and the +x_axis
        theta2_prime = np.arctan2(user_y, user_x) * 180 / np.pi  # in the range [-180, 180]
        theta2_prime = theta2_prime % 360  # in the range [0, 360)
        # print('theta2_prime with respect to +x axis', theta2_prime)  # for test output
        # step 3: convert the panel_angle to respect to +x axis
        panel_angle = panel_angle % 360  # convert range to [0, 360)
        panel_angle = panel_angle - 90
        panel_angle = panel_angle % 360  # convert range to [0, 360)
        # print('panel_angle with respect to +x axis', panel_angle)
        # step 3: the angle between the tower_user vector and panel facing direction
        theta2 = (theta2_prime - panel_angle) % 360
        return theta2


    def getUserPanelAnglePixel_v1(tower_x, tower_y, user_x, user_y, panel_angle):
        def dotproduct(x1, y1, x2, y2):
            return x1 * x2 + y1 * y2

        def length(x, y):
            return math.sqrt(dotproduct(x, y, x, y))

        def getVectorAngle(user_vx, user_vy, tower_vx, tower_vy):
            try:
                vec_angle = math.degrees(math.acos(
                    dotproduct(user_vx, user_vy, tower_vx, tower_vy) / (
                            length(user_vx, user_vy) * length(tower_vx, tower_vy))))
            except:
                vec_angle = -1
            return vec_angle

        def getPanelVector(panel_angle):
            x = 0
            y = 1
            if panel_angle > 180:
                y = -1
            x = y / math.tan(math.radians(panel_angle))
            return x, y

        panel_angle -= 90
        if panel_angle < 0:
            panel_angle += 360
        user_vx = user_x - tower_x
        user_vy = user_y - tower_y
        try:
            tower_vx, tower_vy = getPanelVector(panel_angle)
            angle = getVectorAngle(user_vx, user_vy, tower_vx, tower_vy)
        except:
            angle = -1
        return angle


    """
    Author: Rishabh
    """


    def getUserMovingAngle(compass_dir, panel_angle):
        orientation_wrt_panel = compass_dir - panel_angle
        if orientation_wrt_panel < 0:
            orientation_wrt_panel += 360
        return orientation_wrt_panel


    def getUserPanelAngleGeo(tower_lon, tower_lat, user_lon, user_lat, panel_angle):
        def dotproduct(x1, y1, x2, y2):
            return x1 * x2 + y1 * y2

        def length(x, y):
            return math.sqrt(dotproduct(x, y, x, y))

        def getVectorAngle(user_vx, user_vy, tower_vx, tower_vy):
            try:
                vec_angle = math.degrees(math.acos(
                    dotproduct(user_vx, user_vy, tower_vx, tower_vy) / (
                            length(user_vx, user_vy) * length(tower_vx, tower_vy))))
            except:
                vec_angle = -1
            return vec_angle

        if panel_angle <= 90:
            panel_angle = 90 - panel_angle
        else:
            panel_angle = 360 - (panel_angle - 90)
        user_vlon = (user_lon - tower_lon) * math.cos(math.radians((tower_lat + user_lat) / 2))
        user_vlat = user_lat - tower_lat
        tower_vlat = 1
        if panel_angle > 180:
            tower_vlat = -1
        try:
            tower_vlon = tower_vlat / math.tan(math.radians(panel_angle))
            angle = getVectorAngle(user_vlon, user_vlat, tower_vlon, tower_vlat)
        except:
            angle = -1
        return angle


    # find the important towers for the current location from location_tower.csv file
    src_towers_file = '{}/Towers.csv'.format(DATA_DIR)
    location_towers_df = pd.read_csv(src_towers_file)
    location_towers_df.reset_index(drop=True, inplace=True)

    ctr = 0
    total_rows = session_logs.shape[0]
    session_logs['compassDirection'] = session_logs['compassDirection'].astype(int)

    # keep track of records with multiple mcids within a second \todo
    session_logs['num_mcids'] = session_logs['mCid'].apply(lambda x: len(x))
    # taking last mcid/tower if there are multiple mcids \todo
    session_logs['mCid'] = session_logs['mCid'].apply(lambda x: x[-1]).astype(int)
    session_logs['towerid'] = session_logs['towerid'].apply(lambda x: x[-1]).astype(int)

    session_logs['pixel_256_z17_x'] = session_logs['pixel_256_z17_x'].astype(int)
    session_logs['pixel_256_z17_y'] = session_logs['pixel_256_z17_y'].astype(int)

    session_logs['nrStatus_array'] = session_logs['nrStatus']
    session_logs['nrStatus'] = session_logs['nrStatus'].apply(lambda x: x[-1]).astype(str)

    cur_location_id = 'lt'
    # find the important towers for the current location from location_tower.csv file
    loc_towers = location_towers_df[location_towers_df['location_id'] == cur_location_id]
    loc_towers.reset_index(drop=True, inplace=True)


    def getAllPanelsAngleDistanceOrientation(row):
        global ctr
        global total_rows
        ctr += 1
        if ctr % 200 == 0:
            print("{}/{} Finished".format(ctr, total_rows))
        user_pixel17_x = row['pixel_256_z17_x']
        user_pixel17_y = row['pixel_256_z17_y']
        user_pixel15_x = row['pixel_256_z15_x']
        user_pixel15_y = row['pixel_256_z15_y']
        user_long_x = row['longitude']
        user_lat_y = row['latitude']
        cur_tower = int(row['towerid'])
        compass_direction = row['compassDirection']

        # towers important for location_id
        towers_dist_angle = []

        for tidx, towerid in enumerate(loc_towers['tower_id'].unique().tolist()):
            tower_info_df = loc_towers[loc_towers['tower_id'] == towerid]
            tower_id = int(tower_info_df.iloc[0]['tower_id'])
            tower_connected_flag = cur_tower == tower_id
            tower_x_z17_pixel = tower_info_df.iloc[0]['pixel_256_z17_x']
            tower_y_z17_pixel = tower_info_df.iloc[0]['pixel_256_z17_y']
            tower_x_z15_pixel = tower_info_df.iloc[0]['pixel_256_z15_x']
            tower_y_z15_pixel = tower_info_df.iloc[0]['pixel_256_z15_y']
            tower_long_x = tower_info_df.iloc[0]['longitude']
            tower_lat_y = tower_info_df.iloc[0]['latitude']

            # Calculate distance from tower using pixel
            dist_pixel_z17 = getDistancePixelInMeters(tower_x_z17_pixel, tower_y_z17_pixel, user_pixel17_x,
                                                      user_pixel17_y, 44.977)
            dist_pixel_z15 = getDistancePixelInMeters(tower_x_z15_pixel, tower_y_z15_pixel, user_pixel15_x,
                                                      user_pixel15_y,
                                                      44.977)

            # Calculate distance from tower using lat, long
            dist_geo = getDistanceGeoInMeters(tower_long_x, tower_lat_y, user_long_x, user_lat_y)

            for ind, panel_row in tower_info_df.iterrows():
                # calculate tower angle and moving angle w.r.t. each panel
                panel_angle = tower_info_df.at[ind, 'panel_angle']

                # Calculate angle towards tower using pixel
                angle_pixel = getUserPanelAnglePixel(tower_x_z17_pixel, tower_y_z17_pixel, user_pixel17_x,
                                                     user_pixel17_y, panel_angle)

                # Calculate angle towards tower using lat, long
                angle_geo = getUserPanelAngleGeo(tower_long_x, tower_lat_y, user_long_x, user_lat_y, panel_angle)

                # calculate moving angle w.r.t. tower
                moving_angle = getUserMovingAngle(compass_direction, panel_angle)

                towers_dist_angle.append((tower_id, tower_connected_flag, dist_pixel_z17, dist_pixel_z15, dist_geo,
                                          angle_pixel, angle_geo, moving_angle))

        if len(towers_dist_angle) > 1:
            # sort the towers based on which one the user is closest to at this moment
            # sort by dist_geo and angle_geo
            towers_dist_angle = sorted(towers_dist_angle, key=itemgetter(4, 6))
        # assign these values to corresponding columns of this row
        connected_tower_found = False
        for i in range(len(towers_dist_angle)):
            row['panel_towerid{}'.format(i + 1)] = towers_dist_angle[i][0]
            row['tower_connected_flag{}'.format(i + 1)] = towers_dist_angle[i][1]
            row['tower_dist{}_z17_pixel'.format(i + 1)] = towers_dist_angle[i][2]
            row['tower_dist{}_z15_pixel'.format(i + 1)] = towers_dist_angle[i][3]
            row['tower_dist{}_geo'.format(i + 1)] = towers_dist_angle[i][4]
            row['panel_angle{}_pixel'.format(i + 1)] = towers_dist_angle[i][5]
            row['panel_angle{}_geo'.format(i + 1)] = towers_dist_angle[i][6]
            row['user_moving_angle{}'.format(i + 1)] = towers_dist_angle[i][7]

            # if connected assign to connected set of columns
            if towers_dist_angle[i][1]:
                connected_tower_found = True
                row['panel_towerid'] = towers_dist_angle[i][0]
                row['tower_connected_flag'] = towers_dist_angle[i][1]
                row['tower_dist_z17_pixel'] = towers_dist_angle[i][2]
                row['tower_dist_z15_pixel'] = towers_dist_angle[i][3]
                row['tower_dist_geo'] = towers_dist_angle[i][4]
                row['panel_angle_pixel'] = towers_dist_angle[i][5]
                row['panel_angle_geo'] = towers_dist_angle[i][6]
                row['user_moving_angle'] = towers_dist_angle[i][7]

        # if tower was connected to none of the 5G towers, assign -1
        if not connected_tower_found:
            row['panel_towerid'] = -1
            row['tower_connected_flag'] = False
            row['tower_dist_z17_pixel'] = -1
            row['tower_dist_z15_pixel'] = -1
            row['tower_dist_geo'] = -1
            row['panel_angle_pixel'] = -1
            row['panel_angle_geo'] = -1
            row['user_moving_angle'] = -1

        for i in range(len(towers_dist_angle), MAX_NUM_PANELS):
            row['panel_towerid{}'.format(i + 1)] = -1
            row['tower_connected_flag{}'.format(i + 1)] = -1
            row['tower_dist{}_z17_pixel'.format(i + 1)] = -1
            row['tower_dist{}_z15_pixel'.format(i + 1)] = -1
            row['tower_dist{}_geo'.format(i + 1)] = -1
            row['panel_angle{}_pixel'.format(i + 1)] = -1
            row['panel_angle{}_geo'.format(i + 1)] = -1
            row['user_moving_angle{}'.format(i + 1)] = -1

        return row


    print("Adding Feature Columns to the Data")
    # calculate the distance and angle for each panel up to MAX_NUM_PANELS
    session_logs = session_logs.apply(getAllPanelsAngleDistanceOrientation, axis=1)

    # export results
    session_logs.to_csv(log_filename, index=False, header=True)
    print('file saved ({})..'.format(log_filename))
    print('=======================================================================')
