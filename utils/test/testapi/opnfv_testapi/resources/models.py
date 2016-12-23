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
# feng.xiaowei@zte.com.cn  add ModelBase                           12-20-2016
##############################################################################
import copy

from opnfv_testapi.tornado_swagger import swagger


class ModelBase(object):

    def _format(self, excludes):
        new_obj = copy.deepcopy(self)
        dicts = new_obj.__dict__
        for k in dicts.keys():
            if k in excludes:
                del dicts[k]
            elif dicts[k]:
                if hasattr(dicts[k], 'format'):
                    dicts[k] = dicts[k].format()
                elif isinstance(dicts[k], list):
                    hs = list()
                    [hs.append(h.format() if hasattr(h, 'format') else str(h))
                     for h in dicts[k]]
                    dicts[k] = hs
                elif not isinstance(dicts[k], (str, int, float, dict)):
                    dicts[k] = str(dicts[k])
        return dicts

    def format(self):
        return self._format(['_id'])

    def format_http(self):
        return self._format([])

    @staticmethod
    def attr_parser():
        return {}

    @classmethod
    def from_dict(cls, a_dict):
        if a_dict is None:
            return None

        attr_parser = cls.attr_parser()
        t = cls()
        for k, v in a_dict.iteritems():
            value = v
            if isinstance(v, dict) and k in attr_parser:
                value = attr_parser[k].from_dict(v)
            elif isinstance(v, list) and k in attr_parser:
                value = []
                for item in v:
                    value.append(attr_parser[k].from_dict(item))

            t.__setattr__(k, value)

        return t


class CreateResponse(ModelBase):
    def __init__(self, href=''):
        self.href = href


@swagger.model()
class Versions(ModelBase):
    """
        @property versions:
        @ptype versions: C{list} of L{Version}
    """

    def __init__(self):
        self.versions = list()

    @staticmethod
    def attr_parser():
        return {'versions': Version}


@swagger.model()
class Version(ModelBase):
    def __init__(self, version=None, description=None):
        self.version = version
        self.description = description
