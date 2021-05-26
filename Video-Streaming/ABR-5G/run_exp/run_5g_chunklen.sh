if [ $# -eq 0 ]
then
    echo "Running in the default setup (provided VMs)"
    interface=ens4
    server_ip=172.31.51.127
else
    echo "Running in the custom setup"
    interface=$1
    server_ip=$2
fi


for trace_file in ../cooked_traces_chunklen/*
    do
        echo "replaying with trace file ${trace_file}" # in format of ../cooked_traces/5g....
        filename=$(basename ${trace_file})
        # Run the 1 sec chunk length
        bash trace_run.sh ${trace_file} > ./bw_truth/bw_fastMPC_${filename} &
        BACK_PID=$!
        /usr/bin/python run_video_1s.py ${server_ip} fastMPC 200 6 ${filename} 5
        kill ${BACK_PID} > /dev/null 2>&1
        kill $(ps aux | grep _server | awk '{print $2}') > /dev/null 2>&1

        # Run the 2 sec chunk length
        bash trace_run.sh ${trace_file} > ./bw_truth/bw_fastMPC_${filename} &
        BACK_PID=$!
        /usr/bin/python run_video_2s.py ${server_ip} fastMPC 200 6 ${filename} 5
        kill ${BACK_PID} > /dev/null 2>&1
        kill $(ps aux | grep _server | awk '{print $2}') > /dev/null 2>&1

        # Run the 4 sec chunk length
        bash trace_run.sh ${trace_file} > ./bw_truth/bw_fastMPC_${filename} &
        BACK_PID=$!
        /usr/bin/python run_video_4s.py ${server_ip} fastMPC 200 6 ${filename} 5
        kill ${BACK_PID} > /dev/null 2>&1
        kill $(ps aux | grep _server | awk '{print $2}') > /dev/null 2>&1

    done