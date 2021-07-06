reset
set terminal postscript eps enhanced color lw 2 "Helvetica" 50 size 14,5.2
set output "power-rsrp-throughput.eps"
set multiplot layout 1,2

set xlabel "Power (W)" offset 0,0.96 font "Helvetica,50"
set ylabel "NR-SS-RSRP (dBm)" offset 2.3 font "Helvetica,50"
# set format x "%.0s%c"
set xtics 2 offset 0.15,0.35
set ytics offset 0.65
set xrange [4:13]  # set xrange [4000:13000]
set yrange [-122:-56] # set yrange [-120:-35]
set lmargin 5.5
set rmargin 2
set tmargin 1.1
set bmargin 2.12
# set offset -0.52,-0.3,0,0

# set palette rgbformulae 10,21,27  # 33,13,10
set palette defined (0 "#d13220", 500 "#e5dd45", 1500 "#32a164" )
set format cb "%.0s%c"
set cbtics 0,1000,1500 offset -0.8
set cbrange [0:1500]
set cblabel "Downlink Throughput (Mbps)" offset -0.5 font "Helvetica,50"
unset colorbox

set grid lc rgb "gray" lw 2
set style line 12 lc rgb 'black' lt 12 lw 1
set datafile separator ","



# set label 1 "Location A (Verizon mmWave, S10)" at screen 0.075,0.95 font "Helvetica,48"
set label 1 "Ann Arbor, MI (UE: S10)" at screen 0.081,0.97 font "Helvetica,48"
set label 4 "mmWave" at 10.02,-113 font ", 44" textcolor rgb "gray40"
plot 'mi-combined.csv' every ::1 u ($10/1000):4:6 notitle with p ps 1.6 pt 7 palette


set colorbox origin screen 0.9,0.2 size 0.08,0.4
unset ylabel
set xrange [3.5:10.8]  # set xrange [3500:10800]
set lmargin 2.5
set rmargin 0.5
# set label 2 "Location B (Verizon mmWave/low-band, S20U)" at screen 0.535,0.95 font "Helvetica,48"
set label 3 "Minneapolis, MN (UE: S20U)" at screen 0.535,0.97 font "Helvetica,48"
set label 4 "low-band" at 5.62,-62 font ", 44" textcolor rgb "gray40"
set label 5 "mmWave" at 8.1,-117 font ", 44" textcolor rgb "gray40"
set arrow from 3.8,-113.94 to 8.2,-59.53 nohead lc rgb "gray60" lw 5.5 dt (7,9)  # y=12.375x-161
# set arrow from 6.25,-62 to 5.7,-62 head filled size screen 0.01,25,60 lc rgb "gray40" lw 2

plot 'mn-combined_all.csv' every ::1 u ($2/1000):1:4 notitle w p ps 1.6 pt 7 palette

