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
from datetime import datetime

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
            if not (self.request.headers.get("Content-Type") is None):
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
    """

    def initialize(self):
        """ Prepares the database for the entire class """
        super(PodHandler, self).initialize()

    @asynchronous
    @gen.coroutine
    def get(self, pod_id=None):
        """
        Get all pods or a single pod
        :param pod_id:
        """

        if pod_id is None:
            pod_id = ""

        get_request = dict()

        if len(pod_id) > 0:
            get_request["_id"] = int(pod_id)

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
        if not (mongo_dict is None):
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
            if not (mongo_dict is None):
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

        # check for an existing case to be deleted
        mongo_dict = yield self.db.test_cases.find_one(
            {'project_name': project_name})
        test_project = TestProject.testproject_from_dict(mongo_dict)
        if test_project is None:
            raise HTTPError(HTTP_NOT_FOUND,
                            "{} could not be found as a project to be deleted"
                            .format(project_name))

        # just delete it, or maybe save it elsewhere in a future
        res = yield self.db.test_projects.remove(
            {'project_name': project_name})
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
        if not (mongo_dict is None):
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
         - pod : pod ID

        :param result_id: Get a result by ID
        :raise HTTPError

        GET /results/project=functest&case=keystone.catalog&pod=1
        => get results with optional filters
        """

        project_arg = self.get_query_argument("project", None)
        case_arg = self.get_query_arguments("case", None)
        pod_arg = self.get_query_arguments("pod", None)

        # prepare request
        get_request = dict()
        if result_id is None:
            if not (project_arg is None):
                get_request["project_name"] = project_arg

            if not (case_arg is None):
                get_request["case_name"] = case_arg

            if not (pod_arg is None):
                get_request["pod_id"] = pod_arg
        else:
            get_request["_id"] = result_id

        res = []
        # fetching results
        cursor = self.db.test_cases.find(get_request)
        while (yield cursor.fetch_next):
            test_case = TestCase.test_case_from_dict(cursor.next_object)
            res.append(test_case.format_http())

        # building meta object
        meta = dict()
        meta["total"] = res.count()

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
        if self.json_args.get("pod_id") is None:
            raise HTTPError(HTTP_BAD_REQUEST)

        # TODO : replace checks with jsonschema
        # check for project
        mongo_dict = yield self.db.test_projects.find_one(
            {"name": self.json_args.get("project_name")})
        if not (mongo_dict is None):
            raise HTTPError(HTTP_NOT_FOUND,
                            "Could not find project [{}] "
                            .format(self.json_args.get("project_name")))

        # check for case
        mongo_dict = yield self.db.test_cases.find_one(
            {"name": self.json_args.get("case_name")})
        if not (mongo_dict is None):
            raise HTTPError(HTTP_NOT_FOUND,
                            "Could not find case [{}] "
                            .format(self.json_args.get("case_name")))

        # check for pod
        mongo_dict = yield self.db.pod.find_one(
            {"_id": self.json_args.get("pod_id")})
        if not (mongo_dict is None):
            raise HTTPError(HTTP_NOT_FOUND,
                            "Could not find POD [{}] "
                            .format(self.json_args.get("pod_id")))

        # convert payload to object
        test_result = TestResult.test_result_from_dict(self.json_args)
        test_result.creation_date = datetime.now()

        future = self.db.test_results.insert(test_result.format())
        result = yield future
        test_result._id = result

        self.finish_request(test_result.format_http())
