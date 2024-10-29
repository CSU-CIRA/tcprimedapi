"""Basic tests for tcprimedapi."""
import datetime
import pytest
import tcprimedapi


def test_object_keys_uninit():
    """Test that object keys raises error when uninitalized."""
    with pytest.raises(RuntimeError):
        tcprimedapi.Client().object_keys


def test_object_keys_bad_set():
    """Test that object keys setter raises error with bad value."""
    with pytest.raises(ValueError):
        tcprimedapi.Client().object_keys = ['bob']


def test_object_keys_bad_type():
    """Test that object keys setter raises error with bad value."""
    with pytest.raises(TypeError):
        tcprimedapi.Client().object_keys = 'bob'


def test_object_keys_valid_set():
    """Test that object keys setter works for valid value."""
    values = [
        'v01r01/final/2019/AL/20/TCPRIMED_v01r01-final_AL202019_GMI_GPM_032651_20191127125541.nc'
    ]
    tcpc = tcprimedapi.Client()
    tcpc.object_keys = values
    assert tcpc.object_keys == values


def test_data_request_bad_key():
    """Test that data request key-value pairs raises error with bad keys."""
    bad_keys = ['filetype', 'startdate', 'cyclone_numner']
    for bad_key in bad_keys:
        with pytest.raises(ValueError):
            tcprimedapi.Client()._check_data_request({bad_key: ['value']})


def test_data_request_bad_value_typeerror():
    """Test that data request key-value pairs raises error with bad values."""
    # Type errors
    bad_values = {
        'atcf_id': 'al062018',
        'season': [2018],
        'start_date': '20180808',
        'end_date': '20180808'
    }
    for key, value in bad_values.items():
        with pytest.raises(TypeError):
            tcprimedapi.Client()._check_data_request({key: value})


def test_data_request_bad_value_valueerror():
    """Test that data request key-value pairs raises error with bad values."""
    # Value errors
    bad_values = {
        'atcf_id': ['al892018'],
        'season': ['1890'],
        'basin': ['WO'],
        'cyclone_number': ['50'],
    }
    for key, value in bad_values.items():
        with pytest.raises(ValueError):
            tcprimedapi.Client()._check_data_request({key: value})


def test_data_request_good_pair():
    """Test that data request key-value pairs raises error with bad values."""
    good_pairs = {
        'start_date': datetime.datetime.now(),
        'end_date': datetime.datetime.now(),
        'atcf_id': ['al062018'],
        'season': ['2018'],
        'basin': ['WP'],
        'cyclone_number': ['01'],
    }
    for key, value in good_pairs.items():
        assert tcprimedapi.Client()._check_data_request({key: value}) is None


def test_check_version_bad_value():
    """Test that check version raises error with bad value."""
    with pytest.raises(ValueError):
        tcprimedapi.Client()._check_version(['v09r00'], ['final'])


def test_check_version_old_value():
    """Test that check version raises error with bad value."""
    with pytest.raises(ValueError):
        tcprimedapi.Client()._check_version(['v01r00'], ['final'])


def test_check_version_type_bad_value():
    """Test that check version raises error with bad value."""
    with pytest.raises(ValueError):
        tcprimedapi.Client()._check_version(['v01r01'], ['latest'])


def test_check_version_valid():
    """Test that check version valid."""
    assert tcprimedapi.Client()._check_version(['v01r01'], ['final']) is None
    assert tcprimedapi.Client()._check_version(['v01r01'],
                                               ['preliminary']) is None


def test_check_file_type_bad():
    """Test that check file_type raises error with bad value."""
    with pytest.raises(ValueError):
        tcprimedapi.Client()._check_file_type(['bob'])


def test_check_file_type_valid_sensor():
    """Test that check file_type works with good values."""
    assert tcprimedapi.Client()._check_file_type(['GMI']) is None


def test_check_file_type_valid_platform():
    """Test that check file_type works with good values."""
    assert tcprimedapi.Client()._check_file_type(['GPM']) is None


def test_check_file_type_valid_env():
    """Test that check file_type works with good values."""
    assert tcprimedapi.Client()._check_file_type(['env']) is None


def test_check_date_none():
    """Test that check date is true if date is None."""
    assert tcprimedapi.Client()._check_date('', None)


def test_query_atcf_id_season_bad():
    """Test that query raises error when atcf_id and season set."""
    with pytest.raises(ValueError):
        tcprimedapi.Client().query({
            'atcf_id': ['al092019'],
            'season': ['2019']
        })


def test_query_atcf_id_basin_bad():
    """Test that query raises error when atcf_id and basin set."""
    with pytest.raises(ValueError):
        tcprimedapi.Client().query({'atcf_id': ['al092019'], 'basin': ['al']})


def test_query_atcf_id_cynum_bad():
    """Test that query raises error when atcf_id and cyclone number set."""
    with pytest.raises(ValueError):
        tcprimedapi.Client().query({
            'atcf_id': ['al092019'],
            'cyclone_number': ['09']
        })


def test_find_match_atcf_id_bad():
    """Test that no matches with bad atcf_id."""
    assert not len(tcprimedapi.Client()._find_matches({'atcf_id': 'al992019'}))
