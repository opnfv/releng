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
##############################################################################

import json
from datetime import datetime, timedelta

from tornado.web import RequestHandler, asynchronous, HTTPError
from tornado import gen

from models import CreateResponse
from resources.result_models import TestResult
from resources.testcase_models import Testcase
from resources.project_models import Project
from resources.pod_models import Pod
from common.constants import DEFAULT_REPRESENTATION, HTTP_BAD_REQUEST, \
    HTTP_NOT_FOUND, HTTP_FORBIDDEN
from common.config import prepare_put_request
from dashboard.dashboard_utils import check_dashboard_ready_project, \
    check_dashboard_ready_case, get_dashboard_result


def format_data(data, cls):
    cls_data = cls.from_dict(data)
    return cls_data.format_http()


class GenericApiHandler(RequestHandler):
    """
    The purpose of this class is to take benefit of inheritance and prepare
    a set of common functions for
    the handlers
    """

    def initialize(self):
        """ Prepares the database for the entire class """
        self.db = self.settings["db"]

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
                else:
                    self.json_args = None

    def finish_request(self, json_object=None):
        if json_object:
            self.write(json.dumps(json_object))
        self.set_header("Content-Type", DEFAULT_REPRESENTATION)
        self.finish()

    def _create_response(self, resource):
        href = self.request.full_url() + '/' + resource
        return CreateResponse(href=href).format()


class VersionHandler(GenericApiHandler):
    """ Display a message for the API version """
    def get(self):
        self.finish_request([{'v1': 'basics'}])


class PodHandler(GenericApiHandler):
    """ Handle the requests about the POD Platforms
    HTTP Methdods :
        - GET : Get PODS
        - POST : Create a pod
        - DELETE : DELETE POD
    """

    def initialize(self):
        """ Prepares the database for the entire class """
        super(PodHandler, self).initialize()

    @asynchronous
    @gen.coroutine
    def get(self, pod_name=None):
        """
        Get all pods or a single pod
        :param pod_id:
        """
        query = dict()

        if pod_name is not None:
            query["name"] = pod_name
            answer = yield self.db.pods.find_one(query)
            if answer is None:
                raise HTTPError(HTTP_NOT_FOUND,
                                "{} Not Exist".format(pod_name))
            else:
                answer = format_data(answer, Pod)
        else:
            res = []
            cursor = self.db.pods.find(query)
            while (yield cursor.fetch_next):
                res.append(format_data(cursor.next_object(), Pod))
            answer = {'pods': res}

        self.finish_request(answer)

    @asynchronous
    @gen.coroutine
    def post(self):
        """ Create a POD"""

        if self.json_args is None:
            raise HTTPError(HTTP_BAD_REQUEST)

        query = {"name": self.json_args.get("name")}

        # check for existing name in db
        the_pod = yield self.db.pods.find_one(query)
        if the_pod is not None:
            raise HTTPError(HTTP_FORBIDDEN,
                            "{} already exists as a pod".format(
                                self.json_args.get("name")))

        pod = Pod.from_dict(self.json_args)
        pod.creation_date = datetime.now()

        yield self.db.pods.insert(pod.format())
        self.finish_request(self._create_response(pod.name))

    @asynchronous
    @gen.coroutine
    def delete(self, pod_name):
        """ Remove a POD

        # check for an existing pod to be deleted
        mongo_dict = yield self.db.pods.find_one(
            {'name': pod_name})
        pod = TestProject.pod(mongo_dict)
        if pod is None:
            raise HTTPError(HTTP_NOT_FOUND,
                            "{} could not be found as a pod to be deleted"
                            .format(pod_name))

        # just delete it, or maybe save it elsewhere in a future
        res = yield self.db.projects.remove(
            {'name': pod_name})

        self.finish_request(answer)
        """
        pass


class ProjectHandler(GenericApiHandler):
    """
    TestProjectHandler Class
    Handle the requests about the Test projects
    HTTP Methdods :
        - GET : Get all test projects and details about a specific one
        - POST : Add a test project
        - PUT : Edit test projects information (name and/or description)
        - DELETE : Remove a test project
    """

    def initialize(self):
        """ Prepares the database for the entire class """
        super(ProjectHandler, self).initialize()

    @asynchronous
    @gen.coroutine
    def get(self, project_name=None):
        """
        Get Project(s) info
        :param project_name:
        """

        query = dict()

        if project_name is not None:
            query["name"] = project_name
            answer = yield self.db.projects.find_one(query)
            if answer is None:
                raise HTTPError(HTTP_NOT_FOUND,
                                "{} Not Exist".format(project_name))
            else:
                answer = format_data(answer, Project)
        else:
            res = []
            cursor = self.db.projects.find(query)
            while (yield cursor.fetch_next):
                res.append(format_data(cursor.next_object(), Project))
            answer = {'projects': res}

        self.finish_request(answer)

    @asynchronous
    @gen.coroutine
    def post(self):
        """ Create a test project"""

        if self.json_args is None:
            raise HTTPError(HTTP_BAD_REQUEST)

        query = {"name": self.json_args.get("name")}

        # check for name in db
        the_project = yield self.db.projects.find_one(query)
        if the_project is not None:
            raise HTTPError(HTTP_FORBIDDEN,
                            "{} already exists as a project".format(
                                self.json_args.get("name")))

        project = Project.from_dict(self.json_args)
        project.creation_date = datetime.now()

        yield self.db.projects.insert(project.format())
        self.finish_request(self._create_response(project.name))

    @asynchronous
    @gen.coroutine
    def put(self, project_name):
        """ Updates the name and description of a test project"""

        if self.json_args is None:
            raise HTTPError(HTTP_BAD_REQUEST)

        query = {'name': project_name}
        from_project = yield self.db.projects.find_one(query)
        if from_project is None:
            raise HTTPError(HTTP_NOT_FOUND,
                            "{} could not be found".format(project_name))

        project = Project.from_dict(from_project)
        new_name = self.json_args.get("name")
        new_description = self.json_args.get("description")

        # check for payload name parameter in db
        # avoid a request if the project name has not changed in the payload
        if new_name != project.name:
            to_project = yield self.db.projects.find_one(
                {"name": new_name})
            if to_project is not None:
                raise HTTPError(HTTP_FORBIDDEN,
                                "{} already exists as a project"
                                .format(new_name))

        # new dict for changes
        request = dict()
        request = prepare_put_request(request,
                                      "name",
                                      new_name,
                                      project.name)
        request = prepare_put_request(request,
                                      "description",
                                      new_description,
                                      project.description)

        """ raise exception if there isn't a change """
        if not request:
            raise HTTPError(HTTP_FORBIDDEN, "Nothing to update")

        """ we merge the whole document """
        edit_request = project.format()
        edit_request.update(request)

        """ Updating the DB """
        yield self.db.projects.update({'name': project_name}, edit_request)
        new_project = yield self.db.projects.find_one({"_id": project._id})

        self.finish_request(format_data(new_project, Project))

    @asynchronous
    @gen.coroutine
    def delete(self, project_name):
        """ Remove a test project"""
        query = {'name': project_name}

        # check for an existing project to be deleted
        project = yield self.db.projects.find_one(query)
        if project is None:
            raise HTTPError(HTTP_NOT_FOUND,
                            "{} could not be found as a project to be deleted"
                            .format(project_name))

        # just delete it, or maybe save it elsewhere in a future
        yield self.db.projects.remove(query)

        self.finish_request()


class TestcaseHandler(GenericApiHandler):
    """
    TestCasesHandler Class
    Handle the requests about the Test cases for test projects
    HTTP Methdods :
        - GET : Get all test cases and details about a specific one
        - POST : Add a test project
        - PUT : Edit test projects information (name and/or description)
    """

    def initialize(self):
        """ Prepares the database for the entire class """
        super(TestcaseHandler, self).initialize()

    @asynchronous
    @gen.coroutine
    def get(self, project_name, case_name=None):
        """
        Get testcases(s) info
        :param project_name:
        :param case_name:
        """

        query = {'project_name': project_name}

        if case_name is not None:
            query["name"] = case_name
            answer = yield self.db.testcases.find_one(query)
            if answer is None:
                raise HTTPError(HTTP_NOT_FOUND,
                                "{} Not Exist".format(case_name))
            else:
                answer = format_data(answer, Testcase)
        else:
            res = []
            cursor = self.db.testcases.find(query)
            while (yield cursor.fetch_next):
                res.append(format_data(cursor.next_object(), Testcase))
            answer = {'testcases': res}

        self.finish_request(answer)

    @asynchronous
    @gen.coroutine
    def post(self, project_name):
        """ Create a test case"""

        if self.json_args is None:
            raise HTTPError(HTTP_BAD_REQUEST,
                            "Check your request payload")

        # retrieve test project
        project = yield self.db.projects.find_one(
            {"name": project_name})
        if project is None:
            raise HTTPError(HTTP_FORBIDDEN,
                            "Could not find project {}"
                            .format(project_name))

        case_name = self.json_args.get('name')
        the_testcase = yield self.db.testcases.find_one(
            {"project_name": project_name, 'name': case_name})
        if the_testcase:
            raise HTTPError(HTTP_FORBIDDEN,
                            "{} already exists as a case in project {}"
                            .format(case_name, project_name))

        testcase = Testcase.from_dict(self.json_args)
        testcase.project_name = project_name
        testcase.creation_date = datetime.now()

        yield self.db.testcases.insert(testcase.format())
        self.finish_request(self._create_response(testcase.name))

    @asynchronous
    @gen.coroutine
    def put(self, project_name, case_name):
        """
        Updates the name and description of a test case
        :raises HTTPError (HTTP_NOT_FOUND, HTTP_FORBIDDEN)
        """

        query = {'project_name': project_name, 'name': case_name}

        if self.json_args is None:
            raise HTTPError(HTTP_BAD_REQUEST, "No payload")

        # check if there is a case for the project in url parameters
        from_testcase = yield self.db.testcases.find_one(query)
        if from_testcase is None:
            raise HTTPError(HTTP_NOT_FOUND,
                            "{} could not be found as a {} case to be updated"
                            .format(case_name, project_name))

        testcase = Testcase.from_dict(from_testcase)
        new_name = self.json_args.get("name")
        new_project_name = self.json_args.get("project_name")
        if not new_project_name:
            new_project_name = project_name
        new_description = self.json_args.get("description")

        # check if there is not an existing test case
        # with the name provided in the json payload
        if new_name != case_name or new_project_name != project_name:
            to_testcase = yield self.db.testcases.find_one(
                {'project_name': new_project_name, 'name': new_name})
            if to_testcase is not None:
                raise HTTPError(HTTP_FORBIDDEN,
                                "{} already exists as a case in project"
                                .format(new_name, new_project_name))

        # new dict for changes
        request = dict()
        request = prepare_put_request(request,
                                      "name",
                                      new_name,
                                      testcase.name)
        request = prepare_put_request(request,
                                      "project_name",
                                      new_project_name,
                                      testcase.project_name)
        request = prepare_put_request(request,
                                      "description",
                                      new_description,
                                      testcase.description)

        # we raise an exception if there isn't a change
        if not request:
            raise HTTPError(HTTP_FORBIDDEN,
                            "Nothing to update")

        # we merge the whole document """
        edit_request = testcase.format()
        edit_request.update(request)

        """ Updating the DB """
        yield self.db.testcases.update(query, edit_request)
        new_case = yield self.db.testcases.find_one({"_id": testcase._id})
        self.finish_request(format_data(new_case, Testcase))

    @asynchronous
    @gen.coroutine
    def delete(self, project_name, case_name):
        """ Remove a test case"""

        query = {'project_name': project_name, 'name': case_name}

        # check for an existing case to be deleted
        testcase = yield self.db.testcases.find_one(query)
        if testcase is None:
            raise HTTPError(HTTP_NOT_FOUND,
                            "{}/{} could not be found as a case to be deleted"
                            .format(project_name, case_name))

        # just delete it, or maybe save it elsewhere in a future
        yield self.db.testcases.remove(query)
        self.finish_request()


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
