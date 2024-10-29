"""Provides an example for in-memory (aka, not saved locally)."""
# Standard library
import datetime
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
# Set an end date
end_date = datetime.datetime(year=2019, month=9, day=16)
# Request dictionary
data_request = {"atcf_id": atcf_id,
                "file_type": file_type,
                "end_date": end_date}
# Make a data request query
tcpc.query(data_request)
# Loop through keys
for key in tcpc.object_keys:
    print(key)
