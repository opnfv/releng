from os import path
import random, string
import pytest


@pytest.fixture
def config_normal():
    return path.join(path.dirname(__file__), '../../../etc/config.ini')

@pytest.fixture
def config_does_not_exist():
    return path.join(path.dirname(__file__), '../../../etc/',''.join(random.choice(string.lowercase) for i in range(10)),'.ini')
