#!/usr/bin/env bash
# @author: Arvind Narayanan

interface="ens3"
latency=54

# Clean up
sudo modprobe -r ifb
sudo tc qdisc del dev $interface ingress
sudo ip link set dev $interface down
echo "Finished cleaning"

sleep 1

# Setup
sudo ip link set dev $interface up
sudo modprobe ifb numifbs=2
sudo ip link set dev ifb0 up
# sudo ip link set dev ifb1 up
echo "Setup"

sleep 2

# REDIRECT INGRESS eth0 -> ifb0
sudo tc qdisc add dev $interface handle ffff: ingress
sudo tc filter add dev $interface parent ffff: protocol all u32 match u32 0 0 action mirred egress redirect dev ifb0
echo "Filters setup."

sudo tc qdisc add dev ifb0 handle 1: root tbf rate 140mbit burst 20k latency $latency"ms"
echo "4G | Latency: $latency"

