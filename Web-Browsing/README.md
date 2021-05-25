# Web Browsing 

This folder contains the dataset and plotting scripts for the Web Browsing measurements conducted using [Chrome-HAR-Capturer](https://github.com/cyrus-and/chrome-har-capturer) to automatically browse websites and capture the HAR file and using TCPDUMP to collect the network traces to analysis the throughput information.

## Folder Structure

|              Filename              |                         Description                          |
| :--------------------------------: | :----------------------------------------------------------: |
|         `preprocessing.py`         | Analysis the HAR File and TCPDUMP File, generate the `WebSet.pickle` and `fileStatistics.pickle` for futher analysis. |
| `objectnum-plt-energy-analysis.py` |                    Generate Figure.19 a.                     |
| `pagesize-plt-energy-analysis.py`  |                    Generate Figure. 19 b.                    |
|           `draw-cdf.py`            |                     Generate Figure. 20                      |
|     `energy-time-analysis.py`      |                     Generate Figure 21.                      |
|      `tree-generation-M1.py`       |                    Generate Figure 22.a.                     |
|      `tree-generation-M4.py`       |                    Generate Figure 22.b.                     |
|      `interface-selection.py`      |                      Generate Table 6.                       |



## Data Folder Structure

Since the dataset is too large, We release the data folder in [Google Drive](https://drive.google.com/drive/folders/1ADDPvkAGiRTYAIxJJUzuY_UhMTW9Ifm0?usp=sharing). 

We describe the dataset information in [Web Page Experiments Log.csv](https://drive.google.com/file/d/1ShOFsJ22KvY4ImFQZgnAl3GaHWOwb2Y6/view?usp=sharing) File in the data folder. The Log File's structure is formed like the table below.

| TimestampID | Directory | Carrier | Network Type | websitesRange |
| :---------: | :-------: | :-----: | :----------: | :-----------: |
|     T1      |    D1     |   C1    |    4G/5G     |    W10-W11    |
|     T2      |    D2     |   C2    |    4G/5G     |    W20-W21    |
|     ...     |    ...    |   ...   |     ...      |      ...      |
|     Tn      |    Dn     |   Cn    |    4G/5G     |    Wn0-Wn1    |

* `TimestampID` is the timestamp ID when the experiment started.
* `DirectoryID` is the directory name to locate the experiment data folder.
* `Carrier` is the carrier Type we used in the experiment. 
* `Network Type` is the network type when we did the experiment. It will be 4G or 5G.
* `websiteRange` will indicate the collected websitesID range. For example, 1-1500 means collect the Top 1-1500 websites in the [Alexa Rankings](https://www.alexa.com/topsites).

Thus, to access `nth` round of experiment, the collected har file data can be accessed using `Dn/har-file/Tn` path under data folder. And the collected TCPDUMP file can be accessed using `Dn/tcpdump-file/Tn` path under data folder.



## Generate Plots

We have built scripts that uses the dataset provided to generate the plots shown in our paper. More specifically, the scripts will generate Figures 19 to 22 and along with Table6.

### Requirements

* Python>=3.6
* Scapy>=2.4.4
* Numpy>=1.19.5
* haralyzer>=1.8.0
* seaborn>=0.10.0 
* Scikit-learn>=0.24.1
* Matplotlib>=3.1.3
* graphviz>=0.16



### Running Code

#### 1.Preprocessing

After cloning the repo and download the raw dataset from google drive. Then use `preprocessing.py` to generate the processed data and save it to `WebSet.pickle` and `fileStatistics.pickle`.

```shell
python preprocessing.py --data_path ./Webbrowsing
```

When the preprocessing is done, the  `WebSet.pickle` and `fileStatistics.pickle` will be saved in your current directory. (This step usually takes several hours.)

To save your time, we have offered our generated pickle file in the Shared Google Folder.

#### 2. Generate the graphs

When we have got the pickle files then we can begin to generate the graphs.

```bash
python objectnum-plt-energy-analysis.py #generate objectnum-plt-energy-relation.pdf for Figure 19.a
python pagesize-plt-energy-analysis.py #generate objectnum-plt-energy-relation.pdf for Figure 19.b
python draw-cdf.py # generate cdf-energy.pdf and cdf-plt.pdf for Figure 20
python energy-time-analysis.py #generate energy-plt-relation.pdf for Figure 21
python tree-generation-M1.py #generate tree-M1.png for Figure 22.a.
python tree-generation-M4.py #generate tree-M4.png for Figure 22.b.
python interface-selection.py #generate Table6.
```

