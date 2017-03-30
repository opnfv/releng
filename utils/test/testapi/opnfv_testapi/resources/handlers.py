##############################################################################
# Copyright (c) 2015 Orange
# guyrodrigue.koffi@orange.com / koffirodrigue@gmail.com
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
# feng.xiaowei@zte.com.cn refactor db.pod to db.pods         5-19-2016
# feng.xiaowei@zte.com.cn refactor test_project to project   5-19-2016
# feng.xiaowei@zte.com.cn refactor response body             5-19-2016
# feng.xiaowei@zte.com.cn refactor pod/project response info 5-19-2016
# feng.xiaowei@zte.com.cn refactor testcase related handler  5-20-2016
# feng.xiaowei@zte.com.cn refactor result related handler    5-23-2016
# feng.xiaowei@zte.com.cn refactor dashboard related handler 5-24-2016
# feng.xiaowei@zte.com.cn add methods to GenericApiHandler   5-26-2016
# feng.xiaowei@zte.com.cn remove PodHandler                  5-26-2016
# feng.xiaowei@zte.com.cn remove ProjectHandler              5-26-2016
# feng.xiaowei@zte.com.cn remove TestcaseHandler             5-27-2016
# feng.xiaowei@zte.com.cn remove ResultHandler               5-29-2016
# feng.xiaowei@zte.com.cn remove DashboardHandler            5-30-2016
##############################################################################

from datetime import datetime
import functools
import json

from tornado import gen
from tornado import web

import models
from opnfv_testapi.common import raises
from opnfv_testapi.tornado_swagger import swagger

DEFAULT_REPRESENTATION = "application/json"


class GenericApiHandler(web.RequestHandler):
    def __init__(self, application, request, **kwargs):
        super(GenericApiHandler, self).__init__(application, request, **kwargs)
        self.db = self.settings["db"]
        self.json_args = None
        self.table = None
        self.table_cls = None
        self.db_projects = 'projects'
        self.db_pods = 'pods'
        self.db_testcases = 'testcases'
        self.db_results = 'results'
        self.db_scenarios = 'scenarios'
        self.auth = self.settings["auth"]

    def prepare(self):
        if self.request.method != "GET" and self.request.method != "DELETE":
            if self.request.headers.get("Content-Type") is not None:
                if self.request.headers["Content-Type"].startswith(
                        DEFAULT_REPRESENTATION):
                    try:
                        self.json_args = json.loads(self.request.body)
                    except (ValueError, KeyError, TypeError) as error:
                        raises.BadRequest("Bad Json format [{}]".format(error))

    def finish_request(self, json_object=None):
        if json_object:
            self.write(json.dumps(json_object))
        self.set_header("Content-Type", DEFAULT_REPRESENTATION)
        self.finish()

    def _create_response(self, resource):
        href = self.request.full_url() + '/' + str(resource)
        return models.CreateResponse(href=href).format()

    def format_data(self, data):
        cls_data = self.table_cls.from_dict(data)
        return cls_data.format_http()

    def authenticate(method):
        @web.asynchronous
        @gen.coroutine
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            if self.auth:
                try:
                    token = self.request.headers['X-Auth-Token']
                except KeyError:
                    raises.Unauthorized("No Authentication Header.")
                query = {'access_token': token}
                check = yield self._eval_db_find_one(query, 'tokens')
                if not check:
                    raises.Forbidden("Invalid Token.")
            ret = yield gen.coroutine(method)(self, *args, **kwargs)
            raise gen.Return(ret)
        return wrapper

    @authenticate
    def _create(self, miss_checks, db_checks, **kwargs):
        """
        :param miss_checks: [miss1, miss2]
        :param db_checks: [(table, exist, query, error)]
        """
        if self.json_args is None:
            raises.BadRequest('no body')

        data = self.table_cls.from_dict(self.json_args)
        for miss in miss_checks:
            miss_data = data.__getattribute__(miss)
            if miss_data is None or miss_data == '':
                raises.BadRequest('{} missing'.format(miss))

        for k, v in kwargs.iteritems():
            data.__setattr__(k, v)

        for table, exist, query, error in db_checks:
            check = yield self._eval_db_find_one(query(data), table)
            if (exist and not check) or (not exist and check):
                code, message = error(data)
                raises.CodeTBD(code, message)

        if self.table != 'results':
            data.creation_date = datetime.now()
        _id = yield self._eval_db(self.table, 'insert', data.format(),
                                  check_keys=False)
        if 'name' in self.json_args:
            resource = data.name
        else:
            resource = _id
        self.finish_request(self._create_response(resource))

    @web.asynchronous
    @gen.coroutine
    def _list(self, query=None, res_op=None, *args, **kwargs):
        if query is None:
            query = {}
        data = []
        cursor = self._eval_db(self.table, 'find', query)
        if 'sort' in kwargs:
            cursor = cursor.sort(kwargs.get('sort'))
        if 'last' in kwargs:
            cursor = cursor.limit(kwargs.get('last'))
        while (yield cursor.fetch_next):
            data.append(self.format_data(cursor.next_object()))
        if res_op is None:
            res = {self.table: data}
        else:
            res = res_op(data, *args)
        self.finish_request(res)

    @web.asynchronous
    @gen.coroutine
    def _get_one(self, query):
        data = yield self._eval_db_find_one(query)
        if data is None:
            raises.NotFound("[{}] not exist in table [{}]"
                            .format(query, self.table))
        self.finish_request(self.format_data(data))

    @authenticate
    def _delete(self, query):
        data = yield self._eval_db_find_one(query)
        if data is None:
            raises.NotFound("[{}] not exit in table [{}]"
                            .format(query, self.table))

        yield self._eval_db(self.table, 'remove', query)
        self.finish_request()

    @authenticate
    def _update(self, query, db_keys):
        if self.json_args is None:
            raises.BadRequest("No payload")

        # check old data exist
        from_data = yield self._eval_db_find_one(query)
        if from_data is None:
            raises.NotFound("{} could not be found in table [{}]"
                            .format(query, self.table))

        data = self.table_cls.from_dict(from_data)
        # check new data exist
        equal, new_query = self._update_query(db_keys, data)
        if not equal:
            to_data = yield self._eval_db_find_one(new_query)
            if to_data is not None:
                raises.Forbidden("{} already exists in table [{}]"
                                 .format(new_query, self.table))

        # we merge the whole document """
        edit_request = self._update_requests(data)

        """ Updating the DB """
        yield self._eval_db(self.table, 'update', query, edit_request,
                            check_keys=False)
        edit_request['_id'] = str(data._id)
        self.finish_request(edit_request)

    def _update_requests(self, data):
        request = dict()
        for k, v in self.json_args.iteritems():
            request = self._update_request(request, k, v,
                                           data.__getattribute__(k))
        if not request:
            raises.Forbidden("Nothing to update")

        edit_request = data.format()
        edit_request.update(request)
        return edit_request

    @staticmethod
    def _update_request(edit_request, key, new_value, old_value):
        """
        This function serves to prepare the elements in the update request.
        We try to avoid replace the exact values in the db
        edit_request should be a dict in which we add an entry (key) after
        comparing values
        """
        if not (new_value is None):
            if new_value != old_value:
                edit_request[key] = new_value

        return edit_request

    def _update_query(self, keys, data):
        query = dict()
        equal = True
        for key in keys:
            new = self.json_args.get(key)
            old = data.__getattribute__(key)
            if new is None:
                new = old
            elif new != old:
                equal = False
            query[key] = new
        return equal, query

    def _eval_db(self, table, method, *args, **kwargs):
        exec_collection = self.db.__getattr__(table)
        return exec_collection.__getattribute__(method)(*args, **kwargs)

    def _eval_db_find_one(self, query, table=None):
        if table is None:
            table = self.table
        return self._eval_db(table, 'find_one', query)


class VersionHandler(GenericApiHandler):
    @swagger.operation(nickname='listAllVersions')
    def get(self):
        """
            @description: list all supported versions
            @rtype: L{Versions}
        """
        versions = [{'version': 'v1.0', 'description': 'basics'}]
        self.finish_request({'versions': versions})
