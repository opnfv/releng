import argparse
import pytest


def test_config_normal(mocker, config_normal):
    mocker.patch(
        'argparse.ArgumentParser.parse_known_args',
        return_value=(argparse.Namespace(config_file=config_normal), None))
    from opnfv_testapi.common import config
    CONF = config.Config()
    assert CONF.mongo_url == 'mongodb://127.0.0.1:27017/'
    assert CONF.mongo_dbname == 'test_results_collection'
    assert CONF.api_port == 8000
    assert CONF.api_debug is True
    assert CONF.api_authenticate is False
    assert CONF.ui_url == 'http://localhost:8000'

def test_config_file_does_not_exist(mocker, config_does_not_exist):
    mocker.patch(
        'argparse.ArgumentParser.parse_known_args',
        return_value=(argparse.Namespace(config_file=config_does_not_exist), None))
    from opnfv_testapi.common import config
    with pytest.raises(Exception) as ex:
        CONF = config.Config()
        assert "config file not found" in str(ex.value)
