from os import path

import pytest


@pytest.fixture
def config_normal():
    return path.join(path.dirname(__file__), 'common/normal.ini')


@pytest.fixture
def config_token():
    return path.join(path.dirname(__file__), 'common/token.ini')
