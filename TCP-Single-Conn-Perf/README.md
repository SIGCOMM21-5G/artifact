# TCP Single Connection Performance
This folder contains the dataset, processing and plotting scripts for TCP single connection performance measurements conducted using **5GTracker** and Azure VMs. It covers Figure 8 referred in Section 3.2 of the paper.

## Folder Structure

| Filename | Description |
|----------|-------------|
|`data/TCP-Single-Conn-Perf.csv`|Contains description of the runs done|
|`data/ping/az-[server_location].csv`|Ping tests for each azure server|
|`data/client/[iperf_run_number].json`|Raw Iperf logs collected on client side|
|`data/UE-Azure-Server-Distance.csv`|CSV-based file containing distance between UE and Microsoft Azure servers tested|
|`data-processed/TCP-Single-Conn-Perf_combined.csv`|CSV-based combined file containing summarized results for all runs. See the [Dataset Description](#dataset-description) section for more details|
|`Process-Logs.py`|Python script to process logs for TCP single connection performance|
|`plot-section3-figure8.py`|Python script to generate figure 8. See the [Generating Plots](#generating-plots) section for more details| 

## Dataset Description

| Field Name | Description |
|-------------|-------------|
|`server_location`|Location of Microsoft Azure server in US
|`latency_min`|Minimum latency seen for server in ping test (ms)
|`type`|Connection type used (TCP-1 default, UDP, TCP-8, TCP-1 tuned) 
|`iperf_run_number`|Iperf run number in 5GTracker
|`distance`|Distance between client and azure servers (miles)
|`throughput_rolled3_avg`|Average throughput calculated after rolling with window size 3 (Mbps)
|`throughput_avg`|Average throughput calculated from raw values (Mbps)
|`throughput_max`|Maximum throughput seen for each run (Mbps)
|`throughput_90tile`|90th percentile throughput seen for each run (Mbps)
|`throughput_95tile`|95th percentile throughput seen for each run (Mbps)
|`throughput_median`|Median throughput seen for run (Mbps)

## Generating Plots

The scripts will generate Figure 8.

### Requirements
Here are the software/package requirements. The version number in the bracket indicates the minimum version that our script has been tested on.

- Python 3 (3.7.7 and higher)
- Pandas (1.1.3 and higher)
- Matplotlib (3.3.1 and higher)

### Running code
To regenerate the processed logs, the following command can be used.

```bash
python3 Process-Logs.py
```

The processed logs will be placed in `data-processed` folder. The [Folder Structure](#folder-structure) section gives a detailed overview of all the files in `data-processed` folder.

To generate Figure 8 shown in the paper, simply run the following command

```bash
python3 plot-section3-figure8.py
```

This will create a `plots` folder having figures in 3 formats (png, pdf and eps).
