##############################################################################
# Copyright (c) 2015 Orange
# guyrodrigue.koffi@orange.com / koffirodrigue@gmail.com
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

import json

from tornado.web import RequestHandler, asynchronous, HTTPError
from tornado import gen
from datetime import datetime, timedelta

from models import Pod, TestProject, TestCase, TestResult
from common.constants import DEFAULT_REPRESENTATION, HTTP_BAD_REQUEST, \
    HTTP_NOT_FOUND, HTTP_FORBIDDEN
from common.config import prepare_put_request


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
        if not (self.request.method == "GET"):
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

    def finish_request(self, json_object):
        self.write(json.dumps(json_object))
        self.set_header("Content-Type", DEFAULT_REPRESENTATION)
        self.finish()


class VersionHandler(RequestHandler):
    """ Display a message for the API version """
    def get(self):
        self.write("Collection of test result API, v1")


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
        get_request = dict()

        if pod_name is not None:
            get_request["name"] = pod_name

        res = []
        cursor = self.db.pod.find(get_request)
        while (yield cursor.fetch_next):
            pod = Pod.pod_from_dict(cursor.next_object())
            res.append(pod.format())

        meta = dict()
        meta["total"] = len(res)
        meta["success"] = True if len(res) > 0 else False

        answer = dict()
        answer["pods"] = res
        answer["meta"] = meta

        self.finish_request(answer)

    @asynchronous
    @gen.coroutine
    def post(self):
        """ Create a POD"""

        if self.json_args is None:
            raise HTTPError(HTTP_BAD_REQUEST)

        query = {"name": self.json_args.get("name")}

        # check for existing name in db
        mongo_dict = yield self.db.pod.find_one(query)
        if mongo_dict is not None:
            raise HTTPError(HTTP_FORBIDDEN,
                            "{} already exists as a pod".format(
                                self.json_args.get("name")))

        pod = Pod.pod_from_dict(self.json_args)
        pod.creation_date = datetime.now()

        future = self.db.pod.insert(pod.format())
        result = yield future
        pod._id = result

        meta = dict()
        meta["success"] = True
        meta["uri"] = "/pods/{}".format(pod.name)

        answer = dict()
        answer["pod"] = pod.format_http()
        answer["meta"] = meta

        self.finish_request(answer)

    @asynchronous
    @gen.coroutine
    def delete(self, pod_name):
        """ Remove a POD

        # check for an existing pod to be deleted
        mongo_dict = yield self.db.pod.find_one(
            {'name': pod_name})
        pod = TestProject.pod(mongo_dict)
        if pod is None:
            raise HTTPError(HTTP_NOT_FOUND,
                            "{} could not be found as a pod to be deleted"
                            .format(pod_name))

        # just delete it, or maybe save it elsewhere in a future
        res = yield self.db.test_projects.remove(
            {'name': pod_name})

        meta = dict()
        meta["success"] = True
        meta["deletion-data"] = res

        answer = dict()
        answer["meta"] = meta

        self.finish_request(answer)
        """
        pass


class TestProjectHandler(GenericApiHandler):
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
        super(TestProjectHandler, self).initialize()

    @asynchronous
    @gen.coroutine
    def get(self, project_name=None):
        """
        Get Project(s) info
        :param project_name:
        """

        if project_name is None:
            project_name = ""

        get_request = dict()

        if len(project_name) > 0:
            get_request["name"] = project_name

        res = []
        cursor = self.db.test_projects.find(get_request)
        while (yield cursor.fetch_next):
            test_project = TestProject.testproject_from_dict(
                cursor.next_object())
            res.append(test_project.format_http())

        meta = dict()
        meta["total"] = len(res)
        meta["success"] = True if len(res) > 0 else False

        answer = dict()
        answer["test_projects"] = res
        answer["meta"] = meta

        self.finish_request(answer)

    @asynchronous
    @gen.coroutine
    def post(self):
        """ Create a test project"""

        if self.json_args is None:
            raise HTTPError(HTTP_BAD_REQUEST)

        query = {"name": self.json_args.get("name")}

        # check for name in db
        mongo_dict = yield self.db.test_projects.find_one(query)
        if mongo_dict is not None:
            raise HTTPError(HTTP_FORBIDDEN,
                            "{} already exists as a project".format(
                                self.json_args.get("name")))

        test_project = TestProject.testproject_from_dict(self.json_args)
        test_project.creation_date = datetime.now()

        future = self.db.test_projects.insert(test_project.format())
        result = yield future
        test_project._id = result

        self.finish_request(test_project.format_http())

    @asynchronous
    @gen.coroutine
    def put(self, project_name):
        """ Updates the name and description of a test project"""

        print "PUT request for : {}".format(project_name)

        query = {'name': project_name}
        mongo_dict = yield self.db.test_projects.find_one(query)
        test_project = TestProject.testproject_from_dict(mongo_dict)
        if test_project is None:
            raise HTTPError(HTTP_NOT_FOUND,
                            "{} could not be found".format(project_name))

        new_name = self.json_args.get("name")
        new_description = self.json_args.get("description")

        # check for payload name parameter in db
        # avoid a request if the project name has not changed in the payload
        if new_name != test_project.name:
            mongo_dict = yield self.db.test_projects.find_one(
                {"name": new_name})
            if mongo_dict is not None:
                raise HTTPError(HTTP_FORBIDDEN,
                                "{} already exists as a project"
                                .format(new_name))

        # new dict for changes
        request = dict()
        request = prepare_put_request(request,
                                      "name",
                                      new_name,
                                      test_project.name)
        request = prepare_put_request(request,
                                      "description",
                                      new_description,
                                      test_project.description)

        """ raise exception if there isn't a change """
        if not request:
            raise HTTPError(HTTP_FORBIDDEN,
                            "Nothing to update")

        """ we merge the whole document """
        edit_request = test_project.format()
        edit_request.update(request)

        """ Updating the DB """
        res = yield self.db.test_projects.update({'name': project_name},
                                                 edit_request)
        print res
        edit_request["_id"] = str(test_project._id)

        self.finish_request({"message": "success", "content": edit_request})

    @asynchronous
    @gen.coroutine
    def delete(self, project_name):
        """ Remove a test project"""

        print "DELETE request for : {}".format(project_name)

        # check for an existing project to be deleted
        mongo_dict = yield self.db.test_projects.find_one(
            {'name': project_name})
        test_project = TestProject.testproject_from_dict(mongo_dict)
        if test_project is None:
            raise HTTPError(HTTP_NOT_FOUND,
                            "{} could not be found as a project to be deleted"
                            .format(project_name))

        # just delete it, or maybe save it elsewhere in a future
        res = yield self.db.test_projects.remove(
            {'name': project_name})
        print res

        self.finish_request({"message": "success"})


class TestCasesHandler(GenericApiHandler):
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
        super(TestCasesHandler, self).initialize()

    @asynchronous
    @gen.coroutine
    def get(self, project_name, case_name=None):
        """
        Get testcases(s) info
        :param project_name:
        :param case_name:
        """

        if case_name is None:
            case_name = ""

        get_request = dict()
        get_request["project_name"] = project_name

        if len(case_name) > 0:
            get_request["name"] = case_name

        res = []
        cursor = self.db.test_cases.find(get_request)
        print get_request
        while (yield cursor.fetch_next):
                test_case = TestCase.test_case_from_dict(cursor.next_object())
                res.append(test_case.format_http())

        meta = dict()
        meta["total"] = len(res)
        meta["success"] = True if len(res) > 0 else False

        answer = dict()
        answer["test_cases"] = res
        answer["meta"] = meta

        self.finish_request(answer)

    @asynchronous
    @gen.coroutine
    def post(self, project_name):
        """ Create a test case"""

        print "POST Request for {}".format(project_name)

        if self.json_args is None:
            raise HTTPError(HTTP_BAD_REQUEST,
                            "Check your request payload")

        # retrieve test project
        mongo_dict = yield self.db.test_projects.find_one(
            {"name": project_name})
        if mongo_dict is None:
            raise HTTPError(HTTP_FORBIDDEN,
                            "Could not find project {}"
                            .format(project_name))

        # test_project = TestProject.testproject_from_dict(self.json_args)

        case = TestCase.test_case_from_dict(self.json_args)
        case.project_name = project_name
        case.creation_date = datetime.now()

        future = self.db.test_cases.insert(case.format())
        result = yield future
        case._id = result
        self.finish_request(case.format_http())

    @asynchronous
    @gen.coroutine
    def put(self, project_name, case_name):
        """
        Updates the name and description of a test case
        :raises HTTPError (HTTP_NOT_FOUND, HTTP_FORBIDDEN)
        """

        print "PUT request for : {}/{}".format(project_name, case_name)
        case_request = {'project_name': project_name, 'name': case_name}

        # check if there is a case for the project in url parameters
        mongo_dict = yield self.db.test_cases.find_one(case_request)
        test_case = TestCase.test_case_from_dict(mongo_dict)
        if test_case is None:
            raise HTTPError(HTTP_NOT_FOUND,
                            "{} could not be found as a {} case to be updated"
                            .format(case_name, project_name))

        new_name = self.json_args.get("name")
        new_project_name = self.json_args.get("project_name")
        new_description = self.json_args.get("description")

        # check if there is not an existing test case
        # with the name provided in the json payload
        mongo_dict = yield self.db.test_cases.find_one(
            {'project_name': new_project_name, 'name': new_name})
        if mongo_dict is not None:
            raise HTTPError(HTTP_FORBIDDEN,
                            "{} already exists as a project"
                            .format(new_name))

        # new dict for changes
        request = dict()
        request = prepare_put_request(request,
                                      "name",
                                      new_name,
                                      test_case.name)
        request = prepare_put_request(request,
                                      "project_name",
                                      new_project_name,
                                      test_case.project_name)
        request = prepare_put_request(request,
                                      "description",
                                      new_description,
                                      test_case.description)

        # we raise an exception if there isn't a change
        if not request:
            raise HTTPError(HTTP_FORBIDDEN,
                            "Nothing to update")

        # we merge the whole document """
        edit_request = test_case.format()
        edit_request.update(request)

        """ Updating the DB """
        res = yield self.db.test_cases.update(case_request, edit_request)
        print res
        edit_request["_id"] = str(test_case._id)

        self.finish_request({"message": "success", "content": edit_request})

    @asynchronous
    @gen.coroutine
    def delete(self, project_name, case_name):
        """ Remove a test case"""

        print "DELETE request for : {}/{}".format(project_name, case_name)
        case_request = {'project_name': project_name, 'name': case_name}

        # check for an existing case to be deleted
        mongo_dict = yield self.db.test_cases.find_one(case_request)
        test_project = TestProject.testproject_from_dict(mongo_dict)
        if test_project is None:
            raise HTTPError(HTTP_NOT_FOUND,
                            "{}/{} could not be found as a case to be deleted"
                            .format(project_name, case_name))

        # just delete it, or maybe save it elsewhere in a future
        res = yield self.db.test_projects.remove(case_request)
        print res

        self.finish_request({"message": "success"})


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
         - period : x (x last days)


        :param result_id: Get a result by ID
        :raise HTTPError

        GET /results/project=functest&case=vPing&version=Arno-R1 \
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
        get_request = dict()
        if result_id is None:
            if project_arg is not None:
                get_request["project_name"] = project_arg

            if case_arg is not None:
                get_request["case_name"] = case_arg

            if pod_arg is not None:
                get_request["pod_name"] = pod_arg

            if version_arg is not None:
                get_request["version"] = version_arg

            if installer_arg is not None:
                get_request["installer"] = installer_arg

            if period_arg is not None:
                try:
                    period_arg = int(period_arg)
                except:
                    raise HTTPError(HTTP_BAD_REQUEST)

                if period_arg > 0:
                    period = datetime.now() - timedelta(days=period_arg)
                    obj = {"$gte": period}
                    get_request["creation_date"] = obj
        else:
            get_request["_id"] = result_id

        print get_request
        res = []
        # fetching results
        cursor = self.db.test_results.find(get_request)
        while (yield cursor.fetch_next):
            test_result = TestResult.test_result_from_dict(
                cursor.next_object())
            res.append(test_result.format_http())

        # building meta object
        meta = dict()
        meta["total"] = len(res)

        # final response object
        answer = dict()
        answer["test_results"] = res
        answer["meta"] = meta
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
            raise HTTPError(HTTP_BAD_REQUEST)

        # check for missing parameters in the request payload
        if self.json_args.get("project_name") is None:
            raise HTTPError(HTTP_BAD_REQUEST)
        if self.json_args.get("case_name") is None:
            raise HTTPError(HTTP_BAD_REQUEST)
        # check for pod_name instead of id,
        # keeping id for current implementations
        if self.json_args.get("pod_name") is None:
            raise HTTPError(HTTP_BAD_REQUEST)

        # TODO : replace checks with jsonschema
        # check for project
        mongo_dict = yield self.db.test_projects.find_one(
            {"name": self.json_args.get("project_name")})
        if mongo_dict is None:
            raise HTTPError(HTTP_NOT_FOUND,
                            "Could not find project [{}] "
                            .format(self.json_args.get("project_name")))

        # check for case
        mongo_dict = yield self.db.test_cases.find_one(
            {"name": self.json_args.get("case_name")})
        if mongo_dict is None:
            raise HTTPError(HTTP_NOT_FOUND,
                            "Could not find case [{}] "
                            .format(self.json_args.get("case_name")))

        # check for pod
        mongo_dict = yield self.db.pod.find_one(
            {"name": self.json_args.get("pod_name")})
        if mongo_dict is None:
            raise HTTPError(HTTP_NOT_FOUND,
                            "Could not find POD [{}] "
                            .format(self.json_args.get("pod_name")))

        # convert payload to object
        test_result = TestResult.test_result_from_dict(self.json_args)
        test_result.creation_date = datetime.now()

        future = self.db.test_results.insert(test_result.format(),
                                             check_keys=False)
        result = yield future
        test_result._id = result

        self.finish_request(test_result.format_http())
