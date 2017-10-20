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
    assert CONF.api_token_check is False
    assert CONF.api_authenticate is True
    assert CONF.ui_url == 'http://localhost:8000'


def test_config_file_not_exist(mocker):
    mocker.patch('os.path.exists', return_value=False)
    with pytest.raises(Exception) as m_exc:
        from opnfv_testapi.common import config
        config.Config()
    assert 'not found' in str(m_exc.value)
