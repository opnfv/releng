##############################################################################
# Copyright (c) 2015 Orange
# guyrodrigue.koffi@orange.com / koffirodrigue@gmail.com
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
from opnfv_testapi.tornado_swagger import swagger
from handlers import GenericApiHandler
from opnfv_testapi.common.constants import HTTP_FORBIDDEN
from project_models import Project


class GenericProjectHandler(GenericApiHandler):
    def __init__(self, application, request, **kwargs):
        super(GenericProjectHandler, self).__init__(application,
                                                    request,
                                                    **kwargs)
        self.table = 'projects'
        self.table_cls = Project


class ProjectCLHandler(GenericProjectHandler):
    @swagger.operation(nickname="list-all")
    def get(self):
        """
            @description: list all projects
            @return 200: return all projects, empty list is no project exist
            @rtype: L{Projects}
        """
        self._list()

    @swagger.operation(nickname="create")
    def post(self):
        """
            @description: create a project
            @param body: project to be created
            @type body: L{ProjectCreateRequest}
            @in body: body
            @rtype: L{CreateResponse}
            @return 200: project is created.
            @raise 403: project already exists
            @raise 400:  body or name not provided
        """
        def query(data):
            return {'name': data.name}

        def error(data):
            message = '{} already exists as a project'.format(data.name)
            return HTTP_FORBIDDEN, message

        miss_checks = ['name']
        db_checks = [(self.table, False, query, error)]
        self._create(miss_checks, db_checks)


class ProjectGURHandler(GenericProjectHandler):
    @swagger.operation(nickname='get-one')
    def get(self, project_name):
        """
            @description: get a single project by project_name
            @rtype: L{Project}
            @return 200: project exist
            @raise 404: project not exist
        """
        self._get_one({'name': project_name})

    @swagger.operation(nickname="update")
    def put(self, project_name):
        """
            @description: update a single project by project_name
            @param body: project to be updated
            @type body: L{ProjectUpdateRequest}
            @in body: body
            @rtype: L{Project}
            @return 200: update success
            @raise 404: project not exist
            @raise 403: new project name already exist or nothing to update
        """
        query = {'name': project_name}
        db_keys = ['name']
        self._update(query, db_keys)

    @swagger.operation(nickname='delete')
    def delete(self, project_name):
        """
            @description: delete a project by project_name
            @return 200: delete success
            @raise 404: project not exist
        """
        self._delete({'name': project_name})
