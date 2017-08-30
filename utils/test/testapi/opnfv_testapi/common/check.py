##############################################################################
# Copyright (c) 2017 ZTE Corp
# feng.xiaowei@zte.com.cn
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import functools

import cas
from tornado import gen
from tornado import web

from opnfv_testapi.common import constants
from opnfv_testapi.common import message
from opnfv_testapi.common import raises
from opnfv_testapi.common.config import CONF
from opnfv_testapi.db import api as dbapi


def login(method):
    @web.asynchronous
    @gen.coroutine
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        ticket = self.get_query_argument('ticket', default=None)
        if ticket:
            client = cas.CASClient(version='2',
                                   server_url=CONF.lfid_cas_url,
                                   service_url=CONF.ui_url)
            (user, attrs, _) = client.verify_ticket(ticket=ticket)
            print 'login user: {}'.format(user)
            login_user = {
                'user': user,
                'email': attrs.get('mail'),
                'fullname': attrs.get('field_lf_full_name'),
                'groups': constants.TESTAPI_USERS + attrs.get('group', [])
            }
            q_user = {'user': user}
            db_user = yield dbapi.db_find_one(constants.USER_TABLE, q_user)
            if not db_user:
                dbapi.db_save(constants.USER_TABLE, login_user)
            else:
                dbapi.db_update(constants.USER_TABLE, q_user, login_user)

            self.clear_cookie(constants.TESTAPI_ID)
            self.set_secure_cookie(constants.TESTAPI_ID, user)
        ret = yield gen.coroutine(method)(self, *args, **kwargs)
        raise gen.Return(ret)
    return wrapper


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
            check = yield dbapi.db_find_one('tokens', query)
            if not check:
                raises.Forbidden(message.invalid_token())
        ret = yield gen.coroutine(method)(self, *args, **kwargs)
        raise gen.Return(ret)
    return wrapper


def not_exist(xstep):
    @functools.wraps(xstep)
    def wrap(self, *args, **kwargs):
        query = kwargs.get('query')
        data = yield dbapi.db_find_one(self.table, query)
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


def miss_fields(xstep):
    @functools.wraps(xstep)
    def wrap(self, *args, **kwargs):
        fields = kwargs.pop('miss_fields', [])
        if fields:
            for miss in fields:
                miss_data = self.json_args.get(miss)
                if miss_data is None or miss_data == '':
                    raises.BadRequest(message.missing(miss))
        ret = yield gen.coroutine(xstep)(self, *args, **kwargs)
        raise gen.Return(ret)
    return wrap


def carriers_exist(xstep):
    @functools.wraps(xstep)
    def wrap(self, *args, **kwargs):
        carriers = kwargs.pop('carriers', {})
        if carriers:
            for table, query in carriers:
                exist = yield dbapi.db_find_one(table, query())
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
            to_data = yield dbapi.db_find_one(self.table, query())
            if to_data:
                raises.Forbidden(message.exist(self.table, query()))
        ret = yield gen.coroutine(xstep)(self, *args, **kwargs)
        raise gen.Return(ret)
    return wrap


def updated_one_not_exist(xstep):
    @functools.wraps(xstep)
    def wrap(self, data, *args, **kwargs):
        db_keys = kwargs.pop('db_keys', [])
        query = self._update_query(db_keys, data)
        if query:
            to_data = yield dbapi.db_find_one(self.table, query)
            if to_data:
                raises.Forbidden(message.exist(self.table, query))
        ret = yield gen.coroutine(xstep)(self, data, *args, **kwargs)
        raise gen.Return(ret)
    return wrap
