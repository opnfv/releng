##############################################################################
# Copyright (c) 2015 Orange
# guyrodrigue.koffi@orange.com / koffirodrigue@gmail.com
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import handlers
from opnfv_testapi.resources import pod_models
from opnfv_testapi.tornado_swagger import swagger


class GenericPodHandler(handlers.GenericApiHandler):
    def __init__(self, application, request, **kwargs):
        super(GenericPodHandler, self).__init__(application, request, **kwargs)
        self.table = 'pods'
        self.table_cls = pod_models.Pod


class PodCLHandler(GenericPodHandler):
    @swagger.operation(nickname='listAllPods')
    def get(self):
        """
            @description: list all pods
            @return 200: list all pods, empty list is no pod exist
            @rtype: L{Pods}
        """
        self._list()

    @swagger.operation(nickname='createPod')
    def post(self):
        """
            @description: create a pod
            @param body: pod to be created
            @type body: L{PodCreateRequest}
            @in body: body
            @rtype: L{CreateResponse}
            @return 200: pod is created.
            @raise 403: pod already exists
            @raise 400: body or name not provided
        """
        def query():
            return {'name': self.json_args.get('name')}
        miss_fields = ['name']
        self._create(miss_fields=miss_fields, query=query)


class PodGURHandler(GenericPodHandler):
    @swagger.operation(nickname='getPodByName')
    def get(self, pod_name):
        """
            @description: get a single pod by pod_name
            @rtype: L{Pod}
            @return 200: pod exist
            @raise 404: pod not exist
        """
        self._get_one(query={'name': pod_name})

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
