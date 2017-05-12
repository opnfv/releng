import ConfigParser
import os

import pytest

from opnfv_testapi.common import config


@pytest.fixture()
def config_dir():
    return os.path.dirname(__file__)


@pytest.mark.parametrize('exception, config_file, excepted', [
    (config.ParseError, None, '/etc/opnfv_testapi/config.ini not found'),
    (ConfigParser.NoSectionError, 'nosection.ini', 'No section:'),
    (config.ParseError, 'noparam.ini', 'No parameter:'),
    (config.ParseError, 'notint.ini', 'Not int:'),
    (config.ParseError, 'notboolean.ini', 'Not boolean:')])
def pytest_config_exceptions(config_dir, exception, config_file, excepted):
    file = '{}/{}'.format(config_dir, config_file) if config_file else None
    with pytest.raises(exception) as error:
        config.Config.CONFIG = file
        config.Config()
    assert excepted in str(error.value)


def test_config_success():
    config_file = os.path.join(os.path.dirname(__file__),
                               '../../../../etc/config.ini')
    config.Config.CONFIG = config_file
    conf = config.Config()
    assert conf.mongo_url == 'mongodb://127.0.0.1:27017/'
    assert conf.mongo_dbname == 'test_results_collection'
    assert conf.api_port == 8000
    assert conf.api_debug is True
    assert conf.api_authenticate is False
    assert conf.swagger_base_url == 'http://localhost:8000'
