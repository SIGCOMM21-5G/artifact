# Web Browsing 

This folder contains the dataset and plotting scripts for the Web Browsing measurements conducted using [Chrome-HAR-Capturer](https://github.com/cyrus-and/chrome-har-capturer) to automatically browse websites and capture the HAR file and using TCPDUMP to collect the network traces to analysis the throughput information.

## Folder Structure

|              Filename              |                         Description                          |
| :--------------------------------: | :----------------------------------------------------------: |
|         `preprocessing.py`         | Analysis the HAR File and TCPDUMP File, generate the `WebSet.pickle` and `fileStatistics.pickle` for futher analysis. |
| `objectnum-plt-energy-analysis.py` |                    Generate Figure.19 a.                     |
| `pagesize-plt-energy-analysis.py`  |                    Generate Figure. 19 b.                    |
|           `draw-cdf.py`            |                     Generate Figure. 20                      |
|                                    |                                                              |
|     `energy-time-analysis.py`      |                     Generate Figure 21.                      |
|      `tree-generation-M1.py`       |                    Generate Figure 22.a.                     |
|      `tree-generation-M4.py`       |                    Generate Figure 22.b.                     |
|      `interface-selection.py`      |                      Generate Table 6.                       |



## Data Folder Structure

Since the dataset is too large, We release the data folder in [Google Drive](). 

We describe the dataset information in `Web Page Experiments Log.csv` File in the data folder. The Log File's structure is formed like the table below.

| TimestampID | Directory | Carrier | Network Type | websitesRange |
| :---------: | :-------: | :-----: | :----------: | :-----------: |
|     T1      |    D1     |   C1    |    4G/5G     |    W10-W11    |
|     T2      |    D2     |   C2    |    4G/5G     |    W20-W21    |
|     ...     |    ...    |   ...   |     ...      |      ...      |
|     Tn      |    Dn     |   Cn    |    4G/5G     |    Wn0-Wn1    |

* `TimestampID` is the timestamp ID when the experiment started.
* `DirectoryID` is the directory name to locate the experiment data folder.
* `Carrier` is the carrier Type we used in the experiment. 
* `Network Type` is the network type when we did the 
* `websiteRange` will indicate the collected websitesID range. For example, 1-1500 means collect the Top 1-1500 websites in the [Alexa Rankings](https://www.alexa.com/topsites).

Thus, to access `nth` round of experiment, the collected har file data can be accessed using `Dn/har-file/Tn` path under data folder. And the collected TCPDUMP file can be accessed using `Dn/tcpdump-file/Tn` path under data folder.

