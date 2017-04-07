##############################################################################
# Copyright (c) 2015 Orange
# guyrodrigue.koffi@orange.com / koffirodrigue@gmail.com
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

from opnfv_testapi.resources import handlers
from opnfv_testapi.resources import testcase_models
from opnfv_testapi.tornado_swagger import swagger


class GenericTestcaseHandler(handlers.GenericApiHandler):
    def __init__(self, application, request, **kwargs):
        super(GenericTestcaseHandler, self).__init__(application,
                                                     request,
                                                     **kwargs)
        self.table = self.db_testcases
        self.table_cls = testcase_models.Testcase


class TestcaseCLHandler(GenericTestcaseHandler):
    @swagger.operation(nickname="listAllTestCases")
    def get(self, project_name):
        """
            @description: list all testcases of a project by project_name
            @return 200: return all testcases of this project,
                         empty list is no testcase exist in this project
            @rtype: L{TestCases}
        """
        self._list(query={'project_name': project_name})

    @swagger.operation(nickname="createTestCase")
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
        def project_query():
            return {'name': project_name}

        def testcase_query():
            return {'project_name': project_name,
                    'name': self.json_args.get('name')}
        miss_fields = ['name']
        carriers = [(self.db_projects, project_query)]
        self._create(miss_fields=miss_fields,
                     carriers=carriers,
                     query=testcase_query,
                     project_name=project_name)


class TestcaseGURHandler(GenericTestcaseHandler):
    @swagger.operation(nickname='getTestCaseByName')
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
        self._get_one(query=query)

    @swagger.operation(nickname="updateTestCaseByName")
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
        self._update(query=query, db_keys=db_keys)

    @swagger.operation(nickname='deleteTestCaseByName')
    def delete(self, project_name, case_name):
        """
            @description: delete a testcase by project_name and case_name
            @return 200: delete success
            @raise 404: testcase not exist
        """
        query = {'project_name': project_name, 'name': case_name}
        self._delete(query=query)
