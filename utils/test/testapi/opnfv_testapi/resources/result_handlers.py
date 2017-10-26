##############################################################################
# Copyright (c) 2015 Orange
# guyrodrigue.koffi@orange.com / koffirodrigue@gmail.com
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import json
import logging

from bson import objectid
from datetime import datetime
from datetime import timedelta

from opnfv_testapi.common import constants
from opnfv_testapi.common import message
from opnfv_testapi.common import raises
from opnfv_testapi.common.config import CONF
from opnfv_testapi.resources import handlers
from opnfv_testapi.resources import result_models
from opnfv_testapi.tornado_swagger import swagger


class GenericResultHandler(handlers.GenericApiHandler):
    def __init__(self, application, request, **kwargs):
        super(GenericResultHandler, self).__init__(application,
                                                   request,
                                                   **kwargs)
        self.table = self.db_results
        self.table_cls = result_models.TestResult

    def get_int(self, key, value):
        try:
            value = int(value)
        except Exception:
            raises.BadRequest(message.must_int(key))
        return value

    def set_query(self):
        query = dict()
        date_range = dict()

        query['public'] = {'$not': {'$eq': 'false'}}
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
            elif k == 'from':
                date_range.update({'$gte': str(v)})
            elif k == 'to':
                date_range.update({'$lt': str(v)})
            elif k == 'signed':
                username = self.get_secure_cookie(constants.TESTAPI_ID)
                role = self.get_secure_cookie(constants.ROLE)
                if role:
                    del query['public']
                    if role != "reviewer":
                        query['user'] = username
            elif k not in ['last', 'page', 'descend']:
                query[k] = v
            if date_range:
                query['start_date'] = date_range

            # if $lt is not provided,
            # empty/None/null/'' start_date will also be returned
            if 'start_date' in query and '$lt' not in query['start_date']:
                query['start_date'].update({'$lt': str(datetime.now())})

        return query


class ResultsCLHandler(GenericResultHandler):
    @swagger.operation(nickname="queryTestResults")
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
                 - installer : fuel/apex/compass/joid/daisy
                 - build_tag : Jenkins build tag name
                 - period : x last days, incompatible with from/to
                 - from : starting time in 2016-01-01 or 2016-01-01 00:01:23
                 - to : ending time in 2016-01-01 or 2016-01-01 00:01:23
                 - scenario : the test scenario (previously version)
                 - criteria : the global criteria status passed or failed
                 - trust_indicator : evaluate the stability of the test case
                   to avoid running systematically long and stable test case
                 - signed : get logined user result

                GET /results/project=functest&case=vPing&version=Arno-R1 \
                &pod=pod_name&period=15&signed
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
            @param from: i.e. 2016-01-01 or 2016-01-01 00:01:23
            @type from: L{string}
            @in from: query
            @required from: False
            @param to: i.e. 2016-01-01 or 2016-01-01 00:01:23
            @type to: L{string}
            @in to: query
            @required to: False
            @param last: last records stored until now
            @type last: L{string}
            @in last: query
            @required last: False
            @param page: which page to list, default to 1
            @type page: L{int}
            @in page: query
            @required page: False
            @param trust_indicator: must be float
            @type trust_indicator: L{float}
            @in trust_indicator: query
            @required trust_indicator: False
            @param signed: user results or all results
            @type signed: L{string}
            @in signed: query
            @required signed: False
            @param descend: true, newest2oldest; false, oldest2newest
            @type descend: L{string}
            @in descend: query
            @required descend: False
        """
        def descend_limit():
            descend = self.get_query_argument('descend', 'true')
            return -1 if descend.lower() == 'true' else 1

        def last_limit():
            return self.get_int('last', self.get_query_argument('last', 0))

        def page_limit():
            return self.get_int('page', self.get_query_argument('page', 1))

        limitations = {
            'sort': {'_id': descend_limit()},
            'last': last_limit(),
            'page': page_limit(),
            'per_page': CONF.api_results_per_page
        }

        self._list(query=self.set_query(), **limitations)

    @swagger.operation(nickname="createTestResult")
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
        self._post()

    def _post(self):
        def pod_query():
            return {'name': self.json_args.get('pod_name')}

        def project_query():
            return {'name': self.json_args.get('project_name')}

        def testcase_query():
            return {'project_name': self.json_args.get('project_name'),
                    'name': self.json_args.get('case_name')}

        def options_check(field, options):
            return self.json_args.get(field).upper() in options

        miss_fields = ['pod_name', 'project_name', 'case_name']
        carriers = [('pods', pod_query),
                    ('projects', project_query),
                    ('testcases', testcase_query)]
        values_check = [('criteria', options_check, ['PASS', 'FAIL'])]

        self._create(miss_fields=miss_fields,
                     carriers=carriers,
                     values_check=values_check)


class ResultsUploadHandler(ResultsCLHandler):
    @swagger.operation(nickname="uploadTestResult")
    def post(self):
        """
            @description: upload and create a test result
            @param body: result to be created
            @type body: L{ResultCreateRequest}
            @in body: body
            @rtype: L{CreateResponse}
            @return 200: result is created.
            @raise 404: pod/project/testcase not exist
            @raise 400: body/pod_name/project_name/case_name not provided
        """
        logging.info('file upload')
        fileinfo = self.request.files['file'][0]
        is_public = self.get_body_argument('public')
        logging.warning('public:%s', is_public)
        logging.info('results is :%s', fileinfo['filename'])
        logging.info('results is :%s', fileinfo['body'])
        self.json_args = json.loads(fileinfo['body']).copy()
        self.json_args['public'] = is_public

        openid = self.get_secure_cookie(constants.TESTAPI_ID)
        if openid:
            self.json_args['user'] = openid

        super(ResultsUploadHandler, self)._post()


class ResultsGURHandler(GenericResultHandler):
    @swagger.operation(nickname='getTestResultById')
    def get(self, result_id):
        """
            @description: get a single result by result_id
            @rtype: L{TestResult}
            @return 200: test result exist
            @raise 404: test result not exist
        """
        query = dict()
        query["_id"] = objectid.ObjectId(result_id)
        self._get_one(query=query)

    @swagger.operation(nickname="updateTestResultById")
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
        query = {'_id': objectid.ObjectId(result_id)}
        db_keys = []
        self._update(query=query, db_keys=db_keys)
