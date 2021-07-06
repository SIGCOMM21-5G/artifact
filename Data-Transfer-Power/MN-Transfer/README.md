# Power for Data Transfer

This folder contains the dataset and scripts for controlled data transfer power experiments. It covers figures 11 and 12 referred in Section 4.3.

## Folder Structure   

| Filename                    | Description                                                                                                |
|-----------------------------|------------------------------------------------------------------------------------------------------------|
| `data/MN-Transfer-Summary.csv` | Summary file containing description for all the runs done|
| `data/[Device-ID]-[Iperf Run Number].csv` | Logs collected using 5GTracker and Monsoon Power Monitor|
|`data-processed/MN-Transfer_combined.csv`| Processed log file used to generate the figures
|`Process-Logs.py`| Python script to process the log files |
| `plot-section4-figure11.py`           | Python script to plot power vs throughput plot in Section 4 |
| `plot-section4-figure12.py`           | Python script to plot energy efficiency plot in Section 4 |

## Dataset Description

The data were collected with different iPerf target bandwidths and transfer directions.

### Requirements

Here are the software/package requirements. The version number in the bracket indicates the minimum version that our script has been tested on.

- Python 3 (>= 3.7.7)
- Pandas (>= 1.1.3)
- Matplotlib (>= 3.3.1)

### Running code
The processed log file can be found in `data-processed` folder. 

Note that we have only put the experiment summary file `MN-Transfer-Summary.csv` in the `data` folder. To regenerate all logs, download the data from [google-drive](https://drive.google.com/drive/folders/1S6elLQyjvWi2MUQbFLVNFRaLrWJVYBfo?usp=sharing) and put it in the `data` folder.

To generate the logs from scratch, the following command can be used.

```bash
python3 Process-Logs.py
```

To generate figure 11 and 12 presented in the paper, please run the following commands:

```bash
python3 plot-section4-figure11.py
python3 plot-section4-figure12.py
```

If everything succeeded, a `plots` folder should be created with the figure (in 3 formats `.png`, `.pdf` and `.eps`).
