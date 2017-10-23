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

from concurrent.futures import ThreadPoolExecutor
import mock


O_get_secure_cookie = (
    'opnfv_testapi.handlers.base_handlers.GenericApiHandler.get_secure_cookie')


def thread_execute(method, *args, **kwargs):
        with ThreadPoolExecutor(max_workers=2) as executor:
            result = executor.submit(method, *args, **kwargs)
        return result


def mock_invalid_lfid():
    def _mock_invalid_lfid(xstep):
        def wrap(self, *args, **kwargs):
            with mock.patch(O_get_secure_cookie) as m_cookie:
                m_cookie.return_value = 'InvalidUser'
                return xstep(self, *args, **kwargs)
        return wrap
    return _mock_invalid_lfid


def mock_valid_lfid():
    def _mock_valid_lfid(xstep):
        def wrap(self, *args, **kwargs):
            with mock.patch(O_get_secure_cookie) as m_cookie:
                m_cookie.return_value = 'ValidUser'
                return xstep(self, *args, **kwargs)
        return wrap
    return _mock_valid_lfid


def upload(excepted_status, excepted_response):
    def _upload(create_request):
        @functools.wraps(create_request)
        def wrap(self):
            request = create_request(self)
            status, body = self.upload(request)
            if excepted_status == httplib.OK:
                getattr(self, excepted_response)(body)
            else:
                self.assertIn(excepted_response, body)
        return wrap
    return _upload


def create(excepted_status, excepted_response):
    def _create(create_request):
        @functools.wraps(create_request)
        def wrap(self):
            request = create_request(self)
            status, body = self.create(request)
            if excepted_status == httplib.OK:
                getattr(self, excepted_response)(body)
            else:
                self.assertIn(excepted_response, body)
        return wrap
    return _create


def get(excepted_status, excepted_response):
    def _get(get_request):
        @functools.wraps(get_request)
        def wrap(self):
            request = get_request(self)
            status, body = self.get(request)
            if excepted_status == httplib.OK:
                getattr(self, excepted_response)(body)
            else:
                self.assertIn(excepted_response, body)
        return wrap
    return _get


def update(excepted_status, excepted_response):
    def _update(update_request):
        @functools.wraps(update_request)
        def wrap(self):
            request, resource = update_request(self)
            status, body = self.update(request, resource)
            if excepted_status == httplib.OK:
                getattr(self, excepted_response)(request, body)
            else:
                self.assertIn(excepted_response, body)
        return wrap
    return _update


def delete(excepted_status, excepted_response):
    def _delete(delete_request):
        @functools.wraps(delete_request)
        def wrap(self):
            request = delete_request(self)
            if isinstance(request, tuple):
                status, body = self.delete(request[0], *(request[1]))
            else:
                status, body = self.delete(request)
            if excepted_status == httplib.OK:
                getattr(self, excepted_response)(body)
            else:
                self.assertIn(excepted_response, body)
        return wrap
    return _delete


def query(excepted_status, excepted_response, number=0):
    def _query(get_request):
        @functools.wraps(get_request)
        def wrap(self):
            request = get_request(self)
            status, body = self.query(request)
            if excepted_status == httplib.OK:
                getattr(self, excepted_response)(body, number)
            else:
                self.assertIn(excepted_response, body)
        return wrap
    return _query
