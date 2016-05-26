from tornado import gen
from tornado.web import HTTPError, asynchronous

from tornado_swagger_ui.tornado_swagger import swagger
from handlers import GenericApiHandler
from common.constants import HTTP_BAD_REQUEST, HTTP_FORBIDDEN
from pod_models import Pod


class PodCLHandler(GenericApiHandler):
    def initialize(self):
        super(PodCLHandler, self).initialize()

    @swagger.operation(nickname='list-all')
    def get(self):
        """
            @description: list all PODs
            @return 200: list all pods, empty list is no pod exist
            @rtype: L{Pods}
        """
        self._list('pods', Pod)

    # @asynchronous
    @gen.coroutine
    @swagger.operation(nickname='create')
    def post(self):
        """
            @description: Create a POD
            @param body: pod information to be created
            @type body: L{PodCreateRequest}
            @in body: body
            @return 200: pod is created.
            @rtype: L{Pod}
            @raise 403: already exists as a pod
            @raise 400: bad request
        """
        if self.json_args is None:
            raise HTTPError(HTTP_BAD_REQUEST, 'no payload')

        pod = Pod.from_dict(self.json_args)
        name = pod.name
        if name is None or name == '':
            raise HTTPError(HTTP_BAD_REQUEST, 'pod name missing')

        the_pod = yield self.db.pods.find_one({'name': name})
        if the_pod is not None:
            raise HTTPError(HTTP_FORBIDDEN,
                            "{} already exists as a pod".format(
                                self.json_args.get("name")))
        self._create('pods', pod, name)


class PodGURHandler(GenericApiHandler):
    def initialize(self):
        super(PodGURHandler, self).initialize()

    @swagger.operation(nickname='get-one')
    def get(self, pod_name=None):
        """
            @description: Get a single pod by pod_name
            @return 200: pod exist
            @raise 404: pod not exist
            @rtype: L{Pod}
        """
        query = dict()
        query["name"] = pod_name
        self._get_one('pods', Pod, query)

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
