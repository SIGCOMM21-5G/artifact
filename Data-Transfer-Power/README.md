# Power for Data Transfer

This folder contains the dataset and scripts for controlled data transfer power experiments. It covers all the figures referred om Section 4.3 which include Figures 11, 12, 13, 14.

## Folder Structure   

| Filename                    | Description                                                                                                |
|-----------------------------|------------------------------------------------------------------------------------------------------------|
| `data/5GTracker_iPerf/[Exp date]/[Device ID]-[5GTracker Session ID]-01.csv` | Raw session logs collected using 5GTracker |
| `data/5GTracker_iPerf/[Exp date]/[Device ID]-run[Iperf Run Number]-*-iPerf.json` | Raw Iperf logs collected using 5GTracker |
| `data/PowerMonitor/[Exp date]/[Power log name].csv`           | Raw power logs collected using Monsoon Power Monitor |
| `plot_hardware_power.py`           | Python script to plot power values measured by Monsoon power monitor |
| `plot_thrpt_iperf_json.py`           | Python script to plot throughput values recorded by iPerf3 |

## Dataset Description

The data were collected with different iPerf target throughputs and transfer directions. 

Target throughput range:
- 4G: 10-200 Mbps for downlink and 5-30 Mbps for downlink
- 5G: 10-3000 Mbps for downlink and 5-120 Mbps for uplink

We only provide sample data in this repo. Please find the complete dataset and the data summary on [Google drive](https://drive.google.com/drive/folders/1n7IoMMlTvHKtTibUMbzrdnAM2ToKdkdn?usp=sharing).

### Requirements

Here are the software/package requirements. The version number in the bracket indicates the minimum version that our script has been tested on.

- Python 3 (>= 3.7.7)
- Pandas (>= 1.1.3)
- Matplotlib (>= 3.3.1)

### Running code

After cloning the repository, navigate to `Data-Transfer-Power` folder and run the following command.

```
python3 plot_hardware_power.py data/PowerMonitor/20201130/screenmax-5g-udp-loc5-600m-1.csv 2 0 60
python3 plot_thrpt_iperf_json.py data/5GTracker_iPerf/20201130/APPLE-run10045-udp-loc5-600m-1-iPerf.json 0 60
```

The last two parameters indicate the time interval you want to generate the results for. By default the script will process the entire data.
