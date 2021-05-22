#!/usr/bin/python3
"""
author: Arvind
date: May 20, 2019
Description:
Sets the path for experiment folder particular user's system settings.
"""

import platform
import getpass

if platform.system() == 'Linux' and getpass.getuser() == 'op':
    # Arvind - Alienware Machine
    SHARED_DRIVE_FOLDER = '/home/op/sigcomm20/'
    DATA_FOLDER = '/home/op/sigcomm20/Experiments/'
    OUTPUT_FOLDER = ''
elif platform.system() == 'Linux' and getpass.getuser() == 'ahmad':
    # Ahmad - Desktop
    SHARED_DRIVE_FOLDER = '/media/ahmad/D-Drive/MMWAVE-Experiments/'
    DATA_FOLDER = '/media/ahmad/D-Drive/MMWAVE-Experiments/Experiments/'
    OUTPUT_FOLDER = '/home/ahmad/PycharmProjects/Data-Analysis/data_processed/'
