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
python3 dtr_tm.py -d Loc-A-Wild/data-processed/cleaned-logs/ -k t-mobile_nsa -f 1
python3 dtr_tm.py -d Loc-A-Wild/data-processed/cleaned-logs/ -k t-mobile_sa -f 1
python3 dtr_vz.py -d Loc-B-Wild/data-processed/ -k mi-vz-hb -f 1
python3 dtr_vz.py -d Loc-B-Wild/data-processed/ -k mn-vz-hb -f 1
python3 dtr_vz.py -d Loc-B-Wild/data-processed/ -k mn-vz-lb -f 1
```
For the DTR (decision tree regression) step, we use `dtr_vz.py` for all the VZ data and use `dtr_tm.py` for all the TM data. The "f" parameter in `dtr.py` indicates the feature set (1: TH + SS; 2: TH; 3: SS), the example commands above are using TH feature for modeling.
