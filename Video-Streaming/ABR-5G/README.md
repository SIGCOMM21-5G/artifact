# ABR Streaming 5G


## Prerequisites 
* Install the dependecies (tested with Ubuntu 18.04, python2.7, tensorflow 1.14.0 and Selenium v2.39.0)
```
python setup.py
```

## Running Experiments

To run experiments over the `tc` controlled emulated network, go to `run_exp` folder and run the corresponding scripts.

### Run all the 5G experiments the paper have in one script

Inside `run_exp/`, run
```
bash run_all_experiments.sh
```

This script will run all set of 5G related experiments (7 ABR algorithms, throughput predictiors, different chunk length and interface selection).

For the result of different ABR algorithms over 5G, the result will be in `run_exp/results_driving` and `run_exp/results_walking` folder. For throughput predictors, the result will be in `run_exp/results_predict`. For different chunk length, the results will be in `run_exp/results_chunk_length`. For interface selection, the results will be in `run_exp/results_interface_sel`.

### Run a specific set of experiments

- To run a specific experiment, see the corresponding scripts.


| Experiment  | Script | Output Directory |
| ----------- | ----------- | ----------- |
| 7 ABR Algorithms (driving)   |   `run_exp/run_5g_driving.sh`  |  `run_exp/results_driving`|
| 7 ABR Algorithms (walking)   | `run_exp/run_5g_driving.sh`    |  `run_exp/results_walking`|
| Throughput Predictor   | `run_exp/run_5g_predict.sh`    |  `run_exp/results_predict`|
| Different Chunk Length   | `run_exp/run_5g_chunklen.sh`    |  `run_exp/results_chunklen`|
| Interface Selection   | `run_exp/run_5g_interface_sel.sh`    |  `run_exp/results_interface_sel`|

### Output file format
The output files will be logs recording information (bitrate, stall, etc) about each video session. The name will be in the format of `log_<ABR alrgoithm>_<trace_file>_<specific_setting(optional)>`. 

The content in the logs are in format of `[timestamp(s)   bitrate(kbps) buffer_length(s) stall_time(s) chunck_size(Bytes) download_time(ms) QoE_reward]`.

## Real test experiments

Since we do the experiments on AWS instances and the price is quite high, we currently have the VMs released. If required, we can provide two AWS VMs (a client-server pair) for tesing all the experiments.



## Ackowledgement 

The baseline of the experiment code are modified from the [Pensieve](http://web.mit.edu/pensieve/) repository. 