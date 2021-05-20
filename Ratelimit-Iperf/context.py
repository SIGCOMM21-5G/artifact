#!/usr/bin/env python3
from os import path
import sys
proj_dir = path.abspath(path.join(path.dirname(__file__)))
shared_drive = '/media/ahmad/D-Drive/MMWAVE-Experiments'
data_dir = path.join(shared_drive, 'artifact_release')
data_processed_dir = path.join(proj_dir, 'data-processed')
plot_dir = path.join(proj_dir, 'plots')
utils_dir = path.join(proj_dir, 'utils')
sys.path.append(proj_dir)
