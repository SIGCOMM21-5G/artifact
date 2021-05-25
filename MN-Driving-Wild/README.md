(Can be updated)
# T-Mobile Driving Experiments
This folder contains the dataset, processing and plotting scripts MN driving experiments. It covers Figure 9 referred in Section 3.2 of the paper.

Note that we don't have access to RRC messages to accurately determine the time of handoff, so we use Samsung magic code and manually watch the screen to collect data for handoffs.


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
|`active interface`|Mobile network the device is connected to [NSA-5G, SA-5G, 4G]|
|`handover type`|Handover type [4G to 4G, 4G to 5G, 5G to 4G, 5G to 5G]|

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
