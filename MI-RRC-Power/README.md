# RRC Power

This folder contains the power data for Table 2. For details, we refer readers to sections 4.1 (RRC state inference) and 4.2 in the paper.

## Folder Structure   

| Filename                    | Description                                                                                                |
|-----------------------------|------------------------------------------------------------------------------------------------------------|
| `data/PowerMonitor/[Power log name].csv`           | Raw power logs collected using Monsoon Power Monitor |
| `plot_hardware_power.py`           | Python script to plot power values measured by Monsoon power monitor |

## Dataset Description

The data were collected when repeating RRC state transitions under 4G and 5G (by sending a packet to the UE every 20s). 
- Trace 1-3 were collected when triggering the phone to enter RRC_CONNECTED after 20s inactivity (back to RRC_IDLE).
- Trace 4-6 were collected when performing the same experiment under 5G.

We only provide sample data in this repo. Please find the complete dataset and the data summary on [Google drive](https://drive.google.com/drive/folders/13xJokrKJ6v8PdbgtD-xokCJuVyu_O4eZ?usp=sharing).

### Requirements

Here are the software/package requirements. The version number in the bracket indicates the minimum version that our script has been tested on.

- Python 3 (>= 3.7.7)
- Matplotlib (>= 3.3.1)

### Running code

After cloning the repository, navigate to `MI-Benchmark-Software-Power` folder and run the following command.

```
python3 plot_hardware_power.py data/PowerMonitor/screenmax-5g-loop1-rrc-1.csv 2
```

The last two parameters indicate the time interval you want to generate the results for.
