from tornado import gen
from tornado.web import asynchronous

from tornado_swagger_ui.tornado_swagger import swagger
from handlers import GenericApiHandler
from pod_models import Pod


class GenericPodHandler(GenericApiHandler):
    def __init__(self, application, request, **kwargs):
        super(GenericPodHandler, self).__init__(application, request, **kwargs)
        self.table = 'pods'
        self.table_cls = Pod


class PodCLHandler(GenericPodHandler):
    @swagger.operation(nickname='list-all')
    def get(self):
        """
            @description: list all pods
            @return 200: list all pods, empty list is no pod exist
            @rtype: L{Pods}
        """
        self._list()

    @gen.coroutine
    @swagger.operation(nickname='create')
    def post(self):
        """
            @description: create a pod
            @param body: pod to be created
            @type body: L{PodCreateRequest}
            @in body: body
            @rtype: L{Pod}
            @return 200: pod is created.
            @raise 403: pod already exists
            @raise 400: post without body
        """
        self._create('{} already exists as a {}')


class PodGURHandler(GenericPodHandler):
    @swagger.operation(nickname='get-one')
    def get(self, pod_name):
        """
            @description: get a single pod by pod_name
            @rtype: L{Pod}
            @return 200: pod exist
            @raise 404: pod not exist
        """
        query = dict()
        query['name'] = pod_name
        self._get_one(query)

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
