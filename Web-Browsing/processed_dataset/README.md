## Processing the raw dataset

After cloning the repo and download the contents from google drive's `raw_dataset` directory to repo's `raw_dataset` directory. Then we can apply `preprocessing.py` to generate the processed data and save it to `WebSet.pickle` and `fileStatistics.pickle`.

```shell
python preprocessing.py --data_path ../raw_dataset
```

When the preprocessing is done, the  `WebSet.pickle` and `fileStatistics.pickle` will be saved in your current directory. (This step usually takes several hours.)

**To save your time, we have offered our generated whole pickle file `WebSet.pickle` and `fileStatistics.pickle` in the `processed_dataset` folder in Shared Google Folder. You can directly download and use these two files instead of re-processing from the beginning.**

We also provide incomplete toy pickle file in this Github repo for quick trial run. You can replace the toy pickle file with downloaded full version from Google drive to get correct final results.