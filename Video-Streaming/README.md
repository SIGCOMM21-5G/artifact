# Adaptive Video Streaming

Since we run 7 different ABR algorithms over many traces (both 4G and 5G) sequentially, it will take longer than 24 hours to finish all the experiments. Hence we provide a screencast of running a subset of the traces to illustrate how the video emulation testbed works. We also provide the full results and ploting scripts for the figures in the paper.

## Folder Structure

| Folder Name | Description |
| ----------- | ----------- |
| `ABR-5G` | Code for running video streaming emulation over 5G network traces. See README.md in `ABR-5G` folder for more details. |
| `ABR-4G` | Code for running video streaming emulation over 4G network traces. |
| `Network-Traces` | Contains the traces used for emulation, including the Lumos5G Verizon 4G/5G traces and throughput prediction traces. |
| `Full-Results` | The full video session logs obtained from all the video-related experiments. They are used for plotting the results in the paper. |

## Video session log structure

The video session files inside `Full-Results` are the logs containing information (bitrate, stall, etc) about each video session. The name will be in the format of `log_<ABR alrgoithm>_<trace_file>_<specific_setting(optional)>`. Each file includes 7 fields shown below and each line represents one video chunk during the session.

| Field Name | Description |
| ----------- | ----------- |
| `Timestamp (s)` (column 1) | The download finish time at the video chunk. |
| `bitrate (kbps)` (column 2) | Bitrate of the video chunk. |
| `buffer_length (s)` (column 3) | Contains the video buffer length of the session. |
| `stall_time (s)` (column 4)| Stall time incurred by the chunk. |
| `chunck_size (bytes)` (column 5)| The video chunk size. |
| `download_time (ms)` (column 6)| Download time of the chunk. |
| `QoE_reward` (column 7)| The QoE value of the chunk. |

## Generating Plots

We have built scripts that uses the results provided to generate the plots shown in our paper. More specifically, the scripts will generate Figure 18 and 19.

### Prerequisites

* Python >= 2.7.17, matplotlib >= 2.1.1, scipy >= 0.19.1, numpy >= 1.16.6


To generate the figures, run `bash plot-section5.sh`. A `plots` folder should be created with the figures.

## Real test experiments

Since we perform the experiments on AWS VM instances and the price is quite high, we currently have the VMs released. If required, we can provide two AWS VMs (a client-server pair) for tesing all the experiments. For setting up instructions, please refer to `ABR-5G/README.md`.
