## Structure of the Pickle Files
The preprocessing script will take as input the HAR file and packet trace and extract the following attributes:

* Total page size in bytes
* Average throughput information?
* Average object size in bytes
* Number of objects in web page (e.g. `.js`, `.css`, etc.)
* Page load time 
* Each object's URL information
* Object response's protocol information 
* Number of images and videos

For each webpage loading, we will save these attributes. Data for all the websites is stored in Python-based `dict` data structure as shown below.  into the dict format and save it into the `fileStatistics.pickle`. The dict format is like:

```dict
{
  ('websiteName1' , '4G') : [
    {pageSize:xxx, objectNum:xxx...},
    {pageSize:xxx, objectNum:xxx...},
    {pageSize:xxx, objectNum:xxx...}], 
  ('websiteName2' , '5G') : [
    {pageSize:xxx, objectNum:xxx...},
    {pageSize:xxx, objectNum:xxx...},
    {pageSize:xxx, objectNum:xxx...}]
}
```

We pickled the processed dicts of all the websites into `fileStatistics.pickle`.

We pickle the same data in another file `WebSet.pickle`. The only difference here is it is `set`-based data structure to store the unique names of all the websites visited in our dataset.

Both these two pickles form as the output of the preprocessing step. They will be used to generate scripts and other results.
