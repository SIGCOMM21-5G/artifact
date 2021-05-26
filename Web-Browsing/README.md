# Web Browsing 

This folder contains the dataset and plotting scripts for the Section 6. Web Browsing Part. It contain the codes to generate the Figure. 19 to Figure 22 and Table 6.

## Folder structure

|     Filename      |                         Description                          |
| :---------------: | :----------------------------------------------------------: |
|    raw_dataset    |      The raw collected dataset and detailed description      |
| processed_dataset |         The processing script and processed results.         |
|      scripts      | Scripts Folder for generating all the Figure and Table results. |
| plot-section6.sh  |             One command to run all the scripts.              |
| generated_figure  |            Bash Scripts generated results' folder            |

## Generate Plots

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

#### 1.Preprocessing Steps

* The dataset is really large. It will take a long time to do the preprocessing. If you don't want to go through the processing steps, you can follow the descriptions in `processed_dataset` folder to directly download the pickle files. If you want to preprocess from the beginning, you can continue read such description.
* First follow the description in `raw_dataset` folder, to download the content in the raw_dataset folder.
* Follow the description in `processed_dataset` folder to process the dataset.
* **We have provided the incomplete toy pickle files in `processed_dataset` folder. You can first play with it on the following steps**

#### 2. Generate the graphs

After the pickle file is ready, you can use the provided bash command to generate all the results.

```bash
bash plot-section6.sh
```

The generated results will be saved in the `generated_figure` folder.