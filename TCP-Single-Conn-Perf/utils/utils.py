#!/usr/bin/python3
'''
Description:
Utils file which has the analysis methods to parse the data
'''
import os
import numpy as np
import matplotlib.pyplot as plt

__author__ = "Arvind Narayanan"

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


# function for setting the colors of the box plots pairs
def setBoxColorsNFill(bp, num, cl):
    n2 = 0
    for n in np.arange(0, num):
        plt.setp(bp['boxes'][n], color=cl[(n * 2)])
        plt.setp(bp['caps'][n2], color=cl[(n * 2)])
        plt.setp(bp['caps'][n2 + 1], color=cl[(n * 2)])
        plt.setp(bp['whiskers'][n2], color=cl[(n * 2)])
        plt.setp(bp['whiskers'][n2 + 1], color=cl[(n * 2)])
        # plt.setp(bp['fliers'][0], markeredgecolor='blue')
        plt.setp(bp['medians'][n], color='black')
        n2 += 2
    idx = 0
    for patch in bp['boxes']:
        patch.set_facecolor(cl[(idx * 2) + 1])
        idx += 1
        if idx == num:
            idx = 0


# ref: https://gist.github.com/ihincks/6a420b599f43fcd7dbd79d56798c4e5a
def lighten_color(color, amount=0.5):
    """
  Lightens the given color by multiplying (1-luminosity) by the given amount.
  Input can be matplotlib color string, hex string, or RGB tuple.

  Examples:
  >> lighten_color('g', 0.3)
  >> lighten_color('#F034A3', 0.6)
  >> lighten_color((.3,.55,.1), 0.5)
  """
    import matplotlib.colors as mc
    import colorsys
    try:
        c = mc.cnames[color]
    except:
        c = color
    c = colorsys.rgb_to_hls(*mc.to_rgb(c))
    return colorsys.hls_to_rgb(c[0], 1 - amount * (1 - c[1]), c[2])


# function for setting the colors of the box plots pairs
def setBoxColorsNFillColorS(bp, num, cl, scolor):
    n2 = 0
    for n in np.arange(0, num):
        plt.setp(bp['boxes'][n], color=cl[((n + scolor) * 2)])
        plt.setp(bp['caps'][n2], color=cl[((n + scolor) * 2)])
        plt.setp(bp['caps'][n2 + 1], color=cl[((n + scolor) * 2)])
        plt.setp(bp['whiskers'][n2], color=cl[((n + scolor) * 2)])
        plt.setp(bp['whiskers'][n2 + 1], color=cl[((n + scolor) * 2)])
        # plt.setp(bp['fliers'][0], markeredgecolor='blue')
        plt.setp(bp['medians'][n], color='black')
        n2 += 2
    idx = 0
    for patch in bp['boxes']:
        patch.set_facecolor(cl[((idx + scolor) * 2) + 1])
        idx += 1
        if idx == num:
            idx = 0


# function for setting the colors of the box plots pairs
def setBoxColorsN(bp, num, cl):
    n2 = 0
    for n in np.arange(0, num):
        plt.setp(bp['boxes'][n], color=cl[(n * 2)])
        plt.setp(bp['caps'][n2], color=cl[(n * 2)])
        plt.setp(bp['caps'][n2 + 1], color=cl[(n * 2)])
        plt.setp(bp['whiskers'][n2], color=cl[(n * 2)])
        plt.setp(bp['whiskers'][n2 + 1], color=cl[(n * 2)])
        # plt.setp(bp['fliers'][0], markeredgecolor='blue')
        plt.setp(bp['medians'][n], color='black')
        n2 += 2


# function for setting the colors of the box plots pairs
def setBoxColor(bp, num, cl):
    n2 = 0
    for n in np.arange(0, num):
        plt.setp(bp['boxes'][n], color=cl)
        plt.setp(bp['caps'][n2], color=cl)
        plt.setp(bp['caps'][n2 + 1], color=cl)
        plt.setp(bp['whiskers'][n2], color=cl)
        plt.setp(bp['whiskers'][n2 + 1], color=cl)
        # plt.setp(bp['fliers'][0], markeredgecolor='blue')
        plt.setp(bp['medians'][n], color='black')
        n2 += 2
    for patch in bp['boxes']:
        patch.set_facecolor(lighten_color(cl, .5))


def truncate_colormap(cmap, minval=0.0, maxval=1.0, n=-1):
    import matplotlib
    if n == -1:
        n = cmap.N
    new_cmap = matplotlib.colors.LinearSegmentedColormap.from_list(
        'trunc({name},{a:.2f},{b:.2f})'.format(name=cmap.name, a=minval, b=maxval),
        cmap(np.linspace(minval, maxval, n)))
    return new_cmap


ROMAN_NUMERAL_TABLE = [
    ("M", 1000), ("CM", 900), ("D", 500),
    ("CD", 400), ("C", 100), ("XC", 90),
    ("L", 50), ("XL", 40), ("X", 10),
    ("IX", 9), ("V", 5), ("IV", 4),
    ("I", 1)
]


def convert_to_roman(number):
    """ Convert an integer to Roman
  >>> print(convert_to_roman(45))
  XLV """
    roman_numerals = []
    for numeral, value in ROMAN_NUMERAL_TABLE:
        count = number // value
        number -= count * value
        roman_numerals.append(numeral * count)

    return ''.join(roman_numerals)


def plotme(plt, plot_id, plot_name, plot_path='plots', show_flag=True, png_only=False, pad_inches=0):
    if show_flag:
        print('Showing Plot {}-{}'.format(plot_id, plot_name))
        plt.show(bbox_inches='tight')
    else:
        if not png_only:
            ax = plt.gca()

            if not os.path.exists('{}/png/'.format(plot_path)):
                os.makedirs('{}/png/'.format(plot_path))
            plt.savefig('{}/png/{}-{}.png'.format(plot_path, plot_id, plot_name), format='png', dpi=300,
                        bbox_inches='tight',
                        pad_inches=pad_inches)
            if not os.path.exists('{}/pdf/'.format(plot_path)):
                os.makedirs('{}/pdf/'.format(plot_path))
            plt.savefig('{}/pdf/{}-{}.pdf'.format(plot_path, plot_id, plot_name), format='pdf', dpi=300,
                        bbox_inches='tight',
                        pad_inches=pad_inches)
            # Save it with rasterized points
            ax.set_rasterization_zorder(1)
            if not os.path.exists('{}/eps/'.format(plot_path)):
                os.makedirs('{}/eps/'.format(plot_path))
            plt.savefig('{}/eps/{}-{}.eps'.format(plot_path, plot_id, plot_name), dpi=300, rasterized=True,
                        bbox_inches='tight',
                        pad_inches=0)
        else:
            plt.savefig('{}/{}-{}.png'.format(plot_path, plot_id, plot_name), format='png', dpi=300,
                        bbox_inches='tight',
                        pad_inches=0)
        print('Saved Plot {}-{}'.format(plot_id, plot_name))


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
