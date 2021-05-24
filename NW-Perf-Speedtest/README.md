(temporary document, will update this)

# Network Performance

This folder contains the dataset and plotting scripts for the Speedtest measurements conducted using Ookla's Speedtest app available from Android's Play Store. It covers all the figures referred in Section 3.2 which include Figures 2,3,4,5,6,7. Note, Figure 1 is the same as Figure 2 numbers however the former was plotted on a geographic map.

## Folder Structure   

| Filename                    | Description                                                                                                |
|-----------------------------|------------------------------------------------------------------------------------------------------------|
| `dataset_speedtest_ookla.csv` | CSV-based dataset containing the Speedtest results. See **_Dataset Description_** section below for more details |
| `plots-section3.py`           | Python script to generate plots. See **_Generating Plots_** section below for more details.                      |

## Dataset Description

The dataset file `dataset_speedtest_ookla.csv` contains several fields. We provide description for each field below.

| Field name           | Description of the field                                           |
|----------------------|--------------------------------------------------------------------|
| `Date`               | Timestamp of the test                           |
| `downlink_Mbps`      | Downlink throughput in Megabits per second (Mbps)                  |
| `uplink_Mbps`        | Uplink throughput in Megabits per second (Mbps)                    |
| `latency_ms`         | Round trip latency in millisecond (ms)                             |
| ~~`country_code`~~     | UE's country code  _(planning to remove this column)_                       |
| `connection_mode`    | Number of connections established for throughput measurement (_single_ or _multi_)       |
| `sponsor_name`       | Host/Provider of the Speedtest server                              |
| `UE_model`           | The make and model of the 5G smartphone                            |
| `Server_city`        | City where server is located                                       |
| `Server_state`       | State where server is located                                      |
| `country`            | Country of both the server and the UE                              |
| `carrier`            | Name of the mobile carrier used by UE                              |
| `radio_type`         | Active radio type (e.g. 4G v/s 5G, NSA v/s SA, low vs mmWave band) |
| `UE_Server_distance` | Approximate geographic distance between the UE and the Server      |
| `Speedtest_URL`      | Publicly viewable result of the Speedtest measurement                                           |

## Generating plots

We have built scripts that uses the dataset provided to generate the plots shown in our paper. More specifically, the scripts will generate Figures 2 to 7.
### Requirements

Here are the software/package requirements. The version number in the bracket indicates the minimum version that our script has been tested on.

- Python 3 (>= 3.7.7)
- Pandas (>= 1.1.3)
- Matplotlib (>= 3.3.1)

### Running code

After cloning the repository, navigate to `NW-Perf-Speedtest` folder and simply run the following command.

`python plots-section3.py`

If everything succeeded, a `plots` folder should be created with all the figures (in 3 formats `.png`, `.pdf` and `.eps`).