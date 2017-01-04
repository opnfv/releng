##############################################################################
# Copyright (c) 2015 Orange
# guyrodrigue.koffi@orange.com / koffirodrigue@gmail.com
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
from opnfv_testapi.common.constants import HTTP_FORBIDDEN
from opnfv_testapi.resources.handlers import GenericApiHandler
from opnfv_testapi.resources.testcase_models import Testcase
from opnfv_testapi.tornado_swagger import swagger


class GenericTestcaseHandler(GenericApiHandler):
    def __init__(self, application, request, **kwargs):
        super(GenericTestcaseHandler, self).__init__(application,
                                                     request,
                                                     **kwargs)
        self.table = self.db_testcases
        self.table_cls = Testcase


class TestcaseCLHandler(GenericTestcaseHandler):
    @swagger.operation(nickname="List all TestCases by project_name")
    def get(self, project_name):
        """
            @description: list all testcases of a project by project_name
            @return 200: return all testcases of this project,
                         empty list is no testcase exist in this project
            @rtype: L{TestCases}
        """
        query = dict()
        query['project_name'] = project_name
        self._list(query)

    @swagger.operation(nickname="Create a TestCase by project_name")
    def post(self, project_name):
        """
            @description: create a testcase of a project by project_name
            @param body: testcase to be created
            @type body: L{TestcaseCreateRequest}
            @in body: body
            @rtype: L{CreateResponse}
            @return 200: testcase is created in this project.
            @raise 403: project not exist
                        or testcase already exists in this project
            @raise 400: body or name not provided
        """
        def p_query(data):
            return {'name': data.project_name}

        def tc_query(data):
            return {
                'project_name': data.project_name,
                'name': data.name
            }

        def p_error(data):
            message = 'Could not find project [{}]'.format(data.project_name)
            return HTTP_FORBIDDEN, message

        def tc_error(data):
            message = '{} already exists as a testcase in project {}'\
                .format(data.name, data.project_name)
            return HTTP_FORBIDDEN, message

        miss_checks = ['name']
        db_checks = [(self.db_projects, True, p_query, p_error),
                     (self.db_testcases, False, tc_query, tc_error)]
        self._create(miss_checks, db_checks, project_name=project_name)


class TestcaseGURHandler(GenericTestcaseHandler):
    @swagger.operation(nickname='Get a TestCase by project and case name')
    def get(self, project_name, case_name):
        """
            @description: get a single testcase
                            by case_name and project_name
            @rtype: L{Testcase}
            @return 200: testcase exist
            @raise 404: testcase not exist
        """
        query = dict()
        query['project_name'] = project_name
        query["name"] = case_name
        self._get_one(query)

    @swagger.operation(nickname="Update a TestCase by project and case name")
    def put(self, project_name, case_name):
        """
            @description: update a single testcase
                            by project_name and case_name
            @param body: testcase to be updated
            @type body: L{TestcaseUpdateRequest}
            @in body: body
            @rtype: L{Project}
            @return 200: update success
            @raise 404: testcase or project not exist
            @raise 403: new testcase name already exist in project
                        or nothing to update
        """
        query = {'project_name': project_name, 'name': case_name}
        db_keys = ['name', 'project_name']
        self._update(query, db_keys)

    @swagger.operation(nickname='Delete a TestCase by project and case name')
    def delete(self, project_name, case_name):
        """
            @description: delete a testcase by project_name and case_name
            @return 200: delete success
            @raise 404: testcase not exist
        """
        query = {'project_name': project_name, 'name': case_name}
        self._delete(query)
