##############################################################################
# Copyright (c) 2015 Orange
# guyrodrigue.koffi@orange.com / koffirodrigue@gmail.com
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
# feng.xiaowei@zte.com.cn  mv Pod to pod_models.py                 5-18-2016
# feng.xiaowei@zte.com.cn  add MetaCreateResponse/MetaGetResponse  5-18-2016
# feng.xiaowei@zte.com.cn  mv TestProject to project_models.py     5-19-2016
# feng.xiaowei@zte.com.cn  delete meta class                       5-19-2016
# feng.xiaowei@zte.com.cn  add CreateResponse                      5-19-2016
# feng.xiaowei@zte.com.cn  mv TestCase to testcase_models.py       5-20-2016
# feng.xiaowei@zte.com.cn  mv TestResut to result_models.py        5-23-2016
##############################################################################
from opnfv_testapi.tornado_swagger import swagger


class CreateResponse(object):
    def __init__(self, href=''):
        self.href = href

    @staticmethod
    def from_dict(res_dict):
        if res_dict is None:
            return None

        res = CreateResponse()
        res.href = res_dict.get('href')
        return res

    def format(self):
        return {'href': self.href}


@swagger.model()
class Versions(object):
    """
        @property versions:
        @ptype versions: C{list} of L{Version}
    """
    def __init__(self):
        self.versions = list()

    @staticmethod
    def from_dict(res_dict):
        if res_dict is None:
            return None

        res = Versions()
        for version in res_dict.get('versions'):
            res.versions.append(Version.from_dict(version))
        return res


@swagger.model()
class Version(object):
    def __init__(self, version=None, description=None):
        self.version = version
        self.description = description

    @staticmethod
    def from_dict(a_dict):
        if a_dict is None:
            return None

        ver = Version()
        ver.version = a_dict.get('version')
        ver.description = str(a_dict.get('description'))
        return ver
