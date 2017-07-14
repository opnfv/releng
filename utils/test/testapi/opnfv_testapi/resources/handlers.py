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
from tornado import web

from opnfv_testapi.common import check
from opnfv_testapi.common import message
from opnfv_testapi.common import raises
from opnfv_testapi.db import api as dbapi
from opnfv_testapi.resources import models
from opnfv_testapi.tornado_swagger import swagger

DEFAULT_REPRESENTATION = "application/json"


class GenericApiHandler(web.RequestHandler):
    def __init__(self, application, request, **kwargs):
        super(GenericApiHandler, self).__init__(application, request, **kwargs)
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
                        raises.BadRequest(message.bad_format(str(error)))

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

    @check.authenticate
    @check.no_body
    @check.miss_fields
    @check.carriers_exist
    @check.new_not_exists
    def _create(self, **kwargs):
        """
        :param miss_checks: [miss1, miss2]
        :param db_checks: [(table, exist, query, error)]
        """
        data = self.table_cls.from_dict(self.json_args)
        for k, v in kwargs.iteritems():
            if k != 'query':
                data.__setattr__(k, v)

        if self.table != 'results':
            data.creation_date = datetime.now()
        _id = yield dbapi.db_save(self.table, data.format())
        if 'name' in self.json_args:
            resource = data.name
        else:
            resource = _id
        self.finish_request(self._create_response(resource))

    @web.asynchronous
    @gen.coroutine
    def _list(self, query=None, res_op=None, *args, **kwargs):
        sort = kwargs.get('sort')
        page = kwargs.get('page', 0)
        last = kwargs.get('last', 0)
        per_page = kwargs.get('per_page', 0)
        if query is None:
            query = {}
        cursor = dbapi.db_list(self.table, query)
        records_count = yield cursor.count()
        total_pages = self._calc_total_pages(records_count,
                                             last,
                                             page,
                                             per_page)
        pipelines = self._set_pipelines(query, sort, last, page, per_page)
        cursor = dbapi.db_aggregate(self.table, pipelines)
        data = list()
        while (yield cursor.fetch_next):
            data.append(self.format_data(cursor.next_object()))
        if res_op is None:
            res = {self.table: data}
        else:
            res = res_op(data, *args)
        if total_pages > 0:
            res.update({
                'pagination': {
                    'current_page': kwargs.get('page'),
                    'total_pages': total_pages
                }
            })
        self.finish_request(res)

    @staticmethod
    def _calc_total_pages(records_count, last, page, per_page):
        records_nr = records_count
        if (records_count > last) and (last > 0):
            records_nr = last

        total_pages = 0
        if page > 0:
            total_pages, remainder = divmod(records_nr, per_page)
            if remainder > 0:
                total_pages += 1
        if page > total_pages:
            raises.BadRequest(
                'Request page > total_pages [{}]'.format(total_pages))
        return total_pages

    @staticmethod
    def _set_pipelines(query, sort, last, page, per_page):
        pipelines = list()
        if query:
            pipelines.append({'$match': query})
        if sort:
            pipelines.append({'$sort': sort})

        if page > 0:
            pipelines.append({'$skip': (page - 1) * per_page})
            pipelines.append({'$limit': per_page})
        elif last > 0:
            pipelines.append({'$limit': last})

        return pipelines

    @web.asynchronous
    @gen.coroutine
    @check.not_exist
    def _get_one(self, data, query=None):
        self.finish_request(self.format_data(data))

    @check.authenticate
    @check.not_exist
    def _delete(self, data, query=None):
        yield dbapi.db_delete(self.table, query)
        self.finish_request()

    @check.authenticate
    @check.no_body
    @check.not_exist
    @check.updated_one_not_exist
    def _update(self, data, query=None, **kwargs):
        data = self.table_cls.from_dict(data)
        update_req = self._update_requests(data)
        yield dbapi.db_update(self.table, query, update_req)
        update_req['_id'] = str(data._id)
        self.finish_request(update_req)

    def _update_requests(self, data):
        request = dict()
        for k, v in self.json_args.iteritems():
            request = self._update_request(request, k, v,
                                           data.__getattribute__(k))
        if not request:
            raises.Forbidden(message.no_update())

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
            old = data.get(key)
            if new is None:
                new = old
            elif new != old:
                equal = False
            query[key] = new
        return query if not equal else dict()


class VersionHandler(GenericApiHandler):
    @swagger.operation(nickname='listAllVersions')
    def get(self):
        """
            @description: list all supported versions
            @rtype: L{Versions}
        """
        versions = [{'version': 'v1.0', 'description': 'basics'}]
        self.finish_request({'versions': versions})
