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
