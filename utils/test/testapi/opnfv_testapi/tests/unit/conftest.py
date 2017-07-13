from os import path
import argparse

import pytest


@pytest.fixture
def conf_normal(mocker):
    conf = path.join(path.dirname(__file__), 'common/normal.ini')
    return mocker.patch(
        'argparse.ArgumentParser.parse_known_args',
        return_value=(argparse.Namespace(config_file=conf), None))
