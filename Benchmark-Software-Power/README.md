# Benchmarking Software-based Power Monitor

This folder contains the dataset and scripts for the experiments of benchamarking software-based power monitor. It covers the Table 8 in Appendix A.4 (also see Section 4.6).

## Folder Structure   

| Filename                    | Description                                                                                                |
|-----------------------------|------------------------------------------------------------------------------------------------------------|
| `data/5GTracker_iPerf/[Sampling rate]/[Device ID]-[5GTracker Session ID]-01.csv` | Raw session logs collected using 5GTracker |
| `data/5GTracker_iPerf/[Sampling rate]/[Device ID]-run[Iperf Run Number]-*-iPerf.json` | Raw Iperf logs collected using 5GTracker |
| `data/PowerMonitor/[Sampling rate]/[Power log name].csv`           | Raw power logs collected using Monsoon Power Monitor |
| `plot_hardware_power.py`           | Python script to plot power values measured by Monsoon power monitor |
| `plot_software_power.py`           | Python script to plot power values calculated from current/voltage data collected by 5GTracker |

## Dataset Description

The data were collected when running different types of test cases on the UE and turning on 5GTracker at different logging rates (1Hz, 10Hz). The software power values are measured by 5GTracker through system APIs for current and voltage readings. The hardware power values are measured by Monsoon Power Monitor at 5000Hz. The 5GTracker session logs contains several fields that are useful for this experiment. We provide description for them below.

| Field name           | Description of the field                                           |
|----------------------|--------------------------------------------------------------------|
| `currentNow`      | Instantaneous current readings |
| `voltageNow`      | Instantaneous voltage readings |

We only provide sample data in this repo. Please find the complete dataset and the data summary on [Google drive](https://drive.google.com/drive/folders/1zTzPrJbJs_Z-P6sfPHZAgurgjWQuFI6O?usp=sharing).

### Requirements

Here are the software/package requirements. The version number in the bracket indicates the minimum version that our script has been tested on.

- Python 3 (>= 3.7.5)
- Matplotlib (>= 3.3.1)

### Running code

After cloning the repository, navigate to `Benchmark-Software-Power` folder and run the following command.

```
python3 plot_hardware_power.py data/PowerMonitor/10Hz/screenmax-5g-dl-udp-loc5-50m-2-10hz.csv 2 0 60
python3 plot_software_power.py data/5GTracker_iPerf/10Hz/APPLE-1607638238-01.csv 2 0 60
```

The last two parameters indicate the time interval you want to generate the results for. By default the script will process the entire data.
