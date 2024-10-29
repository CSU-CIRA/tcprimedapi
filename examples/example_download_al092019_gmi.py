"""Provides an example for downloaded files locally."""
# Imports the tcprimedapi API for use
import tcprimedapi

# Creates an instance of the Client
tcpc = tcprimedapi.Client()
# Outlines a TC PRIMED data request
# ---------------------------------
# List of valid ATCF identifiers with the pattern
# * Basin (i.e., AL, EP, CP, WP, IO, SH); Note: case insensitive
# * Annual cyclone number from 01 to 49
# * Season
atcf_id = ["AL092019"]
# List of desired file_types (here, sensor)
file_type = ["GMI"]
# Request dictionary
data_request = {"atcf_id": atcf_id,
                "file_type": file_type}
# Make a data request query
tcpc.query(data_request)
# Target directory name for output
# Note: creates season, basin, cyclone number subdirectories
target_dirname = './'
# Download files
tcpc.download(target_dirname)
