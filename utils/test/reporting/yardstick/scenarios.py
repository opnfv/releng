import yaml
import os
import requests

import reportingConf as conf


response = requests.get(conf.TEST_CONF)
print response.text
yaml_file = yaml.safe_load(response.text)
reporting = yaml_file.get('reporting')

config = {}

for element in reporting:
    name = element['name']
    scenarios = element['scenario']
    for s in scenarios:
        if not config.has_key(name):
            config[name] = {}
        config[name][s] = True
