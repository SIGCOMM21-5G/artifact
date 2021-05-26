#!/bin/bash
echo "Run 7 ABR algorithms over 5G..."
bash run_5g_driving.sh
bash run_5g_walking.sh
echo "Run different throughput predictors over 5G..."
bash run_5g_prediction.sh
echo "Run interface selection schemes..."
bash run_5g_interface.sh
echo "Run different chunk length..."
bash run_5g_chunklen.sh
echo "Run 7 ABR algorithms over 4G..."
cd ../../ABR-4G/run_exp 
bash run_4g_driving.sh
echo "Finished"

