"""Basic test queries for tcprimedapi."""
import datetime
import tcprimedapi


def test_atcf_id_one():
    """Test with single ATCF ID."""
    data_request = {'atcf_id': ['AL062018']}
    tcpc = tcprimedapi.Client()
    tcpc.query(data_request)
    total_matching_files = len(tcpc.object_keys)
    expected_total = 342
    assert total_matching_files == expected_total


def test_atcf_id_multiple():
    """Test with multiple ATCF IDs."""
    data_request = {'atcf_id': ['AL062018', 'AL092018']}
    tcpc = tcprimedapi.Client()
    tcpc.query(data_request)
    total_matching_files = len(tcpc.object_keys)
    expected_total = 469
    assert total_matching_files == expected_total


def test_season_one():
    """Test with one season."""
    data_request = {'season': ['2018']}
    tcpc = tcprimedapi.Client()
    tcpc.query(data_request)
    total_matching_files = len(tcpc.object_keys)
    expected_total = 14690
    assert total_matching_files == expected_total


def test_season_multiple():
    """Test with multiple seasons."""
    data_request = {'season': ['2018', '2019']}
    tcpc = tcprimedapi.Client()
    tcpc.query(data_request)
    total_matching_files = len(tcpc.object_keys)
    expected_total = 28634
    assert total_matching_files == expected_total


def test_season_nodata():
    """Test with no data season."""
    data_request = {'season': ['1970']}
    tcpc = tcprimedapi.Client()
    tcpc.query(data_request)
    total_matching_files = len(tcpc.object_keys)
    expected_total = 0
    assert total_matching_files == expected_total


def test_season_mixed():
    """Test with mixed good/bad seasons."""
    data_request = {'season': ['1970', '2018']}
    tcpc = tcprimedapi.Client()
    tcpc.query(data_request)
    total_matching_files = len(tcpc.object_keys)
    expected_total = 14690
    assert total_matching_files == expected_total


# Slower tests
# ------------
#
#def test_basin():
#    """Test with basin."""
#    data_request = {'basin': ['CP']}
#    tcpc = tcprimedapi.Client()
#    tcpc.query(data_request)
#    total_matching_files = len(tcpc.object_keys)
#    expected_total = 4634
#    assert total_matching_files == expected_total
#
#
#def test_cyclone_number():
#    """Test with an annual cyclone number."""
#    data_request = {'cyclone_number': ['01']}
#    tcpc = tcprimedapi.Client()
#    tcpc.query(data_request)
#    total_matching_files = len(tcpc.object_keys)
#    expected_total = 12237
#    assert total_matching_files == expected_total
#
#
#def test_cyclone_numbers():
#    """Test with annual cyclone numbers."""
#    data_request = {'cyclone_number': ['01', '02']}
#    tcpc = tcprimedapi.Client()
#    tcpc.query(data_request)
#    total_matching_files = len(tcpc.object_keys)
#    expected_total = 24370
#    assert total_matching_files == expected_total


def test_season_basin():
    """Test with a season and basin."""
    data_request = {'season': ['2018'], 'basin': ['AL']}
    tcpc = tcprimedapi.Client()
    tcpc.query(data_request)
    total_matching_files = len(tcpc.object_keys)
    expected_total = 2916
    assert total_matching_files == expected_total


def test_season_multi_basin():
    """Test with a season and two basins."""
    data_request = {'season': ['2018'], 'basin': ['AL', 'EP']}
    tcpc = tcprimedapi.Client()
    tcpc.query(data_request)
    total_matching_files = len(tcpc.object_keys)
    expected_total = 6125
    assert total_matching_files == expected_total


def test_multi_season_basin():
    """Test with two season and a basin."""
    data_request = {'season': ['2018', '2019'], 'basin': ['AL']}
    tcpc = tcprimedapi.Client()
    tcpc.query(data_request)
    total_matching_files = len(tcpc.object_keys)
    expected_total = 5206
    assert total_matching_files == expected_total


def test_season_multi_cyclone_number():
    """Test with a season and two annual cyclone numbers."""
    data_request = {'season': ['2018'], 'cyclone_number': ['01', '02']}
    tcpc = tcprimedapi.Client()
    tcpc.query(data_request)
    total_matching_files = len(tcpc.object_keys)
    expected_total = 1413
    assert total_matching_files == expected_total


def test_season_basin_cyclone_number():
    """Test with a season, basin, and an annual cyclone number."""
    data_request = {
        'season': ['2018'],
        'basin': ['AL'],
        'cyclone_number': ['06']
    }
    tcpc = tcprimedapi.Client()
    tcpc.query(data_request)
    total_matching_files = len(tcpc.object_keys)
    expected_total = 342
    assert total_matching_files == expected_total


def test_atcf_id_file_type():
    """Test with an ATCF id and file type."""
    data_request = {'atcf_id': ['al062018'], 'file_type': ['env', 'GMI']}
    tcpc = tcprimedapi.Client()
    tcpc.query(data_request)
    total_matching_files = len(tcpc.object_keys)
    expected_total = 18
    assert total_matching_files == expected_total


def test_atcf_id_start_date():
    """Test with an ATCF id and start date."""
    data_request = {
        'atcf_id': ['al062018'],
        'start_date': datetime.datetime(year=2018, month=9, day=8)
    }
    tcpc = tcprimedapi.Client()
    tcpc.query(data_request)
    total_matching_files = len(tcpc.object_keys)
    expected_total = 193
    assert total_matching_files == expected_total


def test_atcf_id_start_date_bad():
    """Test with an ATCF id and bad start date."""
    data_request = {
        'atcf_id': ['al062018'],
        'start_date': datetime.datetime(year=2019, month=9, day=8)
    }
    tcpc = tcprimedapi.Client()
    tcpc.query(data_request)
    total_matching_files = len(tcpc.object_keys)
    expected_total = 0
    assert total_matching_files == expected_total


def test_atcf_id_end_date():
    """Test with an ATCF id and end date."""
    data_request = {
        'atcf_id': ['al062018'],
        'end_date': datetime.datetime(year=2018, month=9, day=8)
    }
    tcpc = tcprimedapi.Client()
    tcpc.query(data_request)
    total_matching_files = len(tcpc.object_keys)
    expected_total = 149
    assert total_matching_files == expected_total


def test_atcf_id_end_date_bad():
    """Test with an ATCF id and bad end date."""
    data_request = {
        'atcf_id': ['al062018'],
        'end_date': datetime.datetime(year=2017, month=9, day=8)
    }
    tcpc = tcprimedapi.Client()
    tcpc.query(data_request)
    total_matching_files = len(tcpc.object_keys)
    expected_total = 0
    assert total_matching_files == expected_total


def test_atcf_id_start_end_date():
    """Test with an ATCF id plus start and end date."""
    data_request = {
        'atcf_id': ['al062018'],
        'start_date': datetime.datetime(year=2018, month=8, day=31),
        'end_date': datetime.datetime(year=2018, month=9, day=2)
    }
    tcpc = tcprimedapi.Client()
    tcpc.query(data_request)
    total_matching_files = len(tcpc.object_keys)
    expected_total = 29
    assert total_matching_files == expected_total
