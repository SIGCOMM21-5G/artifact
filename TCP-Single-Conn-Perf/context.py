#!/usr/bin/env python3
from os import path
import sys
proj_dir = path.abspath(path.join(path.dirname(__file__)))
data_dir = path.join(proj_dir, 'data')
data_processed_dir = path.join(proj_dir, 'data-processed')
plot_dir = path.join(proj_dir, 'plots')
utils_dir = path.join(proj_dir, 'utils')
sys.path.append(proj_dir)
