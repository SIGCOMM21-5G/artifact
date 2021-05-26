## Processing the raw dataset

After cloning the repo and download the contents from google drive's `raw_dataset` directory to repo's `raw_dataset` directory. Then we can apply `preprocessing.py` to generate the processed data and save it to `WebSet.pickle` and `fileStatistics.pickle`.

```shell
python preprocessing.py --data_path ../raw_dataset
```

When the preprocessing is done, the  `WebSet.pickle` and `fileStatistics.pickle` will be saved in your current directory. (This step usually takes several hours.)

**To save your time, we have offered our generated whole pickle file `WebSet.pickle` and `fileStatistics.pickle` in the `processed_dataset` folder in Shared Google Folder. You can directly download and use these two files instead of re-processing from the beginning.**

We also provide incomplete toy pickle file in this Github repo for quick trial run. You can replace the toy pickle file with downloaded full version from Google drive to get correct final results.

## Processed Pickle File structure
Using the processing script, we will analyze both the HAR file and Tcpdump file. We will get the following attributes:
* pageSize
* average throughput information
* average object size 
* object number 
* page load time 
* each object's url information
* object response's protocol information 
* image/video number

We will save such attribute into the dict format and save it into the `fileStatistics.pickle`. The dict format is like:

```python
{('websiteName1','4G'):[{pageSize:xxx, objectNum:xxx...},{pageSize:xxx, objectNum:xxx...},{pageSize:xxx, objectNum:xxx...}], ('websiteName2','5G'):[{pageSize:xxx, objectNum:xxx...},{pageSize:xxx, objectNum:xxx...},{pageSize:xxx, objectNum:xxx...}] }
```

The combination of website's name and the network Type is the key in the dict. The corresponding value is a list. Each member of the list is the analyzed attributes for each round's loading.

In `WebSet.pickle` , it will be a `set` structure to contain all the websites' names we have collected.

We will utilize these two pickle file for futher analysis.

