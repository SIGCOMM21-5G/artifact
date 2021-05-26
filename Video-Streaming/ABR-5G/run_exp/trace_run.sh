#!/usr/bin/env bash
# @author: Arvind Narayanan

# throughput file in mbits
traces=$1

# interval to change the traces by (in seconds)
interval=1.0

# separator
sep=" "
printf "$(date +%s.%2N)\n"

while IFS=$sep read -r timestamp fiveg remainder
do
  sleep $interval"s" &

  # change bandwidth 
  y1=$(awk "BEGIN {print $fiveg+0.00001; exit}")
  sudo tc qdisc change dev ifb0 handle 1: root tbf rate $y1"mbit" burst 20k latency 54ms

  # calculate delay
  printf "%5s: %4d Mbps | Timestamp: $(date +%s.%4N) \n" "5G" $fiveg 

  wait
done < $traces

echo "Complete./"
