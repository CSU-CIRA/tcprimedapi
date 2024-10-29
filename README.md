# TC PRIMED API

The NOAA/CSU [Tropical Cyclone PRecipitation, Infrared, Microwave, and Environmental Dataset (TC PRIMED)](https://rammb-data.cira.colostate.edu/tcprimed/) is a global amelioration of tropical cyclone centric data centered on low-Earth orbiting satellite overpasses.

The TC PRIMED data is stored in an artificial intelligence (AI)-ready format via NetCDF files. These data are hosted on an Amazon Web Services (AWS) S3 Bucket as a public dataset through the NOAA Open Data Dissemination program at https://noaa-nesdis-tcprimed-pds.s3.amazonaws.com/index.html.

This API allows users to access specific storms and sensors without having to shift through each individual storm. If you are interested in pulling the entire dataset, consider using the AWS command line interface instead.

## Install
Install the TC PRIMED API with:
```bash
$ pip install tcprimedapi
```

## Example
There are more examples on using the API available in the examples directory.

This example test will print the S3 bucket object key (i.e., the file name).
```bash
$ python
>>> import tcprimedapi
>>> tcpc = tcprimedapi.Client()
>>> tcpc.query({'atcf_id': ['al092019'],
...            'file_type': ['GMI']})
>>> for key in tcpc.object_keys:
...     print(key)
```

## Interfaces
The TC PRIMED API allows users to make data requests with two different behaviors: 1) download files locally and 2) iterate through files in memory.

### Query data request
Users must first query a data request.

To request TC PRIMED data, users create a dictionary containing parameters for their request. The dictionary contains three key, value pairs:

**Storm options:**

You can either specify storm identifiers
- `atcf_id` &mdash; the Automated Tropical Cyclone Forecast System (ATCF) 8 character storm identifier

Or, you can specify one or multiple components of a storm identifier as strings
- `season` &mdash; Four digit season
- `basin` &mdash; Two character basin identifier
- `cyclone_number` &mdash; Two digit cyclone number

Leaving one out pulls everything for that option. For example, not specifying a cyclone number gives all storms for the subset of seasons and basins.

**The overpass and environmental files options:**
- `file_type` &mdash; the low-Earth orbit satellite sensor or platform abbreviation or the environmental file `env`

**Version options:**
- `version` &mdash; optional TC PRIMED version (i.e., `v01r01`)
- `version_type` &mdash; optional TC PRIMED version type (i.e., `final`, `preliminary`) with `final` being the default

**Date time group start and end range options:**
- `start_date` &mdash; optional inclusive start date (file date time stamp must be greater than or equal to this value)
- `end_date` &mdash; optional exclusive end date (file date time stamp must be less than to this value)

As with the example above, `object_keys` can be examined to see if the query matches expectations.

### Download
This option is best for repeatedly accessing a small subset of TC PRIMED files.
```bash
$ python
>>> import tcprimedapi
>>> tcpc = tcprimedapi.Client()
>>> tcpc.query({'atcf_id': ['al092019'],
...            'file_type': ['GMI']})
>>> target_dirname = 'save_here'
>>> tcpc.download(target_dirname=target_dirname)
```

### In Memory
This option is best for one-time access or for saving a subset of data from TC PRIMED files.
```bash
$ python
>>> import tcprimedapi
>>> tcpc = tcprimedapi.Client()
>>> tcpc.query({'atcf_id': ['al092019'],
...            'file_type': ['GMI']})
>>> file_iter = tcpc.inmemory()
```
