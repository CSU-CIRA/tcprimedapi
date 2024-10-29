"""Provides an example for in-memory (aka, not saved locally)."""
# Imports the tcprimedapi API for use
import tcprimedapi
# Import a NetCDF reader
from netCDF4 import Dataset

# Creates an instance of the Client
tcpc = tcprimedapi.Client()
# Outlines a TC PRIMED data request
# ---------------------------------
# List of valid ATCF identifiers with the pattern
# * Basin (i.e., AL, EP, CP, WP, IO, SH); Note: case insensitive
# * Annual cyclone number from 01 to 49
# * Season
atcf_id = ["AL092019"]
# List of desired file type (here, sensor)
file_type = ["GMI"]
# Request dictionary
data_request = {"atcf_id": atcf_id,
                "file_type": file_type}
# Make a data request query
tcpc.query(data_request)
# Loop through the interable
for object_key, memory in tcpc.inmemory():
    print('TC PRIMED S3 object key', object_key)
    with Dataset(object_key, memory=memory) as nc:
        # Shows some of what is in the file.
        print('\tFile data groups:', nc.data_groups)
        print('\tFirst group variables:',
              nc[nc.data_groups.split()[0]].variables.keys())
        # You could use the above save a specific data group locally
        # if desired or store a subset of file data into an array
