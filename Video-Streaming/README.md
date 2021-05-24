# Adaptive Video Streaming

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

To generate the figures, run `bash plot-section5.sh`. A `plots` folder should be created with the figures.