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


def update(excepted_status, excepted_response, *args):
    def _update(update_request):
        @functools.wraps(update_request)
        def wrap(self):
            request, resource = update_request(self)
            status, body = self.update(request, resource, *args)
            if excepted_status == httplib.OK:
                getattr(self, excepted_response)(request, body, *args)
            else:
                self.assertIn(excepted_response, body)
        return wrap
    return _update


def delete(excepted_status, excepted_response, *args):
    def _delete(delete_request):
        @functools.wraps(delete_request)
        def wrap(self):
            request = delete_request(self)
            status, body = self.delete(request, *args)
            if excepted_status == httplib.OK:
                getattr(self, excepted_response)(body, *args)
            else:
                self.assertIn(excepted_response, body)
        return wrap
    return _delete


def query(excepted_status, excepted_response, number=0, *args):
    def _query(get_request):
        @functools.wraps(get_request)
        def wrap(self):
            request = get_request(self)
            status, body = self.query(request, *args)
            if excepted_status == httplib.OK:
                getattr(self, excepted_response)(body, number, *args)
            else:
                self.assertIn(excepted_response, body)
        return wrap
    return _query
