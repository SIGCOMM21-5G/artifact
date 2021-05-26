# Web Browsing 

This folder contains details of the artifacts related to Section 6 (Web Browsing). We provide details of the dataset, analysis scripts as well as plotting scripts to generate Figures 19 to 22 and Table 6.

## Folder structure
|     Filename      |                         Description                          |
| --------------- | ---------------------------------------------------------- |
| raw_dataset    | The raw collected dataset.      |
| processed_dataset | Processed data can be found here         |
| scripts      | Scripts for generating plots and results. |
| plot-section6.sh  | One command to run all the scripts              |
| generated_figure  | Bash Scripts generated results' folder            |


## Requirements

* Python (>=3.6)
* Scapy (>=2.4.4)
* Numpy (>=1.19.5)
* haralyzer (>=1.8.0)
* seaborn (>=0.10.0)
* Scikit-learn (>=0.24.1)
* Matplotlib (>=3.1.3)
* graphviz (>=0.16)



## Data Analysis

#### 1.Preprocessing Steps

* The dataset is large. The preprocessing takes X to Y hours to run on a normal laptop. To save this time, we provide fully processed dataset which can be found in `processed_dataset`. It contains the pickled data structure of the processed data. If you want to preprocess the data from the beginning, you can continue. First follow the description in `raw_dataset` folder, to download the content in the raw_dataset folder.
* Follow the description in `processed_dataset` folder to process the dataset.
* **We have provided the incomplete toy pickle files in `processed_dataset` folder. You can first play with it on the following steps**

#### 2. Generate the graphs

After the pickle file is ready, you can use the provided bash command to generate all the results.

```bash
bash plot-section6.sh
```

The generated results will be saved in the `generated_figure` folder.
