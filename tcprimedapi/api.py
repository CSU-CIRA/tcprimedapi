"""Provides a basic API to pull TC PRIMED data from NODD."""
# Standard library
import os
import re
import sys
import datetime
import itertools
from typing import Optional, Sequence, Generator, Union
# Third-party packages
import boto3
from botocore import UNSIGNED
from botocore.client import Config

# NODD S3 bucket URL and name
# ---------------------------
# Specify the URL to the TC PRIMED S3 bucket. We will use this
# when we want to read from the files in the bucket.
NODD_BASE_URL = "https://noaa-nesdis-tcprimed-pds.S3.amazonaws.com"
# Specify the name of the TC PRIMED S3 bucket. We will use this
# when we call the boto3 resource interface.
BUCKET_NAME = "noaa-nesdis-tcprimed-pds"

# Version information
# -------------------
# Valid versions in TC PRIMED
TCPRIMED_VERSIONS = [
    "v01r01",
]
TCPRIMED_VERSION_TYPES = ["final", "preliminary"]
TCPRIMED_OLD_VERSIONS = [
    "v01r00",
]
# File types in TC PRIMED
# -----------------------
# Valid sensors in TC PRIMED
TCPRIMED_SENSORS = [
    "AMSR2", "AMSRE", "AMSUB", "ATMS", "GMI", "MHS", "SSMI", "SSMIS", "TMI"
]
# Valid intruments in TC PRIMED
TCPRIMED_PLATFORMS = [
    "GCOMW1", "AQUA", "NOAA15", "NOAA16", "NOAA17", "NOAA18", "NOAA19",
    "NOAA20", "NOAA21", "NPP", "GPM", "METOPA", "METOPB", "METOPC", "F11",
    "F13", "F14", "F15", "F16", "F17", "F18", "F19", "TRMM"
]
# Valid environmental file
TCPRIMED_ENV = ['env']

# REGEX patterns
# --------------
# ATCF identifier regular expression pattern
BASIN_REPATTERN = "(al|AL|ep|EP|cp|CP|wp|WP|io|IO|sh|SH)"
BASIN_UPPER_REPATTERN = "(AL|EP|CP|WP|IO|SH)"
CY_REPATTERN = "[0-4][0-9]"
SEASON_REPATTERN = "(19|20)[0-9][0-9]"
ATCF_REPATTERN = f"^(?P<basin>{BASIN_REPATTERN})(?P<cyclone_number>{CY_REPATTERN})(?P<season>{SEASON_REPATTERN})$"
# Date time group regular expression pattern
DTG_REPATTERN = "(?P<dtg>(19|20)[0-9][0-9](0[1-9]|1[0-2])([0-2][0-9]|3[0-1])([0-1][0-9]|2[0-3])[0-5][0-9][0-5][0-9])"
# Object key regular expression pattern
KEY_REPATTERN = f"^v01r01/(final|preliminary)/{SEASON_REPATTERN}/{BASIN_UPPER_REPATTERN}/{CY_REPATTERN}/TCPRIMED_v01r01-(final|preliminary)_{BASIN_UPPER_REPATTERN}{CY_REPATTERN}{SEASON_REPATTERN}(.*).nc$"
# TC PRIMED file name pattern
FILE_REPATTERN = "^TCPRIMED_{version}-{version_type}_{basin}{cyclone_number}{season}(.*)_{file_type}_(.*)nc$"
# Default regex patterns if not specified by the user
DEFAULT_FILE_PATTERN = {
    "version": "v01r01-(final|preliminary)",
    "basin": BASIN_UPPER_REPATTERN,
    "cyclone_number": CY_REPATTERN,
    "season": SEASON_REPATTERN,
    "file_type": "(.*)"
}
# Dictionary keys
# ---------------
# Keys used for in the TC PRIMED file name
FILEPATH_KEYS = [
    'version', 'version_type', 'season', 'basin', 'cyclone_number', 'file_type'
]
# Valid data request keys
VALID_KEYS = FILEPATH_KEYS + ['start_date', 'end_date', 'atcf_id']


class InMemoryFiles:
    """Handle list of object keys."""
    def __init__(self, client, object_keys: Sequence[str]) -> None:
        """
        Handle remote files.

        Parameters
        ----------
        client : boto3.client
            The client instance
        object_keys : list
            A list of valid object keys
        """
        self.client = client
        self.object_keys = object_keys

    def __iter__(self) -> Generator:
        """
        Interate through keys and return memory.

        Yields
        ------
        key : str
            The object key
        memory : bytes
            The block of memory for the file.
        """
        for key in self.object_keys:
            obj = self.client.get_object(Bucket=BUCKET_NAME, Key=key)
            memory = obj['Body'].read()
            yield key, memory


class Client:
    """API for handling TC PRIMED file requests."""
    def __init__(self, verbose: bool = True) -> None:
        """
        Initialize the Client.

        Parameters
        ----------
        verbose : Boolean
            If True, output progress
        """
        self.verbose = verbose
        self.client = boto3.client('s3',
                                   config=Config(signature_version=UNSIGNED))
        # Specify the S3 resource object. signature_version=UNSIGNED
        # allows users to access the public TC PRIMED bucket
        resource = boto3.resource('s3',
                                  config=Config(signature_version=UNSIGNED))
        # Specify the bucket resource
        self.bucket = resource.Bucket(BUCKET_NAME)

        # s3 bucket object keys
        self._object_keys: Union[list[str], None] = None

    @property
    def object_keys(self) -> list[str]:
        """
        Get object key values.

        Returns
        -------
        object_keys : list
            List of S3 bucket object keys

        Raises
        ------
        RuntimeError
            If object keys is not already set.
        """
        if self._object_keys is None:
            raise RuntimeError('Must generate a query or set object_keys')
        return self._object_keys

    @object_keys.setter
    def object_keys(self, values: list[str]):
        """
        Set object key values.

        Parameters
        ----------
        values : Squence
            List of S3 bucket object keys

        Raises
        ------
        ValueError
            If an object key pattern invalid.
        """
        if not isinstance(values, (list, tuple)):
            raise TypeError('Must set object with something list like')
        for val in values:
            if re.match(KEY_REPATTERN, val) is None:
                raise ValueError(f'Invalid object key: {val}')
        self._object_keys = values

    @staticmethod
    def _check_data_request(data_request: dict) -> None:
        """
        Check the validity of data request key value pairs.

        Parameters
        ----------
        data_request : dist
            Request dictionary

        Raises
        ------
        ValueError
            If invalid key or value requested
        """
        for key, values in data_request.items():
            if key not in VALID_KEYS:
                raise ValueError(f'Invalid key in request: {key}')
            if key in ['start_date', 'end_date']:
                if not isinstance(values, (datetime.date, datetime.datetime)):
                    raise TypeError(
                        f'Values for key must be of type datetime: {key}')
                continue
            if not isinstance(values, (list, tuple)):
                raise TypeError(f'Values for key must be list or tuple: {key}')
            for value in values:
                if not isinstance(value, str):
                    raise TypeError(
                        f'Values for key must be of type str: {key}')
                if key in ['atcf_id', 'basin', 'cyclone_number', 'season']:
                    if key in DEFAULT_FILE_PATTERN:
                        tmp_pattern = DEFAULT_FILE_PATTERN[key]
                    else:
                        tmp_pattern = ATCF_REPATTERN
                    match = re.match(tmp_pattern, value)
                    if not match:
                        raise ValueError(f'Invalid value {value} for {key}.')

    @staticmethod
    def _check_version(version_list: Sequence[str],
                       version_type_list: Sequence[str]) -> None:
        """
        Check the validity of version request.

        Parameters
        ----------
        version_list : list
            List of versions requested
        version_type_list : list
            List of version types requested

        Raises
        ------
        ValueError
            If invalid versions requested
        """
        for version in version_list:
            if version not in TCPRIMED_VERSIONS:
                valid_ver = " ,".join(TCPRIMED_VERSIONS)
                if version in TCPRIMED_OLD_VERSIONS:
                    raise ValueError(
                        f'{version} deprecated. Version must be one of {valid_ver}.'
                    )
                raise ValueError(
                    f'{version} invalid. Version must be one of {valid_ver}.')
        for version in version_type_list:
            if version not in TCPRIMED_VERSION_TYPES:
                valid_ver = " ,".join(TCPRIMED_VERSION_TYPES)
                raise ValueError(
                    f'{version} invalid. Version must be one of {valid_ver}.')

    @staticmethod
    def _check_file_type(file_type_list: Sequence[str]) -> None:
        """
        Check the validity of file types request.

        Parameters
        ----------
        file_type_list : list
            List of file type requested

        Raises
        ------
        ValueError
            If invalid file type requested
        """
        for file_type in file_type_list:
            if file_type not in TCPRIMED_SENSORS + TCPRIMED_PLATFORMS + TCPRIMED_ENV:
                raise ValueError(f'Invalid file type {file_type}.')

    @staticmethod
    def _check_date(string: str,
                    date: datetime.datetime,
                    end: Optional[bool] = True,
                    file_type: Optional[str] = None) -> bool:
        """
        Check if date time range.

        Parameters
        ----------
        string : str
            The string containing a dtg
        date : datetime.datetime
            The desired date
        end : Boolean, optional
            Is this an end date?
        file_type : str, optional
            The file type string

        Returns
        -------
        Boolean
            If date range right or no date, True
        """
        # If None, don't check date and return True
        if date is None:
            return True
        # Set a prefix if env file
        prefix = ''
        if file_type == 'env':
            if end:
                prefix = 'e'
            else:
                prefix = 's'
        # See if there is a match
        match = re.search(prefix + DTG_REPATTERN, string)
        if match is not None:
            match_dict = match.groupdict()
            match_date = datetime.datetime.strptime(match_dict['dtg'],
                                                    "%Y%m%d%H%M%S")
            # Check date
            if end and match_date < date:
                # If end_date and exclusive
                return True
            if not end and match_date >= date:
                # If start_date and inclusive
                return True
        return False

    def _find_matches(self, data_request: dict) -> list[str]:
        """
        Build a user data request.

        Parameters
        ----------
        data_request : dict
            Contains TC PRIMED request query.

        Returns
        -------
        object_keys : list
            List of S3 bucket objects.
        """
        # Get bounding date time groups if exist
        end_date = data_request.pop('end_date', None)
        start_date = data_request.pop('start_date', None)
        # Collapse all the combinations to single dictionary
        keys, values = zip(*data_request.items())
        combination_dicts = [
            dict(zip(keys, v)) for v in itertools.product(*values)
        ]
        # Process each combo
        object_keys = []    # S3 bucket object keys
        prefixes = {}    # bucket prefixes
        for combo in combination_dicts:
            # check validity of atcf_id
            if 'atcf_id' in combo:
                match = re.match(ATCF_REPATTERN, combo['atcf_id'])
                if not match:
                    continue
                combo.update(match.groupdict())
                # Make basin upper
                combo['basin'] = combo['basin'].upper()
            # Generate a "path"-like prefix for data on NODD
            prefix_list = []
            for key in FILEPATH_KEYS:
                if key not in combo or key == 'file_type':
                    break
                prefix_list.append(combo[key])
            prefix = "/".join(prefix_list)
            # Store prefix result to reduce time on large searches
            if prefix not in prefixes:
                prefixes[prefix] = self.bucket.objects.filter(Prefix=prefix)
            # Build the file pattern for match
            file_pattern = DEFAULT_FILE_PATTERN.copy()
            for key in FILEPATH_KEYS:
                if key in combo:
                    file_pattern[key] = combo[key]
            pattern = FILE_REPATTERN.format(**file_pattern)
            # Loop through each object key to check for matches
            for obj in prefixes[prefix]:
                basename = os.path.basename(obj.key)
                if re.match(pattern, basename) is None:
                    continue
                # Check end date
                if not self._check_date(basename,
                                        end_date,
                                        end=True,
                                        file_type=combo.get('file_type', None)):
                    continue
                # Check start date
                if not self._check_date(basename,
                                        start_date,
                                        end=False,
                                        file_type=combo.get('file_type', None)):
                    continue
                # Append valid object key
                object_keys.append(obj.key)
        return object_keys

    def query(self, data_request: Optional[dict] = None) -> None:
        """
        Process a user data request.

        Parameters
        ----------
        data_request : dict, optional
            Contains TC PRIMED request query.
        """
        if data_request is None:
            data_request = {}
        if self.verbose:
            print('Querying the following request:\n', data_request)
        # Check data_request keys and values
        self._check_data_request(data_request)
        # Check file type
        if 'file_type' in data_request:
            self._check_file_type(data_request['file_type'])
        # Check version
        if 'version' not in data_request:
            data_request['version'] = [TCPRIMED_VERSIONS[0]]
        if 'version_type' not in data_request:
            data_request['version_type'] = [TCPRIMED_VERSION_TYPES[0]]
        self._check_version(data_request['version'],
                            data_request['version_type'])
        if "atcf_id" in data_request:
            if any(key in data_request
                   for key in ['season', 'basin', 'cyclone_number']):
                raise ValueError(
                    'Cannot define atcf_id and season, basin, or cyclone_number'
                )
        self.object_keys = self._find_matches(data_request)
        if self.verbose:
            print('Total files matching request: %d' % len(self.object_keys))
            sys.stdout.flush()

    def inmemory(self) -> InMemoryFiles:
        """
        Return an interable to use in memory.

        Returns
        -------
        file_iter : InMemoryFiles
            An interable for processing in memory
        """
        return InMemoryFiles(self.client, self.object_keys)

    def _get_url(self,
                 object_key: str,
                 target_dirname: Optional[str] = None) -> None:
        """
        Retrive the data.

        Parameters
        ----------
        object_key : tuple
            The S3 bucket object key
        target_dirname : str
            The base target directory to write files.

        Raises
        ------
        ClientError
            If issue retrieving object
        """
        # Get the header for the object key
        meta_data = self.client.head_object(Bucket=BUCKET_NAME, Key=object_key)
        callback = None
        if self.verbose:
            # Total content length (file size)
            content_length = int(meta_data.get('ContentLength', 0))
            # Amount downloaded
            downloaded = 0
            bar_size = 50

            def progress(chunk):
                """Generate a progress bar."""
                nonlocal downloaded
                downloaded += chunk
                done = int(bar_size * downloaded / content_length)
                sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' *
                                               (bar_size - done)))
                sys.stdout.flush()

            print(f'Downloading {object_key}')
            sys.stdout.flush()
            callback = progress
        if target_dirname is None:
            target_dirname = ''
        output_path = os.path.join(target_dirname, object_key)
        save_storm_dirname = os.path.dirname(output_path)
        if not os.path.exists(save_storm_dirname):
            os.makedirs(save_storm_dirname)
        # Writing file to disk
        with open(output_path, 'wb') as fid:
            self.client.download_fileobj(BUCKET_NAME,
                                         object_key,
                                         fid,
                                         Callback=callback)
        if self.verbose:
            sys.stdout.write("\n")
            sys.stdout.flush()

    def download(self, target_dirname: Optional[str] = None) -> None:
        """
        Download a user data request.

        Parameters
        ----------
        target_dirname : str, optional
            The base target directory to write files.
        """
        for request in self.object_keys:
            self._get_url(request, target_dirname)
