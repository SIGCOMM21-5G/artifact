# Impact of Signal Strength on Power

This folder contains the organized data and scripts for studying the impact of signal strength on power. It covers all the figures referred in Section 4.4 which include Figures 13, 14.

## Folder Structure   

| Filename                    | Description                                                                                                |
|-----------------------------|------------------------------------------------------------------------------------------------------------|
| `[Power-Throughput-RSRP/EnergyEfficiency-RSRP]/[Location]-combined-*.csv` | Processed data for studying Power-RSRP-Throughput relationship |
| `[Power-Throughput-RSRP]/power-rsrp-throughput.gp`           | Gnuplot script for Power-RSRP-Throughput plot |
| `[EnergyEfficiency-RSRP]/calculate-stats.py`           | Python script to calculate stats (e.g., percentiles) of processed data |
| `[EnergyEfficiency-RSRP]/efficiency-rsrp.gp`           | Gnuplot script for EnergyEfficiency-RSRP plot |

## Dataset Description

The data were collected when walking through 5G areas while performing data download/upload.

### Requirements

Here are the software/package requirements. The version number in the bracket indicates the minimum version that our script has been tested on.

- Python 3 (>= 3.7.7)
- Pandas (>= 1.1.3)
- Matplotlib (>= 3.3.1)
- Gnuplot (>= 5.0)

### Running code

After cloning the repository, navigate to `Power-SignalStrength` folder and run the following commands.

```
gnuplot Power-Throughput-RSRP/power-rsrp-throughput.gp
python3 calculate-stats.py -p EnergyEfficiency-RSRP/ -k mn -s ./
python3 calculate-stats.py -p EnergyEfficiency-RSRP/ -k mi -s ./
gnuplot EnergyEfficiency-RSRP/efficiency-rsrp.gp
```
