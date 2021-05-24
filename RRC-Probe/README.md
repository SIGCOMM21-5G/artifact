# RRC-Probe

This folder contains the dataset and plotting scripts for Figure 10. For details, we refer readers to sections 4.1 (RRC state inference) and 4.2 in the paper. The tool for RRC-Probe is part of 5G Tracker. 

## Folder Structure   

| Filename                    | Description                                                                                                |
|-----------------------------|------------------------------------------------------------------------------------------------------------|
| `dataset_rrc_probe.csv` | CSV-based dataset containing the Speedtest results. See **_Dataset Description_** section below for more details |
| `plot-section4-figure10.py`           | Python script to process the data and generate the plot. See **_Generating Plots_** section below for more details.                      |

## Dataset Description

The dataset file `dataset_rrc_probe.csv` contains several fields. We provide description for each field below.

| Field name           | Description of the field                                           |
|----------------------|--------------------------------------------------------------------|
| `enabled_radio_type`               | The radio types (e.g. 4G, low-band 5G NSA, etc.) enabled for the test.                        |
| `carrier`      | Name of the commercial carrier                  |
| `interval`        | Idle time between packets in seconds                    |
| `RTT1`         | ToDO: XX                             |
| `RTT2`    | ToDo: YYY       |
| `Network`       | Radio type active at the time of responding back to the server                            |
| `KeepOrDrop`           | We `keep` the data point if there were no other RX/TX transfer on the UE side between two consecutive RRC-Probe packet arrivals. If some other data transmission occured, we mark them as `bad` and remove such noisy data point from the dataset.              |

## Generating plots

We have built scripts that uses the dataset provided to generate the plots shown in our paper. More specifically, the scripts will generate Figure 10.
### Requirements

Here are the software/package requirements.

- Python 3 (>= 3.7.7)
- Pandas (>= 1.1.3)
- Matplotlib (>= 3.3.1)

### Running code

After cloning the repository, navigate to `RRC-Probe` folder and simply run the following command.

`python plot-section4-figure10.py`

If everything succeeded, a `plots` folder should be created with the figure (in 3 formats `.png`, `.pdf` and `.eps`).