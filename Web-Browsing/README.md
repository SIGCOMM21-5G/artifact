# Web Browsing 

This folder contains details of the artifacts related to Section 6 (Web Browsing). We provide details of the dataset, analysis scripts as well as plotting scripts to generate Figures 19 to 22 and Table 6.

## Folder structure
|     Foldername/Filename      |                         Description                          |
| --------------- | ---------------------------------------------------------- |
| raw_dataset/[date]/har-file/[timeStampID]    | The collected HAR dataset.      |
| raw_dataset/[date]/tcpdump-file/[timeStampID]    | The collected TCPDUMP dataset.      |
| processed_dataset | Processed data can be found here         |
| scripts      | Scripts for generating plots and results. |
| preprocessing.py | Preprocessing Script |
| plot-section6.sh  | One command to run all the scripts              |
| results  | Bash Scripts generated results and save in results folder            |

---

## Requirements

* Python (>=3.6)
* Scapy (>=2.4.4)
* Numpy (>=1.19.5)
* haralyzer (>=1.8.0)
* seaborn (>=0.10.0)
* Scikit-learn (>=0.24.1)
* Matplotlib (>=3.1.3)
* graphviz (>=0.16)

Also, install the `graphviz` package using the following commands on Ubuntu:
```bash
sudo apt-get install graphviz
```

---

## Data Analysis

#### Step 1 (Data Preprocessing)

The dataset is large due to which the preprocessing can take X to Y hours to complete on a normal laptop. To save time, we provide fully processed dataset. 

*Follow these instructions to skip preprocessing step*
   - Download the repository to your computer
   - Replace `processed_dataset` folder with the one in [Google Drive](https://drive.google.com/drive/u/1/folders/1ADDPvkAGiRTYAIxJJUzuY_UhMTW9Ifm0)
   - Proceed to step 2

*Follow these instructions to preprocess complete dataset*
   - Download the repository to your computer
   - Replace the `raw_dataset` with the one in [Google Drive](https://drive.google.com/drive/u/1/folders/1ADDPvkAGiRTYAIxJJUzuY_UhMTW9Ifm0)
   - Run `python preprocessing.py`
   - After the preprocessing is complete, two pickle files `WebSet.pickle` and `fileStatistics.pickle` will be saved in the `processed_dataset` folder. Details of the pickle files can be found [here](processed_dataset).

By default, `raw_dataset` and `processed_data` contain sample files that one could use to test the environment or play with it. 

#### Step 2 (Generate the plots)

Once the both pickle files are present in `processed_dataset` folder, we can use the following bash command to generate all the results and plots.

```bash
bash plot-section6.sh
```
The generated results will be saved in the `results` folder.
