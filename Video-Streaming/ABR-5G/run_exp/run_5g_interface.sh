#!/bin/bash
# sudo sysctl -w net.ipv4.ip_forward=1
bash setup.sh
server_ip=172.31.51.127
for trace_file in ../cooked_traces_driving/*
    do
        filename=$(basename ${trace_file})
        echo "replaying with trace file ${filename}" # in format of 5g_driving...
        bash trace_run.sh ${trace_file} > ./bw_truth/bw_fastMPC_${filename} &
        BACK_PID=$!
        /usr/bin/python run_video.py ${server_ip} fastMPC 240 6 ${filename} 5
        kill ${BACK_PID} > /dev/null 2>&1
        kill $(ps aux | grep _server | awk '{print $2}') > /dev/null 2>&1
    done

for trace_file in ../cooked_traces_multipath/driving/*
    do
        filename=$(basename ${trace_file})
        echo "replaying with trace file ${filename}" # in format of 5g_driving...

        # run 5G aware interface selection
        sudo python interface_scheduler.py ${trace_file} > ./bw_truth/bw_multi_fastMPC_${filename} > /dev/null 2>&1 &
        BACK_PID=$!
        /usr/bin/python run_video.py ${server_ip} intfMPC 200 6 ${filename} 5
        kill $(ps aux | grep _server | awk '{print $2}') > /dev/null 2>&1
        sudo kill $(ps aux | grep interface_scheduler | awk '{print $2}') > /dev/null 2>&1

        # run the oracle interface selection (without conrtol plane overhead)
        sudo python interface_scheduler_no_overhead.py ${trace_file} > ./bw_truth/bw_truth_interfaceMPC_${filename} > /dev/null 2>&1 &
        BACK_PID=$!
        /usr/bin/python run_video.py ${server_ip} intfMPC_no_overhead 200 6 ${filename} 5
        kill $(ps aux | grep _server | awk '{print $2}') > /dev/null 2>&1
        sudo kill $(ps aux | grep interface_scheduler | awk '{print $2}') > /dev/null 2>&1
    done

mv results/* results_interface_sel/