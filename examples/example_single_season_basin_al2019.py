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
# * Basin (i.e., AL, EP, CP, WP, IO, SH); Note: case insensitive
# * Season
basin = ["AL"]
season = ["2019"]
# List of desired file type (here, sensor)
file_type = ["GMI"]
# Request dictionary
data_request = {"basin": basin,
                "season": season,
                "file_type": file_type}
# Make a data request query
tcpc.query(data_request)
# Loop through keys
for key in tcpc.object_keys:
    print(key)
