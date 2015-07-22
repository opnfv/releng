##############################################################################
# Copyright (c) 2015 Orange
# guyrodrigue.koffi@orange.com / koffirodrigue@gmail.com
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

from tornado.web import RequestHandler, asynchronous, HTTPError
from tornado import gen
from models import Pod, TestProject
from common.constants import APPLICATION_JSON, HTTP_BAD_REQUEST, HTTP_NOT_FOUND, HTTP_FORBIDDEN
from common.config import prepare_put_request
import json
from datetime import datetime


class GenericApiHandler(RequestHandler):
    """
    The purpose of this class is to take benefit of inheritance and prepare a set of common functions for
    the handlers
    """
    def initialize(self):
        """ Prepares the database for the entire class """
        self.name = "test_project"

    def prepare(self):
        if not (self.request.method == "GET"):
            if not (self.request.headers.get("Content-Type") is None):
                if self.request.headers["Content-Type"].startswith(APPLICATION_JSON):
                    self.json_args = json.loads(self.request.body)
                else:
                    self.json_args = None

    def finish_request(self, json_object):
        self.write(json.dumps(json_object))
        self.set_header("Content-Type", APPLICATION_JSON)
        self.finish()


class VersionHandler(RequestHandler):
    """ Display a nice message for the API version """
    def get(self):
        self.write("Collecttion of test result API, v1")


class PodHandler(GenericApiHandler):
    """ Handle the requests about the POD Platforms """

    def initialize(self):
        """ Prepares the database for the entire class """
        super(PodHandler, self).initialize()
        self.name = "pod"

    @asynchronous
    @gen.coroutine
    def get(self, pod_id=None):
        """ Get all pods or a single pod """
        if pod_id is None:
            pod_id = ""

        if len(pod_id) == 0:
            res = []
            cursor = self.db.pod.find()
            while (yield cursor.fetch_next):
                pod = Pod.pod_from_dict(cursor.next_object())
                res.append(pod.format())
            self.finish_request(res)
        else:
            pod = yield self.db.pod.find_one({'_id': int(pod_id)})
            if pod is None:
                raise HTTPError(HTTP_NOT_FOUND)
            self.finish_request(pod)


class TestProjectHandler(GenericApiHandler):
    """
    TestProjectHandler Class
    Handle the requests about the Test projects
    HTTP Methdods :
        - GET : Get all test projects and details about a specific one
        - POST : Add a test project
        - PUT : Edit test projects information (name and/or description)
    """

    def initialize(self):
        """ Prepares the database for the entire class """
        super(TestProjectHandler, self).initialize()
        self.name = "test_project"

    """ Get Project(s) info """
    @asynchronous
    @gen.coroutine
    def get(self, project_name=None):
        print "Project Name : {}".format(project_name)
        if project_name is None:
            project_name = ""

        if len(project_name) == 0:
            res = []
            cursor = self.db.test_projects.find()
            while (yield cursor.fetch_next):
                test_project = TestProject.testproject_from_dict(cursor.next_object())
                res.append(test_project.format_http())
            self.finish_request(res)
        else:
            mongo_dict = yield self.db.test_projects.find_one({'name': project_name})
            test_project = TestProject.testproject_from_dict(mongo_dict)
            if test_project is None:
                raise HTTPError(HTTP_NOT_FOUND)
            self.finish_request(test_project.format_http())

    @asynchronous
    @gen.coroutine
    def post(self):
        """ Create a test project"""

        if self.json_args is None:
            raise HTTPError(HTTP_BAD_REQUEST)

        """check for name in db """
        mongo_dict = yield self.db.test_projects.find_one({"name": self.json_args.get("name")})
        if not (mongo_dict is None):
            raise HTTPError(HTTP_FORBIDDEN,
                            "{} already exists as a project".format(self.json_args.get("name")))

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

        mongo_dict = yield self.db.test_projects.find_one({'name': project_name})
        test_project = TestProject.testproject_from_dict(mongo_dict)
        if test_project is None:
            raise HTTPError(HTTP_NOT_FOUND,
                            "{} could not be found as a project to be updated".format(project_name))

        new_name = self.json_args.get("name")
        new_description = self.json_args.get("description")

        """check for name in db """
        mongo_dict = yield self.db.test_projects.find_one({"name": new_name})
        if not (mongo_dict is None):
            raise HTTPError(HTTP_FORBIDDEN,
                            "{} already exists as a project".format(new_name))

        """ new dictionnary for changes """
        request = dict()
        request = prepare_put_request(request, "name", new_name, test_project.name)
        request = prepare_put_request(request, "description", new_description, test_project.description)

        """ raise exception if there isn't a change """
        if not request:
            raise HTTPError(HTTP_FORBIDDEN,
                            "Nothing to update")

        """ we merge the whole document """
        edit_request = test_project.format()
        edit_request.update(request)

        """ Updating the DB """
        res = yield self.db.test_projects.update({'name': project_name}, edit_request)
        print res
        edit_request["_id"] = str(test_project._id)

        self.finish_request({"message": "success", "content": edit_request})


class TestCasesHandler(GenericApiHandler):
    """
    TestCasesHandler Class
    Handle the requests about the Test cases for test projects
    HTTP Methdods :
        - GET : Get all test cases and details about a specific one
        - POST : Add a test project
        - PUT : Edit test projects information (name and/or description)
    """
    pass