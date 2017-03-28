##############################################################################
# Copyright (c) 2017 Huawei Technologies Co.,Ltd and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apaiche.org/licenses/LICENSE-2.0
##############################################################################
import requests

from tornado.escape import json_encode

from api.handlers import BaseHandler
from api import conf


class Projects(BaseHandler):
    def get(self):
        self._set_header()

        url = '{}/projects'.format(conf.base_url)
        projects = requests.get(url).json().get('projects', {})

        project_url = 'https://wiki.opnfv.org/display/{}'
        data = {p['name']: project_url.format(p['name']) for p in projects}

        return self.write(json_encode(data))
