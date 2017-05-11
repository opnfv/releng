##############################################################################
# Copyright (c) 2015 Orange
# guyrodrigue.koffi@orange.com / koffirodrigue@gmail.com
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

from opnfv_testapi.resources import handlers
from opnfv_testapi.resources import project_models
from opnfv_testapi.tornado_swagger import swagger


class GenericProjectHandler(handlers.GenericApiHandler):
    def __init__(self, application, request, **kwargs):
        super(GenericProjectHandler, self).__init__(application,
                                                    request,
                                                    **kwargs)
        self.table = 'projects'
        self.table_cls = project_models.Project


class ProjectCLHandler(GenericProjectHandler):
    @swagger.operation(nickname="listAllProjects")
    def get(self):
        """
            @description: list all projects
            @return 200: return all projects, empty list is no project exist
            @rtype: L{Projects}
        """
        self._list()

    @swagger.operation(nickname="createProject")
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
        def query():
            return {'name': self.json_args.get('name')}
        miss_fields = ['name']
        self._create(miss_fields=miss_fields, query=query)


class ProjectGURHandler(GenericProjectHandler):
    @swagger.operation(nickname='getProjectByName')
    def get(self, project_name):
        """
            @description: get a single project by project_name
            @rtype: L{Project}
            @return 200: project exist
            @raise 404: project not exist
        """
        self._get_one(query={'name': project_name})

    @swagger.operation(nickname="updateProjectByName")
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
        self._update(query=query, db_keys=db_keys)

    @swagger.operation(nickname='deleteProjectByName')
    def delete(self, project_name):
        """
            @description: delete a project by project_name
            @return 200: delete success
            @raise 404: project not exist
        """
        self._delete(query={'name': project_name})
