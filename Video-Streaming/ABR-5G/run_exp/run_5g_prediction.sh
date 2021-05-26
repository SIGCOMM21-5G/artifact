#!/bin/bash
# sudo sysctl -w net.ipv4.ip_forward=1
bash setup.sh
server_ip=172.31.51.127
for trace_file in ../cooked_traces_pred/*
do
    filename=$(basename ${trace_file})
    bash trace_run.sh ${trace_file} > ./bw_truth/bw_MLpredMPC_${filename} &
    BACK_PID=$!
    /usr/bin/python run_video.py ${server_ip} MLpredMPC 200 3 ${filename} 2 # GDBT
    kill ${BACK_PID} > /dev/null 2>&1
    kill $(ps aux | grep _server | awk '{print $2}') > /dev/null 2>&1
    bash trace_run.sh ${trace_file} > ./bw_truth/bw_truthMPC_${filename} &
    BACK_PID=$!
    /usr/bin/python run_video.py ${server_ip} truthMPC 200 3 ${filename} 2 # Ground-truth
    kill ${BACK_PID} > /dev/null 2>&1
    kill $(ps aux | grep _server | awk '{print $2}') > /dev/null 2>&1
    bash trace_run.sh ${trace_file} > ./bw_truth/bw_truthMPC_${filename} &
    BACK_PID=$!
    /usr/bin/python run_video.py ${server_ip} hmMPC 200 3 ${filename} 2 # harmonic mean
    kill ${BACK_PID} > /dev/null 2>&1
    kill $(ps aux | grep _server | awk '{print $2}') > /dev/null 2>&1
done

mv results/* results_predict/