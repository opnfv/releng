#!/usr/bin/python
#
# This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
import requests
import yaml

import utils.reporting_utils as rp_utils

yardstick_conf = rp_utils.get_config('yardstick.test_conf')
response = requests.get(yardstick_conf)
yaml_file = yaml.safe_load(response.text)
reporting = yaml_file.get('reporting')

config = {}

for element in reporting:
    name = element['name']
    scenarios = element['scenario']
    for s in scenarios:
        if name not in config:
            config[name] = {}
        config[name][s] = True
