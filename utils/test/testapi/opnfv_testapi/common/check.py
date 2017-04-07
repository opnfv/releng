##############################################################################
# Copyright (c) 2017 ZTE Corp
# feng.xiaowei@zte.com.cn
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import functools

from tornado import web, gen

from opnfv_testapi.common import raises, message


def authenticate(method):
    @web.asynchronous
    @gen.coroutine
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if self.auth:
            try:
                token = self.request.headers['X-Auth-Token']
            except KeyError:
                raises.Unauthorized(message.unauthorized())
            query = {'access_token': token}
            check = yield self._eval_db_find_one(query, 'tokens')
            if not check:
                raises.Forbidden(message.invalid_token())
        ret = yield gen.coroutine(method)(self, *args, **kwargs)
        raise gen.Return(ret)
    return wrapper


def not_exist(xstep):
    @functools.wraps(xstep)
    def wrap(self, *args, **kwargs):
        query = kwargs.get('query')
        data = yield self._eval_db_find_one(query)
        if not data:
            raises.NotFound(message.not_found(self.table, query))
        ret = yield gen.coroutine(xstep)(self, data, *args, **kwargs)
        raise gen.Return(ret)

    return wrap


def no_body(xstep):
    @functools.wraps(xstep)
    def wrap(self, *args, **kwargs):
        if self.json_args is None:
            raises.BadRequest(message.no_body())
        ret = yield gen.coroutine(xstep)(self, *args, **kwargs)
        raise gen.Return(ret)

    return wrap


def miss(xstep):
    @functools.wraps(xstep)
    def wrap(self, *args, **kwargs):
        miss_checks = kwargs.get('miss_checks')
        if miss_checks:
            for miss in miss_checks:
                miss_data = self.json_args.get(miss)
                if miss_data is None or miss_data == '':
                    raises.BadRequest(message.missing(miss))
        ret = yield gen.coroutine(xstep)(self, *args, **kwargs)
        raise gen.Return(ret)
    return wrap


def carriers_exist(xstep):
    @functools.wraps(xstep)
    def wrap(self, *args, **kwargs):
        carriers = kwargs.get('carriers')
        if carriers:
            for table, query in carriers:
                exist = yield self._eval_db_find_one(query(), table)
                if not exist:
                    raises.Forbidden(message.not_found(table, query()))
        ret = yield gen.coroutine(xstep)(self, *args, **kwargs)
        raise gen.Return(ret)
    return wrap


def new_not_exists(xstep):
    @functools.wraps(xstep)
    def wrap(self, *args, **kwargs):
        query = kwargs.get('query')
        if query:
            to_data = yield self._eval_db_find_one(query())
            if to_data:
                raises.Forbidden(message.exist(self.table, query()))
        ret = yield gen.coroutine(xstep)(self, *args, **kwargs)
        raise gen.Return(ret)
    return wrap


def updated_one_not_exist(xstep):
    @functools.wraps(xstep)
    def wrap(self, data, *args, **kwargs):
        db_keys = kwargs.get('db_keys')
        query = self._update_query(db_keys, data)
        if query:
            to_data = yield self._eval_db_find_one(query)
            if to_data:
                raises.Forbidden(message.exist(self.table, query))
        ret = yield gen.coroutine(xstep)(self, data, *args, **kwargs)
        raise gen.Return(ret)
    return wrap

