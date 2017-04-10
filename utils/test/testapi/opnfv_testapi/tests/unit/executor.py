##############################################################################
# Copyright (c) 2017 ZTE Corp
# feng.xiaowei@zte.com.cn
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import functools
import httplib


def create(excepted_status, excepted_response, *args):
    def _create(create_request):
        @functools.wraps(create_request)
        def wrap(self):
            request = create_request(self)
            status, body = self.create(request, *args)
            if excepted_status == httplib.OK:
                getattr(self, excepted_response)(body, *args)
            else:
                self.assertIn(excepted_response, body)
        return wrap
    return _create


def get(excepted_status, excepted_response, *args):
    def _get(get_request):
        @functools.wraps(get_request)
        def wrap(self):
            request = get_request(self)
            status, body = self.get(request, *args)
            if excepted_status == httplib.OK:
                getattr(self, excepted_response)(body, *args)
            else:
                self.assertIn(excepted_response, body)
        return wrap
    return _get
