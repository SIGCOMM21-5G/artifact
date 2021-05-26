#!/usr/bin/env bash
# @author: Arvind Narayanan

interface="ens3"
latency=54

# Clean up
sudo modprobe -r ifb
sudo tc qdisc del dev $interface ingress
# sudo ip link set dev $interface down
echo "Finished cleaning"