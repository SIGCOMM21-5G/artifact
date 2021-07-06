reset
set terminal postscript eps enhanced color lw 2 "Helvetica,50" size 14,4.6
set output "efficiency-rsrp.eps"
set multiplot layout 1,2

set xlabel "NR-SS-RSRP (dBm)" offset 1.8,-0.3 font "Helvetica,49"
set ylabel "Energy Efficiency (uJ/bit)" offset 0.95,0.4 font "Helvetica,49"
set format y "10^{%T}"
set xtics offset 0.15,-0.52 rotate by 24 center font "Helvetica,41"
set ytics offset 0.8,0
set lmargin 4.7
set rmargin 0.2
set tmargin 1.1
set bmargin 3.2
# set offset -0.52,-0.3,0,0


set grid lc rgb "gray" lw 2
set style line 12 lc rgb 'black' lt 12 lw 1
# set datafile separator ","

set boxwidth 0.4
set style fill solid 0.5 border -1
# set style data histogram
# set style histogram errorbars gap 1
set style data boxplot
set style boxplot outliers pointtype 7
set style boxplot fraction 0.95
set style boxplot nooutliers

set grid xtics,mxtics,ytics,mytics
set grid lw 3,lw 1,lw 3,lw 1
set grid lt 1,dt 2,lt 1,dt 2
set grid lc rgb "gray90",lc rgb "gray90",lc rgb "gray90",lc rgb "gray90"
set logscale y



set xrange [0.2:7.8] # set xrange [-115:-75] # set yrange [-120:-35]
# set yrange [5:12]  # set xrange [4000:13000]
# set label 1 "Location A (Verizon mmWave, S10)" at screen 0.075,0.95 font "Helvetica,48"
# set label 4 "mmWave" at 10.02,-113 font ", 43" textcolor rgb "gray40"
set label 1 "Ann Arbor, MI (UE: S10)" at screen 0.072,0.97 font "Helvetica,48"
plot 'mi.txt' using ($2):($4):($3):($7):($6):xtic(1) with candlesticks lc rgb "purple" lw 2 ti col axes x1y1 whiskerbars, \
			'' using ($2):($5):($5):($5):($5) with candlesticks lw 2 lt 1 lc rgb "black" notitle axes x1y1

unset ylabel
# set xrange [-125:-70] # set yrange [-120:-35]
# set yrange [4:10.5]  # set xrange [3500:10800]
set lmargin 3.4
set rmargin 1.4
# set label 2 "Location B (Verizon mmWave/low-band, S20U)" at screen 0.535,0.95 font "Helvetica,48"
# set label 4 "low-band" at 5.62,-62 font ", 43" textcolor rgb "gray40"
# set label 5 "mmWave" at 8.1,-117 font ", 43" textcolor rgb "gray40"
# set arrow from 3.9,-112.55 to 8.1,-61.76 nohead lc rgb "gray70" lw 4 dt (7,9)  # y=12.375x-161
# set arrow from 6.25,-62 to 5.7,-62 head filled size screen 0.01,25,60 lc rgb "gray40" lw 2
set label 3 "Minneapolis, MN (UE: S20U)" at screen 0.553,0.97 font "Helvetica,48"
plot 'mn.txt' using ($2):($4):($3):($7):($6):xtic(1) with candlesticks lc rgb "purple" lw 2 ti col axes x1y1 whiskerbars, \
			'' using ($2):($5):($5):($5):($5) with candlesticks lw 2 lt 1 lc rgb "black" notitle axes x1y1
