(Can be updated)
# LTE, SA-5G, NSA-5G Driving Experiments
This folder contains the dataset, processing and plotting scripts LTE, SA-5G, NSA-5G Driving experiments conducted using T-Mobile. It covers Figure 9 referred in Section 3.2 of the paper.

Note that we don't have access to RRC messages to accurately determine the handoff event, so we use Samsung Service Code `*#0101#*` to watch the screen and map the handoff events with the overlaid clock app built by us. We also take video of the experiments, and the video recordings for this experiment can be found [here](https://drive.google.com/drive/folders/13hVPulm6r9PMWZ_gHw1o-2sYh5_6L78_?usp=sharing).

**Run the following command to generate plots.**

```bash
python3 plot-section3-figure9.py
```

## Folder Structure

| Filename | Description |
|----------|-------------|
|`data/[Device ID]-[run number]-handoff.csv`|Logs containing handoff information collected using Samsung magic code|
|`data/[Device ID]-[run number]_PM.csv`|Power logs collected using Monsoon Power Monitor|
|`data-processed/[run number].csv`|Processed logs generated after merging power and handoff logs. See the [Dataset Description](#dataset-description) section for more details|
|`Process-Logs.py`|Python script to process handoff and power logs|
|`plot-section3-figure9.py`|Python script to generate Figure 9 in the paper. See the [Generating Plots](#generating-plots) section for more details|


## Dataset Description

| Field Name | Description |
|-------------|-------------|
|`time`|Time elapsed since the start of experiment (sec)|
|`avg_power`|Average power during each second (W)|
|`active interface`|Mobile network the device is connected to [ NSA-5G, SA-5G, 4G(LTE) ]|
|`handover type`|Handover type [ **4t4:** (4G to 4G horizontal handover), **4t5:** (4G to 5G vertical handover), **5t4:** (5G to 4G vertical handover), **5t5:** (5G to 5G horizontal handover) ]|

## Generating Plots

The scripts will generate Figure 9.

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

The processed logs will be placed in `data-processed` folder. The [Dataset Description](#dataset-description) section gives an overview of the data generated after processing raw logs.

To generate Figure 9 shown in the paper, simply run the following command

```bash
python3 plot-section3-figure9.py
```

This will create a `plots` folder having figures in 3 formats (png, pdf and eps).
