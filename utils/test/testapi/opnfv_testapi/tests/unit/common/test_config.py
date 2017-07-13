import argparse
import os

import mock

from opnfv_testapi.common import config

config_file = os.path.join(os.path.dirname(__file__),
                           '../../../../etc/config.ini')

@mock.patch('argparse.ArgumentParser.parse_known_args',
            return_value=(argparse.Namespace(config_file=config_file), None))
def test_config_success(mock_args):
    conf = config.Config()
    assert conf.mongo_url == 'mongodb://127.0.0.1:27017/'
    assert conf.mongo_dbname == 'test_results_collection'
    assert conf.api_port == 8000
    assert conf.api_debug is True
    assert conf.api_authenticate is False
    assert conf.swagger_base_url == 'http://localhost:8000'
