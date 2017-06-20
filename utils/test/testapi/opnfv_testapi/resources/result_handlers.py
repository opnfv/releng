##############################################################################
# Copyright (c) 2015 Orange
# guyrodrigue.koffi@orange.com / koffirodrigue@gmail.com
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
from datetime import datetime
from datetime import timedelta

from bson import objectid

from opnfv_testapi.common import config
from opnfv_testapi.common import message
from opnfv_testapi.common import raises
from opnfv_testapi.resources import handlers
from opnfv_testapi.resources import result_models
from opnfv_testapi.tornado_swagger import swagger

CONF = config.Config()


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
        except:
            raises.BadRequest(message.must_int(key))
        return value

    def set_query(self):
        query = dict()
        date_range = dict()

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
            elif k != 'last' and k != 'page':
                query[k] = v
            if date_range:
                query['start_date'] = date_range
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
            @param page: which page to list
            @type page: L{int}
            @in page: query
            @required page: False
            @param trust_indicator: must be float
            @type trust_indicator: L{float}
            @in trust_indicator: query
            @required trust_indicator: False
        """
        limitations = {'sort': [('start_date', -1)]}
        last = self.get_query_argument('last', 0)
        if last is not None:
            last = self.get_int('last', last)
            limitations.update({'last': last})

        page = self.get_query_argument('page', 1)
        if page is not None:
            page = self.get_int('page', page)
            limitations.update({'page': page,
                                'per_page': CONF.api_results_per_page})

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
        def pod_query():
            return {'name': self.json_args.get('pod_name')}

        def project_query():
            return {'name': self.json_args.get('project_name')}

        def testcase_query():
            return {'project_name': self.json_args.get('project_name'),
                    'name': self.json_args.get('case_name')}

        miss_fields = ['pod_name', 'project_name', 'case_name']
        carriers = [('pods', pod_query),
                    ('projects', project_query),
                    ('testcases', testcase_query)]
        self._create(miss_fields=miss_fields, carriers=carriers)


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
