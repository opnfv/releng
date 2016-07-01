##############################################################################
# Copyright (c) 2015 Orange
# guyrodrigue.koffi@orange.com / koffirodrigue@gmail.com
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
from datetime import datetime, timedelta

from bson.objectid import ObjectId
from tornado.web import HTTPError

from opnfv_testapi.common.constants import HTTP_BAD_REQUEST, HTTP_NOT_FOUND
from opnfv_testapi.resources.handlers import GenericApiHandler
from opnfv_testapi.resources.result_models import TestResult
from opnfv_testapi.tornado_swagger import swagger


class GenericResultHandler(GenericApiHandler):
    def __init__(self, application, request, **kwargs):
        super(GenericResultHandler, self).__init__(application,
                                                   request,
                                                   **kwargs)
        self.table = self.db_results
        self.table_cls = TestResult

    def get_int(self, key, value):
        try:
            value = int(value)
        except:
            raise HTTPError(HTTP_BAD_REQUEST, '{} must be int'.format(key))
        return value

    def set_query(self):
        query = dict()
        for k in self.request.query_arguments.keys():
            v = self.get_query_argument(k)
            if k == 'project' or k == 'pod' or k == 'case':
                query[k + '_name'] = v
            elif k == 'period':
                v = self.get_int(k, v)
                if v > 0:
                    period = datetime.now() - timedelta(days=v)
                    obj = {"$gte": str(period)}
                    query['start_date'] = obj
            elif k == 'trust_indicator':
                query[k + '.current'] = float(v)
            elif k != 'last':
                query[k] = v
        return query


class ResultsCLHandler(GenericResultHandler):
    @swagger.operation(nickname="list-all")
    def get(self):
        """
            @description: Retrieve result(s) for a test project
                          on a specific pod.
            @notes: Retrieve result(s) for a test project on a specific pod.
                Available filters for this request are :
                 - project : project name
                 - case : case name
                 - pod : pod name
                 - version : platform version (Arno-R1, ...)
                 - installer (fuel, ...)
                 - build_tag : Jenkins build tag name
                 - period : x (x last days)
                 - scenario : the test scenario (previously version)
                 - criteria : the global criteria status passed or failed
                 - trust_indicator : evaluate the stability of the test case
                   to avoid running systematically long and stable test case

                GET /results/project=functest&case=vPing&version=Arno-R1 \
                &pod=pod_name&period=15
            @return 200: all test results consist with query,
                         empty list if no result is found
            @rtype: L{TestResults}
            @param pod: pod name
            @type pod: L{string}
            @in pod: query
            @required pod: False
            @param project: project name
            @type project: L{string}
            @in project: query
            @required project: False
            @param case: case name
            @type case: L{string}
            @in case: query
            @required case: False
            @param version: i.e. Colorado
            @type version: L{string}
            @in version: query
            @required version: False
            @param installer: fuel/apex/joid/compass
            @type installer: L{string}
            @in installer: query
            @required installer: False
            @param build_tag: i.e. v3.0
            @type build_tag: L{string}
            @in build_tag: query
            @required build_tag: False
            @param scenario: i.e. odl
            @type scenario: L{string}
            @in scenario: query
            @required scenario: False
            @param criteria: i.e. passed
            @type criteria: L{string}
            @in criteria: query
            @required criteria: False
            @param period: last days
            @type period: L{string}
            @in period: query
            @required period: False
            @param last: last days
            @type last: L{string}
            @in last: query
            @required last: False
            @param trust_indicator: must be float
            @type trust_indicator: L{float}
            @in trust_indicator: query
            @required trust_indicator: False
        """
        last = self.get_query_argument('last', 0)
        if last is not None:
            last = self.get_int('last', last)

        self._list(self.set_query(), sort=[('start_date', -1)], last=last)

    @swagger.operation(nickname="create")
    def post(self):
        """
            @description: create a test result
            @param body: result to be created
            @type body: L{ResultCreateRequest}
            @in body: body
            @rtype: L{CreateResponse}
            @return 200: result is created.
            @raise 404: pod/project/testcase not exist
            @raise 400: body/pod_name/project_name/case_name not provided
        """
        def pod_query(data):
            return {'name': data.pod_name}

        def pod_error(data):
            message = 'Could not find pod [{}]'.format(data.pod_name)
            return HTTP_NOT_FOUND, message

        def project_query(data):
            return {'name': data.project_name}

        def project_error(data):
            message = 'Could not find project [{}]'.format(data.project_name)
            return HTTP_NOT_FOUND, message

        def testcase_query(data):
            return {'project_name': data.project_name, 'name': data.case_name}

        def testcase_error(data):
            message = 'Could not find testcase [{}] in project [{}]'\
                .format(data.case_name, data.project_name)
            return HTTP_NOT_FOUND, message

        miss_checks = ['pod_name', 'project_name', 'case_name']
        db_checks = [('pods', True, pod_query, pod_error),
                     ('projects', True, project_query, project_error),
                     ('testcases', True, testcase_query, testcase_error)]
        self._create(miss_checks, db_checks)


class ResultsGURHandler(GenericResultHandler):
    @swagger.operation(nickname='get-one')
    def get(self, result_id):
        """
            @description: get a single result by result_id
            @rtype: L{TestResult}
            @return 200: test result exist
            @raise 404: test result not exist
        """
        query = dict()
        query["_id"] = ObjectId(result_id)
        self._get_one(query)

    @swagger.operation(nickname="update")
    def put(self, result_id):
        """
            @description: update a single result by _id
            @param body: fields to be updated
            @type body: L{ResultUpdateRequest}
            @in body: body
            @rtype: L{Result}
            @return 200: update success
            @raise 404: result not exist
            @raise 403: nothing to update
        """
        query = {'_id': ObjectId(result_id)}
        db_keys = []
        self._update(query, db_keys)
