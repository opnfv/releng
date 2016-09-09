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

import json
from datetime import datetime

from tornado import gen
from tornado.web import RequestHandler, asynchronous, HTTPError

from models import CreateResponse
from opnfv_testapi.common.constants import DEFAULT_REPRESENTATION, \
    HTTP_BAD_REQUEST, HTTP_NOT_FOUND, HTTP_FORBIDDEN
from opnfv_testapi.tornado_swagger import swagger


class GenericApiHandler(RequestHandler):
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

    def prepare(self):
        if self.request.method != "GET" and self.request.method != "DELETE":
            if self.request.headers.get("Content-Type") is not None:
                if self.request.headers["Content-Type"].startswith(
                        DEFAULT_REPRESENTATION):
                    try:
                        self.json_args = json.loads(self.request.body)
                    except (ValueError, KeyError, TypeError) as error:
                        raise HTTPError(HTTP_BAD_REQUEST,
                                        "Bad Json format [{}]".
                                        format(error))

    def finish_request(self, json_object=None):
        if json_object:
            self.write(json.dumps(json_object))
        self.set_header("Content-Type", DEFAULT_REPRESENTATION)
        self.finish()

    def _create_response(self, resource):
        href = self.request.full_url() + '/' + str(resource)
        return CreateResponse(href=href).format()

    def format_data(self, data):
        cls_data = self.table_cls.from_dict(data)
        return cls_data.format_http()

    @asynchronous
    @gen.coroutine
    def _create(self, miss_checks, db_checks, **kwargs):
        """
        :param miss_checks: [miss1, miss2]
        :param db_checks: [(table, exist, query, error)]
        """
        if self.json_args is None:
            raise HTTPError(HTTP_BAD_REQUEST, "no body")

        data = self.table_cls.from_dict(self.json_args)
        for miss in miss_checks:
            miss_data = data.__getattribute__(miss)
            if miss_data is None or miss_data == '':
                raise HTTPError(HTTP_BAD_REQUEST,
                                '{} missing'.format(miss))

        for k, v in kwargs.iteritems():
            data.__setattr__(k, v)

        for table, exist, query, error in db_checks:
            check = yield self._eval_db_find_one(query(data), table)
            if (exist and not check) or (not exist and check):
                code, message = error(data)
                raise HTTPError(code, message)

        if self.table != 'results':
            data.creation_date = datetime.now()
        _id = yield self._eval_db(self.table, 'insert', data.format(),
                                  check_keys=False)
        if 'name' in self.json_args:
            resource = data.name
        else:
            resource = _id
        self.finish_request(self._create_response(resource))

    @asynchronous
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

    @asynchronous
    @gen.coroutine
    def _get_one(self, query):
        data = yield self._eval_db_find_one(query)
        if data is None:
            raise HTTPError(HTTP_NOT_FOUND,
                            "[{}] not exist in table [{}]"
                            .format(query, self.table))
        self.finish_request(self.format_data(data))

    @asynchronous
    @gen.coroutine
    def _delete(self, query):
        data = yield self._eval_db_find_one(query)
        if data is None:
            raise HTTPError(HTTP_NOT_FOUND,
                            "[{}] not exit in table [{}]"
                            .format(query, self.table))

        yield self._eval_db(self.table, 'remove', query)
        self.finish_request()

    @asynchronous
    @gen.coroutine
    def _update(self, query, db_keys):
        if self.json_args is None:
            raise HTTPError(HTTP_BAD_REQUEST, "No payload")

        # check old data exist
        from_data = yield self._eval_db_find_one(query)
        if from_data is None:
            raise HTTPError(HTTP_NOT_FOUND,
                            "{} could not be found in table [{}]"
                            .format(query, self.table))

        data = self.table_cls.from_dict(from_data)
        # check new data exist
        equal, new_query = self._update_query(db_keys, data)
        if not equal:
            to_data = yield self._eval_db_find_one(new_query)
            if to_data is not None:
                raise HTTPError(HTTP_FORBIDDEN,
                                "{} already exists in table [{}]"
                                .format(new_query, self.table))

        # we merge the whole document """
        edit_request = data.format()
        edit_request.update(self._update_requests(data))

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
            raise HTTPError(HTTP_FORBIDDEN, "Nothing to update")
        return request

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
        print vars(self.db)
        table_obj = vars(self.db)[table]
        return table_obj.__getattribute__(method)(*args, **kwargs)

    def _eval_db_find_one(self, query, table=None):
        if table is None:
            table = self.table
        return self._eval_db(table, 'find_one', query)


class VersionHandler(GenericApiHandler):
    @swagger.operation(nickname='list')
    def get(self):
        """
            @description: list all supported versions
            @rtype: L{Versions}
        """
        versions = [{'version': 'v1.0', 'description': 'basics'}]
        self.finish_request({'versions': versions})
