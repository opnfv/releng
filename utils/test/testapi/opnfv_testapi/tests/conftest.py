import argparse
from os import path

import pytest


@pytest.fixture(scope='function')
def mocker_config_file(mocker):
    config_file = path.join(path.dirname(__file__), '../../etc/config.ini')
    mocker.patch('argparse.ArgumentParser.parse_known_args',
                 return_value=(
                     argparse.Namespace(config_file=config_file), None))
