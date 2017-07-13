def test_config_normal(conf_normal):
    from opnfv_testapi.common.config import CONF
    assert CONF.mongo_url == 'mongodb://127.0.0.1:27017/'
    assert CONF.mongo_dbname == 'test_results_collection'
    assert CONF.api_port == 8000
    assert CONF.api_debug is True
    assert CONF.api_authenticate is False
    assert CONF.swagger_base_url == 'http://localhost:8000'
