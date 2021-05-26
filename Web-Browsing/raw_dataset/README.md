## Raw Data Description

Since the dataset is too large, We release the data folder in [Google Drive](https://drive.google.com/drive/folders/1ADDPvkAGiRTYAIxJJUzuY_UhMTW9Ifm0?usp=sharing). You can download all the contents in `raw_dataset` folder in Google Drive to this folder for futher processing.

We describe the dataset information in `Web Page Experiments Log.csv` File. The Log File's structure is formed like the table below.

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

Thus, to access `nth` round of experiment, the collected har file data can be accessed using `Dn/har-file/Tn` path under raw data folder. And the collected TCPDUMP file can be accessed using `Dn/tcpdump-file/Tn` path under raw data folder.