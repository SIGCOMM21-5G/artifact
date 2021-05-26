#!/usr/bin/python3
'''
Description:
Utils file which has the analysis methods to parse the data
'''
import os
import math
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go



# get colors
cmap10 = plt.cm.tab10  # define the colormap
# extract all colors from the .jet map
colorlist10 = [cmap10(i) for i in range(cmap10.N)]

# get colors
cmap20 = plt.cm.tab20  # define the colormap
# extract all colors from the .jet map
colorlist20 = [cmap20(i) for i in range(cmap20.N)]


# get colors
pastel2 = plt.cm.Pastel2  # define the colormap
# extract all colors from the .jet map
pastel2list = [pastel2(i) for i in range(pastel2.N)]

# get colors
paired = plt.cm.Paired  # define the colormap
# extract all colors from the .jet map
pairedlist = [paired(i) for i in range(paired.N)]

# get colors
set210 = plt.cm.Set2  # define the colormap
# extract all colors from the .jet map
colorlistset2 = [set210(i) for i in range(set210.N)]

def plotme(plt, plot_id, plot_name, plot_path='plots', show_flag=True, png_only=False, pad_inches=0, type='normal'):
  if type == 'normal':
    if show_flag:
      print('Showing Plot {}-{}'.format(plot_id, plot_name))
      plt.show(bbox_inches = 'tight')
    else:
      if not png_only:
        ax = plt.gca()

        if not os.path.exists('{}/png/'.format(plot_path)):
          os.makedirs('{}/png/'.format(plot_path))
        plt.savefig('{}/png/{}-{}.png'.format(plot_path, plot_name, plot_id), format='png', dpi=300, bbox_inches='tight',
                    pad_inches=pad_inches)
        if not os.path.exists('{}/pdf/'.format(plot_path)):
            os.makedirs('{}/pdf/'.format(plot_path))
        plt.savefig('{}/pdf/{}-{}.pdf'.format(plot_path, plot_name, plot_id), format='pdf', dpi=300, bbox_inches='tight',
                    pad_inches=pad_inches)
        # Save it with rasterized points
        ax.set_rasterization_zorder(1)
        if not os.path.exists('{}/eps/'.format(plot_path)):
            os.makedirs('{}/eps/'.format(plot_path))
        plt.savefig('{}/eps/{}-{}.eps'.format(plot_path, plot_name, plot_id), dpi=300, rasterized=True, bbox_inches='tight',
                    pad_inches=0)
      else:
        plt.savefig('{}/{}-{}.png'.format(plot_path, plot_name, plot_id), format='png', dpi=300, bbox_inches='tight',
                    pad_inches=0)
      print('Saved Plot {}-{}'.format(plot_name, plot_id))
  elif type == 'plotly':
    if not png_only:
      if not os.path.exists('{}/pdf/'.format(plot_path)):
          os.makedirs('{}/pdf/'.format(plot_path))
      plt.write_image('{}/pdf/{}-{}.pdf'.format(plot_path, plot_name, plot_id))
      if not os.path.exists('{}/eps/'.format(plot_path)):
          os.makedirs('{}/eps/'.format(plot_path))
      plt.write_image('{}/eps/{}-{}.eps'.format(plot_path, plot_name, plot_id))

    if not os.path.exists('{}/png/'.format(plot_path)):
      os.makedirs('{}/png/'.format(plot_path))
    plt.write_image('{}/png/{}-{}.png'.format(plot_path, plot_name, plot_id))


"""Attach a text label above each bar in *rects*, displaying its height."""
def autolabel(rects, idx, ax):
  for rect in rects:
    height = rect.get_height()
    if isinstance(height, float):
      height = np.round(height, 2)
    ax.annotate('{}'.format(int(height)),
                xy=(rect.get_x() + rect.get_width() / 2, height),
                xytext=(0, 3),  # 3 points vertical offset
                textcoords="offset points",
                ha='center', va='bottom', color=colorlist10[idx])