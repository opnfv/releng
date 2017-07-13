from opnfv_testapi.common import config


def test_config_success(mocker_config_file):
    conf = config.Config()
    assert conf.mongo_url == 'mongodb://127.0.0.1:27017/'
    assert conf.mongo_dbname == 'test_results_collection'
    assert conf.api_port == 8000
    assert conf.api_debug is True
    assert conf.api_authenticate is False
    assert conf.swagger_base_url == 'http://localhost:8000'
