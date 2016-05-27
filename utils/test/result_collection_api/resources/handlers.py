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
##############################################################################

import json
from datetime import datetime, timedelta

from tornado.web import RequestHandler, asynchronous, HTTPError
from tornado import gen

from models import CreateResponse
from resources.result_models import TestResult
from common.constants import DEFAULT_REPRESENTATION, HTTP_BAD_REQUEST, \
    HTTP_NOT_FOUND, HTTP_FORBIDDEN
from common.config import prepare_put_request
from dashboard.dashboard_utils import check_dashboard_ready_project, \
    check_dashboard_ready_case, get_dashboard_result


def format_data(data, cls):
    cls_data = cls.from_dict(data)
    return cls_data.format_http()


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
        href = self.request.full_url() + '/' + resource
        return CreateResponse(href=href).format()

    @asynchronous
    @gen.coroutine
    def _create(self, db_checks, **kwargs):
        """
        :param db_checks: [(table, exist, query, (error, message))]
        :param db_op: (insert/remove)
        :param res_op: (_create_response/None)
        :return:
        """
        if self.json_args is None:
            raise HTTPError(HTTP_BAD_REQUEST, "no body")

        data = self.table_cls.from_dict(self.json_args)
        name = data.name
        if name is None or name == '':
            raise HTTPError(HTTP_BAD_REQUEST,
                            '{} name missing'.format(self.table[:-1]))

        for k, v in kwargs.iteritems():
            data.__setattr__(k, v)

        for table, exist, query, error in db_checks:
            check = yield self._eval_db(table, 'find_one', query(data))
            if (exist and not check) or (not exist and check):
                code, message = error(data)
                raise HTTPError(code, message)

        data.creation_date = datetime.now()
        yield self._eval_db(self.table, 'insert', data.format())
        self.finish_request(self._create_response(name))

    @asynchronous
    @gen.coroutine
    def _list(self, query=None):
        if query is None:
            query = {}
        res = []
        cursor = self._eval_db(self.table, 'find', query)
        while (yield cursor.fetch_next):
            res.append(format_data(cursor.next_object(), self.table_cls))
        self.finish_request({self.table: res})

    @asynchronous
    @gen.coroutine
    def _get_one(self, query):
        data = yield self._eval_db(self.table, 'find_one', query)
        if data is None:
            raise HTTPError(HTTP_NOT_FOUND,
                            "[{}] not exist in table [{}]"
                            .format(query, self.table))
        self.finish_request(format_data(data, self.table_cls))

    @asynchronous
    @gen.coroutine
    def _delete(self, query):
        data = yield self._eval_db(self.table, 'find_one', query)
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
        from_data = yield self._eval_db(self.table, 'find_one', query)
        if from_data is None:
            raise HTTPError(HTTP_NOT_FOUND,
                            "{} could not be found in table [{}]"
                            .format(query, self.table))

        data = self.table_cls.from_dict(from_data)
        # check new data exist
        equal, new_query = self._update_query(db_keys, data)
        if not equal:
            to_data = yield self._eval_db(self.table, 'find_one', new_query)
            if to_data is not None:
                raise HTTPError(HTTP_FORBIDDEN,
                                "{} already exists in table [{}]"
                                .format(new_query, self.table))

        # we merge the whole document """
        edit_request = data.format()
        edit_request.update(self._update_request(data))

        """ Updating the DB """
        yield self._eval_db(self.table, 'update', query, edit_request)
        edit_request['_id'] = str(data._id)
        self.finish_request(edit_request)

    def _update_request(self, data):
        request = dict()
        for k, v in self.json_args.iteritems():
            request = prepare_put_request(request, k, v,
                                          data.__getattribute__(k))
        if not request:
            raise HTTPError(HTTP_FORBIDDEN, "Nothing to update")
        return request

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

    def _eval_db(self, table, method, *args):
        return eval('self.db.%s.%s(*args)' % (table, method))


class VersionHandler(GenericApiHandler):
    """ Display a message for the API version """
    def get(self):
        self.finish_request([{'v1': 'basics'}])


class TestResultsHandler(GenericApiHandler):
    """
    TestResultsHandler Class
    Handle the requests about the Test project's results
    HTTP Methdods :
        - GET : Get all test results and details about a specific one
        - POST : Add a test results
        - DELETE : Remove a test result
    """

    def initialize(self):
        """ Prepares the database for the entire class """
        super(TestResultsHandler, self).initialize()
        self.name = "test_result"

    @asynchronous
    @gen.coroutine
    def get(self, result_id=None):
        """
        Retrieve result(s) for a test project on a specific POD.
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
         - trust_indicator : evaluate the stability of the test case to avoid
         running systematically long and stable test case


        :param result_id: Get a result by ID
        :raise HTTPError

        GET /results/project=functest&case=vPing&version=Arno-R1 \
        &pod=pod_name&period=15
        => get results with optional filters
        """

        # prepare request
        query = dict()
        if result_id is not None:
            query["_id"] = result_id
            answer = yield self.db.results.find_one(query)
            if answer is None:
                raise HTTPError(HTTP_NOT_FOUND,
                                "test result {} Not Exist".format(result_id))
            else:
                answer = format_data(answer, TestResult)
        else:
            pod_arg = self.get_query_argument("pod", None)
            project_arg = self.get_query_argument("project", None)
            case_arg = self.get_query_argument("case", None)
            version_arg = self.get_query_argument("version", None)
            installer_arg = self.get_query_argument("installer", None)
            build_tag_arg = self.get_query_argument("build_tag", None)
            scenario_arg = self.get_query_argument("scenario", None)
            criteria_arg = self.get_query_argument("criteria", None)
            period_arg = self.get_query_argument("period", None)
            trust_indicator_arg = self.get_query_argument("trust_indicator",
                                                          None)

            if project_arg is not None:
                query["project_name"] = project_arg

            if case_arg is not None:
                query["case_name"] = case_arg

            if pod_arg is not None:
                query["pod_name"] = pod_arg

            if version_arg is not None:
                query["version"] = version_arg

            if installer_arg is not None:
                query["installer"] = installer_arg

            if build_tag_arg is not None:
                query["build_tag"] = build_tag_arg

            if scenario_arg is not None:
                query["scenario"] = scenario_arg

            if criteria_arg is not None:
                query["criteria_tag"] = criteria_arg

            if trust_indicator_arg is not None:
                query["trust_indicator_arg"] = trust_indicator_arg

            if period_arg is not None:
                try:
                    period_arg = int(period_arg)
                except:
                    raise HTTPError(HTTP_BAD_REQUEST)

                if period_arg > 0:
                    period = datetime.now() - timedelta(days=period_arg)
                    obj = {"$gte": str(period)}
                    query["creation_date"] = obj

            res = []
            cursor = self.db.results.find(query)
            while (yield cursor.fetch_next):
                res.append(format_data(cursor.next_object(), TestResult))
            answer = {'results': res}

        self.finish_request(answer)

    @asynchronous
    @gen.coroutine
    def post(self):
        """
        Create a new test result
        :return: status of the request
        :raise HTTPError
        """

        # check for request payload
        if self.json_args is None:
            raise HTTPError(HTTP_BAD_REQUEST, 'no payload')

        result = TestResult.from_dict(self.json_args)

        # check for pod_name instead of id,
        # keeping id for current implementations
        if result.pod_name is None:
            raise HTTPError(HTTP_BAD_REQUEST, 'pod is not provided')

        # check for missing parameters in the request payload
        if result.project_name is None:
            raise HTTPError(HTTP_BAD_REQUEST, 'project is not provided')

        if result.case_name is None:
            raise HTTPError(HTTP_BAD_REQUEST, 'testcase is not provided')

        # TODO : replace checks with jsonschema
        # check for pod
        the_pod = yield self.db.pods.find_one({"name": result.pod_name})
        if the_pod is None:
            raise HTTPError(HTTP_NOT_FOUND,
                            "Could not find POD [{}] "
                            .format(self.json_args.get("pod_name")))

        # check for project
        the_project = yield self.db.projects.find_one(
            {"name": result.project_name})
        if the_project is None:
            raise HTTPError(HTTP_NOT_FOUND, "Could not find project [{}] "
                            .format(result.project_name))

        # check for testcase
        the_testcase = yield self.db.testcases.find_one(
            {"name": result.case_name})
        if the_testcase is None:
            raise HTTPError(HTTP_NOT_FOUND,
                            "Could not find testcase [{}] "
                            .format(result.case_name))

        _id = yield self.db.results.insert(result.format(), check_keys=False)

        self.finish_request(self._create_response(_id))


class DashboardHandler(GenericApiHandler):
    """
    DashboardHandler Class
    Handle the requests about the Test project's results
    in a dahboard ready format
    HTTP Methdods :
        - GET : Get all test results and details about a specific one
    """
    def initialize(self):
        """ Prepares the database for the entire class """
        super(DashboardHandler, self).initialize()
        self.name = "dashboard"

    @asynchronous
    @gen.coroutine
    def get(self):
        """
        Retrieve dashboard ready result(s) for a test project
        Available filters for this request are :
         - project : project name
         - case : case name
         - pod : pod name
         - version : platform version (Arno-R1, ...)
         - installer (fuel, ...)
         - period : x (x last days)


        :param result_id: Get a result by ID
        :raise HTTPError

        GET /dashboard?project=functest&case=vPing&version=Arno-R1 \
        &pod=pod_name&period=15
        => get results with optional filters
        """

        project_arg = self.get_query_argument("project", None)
        case_arg = self.get_query_argument("case", None)
        pod_arg = self.get_query_argument("pod", None)
        version_arg = self.get_query_argument("version", None)
        installer_arg = self.get_query_argument("installer", None)
        period_arg = self.get_query_argument("period", None)

        # prepare request
        query = dict()

        if project_arg is not None:
            query["project_name"] = project_arg

        if case_arg is not None:
            query["case_name"] = case_arg

        if pod_arg is not None:
            query["pod_name"] = pod_arg

        if version_arg is not None:
            query["version"] = version_arg

        if installer_arg is not None:
            query["installer"] = installer_arg

        if period_arg is not None:
            try:
                period_arg = int(period_arg)
            except:
                raise HTTPError(HTTP_BAD_REQUEST)
            if period_arg > 0:
                period = datetime.now() - timedelta(days=period_arg)
                obj = {"$gte": str(period)}
                query["creation_date"] = obj

        # on /dashboard retrieve the list of projects and testcases
        # ready for dashboard
        if project_arg is None:
            raise HTTPError(HTTP_NOT_FOUND, "Project name missing")

        if not check_dashboard_ready_project(project_arg):
            raise HTTPError(HTTP_NOT_FOUND,
                            'Project [{}] not dashboard ready'
                            .format(project_arg))

        if case_arg is None:
            raise HTTPError(
                HTTP_NOT_FOUND,
                'Test case missing for project [{}]'.format(project_arg))

        if not check_dashboard_ready_case(project_arg, case_arg):
            raise HTTPError(
                HTTP_NOT_FOUND,
                'Test case [{}] not dashboard ready for project [{}]'
                .format(case_arg, project_arg))

        # special case of status for project
        res = []
        if case_arg != "status":
            cursor = self.db.results.find(query)
            while (yield cursor.fetch_next):
                result = TestResult.from_dict(cursor.next_object())
                res.append(result.format_http())

        # final response object
        self.finish_request(get_dashboard_result(project_arg, case_arg, res))
