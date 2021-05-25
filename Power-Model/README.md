# Power Wild Experiments (data for Power model)

This dataset consists of data collected at two locations. It covers power modeling results presented in Section 4.4 of the paper.

## Folder Structure   

| Filename                    | Description                                                                                                |
|-----------------------------|------------------------------------------------------------------------------------------------------------|
| `Loc-A-Wild` | Data and processing scripts for power experiments conducted at LocA |
| `Loc-B-Wild` | Data and processing scripts for power experiments conducted at LocB |
| `dtr_[locA/locB].py` | Python script to run decision tree regression on processed data |

### Requirements

Here are the software/package requirements. The version number in the bracket indicates the minimum version that our script has been tested on.

- Python 3 (>= 3.7.7)
- Pandas (>= 1.1.3)
- Matplotlib (>= 3.3.1)
- scikit-learn (>= 0.24.0)

### Running code

After cloning the repository, navigate to `Power-Walking-MI` folder and run the following command.

```
python3 dtr_locB.py -d data -k MI-VZ-HB -f 1
```

For the DTR (decision tree regression) step, we use `dtr.py` for all the processed data including MI-side (raw data located under this folder) and MN-side (raw data and processing scripts in [Power-Walking-MN](https://github.com/5G-Measurement/sigcomm21-artifact/tree/main/Power-Walking-MN)) ones. The "f" parameter in `dtr.py` indicates the feature set (1: TH + SS; 2: TH; 3: SS).
