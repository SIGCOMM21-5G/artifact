# MI Power Wild Experiments

This folder contains the dataset and processing scripts for power experiments conducted using **5GTracker** and Monsoon Power Monitor at Ann Arbor, MI.

## Folder Structure   

| Filename                    | Description                                                                                                |
|-----------------------------|------------------------------------------------------------------------------------------------------------|
| `data/5GTracker_iPerf/[Sampling rate]/[Device ID]-[5GTracker Session ID]-01.csv` | Raw session logs collected using 5GTracker |
| `data/5GTracker_iPerf/[Sampling rate]/[Device ID]-run[Iperf Run Number]-*-iPerf.json` | Raw Iperf logs collected using 5GTracker |
| `data/PowerMonitor/[Sampling rate]/[Power log name].csv`           | Raw power logs collected using Monsoon Power Monitor |
| `data/processed_dataset/mi_[Exp data]_[direction]_[TCP/UDP]_[Target throughput]_1.csv`		| Processed logs generated after merging processed 5GTracker logs and raw power logs |
| `generate_dataset.py`           | Python script to process 5GTracker logs and power logs |
| `combine_dataset.py`           | Python script to combine processed data into one csv file |

## Dataset Description

The data were collected when walking through 5G areas while performing data download/upload. The raw data consist of both 5GTracker/iPerf logs and power monitor logs. We also provide a combined data file with key columns extracted from all types of logs, combined from the entire processed dataset. The 5GTracker session logs contains several fields. We provide description for them below.

| Field name           | Description of the field                                           |
|----------------------|--------------------------------------------------------------------|
| `timestamp`      | Timestamp when the data point is generated |
| `nrStatus`      | Mobile device connected to 5G NR or not |
| `LTE_RSRP`      | Reference Signal Received Power for current LTE cell in each second (dBm) |
| `nr_ssRsrp`      | Reference Signal Received Power for current NR cell in each second (dBm) |
| `nr_ssSinr`      | Signal to Interference & Noise Ratio for current NR cell in each second (dBm) |
| `downlink_Mbps`      | Instantaneous voltage readings |
| `uplink_Mbps`      | Instantaneous voltage readings |
| `software_power`      | Power calculated using current and voltage values exposed by sysfs interface (mW) |
| `hardware_power`      | Power obtained by subtracting the base power from the total power measured by Monsoon power monitor (mW) |
| `hardware_power_full`      | Total power measured by Monsoon power monitor (mW) |

We only provide sample data in this repo. Please find the complete dataset and the data summary on [Google drive](https://drive.google.com/drive/folders/17DBed12BaHQtEJmSdcZW2wM_sUwW29XO?usp=sharing).

### Requirements

Here are the software/package requirements. The version number in the bracket indicates the minimum version that our script has been tested on.

- Python 3 (>= 3.7.7)
- Pandas (>= 1.1.3)
- Matplotlib (>= 3.3.1)
- scikit-learn (>= 0.24.0)

### Running code

The following example commands process the raw data to combined data which is ready for regression.

```
python3 generate_dataset.py -t data/5GTracker_iPerf/APPLE-1609992831-01.csv -p data/PowerMonitor/20210106-screenmax-5g-dl-udp-loop1-1200m-1.csv -s data-processed/merged_mi-vz-hb/mi_0106_dl_udp_1200_1.csv -b 3105.223145
python3 combine_dataset.py -t mi-vz-hb -s data/
```

The baseline power can be retrieved from the data summary on [Google drive](https://drive.google.com/drive/folders/17DBed12BaHQtEJmSdcZW2wM_sUwW29XO?usp=sharing).
