from os import path

import pytest


@pytest.fixture
def config_normal():
    return path.join(path.dirname(__file__), '../../../etc/config.ini')
