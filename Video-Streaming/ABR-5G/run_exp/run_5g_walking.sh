#!/bin/bash
# sudo sysctl -w net.ipv4.ip_forward=1
bash setup.sh
server_ip=172.31.51.127
# run for all traces and algos
for trace_file in ../cooked_traces_walking/*
    do
        echo "replaying with trace file ${trace_file}" # in format of ../cooked_traces/5g....
        filename=$(basename ${trace_file})
        echo "replaying with trace file ${filename}" # in format of 5g_driving...
        bash trace_run.sh ${trace_file} > ./bw_truth/bw_robustMPC_${filename} &
        BACK_PID=$!
        /usr/bin/python run_video_walk.py ${server_ip} robustMPC 200 0 ${filename} 6
        kill ${BACK_PID} > /dev/null 2>&1
        kill $(ps aux | grep _server | awk '{print $2}') > /dev/null 2>&1
        bash trace_run.sh ${trace_file} > ./bw_truth/bw_fastMPC_${filename} &
        BACK_PID=$!
        /usr/bin/python run_video_walk.py ${server_ip} fastMPC 200 6 ${filename} 5
        kill ${BACK_PID} > /dev/null 2>&1
        kill $(ps aux | grep _server | awk '{print $2}') > /dev/null 2>&1
        bash trace_run.sh ${trace_file} > ./bw_truth/bw_BB_${filename} &
        BACK_PID=$!
        /usr/bin/python run_video_walk.py ${server_ip} BB 200 2 ${filename} 1
        kill ${BACK_PID} > /dev/null 2>&1
        kill $(ps aux | grep _server | awk '{print $2}') > /dev/null 2>&1
        bash trace_run.sh ${trace_file} > ./bw_truth/bw_RB_${filename} &
        BACK_PID=$!
        /usr/bin/python run_video_walk.py ${server_ip} RB 200 3 ${filename} 4
        kill ${BACK_PID} > /dev/null 2>&1
        kill $(ps aux | grep _server | awk '{print $2}') > /dev/null 2>&1
        bash trace_run.sh ${trace_file} > ./bw_truth/bw_BOLA_${filename} &
        BACK_PID=$!
        /usr/bin/python run_video_walk.py ${server_ip} BOLA 200 4 ${filename} 3
        kill ${BACK_PID} > /dev/null 2>&1
        kill $(ps aux | grep _server | awk '{print $2}') > /dev/null 2>&1
        bash trace_run.sh ${trace_file} > ./bw_truth/bw_FESTIVE_${filename} &
        BACK_PID=$!
        /usr/bin/python run_video_walk.py ${server_ip} FESTIVE 200 5 ${filename} 2
        kill ${BACK_PID} > /dev/null 2>&1
        kill $(ps aux | grep _server | awk '{print $2}') > /dev/null 2>&1
        bash trace_run.sh ${trace_file} > ./bw_truth/bw_RL_${filename} &
        BACK_PID=$!
        /usr/bin/python run_video_walk.py ${server_ip} RL 200 9 ${filename} 7
        kill ${BACK_PID} > /dev/null 2>&1
        kill $(ps aux | grep _server | awk '{print $2}') > /dev/null 2>&1
    done

mv results/* results_walking/